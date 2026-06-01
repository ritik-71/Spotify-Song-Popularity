# backend/app/api/v1/endpoints/recommend.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.schemas import RecommendationRequest, RecommendationResponse
from app.services.recommender.py import recommender_service
from app.core.security import get_current_user
from app.models.db_models import User

router = APIRouter()

@router.post("/", response_model=RecommendationResponse, status_code=status.HTTP_200_OK)
def recommend_similar_tracks(
    payload: RecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Finds similarity-based music matches within the top50 library using cosine distance.
    """
    try:
        results = recommender_service.get_similar_tracks(
            target_track=payload.track_name,
            limit=payload.limit
        )
        return results
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommender index lookup failure: {str(e)}"
        )
```

Wait, let's make sure the import is correct! In Python, it is `from app.services.recommender import recommender_service` (without `.py` in the module path).
Ah, yes! Good catch! Let's write `recommend.py` using `from app.services.recommender import recommender_service`.
Let's call the tool now.
