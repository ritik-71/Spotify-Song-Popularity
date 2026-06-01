# backend/app/schemas/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Optional

# --- Authentication Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Minimum 6 character string password")
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    email: EmailStr
    full_name: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Prediction & XAI Schemas ---
class PredictionRequest(BaseModel):
    track_name: str = Field(..., example="Señorita")
    artist_name: str = Field(..., example="Shawn Mendes")
    genre: str = Field(..., example="canadian pop")
    beats_per_minute: float = Field(..., ge=0, example=117.0)
    energy: float = Field(..., ge=0, le=100, example=55.0)
    danceability: float = Field(..., ge=0, le=100, example=76.0)
    loudness_db: float = Field(..., le=0, example=-6.0)
    acousticness: float = Field(..., ge=0, le=100, example=4.0)
    valence: float = Field(..., ge=0, le=100, example=75.0)

class PredictionResponse(BaseModel):
    track_name: str
    artist_name: str
    predicted_popularity: float
    shap_values: Dict[str, float]
    reasoning: str

# --- Vector Recommendation Schemas ---
class RecommendationRequest(BaseModel):
    track_name: str
    limit: int = Field(default=5, ge=1, le=20)

class SimilarTrack(BaseModel):
    track_name: str
    artist_name: str
    genre: str
    similarity_score: float

class RecommendationResponse(BaseModel):
    source_track: str
    recommendations: list[SimilarTrack]

# --- Agent Chat / NLQ Schemas ---
class ChatRequest(BaseModel):
    message: str = Field(..., example="Suggest ways to improve Señorita popularity score.")
    track_metadata: Optional[PredictionRequest] = None

class ChatResponse(BaseModel):
    reply: str
    agent_logs: Optional[str] = None
