"""
Cohort management router for Sigmatch.
Handles cohort listing and synthetic data generation.
"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    CohortAssembleRequest,
    CohortAssembleResponse,
    CohortDetailResponse,
    CohortGenerateRequest,
    CohortGenerateResponse,
    CohortListResponse,
    CohortSummary,
    MatchedPatient,
    Patient
)
from app.services import file_ops, synthetic_data


router = APIRouter(prefix="/api/cohorts", tags=["cohorts"])

COHORTS_DIR = "config_files/pipeline_json_files"


@router.get("", response_model=CohortListResponse)
async def list_cohorts() -> CohortListResponse:
    """
    List all available cohort files.
    Returns filename and patient count for each cohort.
    """
    try:
        cohort_files = file_ops.list_files(COHORTS_DIR, ".json")
        cohorts = []
        
        for filename in cohort_files:
            try:
                patients = file_ops.read_json_list(f"{COHORTS_DIR}/{filename}")
                cohorts.append(CohortSummary(
                    filename=filename,
                    patient_count=len(patients)
                ))
            except Exception:
                # Skip files that can't be parsed
                continue
        
        return CohortListResponse(cohorts=cohorts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing cohorts: {str(e)}")


@router.get("/{filename}", response_model=CohortDetailResponse)
async def get_cohort(filename: str) -> CohortDetailResponse:
    """
    Get details of a specific cohort, including patient list.
    """
    try:
        filepath = f"{COHORTS_DIR}/{filename}"
        
        if not file_ops.file_exists(filepath):
            raise HTTPException(status_code=404, detail=f"Cohort file not found: {filename}")
        
        patients_data = file_ops.read_json_list(filepath)
        
        patients = [
            Patient(
                patient_id=p.get("patient_id", f"P{i+1:03d}"),
                full_text=p.get("full_text", "")
            )
            for i, p in enumerate(patients_data)
        ]
        
        return CohortDetailResponse(
            filename=filename,
            patients=patients,
            patient_count=len(patients)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading cohort: {str(e)}")


@router.post("/generate", response_model=CohortGenerateResponse)
async def generate_cohort(request: CohortGenerateRequest) -> CohortGenerateResponse:
    """
    Generate a synthetic cohort with dummy patient data.
    """
    try:
        # Generate synthetic patients
        patients = synthetic_data.generate_dummy_patients(request.patient_count)
        
        # Determine filename
        filename = f"{request.name}.json"
        filepath = f"{COHORTS_DIR}/{filename}"
        
        # Save the cohort
        file_ops.write_json(filepath, patients)
        
        return CohortGenerateResponse(
            status="generated",
            filename=filename,
            patient_count=len(patients)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cohort: {str(e)}")


def extract_keywords(criteria_text: str) -> list[str]:
    """
    Extract meaningful keywords from a criteria string.
    Removes common words and returns lowercase keywords.
    """
    # Common words to exclude (stop words)
    stop_words = {
        "i", "want", "patients", "who", "are", "is", "the", "a", "an", "and", 
        "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from",
        "as", "that", "this", "it", "be", "have", "has", "had", "was", "were",
        "been", "being", "will", "would", "should", "could", "may", "might",
        "must", "can", "do", "does", "did", "not", "no", "yes", "all", "any",
        "some", "there", "their", "they", "them", "these", "those", "which",
        "what", "when", "where", "why", "how", "received"
    }
    
    # Split by common separators and convert to lowercase
    words = criteria_text.lower().replace(",", " ").replace(".", " ").split()
    
    # Filter out stop words and short words
    keywords = [word.strip() for word in words if word.strip() and word.strip() not in stop_words and len(word.strip()) > 2]
    
    return keywords


@router.post("/assemble", response_model=CohortAssembleResponse)
async def assemble_cohort(request: CohortAssembleRequest) -> CohortAssembleResponse:
    """
    Assemble a cohort by filtering patients based on criteria.
    Searches patient full_text for keywords extracted from all criteria.
    All criteria must match (AND logic).
    """
    try:
        # Load the source cohort
        filepath = f"{COHORTS_DIR}/{request.cohort_source}"
        
        if not file_ops.file_exists(filepath):
            raise HTTPException(
                status_code=404, 
                detail=f"Cohort file not found: {request.cohort_source}"
            )
        
        patients_data = file_ops.read_json_list(filepath)
        
        # Limit to max_patients for searching
        patients_to_search = patients_data[:request.max_patients]
        
        # Extract keywords from each criterion
        criteria_keywords = []
        for criterion in request.criteria:
            keywords = extract_keywords(criterion)
            if keywords:  # Only add if we found keywords
                criteria_keywords.append({
                    "original": criterion,
                    "keywords": keywords
                })
        
        # Match patients
        matched_patients = []
        
        for patient in patients_to_search:
            patient_id = patient.get("patient_id", "Unknown")
            full_text = patient.get("full_text", "").lower()
            
            # Check if patient matches ALL criteria (AND logic)
            match_reasons = []
            all_criteria_met = True
            
            for criteria_item in criteria_keywords:
                # Check if ANY keyword from this criterion appears in the text
                matching_keywords = [
                    kw for kw in criteria_item["keywords"] 
                    if kw in full_text
                ]
                
                if matching_keywords:
                    match_reasons.append(
                        f"Matches '{criteria_item['original']}' (found: {', '.join(matching_keywords)})"
                    )
                else:
                    all_criteria_met = False
                    break
            
            # If all criteria are met, add to matched patients
            if all_criteria_met and match_reasons:
                matched_patients.append(MatchedPatient(
                    patient_id=patient_id,
                    match_reasons=match_reasons
                ))
        
        # Extract patient IDs for convenience
        patient_ids_list = [p.patient_id for p in matched_patients]
        
        return CohortAssembleResponse(
            status="success",
            criteria_used=request.criteria,
            total_searched=len(patients_to_search),
            matched_count=len(matched_patients),
            matched_patients=matched_patients,
            patient_ids_list=patient_ids_list
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error assembling cohort: {str(e)}"
        )

