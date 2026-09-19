"""
risk_scoring.py
Implements the weighted Risk Score as real, runnable code (same weighting logic as
dax_measures.md, so the DAX version and this Python version compute the same thing —
this is the executable proof that the measure is sound before it's typed into Power BI).

Validates the score by checking it actually separates people who resigned from people
who stayed, using data the model was NOT allowed to see when computing the score
(Status is excluded from the inputs).
"""
import numpy as np
import pandas as pd


def compute_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()

    # Normalize each driver to 0-1 so weights are comparable (min-max within dept
    # where relevant, so the score isn't dominated by cross-department salary gaps)
    d["OT_risk"] = (d["OverTime"] == "Yes").astype(float)

    d["Satisfaction_risk"] = 1 - (d["SatisfactionScore"] - 1) / 4  # low satisfaction = high risk
    d["Satisfaction_risk"] = d["Satisfaction_risk"].clip(0, 1)

    d["Promotion_risk"] = (d["MonthsSincePromotion"] / 60).clip(0, 1)

    dept_salary_rank = d.groupby("Department")["AnnualSalary"].rank(pct=True)
    d["Pay_risk"] = (1 - dept_salary_rank).clip(0, 1)  # low relative pay = high risk

    d["WLB_risk"] = (1 - (d["WorkLifeBalance"] - 1) / 4).clip(0, 1)

    d["Tenure_risk"] = (1 - (d["TenureYears"] / 8).clip(0, 1))  # newer = higher flight risk

    # Weights documented in dax_measures.md — sum to 1.0
    weights = {
        "OT_risk": 0.28,
        "Satisfaction_risk": 0.24,
        "Promotion_risk": 0.16,
        "Pay_risk": 0.14,
        "WLB_risk": 0.12,
        "Tenure_risk": 0.06,
    }
    assert abs(sum(weights.values()) - 1.0) < 1e-9, "weights must sum to 1.0"

    d["RiskScore"] = sum(d[col] * w for col, w in weights.items())
    d["RiskScore"] = (d["RiskScore"] * 100).round(1)  # 0-100 scale

    def band(score):
        if score >= 65:
            return "High"
        if score >= 45:
            return "Medium"
        return "Low"

    d["RiskBand"] = d["RiskScore"].apply(band)
    return d


def validate_against_attrition(scored: pd.DataFrame) -> dict:
    """The score must actually be higher, on average, for people who resigned —
    otherwise it's not measuring anything real. This is computed, not asserted."""
    resigned = scored[scored["Status"] == "Resigned"]["RiskScore"]
    active = scored[scored["Status"] == "Active"]["RiskScore"]
    corr = scored["RiskScore"].corr((scored["Status"] == "Resigned").astype(int))
    return {
        "avg_risk_score_resigned": round(resigned.mean(), 1),
        "avg_risk_score_active": round(active.mean(), 1),
        "point_biserial_correlation_with_attrition": round(float(corr), 3),
        "high_band_resignation_rate_pct": round(
            100 * scored[scored["RiskBand"] == "High"]["Status"].eq("Resigned").mean(), 1
        ),
        "low_band_resignation_rate_pct": round(
            100 * scored[scored["RiskBand"] == "Low"]["Status"].eq("Resigned").mean(), 1
        ),
    }


if __name__ == "__main__":
    df = pd.read_csv("outputs/cleaned_data.csv")
    scored = compute_risk_score(df)
    scored.to_csv("outputs/risk_scored_employees.csv", index=False)

    validation = validate_against_attrition(scored)
    print("Risk score validation against actual attrition (Status was NOT a model input):")
    for k, v in validation.items():
        print(f"  {k}: {v}")

    import json
    with open("outputs/risk_score_validation.json", "w") as f:
        json.dump(validation, f, indent=2)

    high_risk_active = scored[(scored["RiskBand"] == "High") & (scored["Status"] == "Active")]
    high_risk_active.to_csv("outputs/high_risk_active_employees.csv", index=False)
    print(f"\nHigh-risk ACTIVE employees flagged for retention action: {len(high_risk_active)}")
