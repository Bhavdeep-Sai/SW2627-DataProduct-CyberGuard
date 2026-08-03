"""
Pytest Test Suite for Rule-Based Cybersecurity Threat Engine
"""
import pytest
import pandas as pd
from cyberguard.analytics.threat_rules import ThreatRuleEngine

def test_threat_rule_evaluation():
    engine = ThreatRuleEngine()
    
    test_data = pd.DataFrame([
        {
            "username": "user_1", "status": "Failed", "geo_speed_kmh": 1200.0,
            "geo_dist_km": 500.0, "user_failed_count_10m": 6, "ip_failed_count_10m": 1,
            "ip_distinct_users_10m": 2
        },
        {
            "username": "root", "status": "Failed", "geo_speed_kmh": 10.0,
            "geo_dist_km": 5.0, "user_failed_count_10m": 1, "ip_failed_count_10m": 1,
            "ip_distinct_users_10m": 1
        },
        {
            "username": "user_2", "status": "Success", "geo_speed_kmh": 20.0,
            "geo_dist_km": 10.0, "user_failed_count_10m": 0, "ip_failed_count_10m": 0,
            "ip_distinct_users_10m": 1
        }
    ])
    
    res = engine.evaluate_dataframe(test_data)
    
    # Event 0: Impossible Travel (speed 1200 km/h) & Brute Force (user_failed_count_10m = 6)
    assert res.loc[0, "flag_impossible_travel"] == True
    assert res.loc[0, "flag_brute_force"] == True
    
    # Event 1: Privilege Escalation targeting 'root'
    assert res.loc[1, "flag_privilege_escalation"] == True
    
    # Event 2: Normal
    assert res.loc[2, "threat_vector"] == "None"
