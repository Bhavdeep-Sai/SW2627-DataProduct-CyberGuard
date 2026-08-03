"""
CyberGuard Dataset Validator & Quality Enforcement Module
"""
import re
import pandas as pd
from typing import Tuple, Dict, Any
from cyberguard.utils.logger import get_logger

logger = get_logger("validator")

REQUIRED_COLUMNS = [
    "timestamp", "username", "ip_address", "country",
    "status", "device_type"
]

IPV4_REGEX = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"

class DataValidator:
    """Enterprise Data Quality & Schema Enforcement Validator"""
    
    @staticmethod
    def validate_schema(df: pd.DataFrame) -> Tuple[bool, list]:
        """Check whether all required columns are present in DataFrame."""
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        is_valid = len(missing) == 0
        if not is_valid:
            logger.error(f"Missing required columns: {missing}")
        return is_valid, missing

    @staticmethod
    def clean_and_validate(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Perform comprehensive cleaning:
        1. Remove exact duplicate rows
        2. Convert timestamp to datetime, coerce errors
        3. Fill missing values with defaults
        4. Validate IP format
        5. Standardize status to ('Success', 'Failed')
        """
        initial_count = len(df)
        report = {
            "initial_records": initial_count,
            "duplicates_removed": 0,
            "null_timestamps_fixed": 0,
            "invalid_ips_flagged": 0,
            "clean_records": 0
        }
        
        cleaned = df.copy()
        
        # 1. Duplicate Removal
        cleaned = cleaned.drop_duplicates().reset_index(drop=True)
        report["duplicates_removed"] = initial_count - len(cleaned)
        
        # 2. Timestamp Normalization
        cleaned["timestamp"] = pd.to_datetime(cleaned["timestamp"], errors="coerce")
        null_ts = cleaned["timestamp"].isna()
        report["null_timestamps_fixed"] = int(null_ts.sum())
        # Drop rows with unparseable timestamps
        cleaned = cleaned.dropna(subset=["timestamp"]).reset_index(drop=True)
        
        # 3. Missing Values Imputation
        cleaned["username"] = cleaned["username"].fillna("unknown_user").astype(str)
        cleaned["ip_address"] = cleaned["ip_address"].fillna("0.0.0.0").astype(str)
        cleaned["country"] = cleaned["country"].fillna("UNKNOWN").astype(str)
        cleaned["city"] = cleaned["city"].fillna("Unknown").astype(str) if "city" in cleaned.columns else "Unknown"
        cleaned["device_type"] = cleaned["device_type"].fillna("Unknown-Device").astype(str)
        cleaned["status"] = cleaned["status"].astype(str).str.capitalize()
        cleaned["status"] = cleaned["status"].apply(lambda x: "Success" if x in ["Success", "Pass", "Ok", "1"] else "Failed")
        
        # Geolocation defaults if missing
        if "latitude" not in cleaned.columns:
            cleaned["latitude"] = 0.0
        else:
            cleaned["latitude"] = pd.to_numeric(cleaned["latitude"], errors="coerce").fillna(0.0)
            
        if "longitude" not in cleaned.columns:
            cleaned["longitude"] = 0.0
        else:
            cleaned["longitude"] = pd.to_numeric(cleaned["longitude"], errors="coerce").fillna(0.0)

        # 4. IP Regex Validation
        ip_valid = cleaned["ip_address"].str.match(IPV4_REGEX, na=False)
        report["invalid_ips_flagged"] = int((~ip_valid).sum())
        
        report["clean_records"] = len(cleaned)
        logger.info(f"Data Validation Complete: {report['clean_records']}/{report['initial_records']} valid records.")
        return cleaned, report
