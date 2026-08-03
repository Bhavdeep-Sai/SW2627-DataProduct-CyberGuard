"""
SQLite Normalized Database Schema Manager & Data Ingestor
"""
import sqlite3
import pandas as pd
from pathlib import Path
from cyberguard.config.settings import DATABASE_PATH
from cyberguard.utils.logger import get_logger

logger = get_logger("db_manager")

SCHEMA_DDL = """
-- 1. Users Normalized Table
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    role TEXT DEFAULT 'Standard'
);

-- 2. Devices Normalized Table
CREATE TABLE IF NOT EXISTS devices (
    device_id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_type TEXT UNIQUE
);

-- 3. Auth Events Fact Table
CREATE TABLE IF NOT EXISTS auth_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL,
    username TEXT NOT NULL,
    ip_address TEXT NOT NULL,
    country TEXT,
    city TEXT,
    latitude REAL,
    longitude REAL,
    status TEXT NOT NULL,
    device_type TEXT,
    user_agent TEXT,
    threat_vector TEXT,
    anomaly_score REAL,
    risk_score REAL,
    severity TEXT,
    confidence REAL,
    primary_reason TEXT,
    recommended_action TEXT,
    FOREIGN KEY (username) REFERENCES users (username)
);

-- 4. Risk Alerts Summary Table
CREATE TABLE IF NOT EXISTS risk_alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER,
    timestamp TIMESTAMP,
    username TEXT,
    severity TEXT,
    risk_score REAL,
    primary_reason TEXT,
    FOREIGN KEY (event_id) REFERENCES auth_events (event_id)
);

-- Indexes for high performance analytical querying
CREATE INDEX IF NOT EXISTS idx_auth_username_ts ON auth_events (username, timestamp);
CREATE INDEX IF NOT EXISTS idx_auth_ip ON auth_events (ip_address);
CREATE INDEX IF NOT EXISTS idx_auth_risk ON auth_events (risk_score);
CREATE INDEX IF NOT EXISTS idx_auth_severity ON auth_events (severity);

-- Analytical View 1: User Risk Summary with Window Functions
CREATE VIEW IF NOT EXISTS v_user_risk_summary AS
SELECT 
    username,
    COUNT(*) as total_logins,
    SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) as total_failures,
    ROUND(CAST(SUM(CASE WHEN status = 'Failed' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100.0, 2) as failure_rate_pct,
    MAX(risk_score) as max_risk_score,
    AVG(risk_score) as avg_risk_score,
    COUNT(DISTINCT ip_address) as distinct_ips,
    COUNT(DISTINCT country) as distinct_countries
FROM auth_events
GROUP BY username;

-- Analytical View 2: High Severity Incident Timeline
CREATE VIEW IF NOT EXISTS v_threat_timeline AS
SELECT 
    event_id,
    timestamp,
    username,
    ip_address,
    country,
    status,
    threat_vector,
    risk_score,
    severity,
    primary_reason
FROM auth_events
WHERE risk_score >= 70.0
ORDER BY timestamp DESC;
"""

DROP_DDL = """
DROP VIEW IF EXISTS v_user_risk_summary;
DROP VIEW IF EXISTS v_threat_timeline;
DROP TABLE IF EXISTS risk_alerts;
DROP TABLE IF EXISTS auth_events;
DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS users;
"""

class DatabaseManager:
    """Manages SQLite schema creation, data ingestion, and analytical views."""

    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path

    def init_database(self, force_recreate: bool = False) -> None:
        """Create tables, indexes, and views."""
        logger.info(f"Initializing SQLite database at {self.db_path}...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if force_recreate:
            cursor.executescript(DROP_DDL)
            
        cursor.executescript(SCHEMA_DDL)
        conn.commit()
        conn.close()
        logger.info("Database schema & views initialized successfully.")

    def ingest_events(self, df: pd.DataFrame) -> None:
        """Populate database tables from processed DataFrame."""
        self.init_database(force_recreate=True)
        logger.info(f"Ingesting {len(df)} records into SQLite database...")
        conn = sqlite3.connect(self.db_path)
        
        # 1. Populate Users Table
        users_df = df.groupby("username").agg(
            first_seen=("timestamp", "min"),
            last_seen=("timestamp", "max")
        ).reset_index()
        users_df["role"] = users_df["username"].apply(
            lambda u: "Administrator" if u in ["root", "admin", "sysadmin"] else "Standard"
        )
        users_df.to_sql("users", conn, if_exists="replace", index=False)

        # 2. Populate Devices Table
        devices_df = pd.DataFrame({"device_type": df["device_type"].unique()})
        devices_df.to_sql("devices", conn, if_exists="replace", index_label="device_id")

        # 3. Populate Auth Events Fact Table
        db_cols = [
            "timestamp", "username", "ip_address", "country", "city",
            "latitude", "longitude", "status", "device_type", "user_agent",
            "threat_vector", "anomaly_score", "risk_score", "severity",
            "confidence", "primary_reason", "recommended_action"
        ]
        # Keep only columns present in df
        available_cols = [c for c in db_cols if c in df.columns]
        df[available_cols].to_sql("auth_events", conn, if_exists="replace", index_label="event_id")

        # 4. Populate Risk Alerts
        high_risk = df[df["risk_score"] >= 70.0].copy()
        if not high_risk.empty:
            alerts_df = high_risk[["timestamp", "username", "severity", "risk_score", "primary_reason"]].copy()
            alerts_df.to_sql("risk_alerts", conn, if_exists="replace", index_label="alert_id")

        conn.commit()
        conn.close()
        logger.info("Database ingestion complete.")

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame."""
        conn = sqlite3.connect(self.db_path)
        res = pd.read_sql_query(query, conn)
        conn.close()
        return res
