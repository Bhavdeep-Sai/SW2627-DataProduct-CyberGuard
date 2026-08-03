# CyberGuard Architecture & System Design Document

## 1. System Overview & Data Flow
CyberGuard follows a clean, decoupled 5-tier enterprise software architecture:

```
+-----------------------------------------------------------------------+
|                         DATA TELEMETRY INTAKE                         |
|             (Raw Authentication Event Logs: CSV / JSON API)           |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    DATA ENGINEERING & ETL PIPELINE                    |
|       - Schema Validation & Clean (DataValidator)                     |
|       - Velocity & Geographical Distance Calculation (Haversine)      |
|       - 10-Min Rolling Failure & Distinct User Windowing              |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                  THREAT DETECTION & ML ANOMALY ENGINE                 |
|   Rule Threat Engine                   ML Anomaly Suite               |
|   - Impossible Travel                  - Isolation Forest             |
|   - Brute Force Burst                  - One-Class SVM / LOF          |
|   - Credential Stuffing                - DBSCAN / MLP Autoencoder     |
|   - Privilege Escalation                                              |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                      COMPOSITE RISK ENGINE & AI                       |
|   - Composite Risk Score (0-100) & Severity Level Mapping             |
|   - Confidence Factor Calculation & Recommended Action Playbooks       |
|   - AI Natural Language Insight Generator                             |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                     DATABASE & REPORTING SERVICE                      |
|   - SQLite Normalized Tables (users, devices, auth_events, alerts)    |
|   - Window Function Views (v_user_risk_summary, v_threat_timeline)    |
|   - Automated PDF Briefing & CSV Exporter (SOCReportGenerator)        |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    STREAMLIT SOC ENTERPRISE UI                        |
|   - Executive Overview       - Real-Time Incident Explorer            |
|   - ML Anomaly Benchmark     - Geo & Impossible Travel Map            |
|   - Behavioral Profiler      - SQL Analytical Studio                  |
+-----------------------------------------------------------------------+
```

---

## 2. Component Design & Responsibilities

1. `cyberguard.etl`: Responsible for strict schema enforcement, missing data imputation, timestamp normalization, geographical speed derivation (km/h), and windowed velocity aggregations.
2. `cyberguard.analytics`: Houses domain-specific security rules for detecting Impossible Travel, Brute Force, Credential Stuffing, and Privilege Escalation attempts.
3. `cyberguard.models`: Provides multi-model benchmarking (Isolation Forest, One-Class SVM, LOF, DBSCAN, Autoencoder) and fits the production anomaly engine.
4. `cyberguard.risk`: Synthesizes heuristic rules and ML anomaly scores into a unified 0-100 Risk Score with SOC actionable recommendations.
5. `cyberguard.ai`: Generates natural language threat briefings for executives and analysts.
6. `cyberguard.sql`: Manages SQLite database creation, indexing, normalized table ingestion, and window analytics.
7. `cyberguard.dashboard`: Modular Streamlit views rendering interactive Plotly charts and tables.
8. `cyberguard.reporting`: Produces downloadable PDF and CSV SOC incident reports.
