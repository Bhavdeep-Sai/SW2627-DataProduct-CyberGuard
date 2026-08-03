"""
User & Device Behavioral Baseline Profiler
"""
import pandas as pd
from typing import Dict, Any
from cyberguard.utils.logger import get_logger

logger = get_logger("profiler")

class BehavioralProfiler:
    """Builds historical baseline profiles for Users and Devices."""

    @staticmethod
    def build_user_profiles(df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate behavioral baseline statistics per username."""
        logger.info("Building User Behavioral Profiles...")
        
        profiles = df.groupby("username").agg(
            total_attempts=("status", "count"),
            failed_attempts=("is_failed", "sum"),
            successful_attempts=("is_success", "sum"),
            unique_ips=("ip_address", "nunique"),
            unique_countries=("country", "nunique"),
            unique_devices=("device_type", "nunique"),
            max_speed_kmh=("geo_speed_kmh", "max"),
            first_seen=("timestamp", "min"),
            last_seen=("timestamp", "max")
        ).reset_index()

        profiles["failure_rate_pct"] = round((profiles["failed_attempts"] / profiles["total_attempts"]) * 100.0, 2)
        
        # Attach threat counts if columns present
        if "flag_impossible_travel" in df.columns:
            imp_travel = df.groupby("username")["flag_impossible_travel"].sum().reset_index()
            brute_force = df.groupby("username")["flag_brute_force"].sum().reset_index()
            profiles = profiles.merge(imp_travel, on="username", how="left").merge(brute_force, on="username", how="left")
            profiles["impossible_travel_events"] = profiles["flag_impossible_travel"].fillna(0).astype(int)
            profiles["brute_force_events"] = profiles["flag_brute_force"].fillna(0).astype(int)
            profiles = profiles.drop(columns=["flag_impossible_travel", "flag_brute_force"])

        return profiles

    @staticmethod
    def build_device_profiles(df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate behavioral profile per device_type."""
        logger.info("Building Device Behavioral Profiles...")
        
        profiles = df.groupby("device_type").agg(
            total_attempts=("status", "count"),
            failed_attempts=("is_failed", "sum"),
            unique_users=("username", "nunique"),
            unique_ips=("ip_address", "nunique"),
            unique_countries=("country", "nunique")
        ).reset_index()

        profiles["failure_rate_pct"] = round((profiles["failed_attempts"] / profiles["total_attempts"]) * 100.0, 2)
        return profiles
