# backend/app/api/v1/endpoints/explain.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.db_models import ExplainabilityLog, TrackMetric
from app.core.security import get_current_user
from app.models.db_models import User

router = APIRouter()

@router.get("/{track_metric_id}", status_code=status.HTTP_200_OK)
def get_track_explanation(
    track_metric_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetches SHAP attributions and LLM structural critiques for a specific prediction request.
    """
    track = db.query(TrackMetric).filter(TrackMetric.id == track_metric_id).first()
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track prediction log not found."
        )
    if track.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access to this prediction log."
        )
        
    explanation = db.query(ExplainabilityLog).filter(ExplainabilityLog.track_metric_id == track_metric_id).first()
    if not explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Explainability audit not found for this metric."
        )
        
    return {
        "track_name": track.track_name,
        "artist_name": track.artist_name,
        "predicted_popularity": track.predicted_popularity,
        "shap_values": explanation.shap_values,
        "reasoning": explanation.summary_reasoning,
        "lime_explanation": explanation.lime_explanation,
        "created_at": explanation.created_at
    }
