"""
data_generator.py
Generates a reproducible SYNTHETIC HR dataset (NOT a real company's data).
Seeded for reproducibility. Deliberately encodes realistic relationships between
overtime, tenure, satisfaction, promotion stagnation, salary position and attrition
so downstream analytics (risk scoring, dashboards) have real patterns to find.
"""
import numpy as np
import pandas as pd

SEED = 42
N_EMPLOYEES = 1200

DEPARTMENTS = ["Sales", "Engineering", "Operations", "Finance", "HR", "Customer Support"]
ROLES = {
    "Sales": ["Sales Executive", "Account Manager", "Sales Manager"],
    "Engineering": ["Software Engineer", "Senior Engineer", "Engineering Manager"],
    "Operations": ["Ops Analyst", "Ops Manager", "Process Lead"],
    "Finance": ["Financial Analyst", "Accountant", "Finance Manager"],
    "HR": ["HR Generalist", "Recruiter", "HR Manager"],
    "Customer Support": ["Support Associate", "Support Lead", "Support Manager"],
}


def generate_clean_dataset(n=N_EMPLOYEES, seed=SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    dept = rng.choice(DEPARTMENTS, size=n, p=[0.22, 0.20, 0.18, 0.14, 0.10, 0.16])
    role = np.array([rng.choice(ROLES[d]) for d in dept])
    tenure_years = np.round(rng.gamma(shape=2.0, scale=1.8, size=n), 1).clip(0.1, 20)
    age = np.clip((rng.normal(34, 8, size=n) + tenure_years * 0.4).astype(int), 21, 62)

    base_salary = {
        "Sales": 650000, "Engineering": 950000, "Operations": 600000,
        "Finance": 750000, "HR": 550000, "Customer Support": 480000,
    }
    salary = np.array([
        base_salary[d] * (1 + 0.06 * min(t, 10)) * rng.uniform(0.85, 1.15)
        for d, t in zip(dept, tenure_years)
    ]).round(-3)

    overtime = rng.choice([1, 0], size=n, p=[0.32, 0.68])
    months_since_promotion = rng.integers(1, 61, size=n)
    satisfaction = np.clip(rng.normal(3.4, 0.9, size=n), 1, 5).round(1)
    work_life_balance = np.clip(
        rng.normal(3.3, 0.9, size=n) - overtime * 0.6, 1, 5
    ).round(1)
    performance_rating = np.clip(rng.normal(3.2, 0.7, size=n), 1, 5).round(1)

    salary_percentile = pd.Series(salary).groupby(pd.Series(dept)).rank(pct=True).values

    # Deliberate signal: attrition probability rises with overtime, low satisfaction,
    # promotion stagnation and low relative pay; falls with tenure and performance.
    logit = (
        -2.1
        + 1.15 * overtime
        + 0.55 * (satisfaction < 3.0)
        + 0.006 * months_since_promotion
        - 0.9 * (salary_percentile > 0.6)
        - 0.05 * np.minimum(tenure_years, 8)
        + 0.25 * (performance_rating < 2.8)
        + rng.normal(0, 0.35, size=n)
    )
    prob_attrition = 1 / (1 + np.exp(-logit))
    attrition = (rng.uniform(size=n) < prob_attrition).astype(int)
    status = np.where(attrition == 1, "Resigned", "Active")

    df = pd.DataFrame({
        "EmployeeID": [f"EMP{i:05d}" for i in range(1, n + 1)],
        "Department": dept,
        "Role": role,
        "Age": age,
        "TenureYears": tenure_years,
        "AnnualSalary": salary,
        "OverTime": np.where(overtime == 1, "Yes", "No"),
        "MonthsSincePromotion": months_since_promotion,
        "SatisfactionScore": satisfaction,
        "WorkLifeBalance": work_life_balance,
        "PerformanceRating": performance_rating,
        "Status": status,
    })
    return df


if __name__ == "__main__":
    df = generate_clean_dataset()
    df.to_csv("outputs/clean_master_data.csv", index=False)
    print(f"Generated {len(df)} synthetic employee records -> outputs/clean_master_data.csv")
    print(df["Status"].value_counts())
