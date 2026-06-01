# backend/app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import auth, predict, explain, recommend, chat

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(predict.router, prefix="/predict", tags=["Real-time Prediction"])
api_router.include_router(explain.router, prefix="/explain", tags=["Explainable AI (XAI)"])
api_router.include_router(recommend.router, prefix="/recommend", tags=["Recommendation Engine"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI Agentic Chat"])
