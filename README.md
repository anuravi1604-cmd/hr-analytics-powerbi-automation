# 👥 HR Analytics & Attrition Dashboard

An interactive Streamlit dashboard for exploring employee attrition patterns using a reproducible synthetic HR dataset. The project combines Python data analysis with Power BI / Power Automate design specifications and a clickable UX prototype.

> **Scope note:** This repository is a portfolio prototype. The HR data is synthetic, and the Power BI / Power Automate components are implementation blueprints rather than connected production systems.

## What is implemented

- **Synthetic HR dataset:** `data_generator.py` generates 1,200 reproducible employee records with demographics, role, salary, tenure, overtime, satisfaction, performance, and attrition fields.
- **Interactive dashboard:** `streamlit_app.py` provides department and overtime filters, headcount/attrition KPIs, department-level attrition analysis, overtime vs. attrition charts, and a filtered employee table.
- **Attrition logic:** The synthetic-data generator deliberately introduces relationships between satisfaction, overtime, work-life balance, tenure, promotion stagnation, salary position, and attrition so the dashboard has patterns to analyze.
- **Power BI / Power Automate design:** Documentation shows how the analytical workflow could be extended into reporting and alerts. These integrations are not connected to live Microsoft services in this repository.
- **UX prototype:** `ux_flow_prototype.html` demonstrates a proposed HR retention-alert experience.

## Dashboard

The Streamlit application is available at the repository's configured Streamlit deployment, if the deployment is active. The app can also be run locally with the instructions below.

### Key views

- Attrition rate by department
- Overtime and attrition distribution
- Headcount, resignations, attrition rate, and average salary for the selected filters
- Employee-level data preview

## Data generation

The dataset is generated locally with a fixed random seed (`42`) for reproducibility. It is **synthetic data**, not a real company employee database.

The generator creates 1,200 records by default and uses rule-based probability adjustments to produce an `Attrition` outcome. Therefore, patterns found in the dashboard describe the generated dataset; they should not be presented as findings from a real workforce study.

## Repository assets

- `streamlit_app.py` — interactive Streamlit dashboard
- `data_generator.py` — synthetic HR data generator
- `hr_employee_data.csv` — generated dataset used by the dashboard
- `power_query_m.txt` — proposed Power Query transformations
- `dax_measures.md` — proposed DAX measures for a Power BI implementation
- `power_automate_flow.md` — Power Automate implementation blueprint
- `FIGMA_UX_FLOW.md` — UX specification
- `ux_flow_prototype.html` — clickable UX prototype
- `dashboard_design.md` — dashboard design specification
- `vba_macro.bas` — example VBA validation logic

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Technology

Python, Pandas, Streamlit, Plotly, Power Query, DAX, VBA, Power Automate (design), and Figma-style UX prototyping.

## License

MIT License. Developed by Anushka.
