"""
Pytest Test Suite for Cybersecurity Risk Engine
"""
import pytest
import pandas as pd
from cyberguard.risk.risk_engine import RiskEngine

def test_risk_engine_scoring():
    engine = RiskEngine()
    
    test_row = pd.Series({
        "flag_brute_force": True,
        "flag_impossible_travel": True,
        "flag_credential_stuffing": False,
        "flag_privilege_escalation": False,
        "anomaly_score": 0.85,
        "status": "Failed",
        "geo_speed_kmh": 1200.0,
        "geo_dist_km": 600.0
    })
    
    risk_info = engine.calculate_event_risk(test_row)
    
    assert risk_info["risk_score"] >= 80.0
    assert risk_info["severity"] in ["HIGH", "CRITICAL"]
    assert risk_info["confidence"] > 0.70
    assert "recommended_action" in risk_info
