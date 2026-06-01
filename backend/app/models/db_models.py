# backend/app/models/db_models.py
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    metrics = relationship("TrackMetric", back_populates="user")

class TrackMetric(Base):
    __tablename__ = "track_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    track_name = Column(String, nullable=False, index=True)
    artist_name = Column(String, nullable=False, index=True)
    genre = Column(String, nullable=False)
    beats_per_minute = Column(Float, nullable=False)
    energy = Column(Float, nullable=False)
    danceability = Column(Float, nullable=False)
    loudness_db = Column(Float, nullable=False)
    acousticness = Column(Float, nullable=False)
    
    # Advanced Engineered Features
    tempo_variance = Column(Float, nullable=False)
    energy_loudness_ratio = Column(Float, nullable=False)
    predicted_popularity = Column(Float, nullable=False)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="metrics")
    explanation = relationship("ExplainabilityLog", back_populates="track_metric", uselist=False)

class ExplainabilityLog(Base):
    __tablename__ = "explainability_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    track_metric_id = Column(UUID(as_uuid=True), ForeignKey("track_metrics.id"), nullable=False)
    shap_values = Column(JSON, nullable=False)      # Stores key-value SHAP feature attribution
    lime_explanation = Column(JSON, nullable=True)
    summary_reasoning = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    track_metric = relationship("TrackMetric", back_populates="explanation")
