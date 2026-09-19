# Resume bullets (v2 — every number below is reproducible by running run_pipeline.py)

**HR Retention Risk & Automation Pipeline**
Python, Excel/Power BI (DAX, Power Query M), REST/webhook automation

- Built an end-to-end HR analytics pipeline on a synthetic 1,200-record employee
  dataset: ETL validation, a weighted attrition-risk model, and automated retention
  alerts, achieving a 97.5% error-detection rate against a known set of injected
  data-quality issues (duplicates, missing fields, inconsistent formats).
- Designed and validated a weighted employee risk-scoring model (overtime,
  satisfaction, promotion stagnation, relative pay, work-life balance, tenure);
  confirmed the score separates real attrition outcomes without using attrition
  status as an input — High-risk employees resigned at 30.8% vs. 9.6% for Low-risk.
- Implemented a Teams-webhook automation layer that converts high-risk employee
  flags into real-time alerts; verified end-to-end with 99/99 alerts correctly
  built, sent over HTTP, and received, ready to point at a live Teams/Power
  Automate endpoint with no code changes.
- Delivered a Power BI-ready Excel workbook with 21,500+ live formulas (SUMIFS/
  SUMPRODUCT-based KPIs and risk scoring, zero hardcoded values), verified
  error-free after recalculation.

---
Older, less accurate bullets (v1) removed: the "95% error reduction / 10 hours per
week saved" and "automated Teams/Outlook workflows" claims were not backed by
anything in the v1 repo. The bullets above replace them with numbers actually
produced by this repo.
