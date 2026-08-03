# CyberGuard Python Package API Reference

## 1. Data Engineering (`cyberguard.etl`)

### `ETLPipeline(raw_csv_path: Path = None)`
End-to-end data ingestion, validation, and feature engineering.
- `.run() -> Tuple[pd.DataFrame, Dict[str, Any]]`: Executes cleaning, normalization, velocity window calculation, and saves output to `data/processed/processed_auth_logs.csv`.

### `DataValidator`
- `.validate_schema(df: pd.DataFrame) -> Tuple[bool, list]`: Validates required column presence.
- `.clean_and_validate(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]`: Cleans duplicates, coerces timestamps, imputes nulls, and validates IPv4 regex.

---

## 2. Security Threat Analytics (`cyberguard.analytics`)

### `ThreatRuleEngine`
- `.evaluate_dataframe(df: pd.DataFrame) -> pd.DataFrame`: Evaluates rule-based threat indicators:
  - `flag_impossible_travel`: Speed > 800 km/h and distance > 100 km.
  - `flag_brute_force`: >= 5 failed logins in 10 minutes.
  - `flag_credential_stuffing`: >= 10 distinct usernames attempted from single IP.
  - `flag_privilege_escalation`: Failed login targeting `root`, `admin`, `sysadmin`.

### `BehavioralProfiler`
- `.build_user_profiles(df: pd.DataFrame) -> pd.DataFrame`: Builds historical baseline profiles per username.
- `.build_device_profiles(df: pd.DataFrame) -> pd.DataFrame`: Builds profile statistics per device type.

---

## 3. Machine Learning (`cyberguard.models`)

### `ModelBenchmarker(contamination: float = 0.08)`
- `.benchmark_models(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]`: Trains and compares Isolation Forest, One-Class SVM, LOF, DBSCAN, and Autoencoder.

### `AnomalyEngine(contamination: float = 0.08)`
- `.fit_predict(df: pd.DataFrame) -> pd.DataFrame`: Fits ensemble model and attaches `anomaly_score` [0.0, 1.0], `is_anomaly`, and `anomaly_confidence`.

---

## 4. Risk Engine (`cyberguard.risk`)

### `RiskEngine`
- `.evaluate_dataframe(df: pd.DataFrame) -> pd.DataFrame`: Computes composite `risk_score` (0-100), `severity`, `confidence`, `primary_reason`, `risk_factors`, `recommended_action`, and `explainability`.

---

## 5. Database & Reporting (`cyberguard.sql` & `cyberguard.reporting`)

### `DatabaseManager(db_path: Path)`
- `.init_database()`: Creates tables (`users`, `devices`, `auth_events`, `risk_alerts`), indexes, and views (`v_user_risk_summary`, `v_threat_timeline`).
- `.ingest_events(df: pd.DataFrame)`: Ingests DataFrame into SQLite tables.

### `SOCReportGenerator(output_dir: Path)`
- `.generate_pdf_report(df: pd.DataFrame, filename: str) -> Path`: Builds executive PDF incident briefing.
- `.export_csv(df: pd.DataFrame, filename: str) -> Path`: Exports dataset to CSV.
