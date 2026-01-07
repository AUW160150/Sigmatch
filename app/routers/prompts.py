"""
Prompt management router for Sigmatch.
Handles GET/PUT for prompt settings.
"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    PromptDetailResponse,
    PromptsResponse,
    PromptsSaveResponse,
    PromptUpdate,
    PromptUpdateResponse
)
from app.services import config_manager


router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.get("", response_model=PromptsResponse)
async def get_prompts() -> PromptsResponse:
    """
    Get all prompt settings.
    Creates default prompts if they don't exist.
    """
    try:
        prompts = config_manager.get_prompt_settings()
        last_modified = config_manager.get_prompt_settings_modified_time()
        
        return PromptsResponse(
            prompts=prompts,
            last_modified=last_modified
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading prompts: {str(e)}")


@router.get("/{agent_name}", response_model=PromptDetailResponse)
async def get_agent_prompt(agent_name: str) -> PromptDetailResponse:
    """
    Get prompt settings for a specific agent.
    """
    try:
        prompts = config_manager.get_prompt_settings()
        
        if agent_name not in prompts:
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_name}")
        
        agent_prompt = prompts[agent_name]
        
        return PromptDetailResponse(
            agent_name=agent_name,
            system_prompt=agent_prompt.get("system_prompt"),
            main_prompt=agent_prompt.get("main_prompt", ""),
            skip=agent_prompt.get("skip", False)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading prompt: {str(e)}")


@router.put("/{agent_name}", response_model=PromptUpdateResponse)
async def update_agent_prompt(agent_name: str, update: PromptUpdate) -> PromptUpdateResponse:
    """
    Update prompt settings for a specific agent.
    Only updates provided fields.
    """
    try:
        updates = update.model_dump(exclude_none=True)
        
        success = config_manager.update_agent_prompt(agent_name, updates)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_name}")
        
        return PromptUpdateResponse(
            status="updated",
            agent_name=agent_name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating prompt: {str(e)}")


@router.post("/save", response_model=PromptsSaveResponse)
async def save_prompts() -> PromptsSaveResponse:
    """
    Save all prompts with versioning.
    Creates a timestamped backup copy.
    """
    try:
        version_file = config_manager.save_prompts_versioned()
        
        return PromptsSaveResponse(
            status="saved",
            version_file=version_file
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving prompts: {str(e)}")

