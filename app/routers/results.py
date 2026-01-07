"""
Results router for Sigmatch.
Handles matching results summary, download, and detailed views.
"""
import csv
import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    MatchingResult,
    ResultsDetailedResponse,
    ResultsSummaryResponse
)
from app.services import config_manager, file_ops, synthetic_data


router = APIRouter(prefix="/api/results", tags=["results"])


def _parse_results_csv(filepath: str) -> list:
    """Parse matching results CSV file."""
    try:
        results = file_ops.read_csv(filepath)
        return results
    except Exception:
        return []


def _get_dummy_summary() -> ResultsSummaryResponse:
    """Generate dummy summary when no results exist."""
    return ResultsSummaryResponse(
        has_results=False,
        cohort_name="no_cohort",
        total_patients=0,
        matched_count=0,
        not_matched_count=0,
        match_percentage=0.0,
        score_distribution={
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0,
            "5": 0
        }
    )


@router.get("/summary", response_model=ResultsSummaryResponse)
async def get_results_summary() -> ResultsSummaryResponse:
    """
    Get matching results summary for visualization.
    
    Reads from the matching_result_dir specified in active config.
    Returns dummy data if no results exist.
    """
    try:
        # Get active config
        config = config_manager.get_active_config()
        cohort_name = config.get("cohortName", "unknown")
        matching_result_dir = config.get("matching_result_dir", "")
        
        # Look for matching_results.csv
        results_file = f"{matching_result_dir}/matching_results.csv"
        
        # Debug logging
        print(f"DEBUG: Looking for results file at: {results_file}")
        print(f"DEBUG: Cohort name: {cohort_name}")
        print(f"DEBUG: Full path: {file_ops.get_full_path(results_file)}")
        print(f"DEBUG: File exists: {file_ops.file_exists(results_file)}")
        
        if not file_ops.file_exists(results_file):
            print(f"WARN: Results file not found, returning dummy data")
            return _get_dummy_summary()
        
        # Parse results
        results = _parse_results_csv(results_file)
        
        if not results:
            return _get_dummy_summary()
        
        # Calculate summary statistics
        total_patients = len(results)
        matched_count = sum(1 for r in results if r.get("final_decision", "").upper() == "MATCH")
        not_matched_count = total_patients - matched_count
        match_percentage = (matched_count / total_patients * 100) if total_patients > 0 else 0.0
        
        # Calculate score distribution
        score_distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        for r in results:
            try:
                score = str(int(r.get("overall_score", 0)))
                if score in score_distribution:
                    score_distribution[score] += 1
            except (ValueError, TypeError):
                pass
        
        return ResultsSummaryResponse(
            has_results=True,
            cohort_name=cohort_name,
            total_patients=total_patients,
            matched_count=matched_count,
            not_matched_count=not_matched_count,
            match_percentage=round(match_percentage, 1),
            score_distribution=score_distribution
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading results: {str(e)}")


@router.get("/download")
async def download_results():
    """
    Download the matching results CSV file.
    Returns dummy CSV if no results exist.
    """
    try:
        # Get active config
        config = config_manager.get_active_config()
        matching_result_dir = config.get("matching_result_dir", "")
        
        # Look for matching_results.csv
        results_file = f"{matching_result_dir}/matching_results.csv"
        
        if file_ops.file_exists(results_file):
            # Read the actual file
            full_path = file_ops.get_full_path(results_file)
            
            def iterfile():
                with open(full_path, "rb") as f:
                    yield from f
            
            return StreamingResponse(
                iterfile(),
                media_type="text/csv",
                headers={
                    "Content-Disposition": "attachment; filename=matching_results.csv"
                }
            )
        else:
            # Generate dummy CSV
            dummy_results = synthetic_data.generate_dummy_results(
                [f"P{i:03d}" for i in range(1, 11)]
            )
            
            # Create CSV in memory
            output = io.StringIO()
            fieldnames = ["patient_id", "final_decision", "overall_score", 
                         "primary_reasons", "concerns", "decision_reasoning"]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(dummy_results)
            
            csv_content = output.getvalue()
            
            return StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": "attachment; filename=dummy_matching_results.csv"
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading results: {str(e)}")


@router.get("/detailed", response_model=ResultsDetailedResponse)
async def get_detailed_results() -> ResultsDetailedResponse:
    """
    Get full matching results data.
    Returns all fields from matching_results.csv.
    """
    try:
        # Get active config
        config = config_manager.get_active_config()
        matching_result_dir = config.get("matching_result_dir", "")
        
        # Look for matching_results.csv
        results_file = f"{matching_result_dir}/matching_results.csv"
        
        if not file_ops.file_exists(results_file):
            # Return empty results
            return ResultsDetailedResponse(results=[])
        
        # Parse results
        results_data = _parse_results_csv(results_file)
        
        results = []
        for r in results_data:
            try:
                result = MatchingResult(
                    patient_id=r.get("patient_id", ""),
                    final_decision=r.get("final_decision", ""),
                    overall_score=int(r.get("overall_score", 0)),
                    primary_reasons=r.get("primary_reasons", ""),
                    concerns=r.get("concerns", ""),
                    decision_reasoning=r.get("decision_reasoning", "")
                )
                results.append(result)
            except (ValueError, TypeError):
                # Skip malformed rows
                continue
        
        return ResultsDetailedResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading detailed results: {str(e)}")

