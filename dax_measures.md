# DAX Measures — Power BI implementation

These mirror `risk_scoring.py` exactly (same weights, same logic), so the Power BI
version and the Python version, which was validated against actual attrition,
compute the same risk score.

```dax
OT Risk =
IF ( SELECTEDVALUE ( Employees[OverTime] ) = "Yes", 1, 0 )

Satisfaction Risk =
MIN ( MAX ( 1 - ( SELECTEDVALUE ( Employees[SatisfactionScore] ) - 1 ) / 4, 0 ), 1 )

Promotion Risk =
MIN ( SELECTEDVALUE ( Employees[MonthsSincePromotion] ) / 60, 1 )

Dept Salary Percentile =
VAR ThisSalary = SELECTEDVALUE ( Employees[AnnualSalary] )
VAR ThisDept = SELECTEDVALUE ( Employees[Department] )
RETURN
    DIVIDE (
        CALCULATE (
            COUNTROWS ( Employees ),
            Employees[Department] = ThisDept,
            Employees[AnnualSalary] <= ThisSalary
        ),
        CALCULATE ( COUNTROWS ( Employees ), Employees[Department] = ThisDept )
    )

Pay Risk =
MIN ( MAX ( 1 - [Dept Salary Percentile], 0 ), 1 )

WLB Risk =
MIN ( MAX ( 1 - ( SELECTEDVALUE ( Employees[WorkLifeBalance] ) - 1 ) / 4, 0 ), 1 )

Tenure Risk =
1 - MIN ( SELECTEDVALUE ( Employees[TenureYears] ) / 8, 1 )

Risk Score =
ROUND (
    100 * (
        [OT Risk]           * SELECTEDVALUE ( Assumptions[OT_Weight], 0.28 ) +
        [Satisfaction Risk] * SELECTEDVALUE ( Assumptions[Sat_Weight], 0.24 ) +
        [Promotion Risk]    * SELECTEDVALUE ( Assumptions[Promo_Weight], 0.16 ) +
        [Pay Risk]          * SELECTEDVALUE ( Assumptions[Pay_Weight], 0.14 ) +
        [WLB Risk]          * SELECTEDVALUE ( Assumptions[WLB_Weight], 0.12 ) +
        [Tenure Risk]       * SELECTEDVALUE ( Assumptions[Tenure_Weight], 0.06 )
    ), 1
)

Risk Band =
SWITCH (
    TRUE (),
    [Risk Score] >= 65, "High",
    [Risk Score] >= 45, "Medium",
    "Low"
)
```

Cross-checked against `outputs/risk_score_validation.json` from the Python
implementation: High-band employees should resign at a meaningfully higher rate than
Low-band employees. In the last validated run: **30.8% vs 9.6%**.
