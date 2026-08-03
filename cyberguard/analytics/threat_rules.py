"""
Rule-Based Cybersecurity Threat Detection Engines
"""
import pandas as pd
from typing import Dict, List, Any
from cyberguard.config.settings import (
    IMPOSSIBLE_TRAVEL_SPEED_KMH,
    BRUTE_FORCE_FAIL_THRESHOLD,
    CREDENTIAL_STUFFING_USER_COUNT,
    PRIVILEGE_ESCALATION_TARGETS
)
from cyberguard.utils.logger import get_logger

logger = get_logger("threat_rules")

class ThreatRuleEngine:
    """Evaluates cyber security threat heuristics against authentication event stream."""

    @staticmethod
    def detect_impossible_travel(row: pd.Series) -> bool:
        """
        Flag impossible travel if physical movement speed between consecutive
        authentications for the same user exceeds 800 km/h and distance > 100 km.
        """
        speed = row.get("geo_speed_kmh", 0.0)
        dist = row.get("geo_dist_km", 0.0)
        return speed > IMPOSSIBLE_TRAVEL_SPEED_KMH and dist > 100.0

    @staticmethod
    def detect_brute_force(row: pd.Series) -> bool:
        """
        Flag brute force if user or IP has >= 5 failed attempts in the last 10 minutes.
        """
        user_fails = row.get("user_failed_count_10m", 0)
        ip_fails = row.get("ip_failed_count_10m", 0)
        return user_fails >= BRUTE_FORCE_FAIL_THRESHOLD or ip_fails >= BRUTE_FORCE_FAIL_THRESHOLD

    @staticmethod
    def detect_credential_stuffing(row: pd.Series) -> bool:
        """
        Flag credential stuffing if single IP attempts logins for >= 10 distinct usernames in 10 minutes.
        """
        distinct_users = row.get("ip_distinct_users_10m", 0)
        return distinct_users >= CREDENTIAL_STUFFING_USER_COUNT

    @staticmethod
    def detect_privilege_escalation(row: pd.Series) -> bool:
        """
        Flag privilege escalation if attempt targets administrative accounts (root, admin, sysadmin).
        """
        username = str(row.get("username", "")).lower()
        status = row.get("status", "")
        return username in PRIVILEGE_ESCALATION_TARGETS and status == "Failed"

    def evaluate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all threat rules to DataFrame and attach indicator columns."""
        logger.info("Evaluating rule-based security threat indicators...")
        result = df.copy()

        result["flag_impossible_travel"] = result.apply(self.detect_impossible_travel, axis=1)
        result["flag_brute_force"] = result.apply(self.detect_brute_force, axis=1)
        result["flag_credential_stuffing"] = result.apply(self.detect_credential_stuffing, axis=1)
        result["flag_privilege_escalation"] = result.apply(self.detect_privilege_escalation, axis=1)

        # Composite Threat Vector Tag
        def get_primary_threat(row):
            threats = []
            if row["flag_impossible_travel"]:
                threats.append("Impossible Travel")
            if row["flag_brute_force"]:
                threats.append("Brute Force")
            if row["flag_credential_stuffing"]:
                threats.append("Credential Stuffing")
            if row["flag_privilege_escalation"]:
                threats.append("Privilege Escalation")
            return ", ".join(threats) if threats else "None"

        result["threat_vector"] = result.apply(get_primary_threat, axis=1)
        logger.info(f"Threat evaluation complete. Flagged {(result['threat_vector'] != 'None').sum()} threat events.")
        return result
