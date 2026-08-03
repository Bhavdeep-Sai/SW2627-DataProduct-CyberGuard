"""
CyberGuard Data Pipeline & Feature Engineering Orchestrator
"""
import numpy as np
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from pathlib import Path
from typing import Tuple, Dict, Any

from cyberguard.config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR
from cyberguard.etl.generator import save_synthetic_dataset
from cyberguard.etl.validator import DataValidator
from cyberguard.utils.logger import get_logger

logger = get_logger("pipeline")

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the Great Circle distance between two points in km."""
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return 0.0
    if lat1 == lat2 and lon1 == lon2:
        return 0.0
        
    R = 6371.0 # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return R * c

class ETLPipeline:
    """End-to-End Data Ingestion, Validation & Feature Engineering Pipeline"""
    
    def __init__(self, raw_csv_path: Path = None):
        self.raw_csv_path = raw_csv_path or (RAW_DATA_DIR / "auth_logs.csv")
        
    def load_raw_data(self) -> pd.DataFrame:
        if not self.raw_csv_path.exists():
            logger.warning(f"Raw data file not found at {self.raw_csv_path}. Generating synthetic logs...")
            self.raw_csv_path = save_synthetic_dataset(self.raw_csv_path)
            
        logger.info(f"Loading raw auth data from {self.raw_csv_path}")
        return pd.read_csv(self.raw_csv_path)

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Derive rich cybersecurity features:
        - Chronological order by user
        - Time diff since last login attempt (seconds)
        - Geo-distance from last login attempt (km)
        - Travel speed (km/h)
        - Sliding 10-min & 1-hour failure counts per user & per IP
        - Is_Failed flag (1/0)
        - Hour of day, day of week
        """
        logger.info("Starting Cybersecurity Feature Engineering...")
        feat = df.sort_values(by=["username", "timestamp"]).copy()
        
        feat["is_failed"] = (feat["status"] == "Failed").astype(int)
        feat["is_success"] = (feat["status"] == "Success").astype(int)
        
        # Temporal features
        feat["hour"] = feat["timestamp"].dt.hour
        feat["day_of_week"] = feat["timestamp"].dt.dayofweek
        feat["is_weekend"] = feat["day_of_week"].isin([5, 6]).astype(int)

        # Lagged features per user
        feat["prev_timestamp"] = feat.groupby("username")["timestamp"].shift(1)
        feat["prev_country"] = feat.groupby("username")["country"].shift(1)
        feat["prev_lat"] = feat.groupby("username")["latitude"].shift(1)
        feat["prev_lon"] = feat.groupby("username")["longitude"].shift(1)
        feat["prev_device"] = feat.groupby("username")["device_type"].shift(1)
        
        # Time delta in minutes & hours
        feat["time_diff_min"] = (feat["timestamp"] - feat["prev_timestamp"]).dt.total_seconds() / 60.0
        feat["time_diff_min"] = feat["time_diff_min"].fillna(999999.0)
        
        # Calculate geographical distance & speed
        distances_km = []
        speeds_kmh = []
        
        for idx, row in feat.iterrows():
            if pd.isna(row["prev_lat"]) or row["time_diff_min"] >= 99999:
                distances_km.append(0.0)
                speeds_kmh.append(0.0)
            else:
                dist = haversine_km(row["prev_lat"], row["prev_lon"], row["latitude"], row["longitude"])
                hours = max(row["time_diff_min"] / 60.0, 0.0001)
                speed = dist / hours
                distances_km.append(round(dist, 2))
                speeds_kmh.append(round(speed, 2))
                
        feat["geo_dist_km"] = distances_km
        feat["geo_speed_kmh"] = speeds_kmh

        # IP-level & User-level rolling failure velocity (10-minute window)
        feat = feat.sort_values(by="timestamp").reset_index(drop=True)
        
        feat_indexed = feat.set_index("timestamp")
        
        ip_fail_10m = feat_indexed.groupby("ip_address")["is_failed"].rolling("10min").sum().reset_index()
        user_fail_10m = feat_indexed.groupby("username")["is_failed"].rolling("10min").sum().reset_index()
        
        feat["ip_failed_count_10m"] = ip_fail_10m["is_failed"].values
        feat["user_failed_count_10m"] = user_fail_10m["is_failed"].values

        # Calculate distinct users per IP in 10-min window
        ip_distinct_counts = []
        for idx, row in feat.iterrows():
            curr_time = row["timestamp"]
            curr_ip = row["ip_address"]
            win_start = curr_time - pd.Timedelta(minutes=10)
            win_df = feat[(feat["ip_address"] == curr_ip) & (feat["timestamp"] >= win_start) & (feat["timestamp"] <= curr_time)]
            ip_distinct_counts.append(win_df["username"].nunique())
            
        feat["ip_distinct_users_10m"] = ip_distinct_counts

        logger.info("Feature engineering completed successfully.")
        return feat

    def run(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        raw_df = self.load_raw_data()
        is_valid, missing_cols = DataValidator.validate_schema(raw_df)
        if not is_valid:
            raise ValueError(f"Schema validation failed. Missing: {missing_cols}")
            
        clean_df, report = DataValidator.clean_and_validate(raw_df)
        processed_df = self.engineer_features(clean_df)
        
        output_file = PROCESSED_DATA_DIR / "processed_auth_logs.csv"
        processed_df.to_csv(output_file, index=False)
        logger.info(f"Processed dataset saved to {output_file}")
        
        return processed_df, report

if __name__ == "__main__":
    pipeline = ETLPipeline()
    df, r = pipeline.run()
    print(f"ETL Execution complete. Total rows: {len(df)}")
