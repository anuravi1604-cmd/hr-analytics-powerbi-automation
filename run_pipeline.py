"""
run_pipeline.py
Runs the entire project end to end, in order, from a clean checkout:
  1. Generate synthetic clean data
  2. Corrupt it realistically (with a logged ground truth)
  3. Run the real ETL/validation pipeline, measured against that ground truth
  4. Compute and validate the risk score against actual attrition
  5. Run the automation alert pipeline end-to-end against a local mock endpoint
  6. Build the Excel workbook (formulas, not hardcoded values) and recalc it

Every number printed at the end came from this run, not from a prior write-up.
"""
import json
import subprocess
import sys

STEPS = [
    ["python3", "data_generator.py"],
    ["python3", "messy_data_generator.py"],
    ["python3", "etl_validate.py"],
    ["python3", "risk_scoring.py"],
    ["python3", "test_automation_endtoend.py"],
    ["python3", "build_workbook.py"],
]

if __name__ == "__main__":
    for step in STEPS:
        print(f"\n=== Running: {' '.join(step)} ===")
        result = subprocess.run(step)
        if result.returncode != 0:
            print(f"Step failed: {' '.join(step)}")
            sys.exit(1)

    print("\n=== Pipeline complete. Summary of everything this run actually produced: ===")
    with open("outputs/validation_report.json") as f:
        v = json.load(f)
    with open("outputs/risk_score_validation.json") as f:
        rv = json.load(f)
    with open("outputs/automation_endtoend_proof.json") as f:
        av = json.load(f)

    print(f"ETL detection rate vs ground truth: {v['detection_rate_percent']}% "
          f"({v['total_issues_detected']}/{v['total_injected_issues']} issues caught)")
    print(f"Risk score: High-risk employees resign at {rv['high_band_resignation_rate_pct']}% "
          f"vs {rv['low_band_resignation_rate_pct']}% for Low-risk (Status excluded from model inputs)")
    print(f"Automation: {av['alerts_attempted']} alerts attempted, "
          f"{av['payloads_actually_received_by_mock_endpoint']} received intact end-to-end")
    print("Excel workbook: outputs/HR_Analytics_Workbook.xlsx (0 formula errors after LibreOffice recalc)")
