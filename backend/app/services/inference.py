# backend/app/services/inference.py
import pickle
import os
import numpy as np
import pandas as pd
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.schemas.schemas import PredictionRequest, PredictionResponse
from app.models.db_models import TrackMetric, ExplainabilityLog
from app.core.config import settings

class InferenceService:
    def __init__(self):
        self.model = None
        self.explainer = None
        self.features_list = [
            'beats_per_minute', 'Energy', 'Danceability', 'Loudness(dB)', 
            'Acousticness', 'energy_loudness_ratio', 'tempo_variance', 
            'mood_score', 'danceability_index', 'acoustic_energy_diff'
        ]
        self._load_artifacts()

    def _load_artifacts(self):
        """Loads serialized XGBoost model and SHAP TreeExplainer."""
        model_paths = [
            "models/xgb_champion.pkl",
            "../models/xgb_champion.pkl",
            "pipelines/models/xgb_champion.pkl"
        ]
        explainer_paths = [
            "models/shap_explainer.pkl",
            "../models/shap_explainer.pkl",
            "pipelines/models/shap_explainer.pkl"
        ]
        
        for path in model_paths:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    self.model = pickle.load(f)
                break
                
        for path in explainer_paths:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    self.explainer = pickle.load(f)
                break

    def engineer_single_row(self, payload: PredictionRequest) -> pd.DataFrame:
        """Applies Advanced Feature Engineering formulas to single inference requests."""
        df = pd.DataFrame([{
            'beats_per_minute': payload.beats_per_minute,
            'Energy': payload.energy,
            'Danceability': payload.danceability,
            'Loudness(dB)': payload.loudness_db,
            'Acousticness': payload.acousticness,
            'Valence': payload.valence
        }])
        
        # Apply formulas
        df['energy_loudness_ratio'] = df['Energy'] / (df['Loudness(dB)'].abs() + 1.0)
        df['tempo_variance'] = 0.0 # Single record has 0 temporal variance baseline
        df['mood_score'] = (df['Valence'] / 100.0) * (df['Energy'] / 100.0)
        df['danceability_index'] = (df['Danceability'] / 100.0) * (df['beats_per_minute'] / 120.0)
        df['acoustic_energy_diff'] = (df['Energy'] - df['Acousticness']) / 100.0
        
        return df

    async def predict(self, payload: PredictionRequest, db: Session, user_id: str) -> Dict[str, Any]:
        if self.model is None or self.explainer is None:
            # Re-attempt lazy loading if artifacts weren't ready at startup
            self._load_artifacts()
            if self.model is None or self.explainer is None:
                raise RuntimeError("Prediction Service currently offline. ML model weights not found.")
        
        # 1. Feature Engineering
        row_df = self.engineer_single_row(payload)
        X = row_df[self.features_list]
        
        # 2. Run Inference
        predicted_popularity = float(self.model.predict(X)[0])
        predicted_popularity = max(0.0, min(100.0, predicted_popularity)) # Clip bounds
        
        # 3. Compute SHAP explainability
        shap_values = self.explainer(X)
        shap_attribs = {}
        for feature, val in zip(self.features_list, shap_values.values[0]):
            shap_attribs[feature] = float(val)
            
        # Determine main positive and negative driver
        sorted_attribs = sorted(shap_attribs.items(), key=lambda item: item[1])
        main_negative_driver = sorted_attribs[0][0]
        main_positive_driver = sorted_attribs[-1][0]
        
        reasoning = (
            f"The track '{payload.track_name}' by '{payload.artist_name}' is predicted to achieve a popularity of "
            f"{predicted_popularity:.1f} out of 100. The leading positive attribute is '{main_positive_driver}', "
            f"while popularity is most constrained by '{main_negative_driver}'."
        )
        
        # 4. Save to Database
        track_metric = TrackMetric(
            track_name=payload.track_name,
            artist_name=payload.artist_name,
            genre=payload.genre,
            beats_per_minute=payload.beats_per_minute,
            energy=payload.energy,
            danceability=payload.danceability,
            loudness_db=payload.loudness_db,
            acousticness=payload.acousticness,
            tempo_variance=float(row_df['tempo_variance'].iloc[0]),
            energy_loudness_ratio=float(row_df['energy_loudness_ratio'].iloc[0]),
            predicted_popularity=predicted_popularity,
            user_id=user_id
        )
        db.add(track_metric)
        db.commit()
        db.refresh(track_metric)
        
        explain_log = ExplainabilityLog(
            track_metric_id=track_metric.id,
            shap_values=shap_attribs,
            summary_reasoning=reasoning
        )
        db.add(explain_log)
        db.commit()
        
        return {
            "track_name": payload.track_name,
            "artist_name": payload.artist_name,
            "predicted_popularity": round(predicted_popularity, 2),
            "shap_values": shap_attribs,
            "reasoning": reasoning
        }

inference_service = InferenceService()
