"""
Pytest Test Suite for SQLite Database Manager & Analytical Views
"""
import pytest
import pandas as pd
from pathlib import Path
from cyberguard.sql.db_manager import DatabaseManager
from cyberguard.etl.pipeline import ETLPipeline
from cyberguard.risk.risk_engine import RiskEngine

def test_database_manager(tmp_path):
    test_db = tmp_path / "test_cyberguard.db"
    db_mgr = DatabaseManager(db_path=test_db)
    db_mgr.init_database()
    
    # Ingest data
    pipeline = ETLPipeline()
    df, _ = pipeline.run()
    risk_engine = RiskEngine()
    final_df = risk_engine.evaluate_dataframe(df)
    
    db_mgr.ingest_events(final_df)
    
    # Test table query
    res = db_mgr.execute_query("SELECT COUNT(*) as cnt FROM auth_events;")
    assert res.loc[0, "cnt"] > 0
    
    # Test View query
    view_res = db_mgr.execute_query("SELECT * FROM v_user_risk_summary;")
    assert len(view_res) > 0
    assert "max_risk_score" in view_res.columns
