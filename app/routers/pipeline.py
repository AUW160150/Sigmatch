"""
Pipeline execution router for Sigmatch.
Generates pipeline command strings (does NOT execute them).
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models.schemas import (
    PipelineRunRequest,
    PipelineRunResponse,
    PipelineStatusResponse
)
from app.services import config_manager, file_ops


router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


# In-memory storage for pipeline status (placeholder for future implementation)
_pipeline_status = {
    "status": "idle",
    "last_run": None,
    "last_command": None
}


@router.post("/run", response_model=PipelineRunResponse)
async def run_pipeline(request: PipelineRunRequest) -> PipelineRunResponse:
    """
    Generate the pipeline command string.
    
    Does NOT execute the pipeline - returns the command for the user to run.
    """
    try:
        # Build the command string
        command_parts = [
            "python orchestrate_pipeline.py",
            f"--data_config_json {request.config_path}",
            f"--run_ocr {request.run_ocr}",
            f"--do_llm_summarization {request.do_llm_summarization}",
            f"--do_patient_matching {request.do_patient_matching}",
            f"--do_evaluation {request.do_evaluation}"
        ]
        
        command = " ".join(command_parts)
        
        # Print command to console for user to run
        print(f"\n{'='*80}")
        print(f"PIPELINE COMMAND TO RUN:")
        print(f"{command}")
        print(f"{'='*80}\n")
        
        # Get the config that will be used
        try:
            config_used = config_manager.get_active_config()
        except Exception:
            config_used = {"error": "Could not read config file"}
        
        # Update status (for future tracking)
        _pipeline_status["last_command"] = command
        
        return PipelineRunResponse(
            command=command,
            config_used=config_used
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating pipeline command: {str(e)}")


@router.get("/status", response_model=PipelineStatusResponse)
async def get_pipeline_status() -> PipelineStatusResponse:
    """
    Get the current pipeline status.
    
    This is a placeholder for future implementation.
    Real implementation would track actual pipeline execution.
    """
    return PipelineStatusResponse(
        status=_pipeline_status["status"],
        last_run=_pipeline_status["last_run"],
        last_command=_pipeline_status["last_command"]
    )

