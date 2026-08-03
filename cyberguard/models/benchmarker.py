"""
Multi-Model Machine Learning Anomaly Detection Benchmark Evaluator
"""
import time
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import DBSCAN
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score

from cyberguard.config.settings import ML_CONTAMINATION_RATE, ML_MODEL_RANDOM_STATE
from cyberguard.utils.logger import get_logger

logger = get_logger("benchmarker")

FEATURE_COLUMNS = [
    "is_failed", "hour", "day_of_week", "is_weekend",
    "time_diff_min", "geo_dist_km", "geo_speed_kmh",
    "ip_failed_count_10m", "user_failed_count_10m", "ip_distinct_users_10m"
]

class ModelBenchmarker:
    """Evaluates & Benchmarks 5 Anomaly Detection Algorithms."""

    def __init__(self, contamination: float = ML_CONTAMINATION_RATE):
        self.contamination = contamination
        self.scaler = StandardScaler()

    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract and standardize numeric feature matrix X."""
        X = df[FEATURE_COLUMNS].copy().fillna(0.0)
        return self.scaler.fit_transform(X)

    def benchmark_models(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Train and compare Isolation Forest, One-Class SVM, LOF, DBSCAN, and Autoencoder."""
        logger.info("Starting Multi-Model Anomaly Detection Benchmarking...")
        X = self.prepare_features(df)
        
        # Ground truth proxy from threat rules if present (for precision/recall benchmark)
        y_true = None
        if "threat_vector" in df.columns:
            y_true = (df["threat_vector"] != "None").astype(int)
        elif "attack_label" in df.columns:
            y_true = (df["attack_label"] != "Normal").astype(int)

        results = []
        models = {}

        # 1. Isolation Forest
        t0 = time.time()
        iso = IsolationForest(contamination=self.contamination, random_state=ML_MODEL_RANDOM_STATE)
        iso_preds = iso.fit_predict(X)
        iso_binary = np.where(iso_preds == -1, 1, 0)
        iso_time = time.time() - t0
        models["IsolationForest"] = iso
        results.append(self._metrics("Isolation Forest", y_true, iso_binary, iso_time, len(X)))

        # 2. One-Class SVM
        t0 = time.time()
        ocsvm = OneClassSVM(nu=self.contamination, kernel="rbf", gamma="scale")
        ocsvm_preds = ocsvm.fit_predict(X)
        ocsvm_binary = np.where(ocsvm_preds == -1, 1, 0)
        ocsvm_time = time.time() - t0
        models["OneClassSVM"] = ocsvm
        results.append(self._metrics("One-Class SVM", y_true, ocsvm_binary, ocsvm_time, len(X)))

        # 3. Local Outlier Factor (LOF)
        t0 = time.time()
        lof = LocalOutlierFactor(n_neighbors=20, contamination=self.contamination)
        lof_preds = lof.fit_predict(X)
        lof_binary = np.where(lof_preds == -1, 1, 0)
        lof_time = time.time() - t0
        models["LocalOutlierFactor"] = lof
        results.append(self._metrics("Local Outlier Factor", y_true, lof_binary, lof_time, len(X)))

        # 4. DBSCAN
        t0 = time.time()
        dbscan = DBSCAN(eps=2.5, min_samples=5)
        db_clusters = dbscan.fit_predict(X)
        db_binary = np.where(db_clusters == -1, 1, 0)
        db_time = time.time() - t0
        models["DBSCAN"] = dbscan
        results.append(self._metrics("DBSCAN", y_true, db_binary, db_time, len(X)))

        # 5. MLP Autoencoder
        t0 = time.time()
        autoenc = MLPRegressor(hidden_layer_sizes=(8, 4, 8), max_iter=200, random_state=ML_MODEL_RANDOM_STATE)
        autoenc.fit(X, X)
        X_recon = autoenc.predict(X)
        recon_errors = np.mean(np.square(X - X_recon), axis=1)
        threshold = np.percentile(recon_errors, 100 * (1 - self.contamination))
        auto_binary = np.where(recon_errors > threshold, 1, 0)
        auto_time = time.time() - t0
        models["Autoencoder"] = autoenc
        results.append(self._metrics("MLP Autoencoder", y_true, auto_binary, auto_time, len(X)))

        benchmark_df = pd.DataFrame(results)
        logger.info(f"Benchmarking complete:\n{benchmark_df.to_string(index=False)}")
        return benchmark_df, models

    def _metrics(self, name: str, y_true: np.ndarray, y_pred: np.ndarray, latency: float, total: int) -> dict:
        anom_count = int(np.sum(y_pred))
        anom_ratio = round(anom_count / total, 4)
        
        if y_true is not None and len(np.unique(y_true)) > 1:
            p = round(precision_score(y_true, y_pred, zero_division=0), 4)
            r = round(recall_score(y_true, y_pred, zero_division=0), 4)
            f1 = round(f1_score(y_true, y_pred, zero_division=0), 4)
        else:
            p, r, f1 = 0.0, 0.0, 0.0

        return {
            "Model Name": name,
            "Anomalies Detected": anom_count,
            "Anomaly Ratio": anom_ratio,
            "Precision": p,
            "Recall": r,
            "F1 Score": f1,
            "Inference Time (s)": round(latency, 4)
        }
