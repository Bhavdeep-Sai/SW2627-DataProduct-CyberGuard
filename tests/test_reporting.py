"""
Pytest Test Suite for SOC Report Generator (PDF & CSV)
"""
import pytest
import pandas as pd
from pathlib import Path
from cyberguard.reporting.report_generator import SOCReportGenerator
from cyberguard.etl.pipeline import ETLPipeline
from cyberguard.risk.risk_engine import RiskEngine

def test_report_generator(tmp_path):
    pipeline = ETLPipeline()
    df, _ = pipeline.run()
    risk_engine = RiskEngine()
    final_df = risk_engine.evaluate_dataframe(df)
    
    reporter = SOCReportGenerator(output_dir=tmp_path)
    
    # 1. Test CSV Export
    csv_file = reporter.export_csv(final_df, filename="test_report.csv")
    assert csv_file.exists()
    assert csv_file.stat().st_size > 0

    # 2. Test PDF Export
    pdf_file = reporter.generate_pdf_report(final_df, filename="test_report.pdf")
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 0
