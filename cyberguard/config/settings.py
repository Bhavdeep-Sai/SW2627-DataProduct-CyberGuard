"""
CyberGuard System Configuration & Threshold Settings
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "output"
REPORTS_DIR = BASE_DIR / "reports"
DATABASE_PATH = DATA_DIR / "cyberguard.db"

# Ensure required directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Cybersecurity Threat Thresholds
IMPOSSIBLE_TRAVEL_SPEED_KMH = 800.0  # Max realistic speed between login locations
BRUTE_FORCE_FAIL_THRESHOLD = 5       # Failed attempts within time window
BRUTE_FORCE_WINDOW_MINUTES = 10      # Window in minutes
CREDENTIAL_STUFFING_USER_COUNT = 10  # Distinct users attempted from same IP within window
PRIVILEGE_ESCALATION_TARGETS = ["root", "admin", "administrator", "sysadmin", "system"]

# Risk Scoring Thresholds
RISK_LEVEL_LOW = 30
RISK_LEVEL_MEDIUM = 60
RISK_LEVEL_HIGH = 80

# Machine Learning Settings
ML_MODEL_RANDOM_STATE = 42
ML_CONTAMINATION_RATE = 0.08
