# pipelines/feature_engineering.py
import pandas as pd
import numpy as np

def compute_advanced_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes professional-grade audio features and indices.
    """
    # Defensive programming: ensure columns exist
    required_cols = {'beats_per_minute', 'Energy', 'Danceability', 'Loudness(dB)', 'Valence', 'Acousticness'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Ingested dataframe is missing required features: {missing}")
        
    df = df.copy()

    # 1. Energy-to-Loudness Ratio (measures acoustic density and pressure)
    # Scaled to prevent division by zero or large scale issues
    df['energy_loudness_ratio'] = df['Energy'] / (df['Loudness(dB)'].abs() + 1.0)
    
    # 2. Tempo Variance (pct difference in beats per minute relative to moving average of tracks)
    df['tempo_variance'] = df['beats_per_minute'].pct_change().fillna(0.0)
    
    # 3. Mood Index Score (Valence (happiness/sentiment) * Energy (power/drive))
    df['mood_score'] = (df['Valence'] / 100.0) * (df['Energy'] / 100.0)
    
    # 4. Danceability Index (Interaction between rhythm and dance metrics)
    df['danceability_index'] = (df['Danceability'] / 100.0) * (df['beats_per_minute'] / 120.0)
    
    # 5. Acoustic-to-Electronic Difference
    df['acoustic_energy_diff'] = (df['Energy'] - df['Acousticness']) / 100.0

    return df
