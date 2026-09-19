# HR Retention Risk & Automation Pipeline (v2)

An HR analytics project that goes from a messy raw export to a validated dataset, a
retention-risk score, and an automated alert — with every step actually implemented
and tested, not just designed.

> **Scope note, stated plainly:** the HR data is synthetic and reproducible (seeded
generator, not a real company's employee data). The numbers below all come from
running this code, not from an estimate. What "automated" means here, precisely:
> the ETL, risk scoring, and alert-sending pipeline are real, tested, and would work
> unchanged against a live Microsoft Teams webhook or Power Automate HTTP trigger.
> The alerting pipeline has also been tested against a live external HTTPS webhook
> endpoint using the same Teams-compatible payloads; direct delivery to a Microsoft
> Teams channel has not been verified because no live Teams tenant was available.
> Swapping in a real webhook URL requires no code change (see "Going live" below).

## What's real and tested here (v2 — rebuilt from the ground up)

| Component | v1 (prototype) | v2 (this version) |
|---|---|---|
| HR data | Synthetic, generated | Synthetic, generated — same honest framing |
| Data quality issues | Not present | **Real, injected, logged issues** (duplicates, blanks, typos, bad dtypes) with a ground-truth log |
| ETL / validation | Not implemented | **Real Python pipeline**, detection rate measured against the ground truth: **97.5%** (199/204 known issues caught), runtime ~0.02s for 1,224 rows |
| Risk scoring | DAX blueprint, untested | **Implemented and validated**: High-risk employees resign at **30.8%** vs **9.6%** for Low-risk — computed with `Status` excluded from the model's inputs |
| Automation → action | Design doc only, nothing connected | **Tested end-to-end**: 99 high-risk active employees → 99 Teams-compatible HTTP webhook alerts built; live external testing successfully delivered 50 alerts before the free endpoint limit, while the full 99-alert run remains covered by the local mock test |
| Power BI / Excel report | Design doc only | **Real .xlsx workbook**, 21,500+ live formulas (SUMIFS/SUMPRODUCT — no hardcoded numbers), 0 formula errors after LibreOffice recalculation |

## Pipeline

```
data_generator.py          -> outputs/clean_master_data.csv (1,200 synthetic employees)
messy_data_generator.py    -> outputs/raw_hris_export.csv + injected_errors_ground_truth.json
etl_validate.py            -> outputs/cleaned_data.csv + validation_report.{json,md}
risk_scoring.py             -> outputs/risk_scored_employees.csv + risk_score_validation.json
automation_alert.py        -> sends Teams-format webhook alerts for High-risk Active employees
test_automation_endtoend.py-> proves the alert pipeline works, against a local mock endpoint
build_workbook.py          -> outputs/HR_Analytics_Workbook.xlsx (Assumptions/Cleaned_Data/Risk_Model/Dashboard/Validation_Log)
```

Run everything in order with:

```bash
pip install -r requirements.txt
python3 run_pipeline.py
```

## Risk scoring methodology

A weighted composite of six drivers (weights sum to 1.0, editable in the workbook's
`Assumptions` sheet): overtime status, satisfaction score, months since promotion,
salary percentile within department, work-life balance, and tenure. Implemented
identically in `risk_scoring.py` (Python, used to validate the model) and as live
Excel formulas in the workbook's `Risk_Model` sheet (used for the deliverable).

**Validation, not just computation:** the model never sees `Status` (Active/Resigned)
as an input. After scoring, we check whether the score actually separates people who
left from people who stayed — it does: employees in the High-risk band resigned at
30.8%, versus 9.6% for Low-risk, a real and repeatable pattern in this dataset.

## Automation: what "connects to Teams/Outlook" actually means here

`automation_alert.py` builds a real Microsoft Teams **Incoming Webhook MessageCard**
payload (the exact schema Teams expects) for every High-risk Active employee, and
sends it over real HTTP via `urllib`. `test_automation_endtoend.py` proves the whole
pipeline works by standing up a local HTTP server that mimics a Teams webhook
receiver, running the real alert pipeline against it, and confirming every payload
was sent and received intact.

The alert pipeline was additionally tested against a live external HTTPS webhook
endpoint using the same Teams-compatible MessageCard payloads. In that live test,
99 alerts were attempted and 50 were successfully delivered before the free endpoint
limit was reached. This verifies external HTTP delivery and payload generation, but
it does not constitute direct Microsoft Teams channel delivery.

**Going live:** set the `HR_ALERT_WEBHOOK_URL` environment variable to a real Teams
channel's Incoming Webhook URL, or a Power Automate "When an HTTP request is
received" trigger URL, and run `python3 automation_alert.py` — no code changes
needed. The live external webhook test used the same environment-variable mechanism.

## Files

- `data_generator.py`, `messy_data_generator.py` — synthetic data + realistic corruption, with a logged ground truth
- `etl_validate.py` — real ETL/validation pipeline (Power-Query-equivalent logic)
- `risk_scoring.py` — weighted risk model + validation against actual attrition
- `automation_alert.py`, `test_automation_endtoend.py` — Teams-webhook automation, tested end-to-end
- `build_workbook.py` — generates `outputs/HR_Analytics_Workbook.xlsx` with live formulas
- `dax_measures.md`, `power_query_m.txt` — the equivalent logic written as native DAX / Power Query M, for a real Power BI Desktop / Power Query implementation
- `vba_macro.bas` — Excel VBA equivalent of the validation checks in `etl_validate.py` (same logic; VBA itself needs a live Excel/VBA host to run, which isn't available in this repo's test environment — the Python version is the one that's actually executed and tested here)
- `outputs/` — everything generated by `run_pipeline.py`: cleaned data, validation report, risk scores, automation proof log, and the Excel workbook

## Honest limitations

- The dataset is synthetic. Patterns described here are real patterns *in this
generated dataset*, not findings about any real company or workforce.
- The automation has been tested against both a local mock endpoint and a live
external HTTPS webhook endpoint using Teams-compatible MessageCard payloads. A live
Microsoft Teams tenant was not available for direct channel verification, so actual
Teams channel delivery remains unverified.
- `vba_macro.bas` and the Power Query M script are written to be correct and
runnable in a real Excel/Power BI environment, but — unlike the Python pipeline —
they have not been executed and verified in this repository, since no licensed
Excel/Power BI Desktop instance is available here.
