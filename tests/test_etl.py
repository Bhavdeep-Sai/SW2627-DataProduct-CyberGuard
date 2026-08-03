"""
Pytest Test Suite for Data Engineering & ETL Pipeline
"""
import pytest
import pandas as pd
from cyberguard.etl.generator import generate_synthetic_auth_logs
from cyberguard.etl.validator import DataValidator
from cyberguard.etl.pipeline import ETLPipeline, haversine_km

def test_haversine_km():
    # Distance between San Francisco (37.7749, -122.4194) and Tokyo (35.6762, 139.6503) is ~8280 km
    dist = haversine_km(37.7749, -122.4194, 35.6762, 139.6503)
    assert dist > 8000 and dist < 8500
    
    # Distance between same coordinates is 0
    assert haversine_km(37.7749, -122.4194, 37.7749, -122.4194) == 0.0

def test_synthetic_auth_generator():
    df = generate_synthetic_auth_logs(num_records=100)
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 100
    assert "timestamp" in df.columns
    assert "username" in df.columns
    assert "status" in df.columns

def test_data_validator():
    raw_df = generate_synthetic_auth_logs(num_records=50)
    is_valid, missing = DataValidator.validate_schema(raw_df)
    assert is_valid
    assert len(missing) == 0

    clean_df, report = DataValidator.clean_and_validate(raw_df)
    assert report["clean_records"] == len(clean_df)
    assert clean_df["status"].isin(["Success", "Failed"]).all()

def test_etl_pipeline_run():
    pipeline = ETLPipeline()
    df, report = pipeline.run()
    assert isinstance(df, pd.DataFrame)
    assert "geo_speed_kmh" in df.columns
    assert "ip_failed_count_10m" in df.columns
    assert len(df) > 0
