"""
Config management router for Sigmatch.
Handles GET/POST /api/config and POST /api/config/snapshot endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from app.models.schemas import (
    ConfigResponse, 
    ConfigSaveResponse, 
    DataConfig,
    SnapshotResponse
)
from app.services import config_manager, file_ops


router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("", response_model=ConfigResponse)
async def get_config() -> ConfigResponse:
    """
    Get the current active configuration.
    Creates default config if it doesn't exist.
    """
    try:
        config = config_manager.get_active_config()
        last_modified = config_manager.get_active_config_modified_time()
        
        return ConfigResponse(
            config=config,
            last_modified=last_modified
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading config: {str(e)}")


@router.post("", response_model=ConfigSaveResponse)
async def save_config(config: DataConfig) -> ConfigSaveResponse:
    """
    Save configuration with versioning.
    
    1. Validates the config
    2. Auto-generates paths based on cohortName
    3. Creates directories if they don't exist
    4. Saves versioned copy
    5. Updates active_data_config.json
    """
    try:
        # Convert Pydantic model to dict
        config_dict = config.model_dump(exclude_none=True)
        
        # Debug logging
        print(f"DEBUG: Received config: {config_dict}")
        
        # Save config and get filenames
        version_file, active_file = config_manager.save_config(config_dict)
        
        return ConfigSaveResponse(
            status="saved",
            version_file=version_file,
            active_file=active_file
        )
    except Exception as e:
        print(f"ERROR: Failed to save config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving config: {str(e)}")


@router.post("/snapshot", response_model=SnapshotResponse)
async def create_snapshot() -> SnapshotResponse:
    """
    Create a full snapshot of all config files.
    Saves copies of all configuration files to a timestamped snapshot directory.
    """
    try:
        snapshot_dir, files_saved = file_ops.create_snapshot()
        
        return SnapshotResponse(
            status="saved",
            snapshot_dir=snapshot_dir,
            files_saved=files_saved
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating snapshot: {str(e)}")

