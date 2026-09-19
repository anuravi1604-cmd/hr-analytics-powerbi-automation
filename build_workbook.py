"""
build_workbook.py
Builds HR_Analytics_Workbook.xlsx:
  - Assumptions   : editable weight table (yellow fill = user-editable inputs)
  - Cleaned_Data  : the ETL output (values — this is the Power Query load step)
  - Risk_Model    : per-employee risk score computed with REAL Excel formulas that
                    reference the Assumptions weights, so it recalculates live —
                    not a column of Python-computed numbers pasted in.
  - Dashboard     : KPIs and a chart computed with SUMIFS/COUNTIFS formulas.
  - Validation_Log: the ETL validation report (values — a log of a completed run).
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.utils import get_column_letter

FONT = "Arial"
HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(name=FONT, bold=True, color="FFFFFF", size=11)
INPUT_FILL = PatternFill("solid", fgColor="FFFF00")
BASE_FONT = Font(name=FONT, size=10)
BOLD = Font(name=FONT, bold=True, size=10)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def style_header_row(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER


def autosize(ws, ncols, min_w=10, max_w=32):
    for c in range(1, ncols + 1):
        col = get_column_letter(c)
        maxlen = min_w
        for cell in ws[col]:
            if cell.value is not None:
                maxlen = max(maxlen, len(str(cell.value)) + 2)
        ws.column_dimensions[col].width = min(maxlen, max_w)


def build():
    cleaned = pd.read_csv("outputs/cleaned_data.csv")
    validation = pd.read_json("outputs/validation_report.json", typ="series")
    issues = validation["issues_detected_and_fixed_by_type"]
    gt = validation["ground_truth_injected_by_type"]

    wb = Workbook()

    # ---------------- Assumptions ----------------
    ws = wb.active
    ws.title = "Assumptions"
    ws["A1"] = "HR Retention Risk Model — Assumptions"
    ws["A1"].font = Font(name=FONT, bold=True, size=14)
    ws["A3"] = "Edit the weights below (yellow cells). They must sum to 1.00 — B10 checks this live."
    ws["A3"].font = BASE_FONT

    headers = ["Risk Driver", "Weight", "Definition"]
    ws.append([])
    ws.append(headers)
    style_header_row(ws, ws.max_row, 3)

    rows = [
        ("Overtime", 0.28, "1 if employee is currently on overtime, else 0"),
        ("Low Satisfaction", 0.24, "Higher when SatisfactionScore is low (1-5 scale, inverted)"),
        ("Promotion Stagnation", 0.16, "MonthsSincePromotion / 60, capped at 1"),
        ("Below-Department Pay", 0.14, "1 minus the employee's salary percentile within their department"),
        ("Poor Work-Life Balance", 0.12, "Higher when WorkLifeBalance is low (1-5 scale, inverted)"),
        ("Low Tenure", 0.06, "Higher for employees with under 8 years tenure"),
    ]
    first_weight_row = ws.max_row + 1
    for name, w, defn in rows:
        ws.append([name, w, defn])
        r = ws.max_row
        ws.cell(row=r, column=2).fill = INPUT_FILL
        ws.cell(row=r, column=2).number_format = "0.00"
        for c in range(1, 4):
            ws.cell(row=r, column=c).font = BASE_FONT
            ws.cell(row=r, column=c).border = BORDER
    last_weight_row = ws.max_row

    ws.append([])
    check_row = ws.max_row + 1
    ws.cell(row=check_row, column=1, value="Weights sum to (must equal 1.00):").font = BOLD
    ws.cell(row=check_row, column=2, value=f"=SUM(B{first_weight_row}:B{last_weight_row})").font = BOLD
    ws.cell(row=check_row, column=2).number_format = "0.00"

    ws.append([])
    band_row = ws.max_row + 1
    ws.cell(row=band_row, column=1, value="Risk band thresholds (0-100 scale):").font = BOLD
    ws.append(["High risk: score >=", 65])
    ws.append(["Medium risk: score >=", 45])
    ws.cell(row=ws.max_row - 1, column=2).fill = INPUT_FILL
    ws.cell(row=ws.max_row, column=2).fill = INPUT_FILL
    high_thresh_cell = f"Assumptions!$B${ws.max_row - 1}"
    med_thresh_cell = f"Assumptions!$B${ws.max_row}"

    weight_cells = {
        "OT": f"Assumptions!$B${first_weight_row}",
        "Sat": f"Assumptions!$B${first_weight_row + 1}",
        "Promo": f"Assumptions!$B${first_weight_row + 2}",
        "Pay": f"Assumptions!$B${first_weight_row + 3}",
        "WLB": f"Assumptions!$B${first_weight_row + 4}",
        "Tenure": f"Assumptions!$B${first_weight_row + 5}",
    }
    autosize(ws, 3, max_w=46)

    # ---------------- Cleaned_Data ----------------
    ws2 = wb.create_sheet("Cleaned_Data")
    cols = list(cleaned.columns)
    ws2.append(cols)
    style_header_row(ws2, 1, len(cols))
    for _, row in cleaned.iterrows():
        ws2.append(list(row))
    for r in range(2, ws2.max_row + 1):
        for c in range(1, len(cols) + 1):
            ws2.cell(row=r, column=c).font = BASE_FONT
    autosize(ws2, len(cols))
    ws2.freeze_panes = "A2"
    n_data_rows = len(cleaned)
    last_data_row = n_data_rows + 1

    col_idx = {name: i + 1 for i, name in enumerate(cols)}

    # ---------------- Risk_Model (REAL FORMULAS) ----------------
    ws3 = wb.create_sheet("Risk_Model")
    model_headers = [
        "EmployeeID", "Department", "OverTime", "SatisfactionScore", "MonthsSincePromotion",
        "AnnualSalary", "DeptSalaryPercentile", "WorkLifeBalance", "TenureYears",
        "OT_risk", "Satisfaction_risk", "Promotion_risk", "Pay_risk", "WLB_risk", "Tenure_risk",
        "RiskScore", "RiskBand", "Status",
    ]
    ws3.append(model_headers)
    style_header_row(ws3, 1, len(model_headers))
    mi = {name: i + 1 for i, name in enumerate(model_headers)}

    for i in range(n_data_rows):
        r = i + 2
        src = r  # Cleaned_Data row aligns 1:1 with Risk_Model row
        def cd(field):
            return f"Cleaned_Data!{get_column_letter(col_idx[field])}{src}"

        ws3.cell(row=r, column=mi["EmployeeID"], value=f"={cd('EmployeeID')}")
        ws3.cell(row=r, column=mi["Department"], value=f"={cd('Department')}")
        ws3.cell(row=r, column=mi["OverTime"], value=f"={cd('OverTime')}")
        ws3.cell(row=r, column=mi["SatisfactionScore"], value=f"={cd('SatisfactionScore')}")
        ws3.cell(row=r, column=mi["MonthsSincePromotion"], value=f"={cd('MonthsSincePromotion')}")
        ws3.cell(row=r, column=mi["AnnualSalary"], value=f"={cd('AnnualSalary')}")
        ws3.cell(row=r, column=mi["WorkLifeBalance"], value=f"={cd('WorkLifeBalance')}")
        ws3.cell(row=r, column=mi["TenureYears"], value=f"={cd('TenureYears')}")
        ws3.cell(row=r, column=mi["Status"], value=f"={cd('Status')}")

        dept_col = get_column_letter(mi["Department"])
        sal_col = get_column_letter(mi["AnnualSalary"])
        dept_range = f"${dept_col}$2:${dept_col}${last_data_row}"
        sal_range = f"${sal_col}$2:${sal_col}${last_data_row}"
        # Percentile of this salary within same-department salaries (SUMPRODUCT-based, no array-entry needed)
        pct_formula = (
            f"=SUMPRODUCT(({dept_range}={get_column_letter(mi['Department'])}{r})*"
            f"({sal_range}<={get_column_letter(mi['AnnualSalary'])}{r}))/"
            f"SUMPRODUCT(({dept_range}={get_column_letter(mi['Department'])}{r})*1)"
        )
        ws3.cell(row=r, column=mi["DeptSalaryPercentile"], value=pct_formula)

        ot_col = get_column_letter(mi["OverTime"])
        sat_col = get_column_letter(mi["SatisfactionScore"])
        promo_col = get_column_letter(mi["MonthsSincePromotion"])
        pctile_col = get_column_letter(mi["DeptSalaryPercentile"])
        wlb_col = get_column_letter(mi["WorkLifeBalance"])
        tenure_col = get_column_letter(mi["TenureYears"])

        ws3.cell(row=r, column=mi["OT_risk"], value=f'=IF({ot_col}{r}="Yes",1,0)')
        ws3.cell(row=r, column=mi["Satisfaction_risk"], value=f"=MIN(MAX(1-({sat_col}{r}-1)/4,0),1)")
        ws3.cell(row=r, column=mi["Promotion_risk"], value=f"=MIN({promo_col}{r}/60,1)")
        ws3.cell(row=r, column=mi["Pay_risk"], value=f"=MIN(MAX(1-{pctile_col}{r},0),1)")
        ws3.cell(row=r, column=mi["WLB_risk"], value=f"=MIN(MAX(1-({wlb_col}{r}-1)/4,0),1)")
        ws3.cell(row=r, column=mi["Tenure_risk"], value=f"=1-MIN({tenure_col}{r}/8,1)")

        otr = f"{get_column_letter(mi['OT_risk'])}{r}"
        satr = f"{get_column_letter(mi['Satisfaction_risk'])}{r}"
        promor = f"{get_column_letter(mi['Promotion_risk'])}{r}"
        payr = f"{get_column_letter(mi['Pay_risk'])}{r}"
        wlbr = f"{get_column_letter(mi['WLB_risk'])}{r}"
        tenr = f"{get_column_letter(mi['Tenure_risk'])}{r}"
        score_formula = (
            f"=ROUND(100*({otr}*{weight_cells['OT']}+{satr}*{weight_cells['Sat']}"
            f"+{promor}*{weight_cells['Promo']}+{payr}*{weight_cells['Pay']}"
            f"+{wlbr}*{weight_cells['WLB']}+{tenr}*{weight_cells['Tenure']}),1)"
        )
        ws3.cell(row=r, column=mi["RiskScore"], value=score_formula)

        score_col = get_column_letter(mi["RiskScore"])
        band_formula = (
            f'=IF({score_col}{r}>={high_thresh_cell},"High",'
            f'IF({score_col}{r}>={med_thresh_cell},"Medium","Low"))'
        )
        ws3.cell(row=r, column=mi["RiskBand"], value=band_formula)

        for c in range(1, len(model_headers) + 1):
            ws3.cell(row=r, column=c).font = BASE_FONT
        ws3.cell(row=r, column=mi["RiskScore"]).number_format = "0.0"
        ws3.cell(row=r, column=mi["DeptSalaryPercentile"]).number_format = "0.0%"

    autosize(ws3, len(model_headers))
    ws3.freeze_panes = "A2"

    # ---------------- Dashboard (formulas over Risk_Model) ----------------
    ws4 = wb.create_sheet("Dashboard")
    ws4["A1"] = "HR Retention Risk — Live Dashboard"
    ws4["A1"].font = Font(name=FONT, bold=True, size=14)
    ws4["A2"] = "All figures below are formulas over Risk_Model — they update if the weights or data change."
    ws4["A2"].font = Font(name=FONT, italic=True, size=9, color="666666")

    rm_last = last_data_row
    status_col = get_column_letter(mi["Status"])
    ot_col = get_column_letter(mi["OverTime"])
    band_col = get_column_letter(mi["RiskBand"])
    dept_col_rm = get_column_letter(mi["Department"])

    kpi_rows = [
        ("Total Employees (cleaned dataset)", f"=COUNTA(Risk_Model!A2:A{rm_last})"),
        ("Active", f'=COUNTIF(Risk_Model!{status_col}2:{status_col}{rm_last},"Active")'),
        ("Resigned", f'=COUNTIF(Risk_Model!{status_col}2:{status_col}{rm_last},"Resigned")'),
        ("Overall Attrition Rate", f'=COUNTIF(Risk_Model!{status_col}2:{status_col}{rm_last},"Resigned")/COUNTA(Risk_Model!A2:A{rm_last})'),
        ("Attrition Rate — Overtime Employees",
         f'=SUMPRODUCT((Risk_Model!{ot_col}2:{ot_col}{rm_last}="Yes")*(Risk_Model!{status_col}2:{status_col}{rm_last}="Resigned"))'
         f'/SUMPRODUCT((Risk_Model!{ot_col}2:{ot_col}{rm_last}="Yes")*1)'),
        ("Attrition Rate — Non-Overtime Employees",
         f'=SUMPRODUCT((Risk_Model!{ot_col}2:{ot_col}{rm_last}="No")*(Risk_Model!{status_col}2:{status_col}{rm_last}="Resigned"))'
         f'/SUMPRODUCT((Risk_Model!{ot_col}2:{ot_col}{rm_last}="No")*1)'),
        ("High-Risk Employees (Active)",
         f'=SUMPRODUCT((Risk_Model!{band_col}2:{band_col}{rm_last}="High")*(Risk_Model!{status_col}2:{status_col}{rm_last}="Active"))'),
        ("Resignation Rate — High Risk Band",
         f'=SUMPRODUCT((Risk_Model!{band_col}2:{band_col}{rm_last}="High")*(Risk_Model!{status_col}2:{status_col}{rm_last}="Resigned"))'
         f'/SUMPRODUCT((Risk_Model!{band_col}2:{band_col}{rm_last}="High")*1)'),
        ("Resignation Rate — Low Risk Band",
         f'=SUMPRODUCT((Risk_Model!{band_col}2:{band_col}{rm_last}="Low")*(Risk_Model!{status_col}2:{status_col}{rm_last}="Resigned"))'
         f'/SUMPRODUCT((Risk_Model!{band_col}2:{band_col}{rm_last}="Low")*1)'),
    ]
    ws4.append([])
    ws4.append(["Metric", "Value"])
    style_header_row(ws4, ws4.max_row, 2)
    for label, formula in kpi_rows:
        ws4.append([label, formula])
        r = ws4.max_row
        ws4.cell(row=r, column=1).font = BASE_FONT
        ws4.cell(row=r, column=2).font = BOLD
        if "Rate" in label:
            ws4.cell(row=r, column=2).number_format = "0.0%"

    # Attrition rate by department (chart source)
    chart_start = ws4.max_row + 3
    ws4.cell(row=chart_start - 1, column=1, value="Attrition Rate by Department").font = Font(name=FONT, bold=True, size=11)
    ws4.cell(row=chart_start, column=1, value="Department").font = HEADER_FONT
    ws4.cell(row=chart_start, column=2, value="Attrition Rate").font = HEADER_FONT
    ws4.cell(row=chart_start, column=1).fill = HEADER_FILL
    ws4.cell(row=chart_start, column=2).fill = HEADER_FILL
    depts = sorted(cleaned["Department"].unique())
    for i, d in enumerate(depts):
        r = chart_start + 1 + i
        ws4.cell(row=r, column=1, value=d).font = BASE_FONT
        formula = (
            f'=SUMPRODUCT((Risk_Model!{dept_col_rm}2:{dept_col_rm}{rm_last}="{d}")*'
            f'(Risk_Model!{status_col}2:{status_col}{rm_last}="Resigned"))'
            f'/SUMPRODUCT((Risk_Model!{dept_col_rm}2:{dept_col_rm}{rm_last}="{d}")*1)'
        )
        ws4.cell(row=r, column=2, value=formula).number_format = "0.0%"
        ws4.cell(row=r, column=2).font = BASE_FONT
    dept_table_last = chart_start + len(depts)

    chart = BarChart()
    chart.title = "Attrition Rate by Department"
    chart.y_axis.title = "Attrition Rate"
    chart.x_axis.title = "Department"
    data_ref = Reference(ws4, min_col=2, min_row=chart_start, max_row=dept_table_last)
    cats_ref = Reference(ws4, min_col=1, min_row=chart_start + 1, max_row=dept_table_last)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats_ref)
    chart.height, chart.width = 8, 16
    ws4.add_chart(chart, f"D{chart_start}")

    autosize(ws4, 2, max_w=46)

    # ---------------- Validation_Log ----------------
    ws5 = wb.create_sheet("Validation_Log")
    ws5["A1"] = "ETL Validation Report — from a real pipeline run (etl_validate.py)"
    ws5["A1"].font = Font(name=FONT, bold=True, size=13)
    ws5["A3"] = f"Raw rows in: {validation['rows_in_raw_export']}    Clean rows out: {validation['rows_after_cleaning']}    Runtime: {validation['runtime_seconds']}s"
    ws5["A3"].font = BASE_FONT
    ws5.append([])
    ws5.append(["Issue Type", "Detected & Fixed", "Ground-Truth Injected"])
    style_header_row(ws5, ws5.max_row, 3)
    for k in issues:
        ws5.append([k, issues[k], gt.get(k, 0)])
        r = ws5.max_row
        for c in range(1, 4):
            ws5.cell(row=r, column=c).font = BASE_FONT
            ws5.cell(row=r, column=c).border = BORDER
    ws5.append([])
    r = ws5.max_row + 1
    ws5.cell(row=r, column=1, value="Detection rate vs. known ground truth").font = BOLD
    ws5.cell(row=r, column=2, value=f"{validation['detection_rate_percent']}%").font = BOLD
    autosize(ws5, 3, max_w=40)

    out_path = "outputs/HR_Analytics_Workbook.xlsx"
    wb.save(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    build()
