# CyberGuard Utility Scripts

This directory contains clean CLI entrypoint scripts referencing the `cyberguard` production package:

- `run_pipeline.py`: Executes end-to-end data ingestion, validation, threat rules, ML anomaly engine, and risk scoring.
- `run_db.py`: Initializes SQLite tables, views, indexes, and ingests telemetry data into `data/cyberguard.db`.