# Dashboard Design System & Layout Specifications

This design specification details the visual standards, grid layouts, and page structures required to build a premium, glassmorphism-inspired dark-themed dashboard. 

---

## 1. Visual Design Theme (Slate Dark Mode)

Applying a coordinated color palette transforms a default-looking Power BI report into an executive-level application.

| Design Asset | Hex Code | Purpose |
| :--- | :--- | :--- |
| **Main Canvas Background** | `#0F172A` | Deep dark slate navy (Canvas setting, 0% transparency) |
| **Visual/Card Background** | `#1E293B` | Solid slate grey (Visual container background, 10% transparency, rounded corners: 8px) |
| **Primary Metric Color** | `#F8FAFC` | Off-white (Titles, main KPI card labels) |
| **Active/Normal Accent** | `#0D9488` | Deep Teal (Indicates active headcount, high satisfaction) |
| **Attrition/Warning Accent** | `#F43F5E` | Coral Rose (Highlights attrition, high risk segments) |
| **Information Accent** | `#38BDF8` | Cyan Blue (For labels, trend lines, neutral metrics) |

* **Typography**: Font family `Segoe UI` (System default) or `Segoe UI Semibold` for headers. Keep size hierarchical (KPI values: 32pt, Section headers: 14pt, Labels: 9pt).

---

## 2. Page 1: Executive Attrition Overview

* **Objective**: A high-level view of current organization health, tracking attrition volume, rates, and direct operational risk factors.

```
+---------------------------------------------------------------------------------+
|  [Logo]  HR Executive Attrition Insights Dashboard                   (Date/Filters) |
+---------------------------------------------------------------------------------+
|  +--------------+  +--------------+  +--------------+  +---------------------+  |
|  | Active Staff |  | Attrition %  |  | Avg Salary   |  | Overtime Attrition  |  |
|  |    1,008     |  |    16.0%     |  |   $98,400    |  |       35.4%         |  |
|  +--------------+  +--------------+  +--------------+  +---------------------+  |
+---------------------------------------------------------------------------------+
|  +-------------------------------------+  +----------------------------------+  |
|  | Attrition Rate by Dept (Bar Chart)  |  | Overtime vs Retention (Stacked)  |  |
|  | - Sales: 21.3%                      |  |                                  |  |
|  | - Tech: 18.1%                       |  | [Teal: Active | Coral: Left]      |  |
|  | - Finance: 10.4%                    |  | - Overtime Yes: 35.4% Attrition  |  |
|  +-------------------------------------+  +----------------------------------+  |
+---------------------------------------------------------------------------------+
|  +---------------------------------------------------------------------------+  |
|  | Attrition Rate by Job Role (Clustered Column)                              |  |
|  | Tech Leads | Sales Reps | QA Analysts | Software Eng                      |  |
|  +---------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------+
```

### Visual Configuration Details
1. **KPI Cards (New Card Visual)**:
   * Fields: `[Active Headcount]`, `[Attrition Rate]`, `[Avg Annual Salary]`, `[Overtime Attrition Rate]`.
   * Enable Card borders (color `#334155`), callout value color `#F8FAFC`, label color `#94A3B8`.
2. **Attrition Rate by Department (Clustered Bar Chart)**:
   * Y-Axis: `Department`
   * X-Axis: `[Attrition Rate]`
   * Color formatting: Use Conditional Formatting on Bars based on `[Attrition Rate]` (Low = `#0D9488`, High = `#F43F5E`).
3. **Overtime Impact (Stacked Column Chart)**:
   * X-Axis: `Overtime` ("Yes" vs "No")
   * Y-Axis: `[Total Employees]`
   * Legend: `Attrition`
   * Colors: Yes = `#F43F5E` (Attrition), No = `#0D9488` (Active).
4. **Role Breakdown (Clustered Column)**:
   * X-Axis: `Job_Role` (sorted by attrition rate descending)
   * Y-Axis: `[Attrition Rate]`

---

## 3. Page 2: Demographics & Diversity

* **Objective**: Evaluate internal demographics and explore whether specific age groups, marital statuses, or education background levels experience disproportionate churn.

### Layout & Visual Grid
1. **Headcount Distribution (Donut Chart)**:
   * Legend: `Gender`
   * Values: `[Active Headcount]`
   * Colors: Female = `#38BDF8`, Male = `#0D9488`, Non-binary = `#A855F7`.
2. **Attrition by Age Groups (Clustered Column Chart)**:
   * X-Axis: `Age_Group` (ordered: < 25, 25-34, 35-44, 45-54, 55+)
   * Y-Axis: `[Attrition Rate]`
   * Highlight: Visualizes that the "< 25" group typically experiences higher entry-level attrition.
3. **Attrition by Marital Status (Clustered Bar Chart)**:
   * Y-Axis: `Marital_Status`
   * X-Axis: `[Attrition Rate]`
4. **Satisfaction Matrix (Matrix Visual)**:
   * Rows: `Department` -> `Job_Role`
   * Columns: Satisfaction measures: `[Avg Job Satisfaction]`, `[Avg Work-Life Balance]`, `[Avg Env Satisfaction]`.
   * Conditional Formatting: Apply Background Color scales (diverging red-to-green or slate-to-teal) to quickly highlight under-satisfied segments.

---

## 4. Page 3: AI-Assisted Insights & Automation

* **Objective**: Leverage Power BI’s machine learning and AI capabilities alongside Power Automate to enable proactive data queries and workflow triggers.

### Layout & Visual Grid
1. **Decomposition Tree (AI Visual)**:
   * Analyze: `[Attrition Rate]`
   * Explain by: `Department`, `Overtime`, `Job_Satisfaction`, `Risk Segment`.
   * *Recruiter Demo*: Pathfinding tool that shows exactly what paths lead to the highest attrition rate (e.g. Sales -> Overtime Yes -> Low Job Satisfaction has an attrition rate of 78%).
2. **Key Influencers (AI Visual)**:
   * Analyze: `Attrition` (Set to "Yes")
   * Explain by: `Overtime`, `Monthly_Income`, `Percent_Salary_Hike`, `Job_Satisfaction`, `Years_Since_Last_Promotion`.
   * *Recruiter Demo*: This visual isolates variables to state: *"When Job Satisfaction is 1, the likelihood of Attrition increases by 3.4x."*
3. **Smart Narrative Visual (AI Summary Text)**:
   * Automatically generated narratives of the key findings.
4. **System Action Panel**:
   * Add a **Power Automate Button visual**.
   * Label: *"Email Executive Summary Report"*
   * Connect to **Flow 2** to automate reports distribution.
   * Add a **Q&A Visual** in the bottom section labeled: *"Ask Microsoft Copilot about your organization's attrition..."*
