# pipelines/train.py
import numpy as np
import pandas as pd
import xgboost as xgb
import optuna
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
import shap
import pickle
import os

from feature_engineering import compute_advanced_features

# Suppress warnings for cleaner execution logs
import warnings
warnings.filterwarnings('ignore')

def clean_and_normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess, rename columns, and resolve column types."""
    df = df.copy()
    
    # Check if index col exists
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
        
    # Standardize column headers
    rename_map = {
        'Track.Name': 'track_name',
        'Artist.Name': 'artist_name',
        'Beats.Per.Minute': 'beats_per_minute',
        'Loudness..dB..': 'Loudness(dB)',
        'Valence.': 'Valence',
        'Length.': 'Length',
        'Acousticness..': 'Acousticness',
        'Speechiness.': 'Speechiness'
    }
    
    # Rename columns that exist in the mapping
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    df = df.fillna(0)
    return df

def objective(trial, X, y):
    """Optuna objective function for tuning XGBoost parameters."""
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 400),
        'max_depth': trial.suggest_int('max_depth', 3, 8),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.15),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'random_state': 42
    }
    
    kf = KFold(n_splits=3, shuffle=True, random_state=42)
    scores = []
    
    for train_idx, val_idx in kf.split(X, y):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]
        
        model = xgb.XGBRegressor(**params)
        model.fit(X_tr, y_tr)
        preds = model.predict(X_val)
        scores.append(np.sqrt(mean_squared_error(y_val, preds)))
        
    return np.mean(scores)

def execute_pipeline():
    print("Initiating MuseMind AI Training Pipeline...")
    
    # Load dataset
    csv_path = "top50.csv"
    if not os.path.exists(csv_path):
        # Check active directory or absolute paths
        csv_path = "../top50.csv"
        
    df = pd.read_csv(csv_path, encoding='ISO-8859-1')
    
    # Clean and pre-process
    df = clean_and_normalize_data(df)
    
    # Engineer Features
    df = compute_advanced_features(df)
    
    # Features List
    features = [
        'beats_per_minute', 'Energy', 'Danceability', 'Loudness(dB)', 
        'Acousticness', 'energy_loudness_ratio', 'tempo_variance', 
        'mood_score', 'danceability_index', 'acoustic_energy_diff'
    ]
    
    X = df[features]
    y = df['Popularity'].values
    
    # Launch Optuna Search
    print("Running hyperparameter optimization with Optuna...")
    study = optuna.create_study(direction='minimize')
    study.optimize(lambda trial: objective(trial, X, y), n_trials=15)
    
    print(f"Optimal RMSE: {study.best_value:.4f}")
    best_params = study.best_params
    print(f"Optimal Hyperparameters: {best_params}")
    
    # Train champion model
    print("Training final champion model...")
    champion_model = xgb.XGBRegressor(**best_params)
    champion_model.fit(X, y)
    
    # Generate and export SHAP explainer
    print("Calculating SHAP values & attribution weights...")
    explainer = shap.TreeExplainer(champion_model)
    
    # Export artifacts
    os.makedirs("models", exist_ok=True)
    
    with open("models/xgb_champion.pkl", "wb") as f:
        pickle.dump(champion_model, f)
        
    with open("models/shap_explainer.pkl", "wb") as f:
        pickle.dump(explainer, f)
        
    print("Models and explainability artifacts exported to './models/' directory successfully.")

if __name__ == "__main__":
    execute_pipeline()
