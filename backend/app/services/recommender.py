# backend/app/services/recommender.py
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import os

class RecommenderService:
    def __init__(self):
        self.df = None
        self.features = ['beats_per_minute', 'Energy', 'Danceability', 'Loudness..dB..', 'Acousticness']
        self._load_data()

    def _load_data(self):
        """Loads data for local content-based cosine similarity lookup."""
        paths = ["top50.csv", "../top50.csv", "pipelines/top50.csv"]
        for p in paths:
            if os.path.exists(p):
                self.df = pd.read_csv(p, encoding='ISO-8859-1')
                break

    def get_similar_tracks(self, target_track: str, limit: int = 5):
        if self.df is None:
            self._load_data()
            if self.df is None:
                raise RuntimeError("Metadata dataset top50.csv not found. Recommender is offline.")
        
        # Standarize column names for fallback matching
        df_clean = self.df.copy()
        
        # Check matching track
        match_idx = df_clean[df_clean['Track.Name'].str.lower() == target_track.lower()].index
        if len(match_idx) == 0:
            # Try approximate lookup
            match_idx = df_clean[df_clean['Track.Name'].str.lower().str.contains(target_track.lower())].index
            if len(match_idx) == 0:
                raise ValueError(f"Track '{target_track}' not found in the music directory.")
        
        target_idx = match_idx[0]
        
        # Extract features and compute similarities
        features_data = df_clean[self.features]
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features_data)
        
        target_vector = scaled_features[target_idx].reshape(1, -1)
        similarities = cosine_similarity(target_vector, scaled_features).flatten()
        
        # Find indices
        top_indices = np.argsort(similarities)[::-1]
        
        # Exclude self reference
        top_indices = [idx for idx in top_indices if idx != target_idx][:limit]
        
        recommendations = []
        for idx in top_indices:
            recommendations.append({
                "track_name": str(df_clean.iloc[idx]['Track.Name']),
                "artist_name": str(df_clean.iloc[idx]['Artist.Name']),
                "genre": str(df_clean.iloc[idx]['Genre']),
                "similarity_score": float(similarities[idx])
            })
            
        return {
            "source_track": str(df_clean.iloc[target_idx]['Track.Name']),
            "recommendations": recommendations
        }

recommender_service = RecommenderService()
