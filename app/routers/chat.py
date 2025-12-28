"""
Evaluation chat router for Sigmatch.
Handles chat history and evaluation criteria management.
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ChatHistoryResponse,
    ChatMessage,
    ChatMessageRequest,
    ChatMessageResponse,
    SaveCriteriaRequest,
    SaveCriteriaResponse
)
from app.services import config_manager


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history() -> ChatHistoryResponse:
    """
    Get chat history for evaluation criteria.
    Returns all messages and the final criteria if set.
    """
    try:
        criteria = config_manager.get_evaluation_criteria()
        
        messages = [
            ChatMessage(
                role=m.get("role", "user"),
                content=m.get("content", ""),
                timestamp=m.get("timestamp")
            )
            for m in criteria.get("messages", [])
        ]
        
        return ChatHistoryResponse(
            messages=messages,
            final_criteria=criteria.get("final_criteria")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading chat history: {str(e)}")


@router.post("/message", response_model=ChatMessageResponse)
async def add_message(request: ChatMessageRequest) -> ChatMessageResponse:
    """
    Add a message to chat history.
    
    For Phase 1, assistant responses are placeholders.
    Real AI integration comes in future phases.
    """
    try:
        # Add the user message
        message = config_manager.add_chat_message(request.role, request.content)
        
        # If it's a user message, generate a placeholder assistant response
        if request.role == "user":
            # Placeholder response - real AI integration comes later
            assistant_content = (
                f"Thank you for your input. I've noted your message about evaluation criteria. "
                f"In a future version, I'll provide AI-powered suggestions based on your requirements. "
                f"For now, please continue describing your evaluation needs."
            )
            config_manager.add_chat_message("assistant", assistant_content)
        
        return ChatMessageResponse(
            status="added",
            message=ChatMessage(
                role=message["role"],
                content=message["content"],
                timestamp=message["timestamp"]
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding message: {str(e)}")


@router.post("/save-criteria", response_model=SaveCriteriaResponse)
async def save_criteria(request: SaveCriteriaRequest) -> SaveCriteriaResponse:
    """
    Save the final evaluation criteria.
    """
    try:
        config_manager.save_final_criteria(request.final_criteria)
        
        return SaveCriteriaResponse(
            status="saved",
            file="evaluation_criteria.json"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving criteria: {str(e)}")

