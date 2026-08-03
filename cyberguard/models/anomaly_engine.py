"""
Production Machine Learning Anomaly Engine
"""
import numpy as np
import pandas as pd
from typing import Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from cyberguard.models.benchmarker import FEATURE_COLUMNS
from cyberguard.config.settings import ML_CONTAMINATION_RATE, ML_MODEL_RANDOM_STATE
from cyberguard.utils.logger import get_logger

logger = get_logger("anomaly_engine")

class AnomalyEngine:
    """Production Anomaly Scoring Engine combining Isolation Forest and Feature Profiling."""

    def __init__(self, contamination: float = ML_CONTAMINATION_RATE):
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.score_scaler = MinMaxScaler(feature_range=(0.0, 1.0))
        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=ML_MODEL_RANDOM_STATE,
            n_jobs=-1
        )

    def fit_predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fit anomaly detector on DataFrame features and attach:
        - anomaly_score (0.0 to 1.0)
        - is_anomaly (1 / 0)
        - anomaly_confidence (0.5 to 1.0)
        """
        logger.info("Fitting Production Anomaly Engine...")
        result = df.copy()
        
        X = result[FEATURE_COLUMNS].fillna(0.0)
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit Isolation Forest
        self.model.fit(X_scaled)
        
        # Compute raw decision function (lower means more anomalous)
        raw_scores = self.model.decision_function(X_scaled)
        
        # Invert scores so higher = more anomalous (0.0 = completely normal, 1.0 = highly anomalous)
        inverted_scores = -raw_scores
        normalized_scores = self.score_scaler.fit_transform(inverted_scores.reshape(-1, 1)).flatten()
        
        result["anomaly_score"] = np.round(normalized_scores, 4)
        result["is_anomaly"] = (result["anomaly_score"] >= 0.70).astype(int)
        
        # Confidence score calculation
        result["anomaly_confidence"] = np.round(0.5 + (np.abs(result["anomaly_score"] - 0.5)), 2)

        logger.info(f"Anomaly scoring complete. Found {(result['is_anomaly'] == 1).sum()} anomalies out of {len(result)} events.")
        return result
