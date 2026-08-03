"""
Intelligent Enterprise Cybersecurity Risk Engine
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from cyberguard.utils.logger import get_logger

logger = get_logger("risk_engine")

class RiskEngine:
    """
    Computes composite Risk Score (0-100), Severity, Confidence, Risk Factors,
    Primary Reason, Recommended Action, and Explainability.
    """

    @staticmethod
    def calculate_event_risk(row: pd.Series) -> Dict[str, Any]:
        base_score = 0.0
        factors = []
        
        # 1. Rule-based threat contributions
        if row.get("flag_brute_force", False):
            base_score += 45.0
            factors.append("High-velocity failed authentication streak (Brute Force vector)")
            
        if row.get("flag_impossible_travel", False):
            base_score += 40.0
            speed = row.get("geo_speed_kmh", 0)
            dist = row.get("geo_dist_km", 0)
            factors.append(f"Geographical speed anomaly ({speed:.0f} km/h across {dist:.0f} km)")
            
        if row.get("flag_credential_stuffing", False):
            base_score += 50.0
            factors.append("Multi-account access attempt from single IP (Credential Stuffing vector)")
            
        if row.get("flag_privilege_escalation", False):
            base_score += 35.0
            factors.append(f"Failed authentication attempt targeting privileged user '{row.get('username')}'")

        # 2. ML Anomaly Score contribution
        anom_score = row.get("anomaly_score", 0.0)
        if anom_score > 0.5:
            base_score += (anom_score * 30.0)
            factors.append(f"ML Anomaly Model outlier score ({anom_score:.2f})")

        # 3. Status penalty
        if row.get("status") == "Failed":
            base_score += 10.0

        # Cap score at 100.0
        risk_score = round(min(base_score, 100.0), 1)

        # Map Severity Level
        if risk_score >= 85.0:
            severity = "CRITICAL"
        elif risk_score >= 70.0:
            severity = "HIGH"
        elif risk_score >= 40.0:
            severity = "MEDIUM"
        elif risk_score >= 20.0:
            severity = "LOW"
        else:
            severity = "INFO"

        # Calculate Confidence (0.50 to 0.99)
        num_factors = len(factors)
        confidence = round(min(0.60 + (num_factors * 0.12), 0.99), 2)

        # Derive Primary Reason
        if factors:
            primary_reason = factors[0]
        elif row.get("status") == "Failed":
            primary_reason = "Isolated failed authentication attempt"
        else:
            primary_reason = "Normal baseline authentication behavior"

        # Derive Recommended SOC Action
        if severity == "CRITICAL":
            rec_action = "CRITICAL: Immediately isolate endpoint, revoke user session tokens, enforce mandatory MFA reset, and initiate Incident Response (IR) Playbook IR-104."
        elif severity == "HIGH":
            rec_action = "HIGH: Block originating IP on perimeter firewall, lock user account for 60 minutes, and investigate adjacent host logs."
        elif severity == "MEDIUM":
            rec_action = "MEDIUM: Flag account for step-up multi-factor authentication (MFA) and monitor user activity for 24 hours."
        elif severity == "LOW":
            rec_action = "LOW: Log event to SIEM index and update user behavioral baseline profile."
        else:
            rec_action = "INFO: Standard authentication event; no analyst action required."

        # Generate Explainability Narrative
        if factors:
            explainability = (
                f"Incident triggered with Risk Score **{risk_score}/100** ({severity}). "
                f"Contributing factors include: {'; '.join(factors)}. "
                f"Confidence rating is **{int(confidence*100)}%**."
            )
        else:
            explainability = f"Authentication event verified normal with low risk score **{risk_score}/100**."

        return {
            "risk_score": risk_score,
            "severity": severity,
            "confidence": confidence,
            "primary_reason": primary_reason,
            "risk_factors": "; ".join(factors) if factors else "None",
            "recommended_action": rec_action,
            "explainability": explainability
        }

    def evaluate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Computing composite Risk Engine scoring for all events...")
        result = df.copy()
        
        risk_outputs = result.apply(self.calculate_event_risk, axis=1)
        risk_df = pd.DataFrame(list(risk_outputs))
        
        for col in risk_df.columns:
            result[col] = risk_df[col]

        logger.info("Risk Engine evaluation completed successfully.")
        return result
