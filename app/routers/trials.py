"""
Trial management router for Sigmatch.
Handles trial file listing, creation, and upload.
"""
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Any, Dict

from app.models.schemas import (
    TrialCreate,
    TrialCreateResponse,
    TrialListResponse,
    TrialResponse,
    TrialSummary,
    TrialUploadResponse
)
from app.services import file_ops


router = APIRouter(prefix="/api/trials", tags=["trials"])

TRIALS_DIR = "config_files/trial_files"


@router.get("", response_model=TrialListResponse)
async def list_trials() -> TrialListResponse:
    """
    List all available trial files.
    Returns filename, title, and _id for each trial.
    """
    try:
        trial_files = file_ops.list_files(TRIALS_DIR, ".json")
        trials = []
        
        for filename in trial_files:
            try:
                trial_data = file_ops.read_json(f"{TRIALS_DIR}/{filename}")
                trials.append(TrialSummary(
                    filename=filename,
                    title=trial_data.get("title", "Untitled Trial"),
                    id=trial_data.get("_id", filename.replace(".json", ""))
                ))
            except Exception:
                # Skip files that can't be parsed
                continue
        
        return TrialListResponse(trials=trials)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing trials: {str(e)}")


@router.get("/{filename}", response_model=TrialResponse)
async def get_trial(filename: str) -> TrialResponse:
    """
    Get full content of a specific trial file.
    """
    try:
        filepath = f"{TRIALS_DIR}/{filename}"
        
        if not file_ops.file_exists(filepath):
            raise HTTPException(status_code=404, detail=f"Trial file not found: {filename}")
        
        trial_data = file_ops.read_json(filepath)
        
        return TrialResponse(
            id=trial_data.get("_id", filename.replace(".json", "")),
            title=trial_data.get("title", "Untitled Trial"),
            full_text=trial_data.get("full_text", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading trial: {str(e)}")


@router.post("", response_model=TrialCreateResponse)
async def create_trial(trial: TrialCreate) -> TrialCreateResponse:
    """
    Create a new trial file from provided data.
    Auto-generates _id if not provided.
    """
    try:
        # Generate _id if not provided
        trial_id = trial.id
        if not trial_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trial_id = f"trial_{timestamp}"
        
        # Create trial data
        trial_data = {
            "_id": trial_id,
            "title": trial.title,
            "full_text": trial.full_text
        }
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() else "_" for c in trial.title[:30])
        filename = f"{safe_title}_{timestamp}.json"
        filepath = f"{TRIALS_DIR}/{filename}"
        
        # Save the trial
        file_ops.write_json(filepath, trial_data)
        
        return TrialCreateResponse(
            status="created",
            filename=filename,
            path=filepath
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating trial: {str(e)}")


@router.post("/upload", response_model=TrialUploadResponse)
async def upload_trial(file: UploadFile = File(...)) -> TrialUploadResponse:
    """
    Upload a trial JSON file.
    Validates the file structure and saves it.
    """
    try:
        # Validate file extension
        if not file.filename.endswith(".json"):
            raise HTTPException(status_code=400, detail="File must be a JSON file")
        
        # Read and parse the file
        content = await file.read()
        try:
            trial_data = json.loads(content.decode("utf-8"))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
        
        # Validate required fields
        if "full_text" not in trial_data:
            raise HTTPException(status_code=400, detail="Trial must have 'full_text' field")
        
        # Add _id if not present
        if "_id" not in trial_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trial_data["_id"] = f"uploaded_{timestamp}"
        
        # Add title if not present
        if "title" not in trial_data:
            trial_data["title"] = file.filename.replace(".json", "")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = file.filename.replace(".json", "")
        filename = f"{base_name}_{timestamp}.json"
        filepath = f"{TRIALS_DIR}/{filename}"
        
        # Save the file
        file_ops.write_json(filepath, trial_data)
        
        return TrialUploadResponse(
            status="uploaded",
            filename=filename,
            trial=trial_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading trial: {str(e)}")

