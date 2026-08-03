"""
CyberGuard SQLite Database Ingestion & Verification Script
"""
from cyberguard.etl.pipeline import ETLPipeline
from cyberguard.risk.risk_engine import RiskEngine
from cyberguard.sql.db_manager import DatabaseManager

def main():
    print("Ingesting Data into SQLite Database...")
    pipeline = ETLPipeline()
    raw_df, _ = pipeline.run()
    
    risk_engine = RiskEngine()
    final_df = risk_engine.evaluate_dataframe(raw_df)
    
    db_mgr = DatabaseManager()
    db_mgr.ingest_events(final_df)
    
    res = db_mgr.execute_query("SELECT COUNT(*) as event_count FROM auth_events;")
    print(f"Database Ingestion Successful. Total auth_events in SQLite: {res.loc[0, 'event_count']}")

if __name__ == "__main__":
    main()
