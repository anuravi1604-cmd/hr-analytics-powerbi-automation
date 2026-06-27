# DAX Measures & Microsoft Copilot Integration

This reference sheet contains the precise DAX formulas and configuration steps to build calculations and AI features inside your **Enterprise HR Analytics System**.

---

## 1. Core HR Analytics Measures

Create these measures by right-clicking on the `Fact_Employees` table and selecting **New Measure**.

### Total Employees
Calculates the total headcount of all employees (both active and departed) in the record history.
```dax
Total Employees = COUNTROWS(Fact_Employees)
```

### Total Attrition
Calculates the count of employees who have left the organization.
```dax
Total Attrition = CALCULATE(
    [Total Employees],
    Fact_Employees[Attrition] = "Yes"
)
```

### Attrition Rate (%)
Calculates the attrition rate. Essential to use `DIVIDE` to handle division-by-zero errors safely.
```dax
Attrition Rate = DIVIDE([Total Attrition], [Total Employees], 0)
```
*Format this measure as a **Percentage ( % )** with 1 decimal place.*

### Active Headcount
Calculates the current active workforce.
```dax
Active Headcount = CALCULATE(
    [Total Employees],
    Fact_Employees[Attrition] = "No"
)
```

### Average Annual Salary
Calculates the average salary of current or historical employees.
```dax
Avg Annual Salary = AVERAGE(Fact_Employees[Annual_Salary])
```
*Format as **Currency ($)** with 0 decimal places.*

### Average Job Satisfaction
Calculates the average rating (1 to 5) for employee job satisfaction.
```dax
Avg Job Satisfaction = AVERAGE(Fact_Employees[Job_Satisfaction])
```
*Format as a **Decimal Number** with 2 decimal places.*

---

## 2. Advanced & Prescriptive DAX Measures

These metrics showcase high-level logic, indicating potential problem areas for HR management.

### Overtime Attrition Rate (%)
Calculates the attrition rate specifically for employees who work overtime, demonstrating the direct impact of overtime on retention.
```dax
Overtime Attrition Rate = 
CALCULATE(
    [Attrition Rate],
    Fact_Employees[Overtime] = "Yes"
)
```

### Attrition Risk Score (Weighted Index)
Iterates through all active employees and scores their risk of leaving (0 to 100) based on weighted risk indicators:
* **Job Satisfaction (30% weight)**: Lower satisfaction yields higher risk.
* **Work-Life Balance (20% weight)**: Lower balance yields higher risk.
* **Overtime Status (30% weight)**: Employees working overtime receive full risk weight.
* **Salary Hike percentage (20% weight)**: Low historical salary hikes (under 12%) increase risk.

```dax
Employee Risk Score = 
AVERAGEX(
    Fact_Employees,
    VAR SatScore = (6 - Fact_Employees[Job_Satisfaction]) * 20      -- Score: 1=100, 2=80, 3=60, 4=40, 5=20
    VAR WlbScore = (6 - Fact_Employees[Work_Life_Balance]) * 20     -- Score: 1=100, 2=80, 3=60, 4=40, 5=20
    VAR OvertimeScore = IF(Fact_Employees[Overtime] = "Yes", 100, 0)
    VAR SalaryHikeScore = IF(Fact_Employees[Percent_Salary_Hike] < 12, 100, 
                             IF(Fact_Employees[Percent_Salary_Hike] < 16, 50, 0))
    RETURN
    IF(
        Fact_Employees[Attrition] = "Yes",
        BLANK(), -- Exclude already departed employees from risk forecasting
        (SatScore * 0.30) + (WlbScore * 0.20) + (OvertimeScore * 0.30) + (SalaryHikeScore * 0.20)
    )
)
```
*Format as a **Decimal Number** with 1 decimal place.*

### Attrition Risk Segment (Calculated Column)
Creates a categorizer that segments active employees into risk brackets. Right-click the table and choose **New Column**.
```dax
Risk Segment = 
VAR Score = Fact_Employees[Employee Risk Score]
RETURN
IF(ISBLANK(Score), "Resigned",
    IF(Score >= 75, "High Risk",
        IF(Score >= 45, "Medium Risk", "Low Risk")
    )
)
```

---

## 3. Microsoft Copilot Integration

Integrating Microsoft Copilot showcases leading-edge AI adoption on your resume. Here is how to configure and describe these features.

### A. Copilot Smart Narrative Visual (AI Insights)
* **What it does**: Automatically analyzes your visuals and generates a plain-text summary of highlights, trends, and drivers of attrition.
* **Setup Steps**:
  1. In the **Visualizations** pane, select the **Narrative** icon (looks like a page with text).
  2. Choose **Copilot** as the narrative type.
  3. In the Copilot prompt box, type: *"Create a summary of employee attrition rates. Highlight the impact of Overtime, Job Satisfaction, and Department."*
  4. Power BI will generate a dynamic, text-based visual that refreshes automatically as users filter the dashboard.

### B. Natural Language Q&A Visual Configuration
* **What it does**: Allows recruiters/managers to type questions (e.g. *"which department has highest risk segment?"*) and see visual charts generated in real time.
* **Setup Steps**:
  1. Add a **Q&A Visual** to your report canvas.
  2. Go to **Q&A Setup** (gear icon in the visual corner or under the modeling tab).
  3. Under **Teach Q&A**, define custom synonyms so Copilot maps conversational language:
     * Term `Attrition` -> Add Synonyms: `Turnover`, `Exit`, `Resigned`, `Voluntary Churn`
     * Term `Annual_Salary` -> Add Synonyms: `Compensation`, `Paycheck`, `Wages`, `Earnings`
     * Term `Percent_Salary_Hike` -> Add Synonyms: `Raise`, `Increment`, `Salary Increase`
  4. Under **Suggest Questions**, write predefined questions for users to click:
     * *"What is the attrition rate by job role where overtime is Yes?"*
     * *"Show me the distribution of risk segments by department."*

### C. Copilot in DAX (DAX Query View)
* **Resume Highlight**: *"Leveraged DAX Copilot within Microsoft Power BI to draft and troubleshoot complex measures, reducing formula development cycle times by 40%."*
* **How to demo/use**:
  1. Open the **DAX Query View** (icon on the left side of Power BI Desktop).
  2. Click **DAX Copilot** or use `Shift + Space` to ask Copilot questions.
  3. Prompt Copilot: *"Create a measure named LowSatisfactionTechAttrition that calculates the attrition rate of employees in the Technology department with a Job Satisfaction rating of 2 or less."*
  4. Power BI will draft the DAX syntax, which you can insert directly into your model.
