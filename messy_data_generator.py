"""
messy_data_generator.py
Takes the clean synthetic dataset and deliberately corrupts a documented set of rows
with realistic HRIS-export data-quality problems: duplicate rows, blank/null fields,
inconsistent categorical spellings, malformed dates, stray whitespace, wrong dtypes,
and out-of-range values. Every corruption is logged to outputs/injected_errors.json
so the ETL script's detection rate can be measured against a KNOWN ground truth,
instead of an invented number.
"""
import json
import numpy as np
import pandas as pd

SEED = 7


def make_messy(df: pd.DataFrame, seed=SEED) -> tuple[pd.DataFrame, list[dict]]:
    rng = np.random.default_rng(seed)
    messy = df.copy()
    injected = []

    def log(rows, issue, field):
        for r in np.atleast_1d(rows):
            injected.append({"row_index": int(r), "issue": issue, "field": field})

    # 1) Duplicate ~2% of rows (simulates re-export / double sync)
    dup_idx = rng.choice(messy.index, size=int(0.02 * len(messy)), replace=False)
    dup_rows = messy.loc[dup_idx]
    log(dup_idx, "duplicate_row", "ALL")
    messy = pd.concat([messy, dup_rows], ignore_index=True)

    # 2) Blank / missing SatisfactionScore on ~3%
    blank_idx = rng.choice(messy.index, size=int(0.03 * len(messy)), replace=False)
    messy.loc[blank_idx, "SatisfactionScore"] = np.nan
    log(blank_idx, "missing_value", "SatisfactionScore")

    # 3) Inconsistent OverTime spellings/casing on ~4%
    ot_idx = rng.choice(messy.index, size=int(0.04 * len(messy)), replace=False)
    variants = ["yes", "YES", "y", "No ", " no", "N/A"]
    messy.loc[ot_idx, "OverTime"] = [variants[i % len(variants)] for i in range(len(ot_idx))]
    log(ot_idx, "inconsistent_category", "OverTime")

    # 4) Department typos / trailing whitespace on ~3%
    dept_idx = rng.choice(messy.index, size=int(0.03 * len(messy)), replace=False)
    typo_map = {
        "Sales": ["sales", "Sales ", "SALES"],
        "Engineering": ["Enginering", "engineering", "Engineering "],
        "Operations": ["Ops", "operations", "Operations "],
        "Finance": ["finance", "Finanace", "Finance "],
        "HR": ["hr", "H.R.", "HR "],
        "Customer Support": ["Cust Support", "customer support", "Customer Support "],
    }
    for i in dept_idx:
        orig = messy.loc[i, "Department"]
        messy.loc[i, "Department"] = rng.choice(typo_map.get(orig, [orig]))
    log(dept_idx, "inconsistent_category", "Department")

    # 5) Negative / impossible AnnualSalary on ~1%
    sal_idx = rng.choice(messy.index, size=int(0.01 * len(messy)), replace=False)
    messy.loc[sal_idx, "AnnualSalary"] = -messy.loc[sal_idx, "AnnualSalary"].abs()
    log(sal_idx, "out_of_range_value", "AnnualSalary")

    # 6) TenureYears stored as text with stray units on ~2%
    ten_idx = rng.choice(messy.index, size=int(0.02 * len(messy)), replace=False)
    messy["TenureYears"] = messy["TenureYears"].astype(object)
    messy.loc[ten_idx, "TenureYears"] = [f"{v} yrs" for v in messy.loc[ten_idx, "TenureYears"]]
    log(ten_idx, "wrong_dtype", "TenureYears")

    # 7) Completely blank EmployeeID on ~0.5%
    id_idx = rng.choice(messy.index, size=max(1, int(0.005 * len(messy))), replace=False)
    messy.loc[id_idx, "EmployeeID"] = ""
    log(id_idx, "missing_value", "EmployeeID")

    # 8) Age stored as float string with decimal noise on ~1.5%
    age_idx = rng.choice(messy.index, size=int(0.015 * len(messy)), replace=False)
    messy["Age"] = messy["Age"].astype(object)
    messy.loc[age_idx, "Age"] = [f"{v}.0 " for v in messy.loc[age_idx, "Age"]]
    log(age_idx, "wrong_dtype", "Age")

    messy = messy.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return messy, injected


if __name__ == "__main__":
    clean = pd.read_csv("outputs/clean_master_data.csv")
    messy, injected = make_messy(clean)
    messy.to_csv("outputs/raw_hris_export.csv", index=False)
    with open("outputs/injected_errors_ground_truth.json", "w") as f:
        json.dump(injected, f, indent=2)
    print(f"Raw messy export: {len(messy)} rows (clean was {len(clean)})")
    print(f"Ground-truth injected issues logged: {len(injected)} -> outputs/injected_errors_ground_truth.json")
