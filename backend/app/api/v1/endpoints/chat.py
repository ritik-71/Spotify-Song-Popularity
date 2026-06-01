# backend/app/api/v1/endpoints/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.agents import agent_advisory_service
from app.core.security import get_current_user
from app.models.db_models import User

router = APIRouter()

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def consult_music_advisor(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Invokes the MuseMind multi-agent cluster (Analyst, Consultant, Feature Engineer)
    to perform NLP queries or track consultancy.
    """
    try:
        track_dict = payload.track_metadata.dict() if payload.track_metadata else None
        results = await agent_advisory_service.execute_advisory_chain(
            user_query=payload.message,
            track_info=track_dict
        )
        return ChatResponse(
            reply=results["reply"],
            agent_logs=results["agent_logs"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent orchestration pipeline failed: {str(e)}"
        )
