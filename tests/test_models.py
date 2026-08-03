"""
Pytest Test Suite for ML Anomaly Detection Engine & Benchmarker
"""
import pytest
import pandas as pd
from cyberguard.etl.generator import generate_synthetic_auth_logs
from cyberguard.etl.pipeline import ETLPipeline
from cyberguard.models.benchmarker import ModelBenchmarker
from cyberguard.models.anomaly_engine import AnomalyEngine

def test_ml_benchmarker():
    pipeline = ETLPipeline()
    df, _ = pipeline.run()
    
    benchmarker = ModelBenchmarker()
    benchmark_df, models = benchmarker.benchmark_models(df)
    
    assert isinstance(benchmark_df, pd.DataFrame)
    assert len(benchmark_df) == 5
    assert "Isolation Forest" in benchmark_df["Model Name"].values
    assert "MLP Autoencoder" in benchmark_df["Model Name"].values

def test_anomaly_engine():
    pipeline = ETLPipeline()
    df, _ = pipeline.run()
    
    engine = AnomalyEngine()
    scored_df = engine.fit_predict(df)
    
    assert "anomaly_score" in scored_df.columns
    assert scored_df["anomaly_score"].between(0.0, 1.0).all()
    assert "is_anomaly" in scored_df.columns
