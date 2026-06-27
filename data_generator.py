import csv
import random
import os

def generate_hr_data(output_filepath, num_records=1200):
    # Setup roles and salary ranges (annual base salary)
    departments = {
        "Technology": {
            "Software Engineer": (70000, 110000, 1),
            "Senior Engineer": (115000, 160000, 3),
            "Tech Lead": (150000, 190000, 4),
            "Department Director": (180000, 240000, 5),
            "QA Analyst": (55000, 85000, 1)
        },
        "Sales": {
            "Sales Representative": (45000, 70000, 1),
            "Sales Executive": (75000, 110000, 2),
            "Account Manager": (90000, 130000, 3),
            "Sales Director": (160000, 220000, 5)
        },
        "Human Resources": {
            "HR Associate": (48000, 65000, 1),
            "HR Specialist": (68000, 95000, 2),
            "HR Manager": (95000, 135000, 3),
            "HR Director": (150000, 200000, 5)
        },
        "Finance": {
            "Financial Analyst": (65000, 95000, 1),
            "Senior Analyst": (95000, 130000, 3),
            "Finance Manager": (120000, 165000, 4),
            "Finance Director": (175000, 230000, 5)
        },
        "Marketing": {
            "Marketing Coordinator": (45000, 65000, 1),
            "Marketing Specialist": (65000, 90000, 2),
            "Brand Manager": (90000, 130000, 3),
            "Marketing Director": (150000, 210000, 5)
        }
    }

    genders = ["Female", "Male", "Non-binary"]
    marital_statuses = ["Single", "Married", "Divorced"]
    education_fields = ["Computer Science", "Life Sciences", "Marketing", "Finance", "Human Resources", "Other"]
    performance_ratings = [1, 2, 3, 4]  # 1: Needs Improvement, 2: Meets Expectations, 3: Exceeds, 4: Outstanding

    # Target fields
    fields = [
        "Employee_ID", "Age", "Gender", "Marital_Status", "Education_Field",
        "Department", "Job_Role", "Job_Level", "Annual_Salary", "Monthly_Income",
        "Years_At_Company", "Years_Since_Last_Promotion", "Training_Hours_Last_Year",
        "Overtime", "Job_Satisfaction", "Environment_Satisfaction", "Work_Life_Balance",
        "Performance_Rating", "Percent_Salary_Hike", "Attrition"
    ]

    records = []

    # Let's seed for reproducibility
    random.seed(42)

    for i in range(1, num_records + 1):
        emp_id = f"EMP{i:04d}"
        
        # Demographics
        age = random.randint(22, 58)
        gender = random.choice(genders)
        marital = random.choice(marital_statuses)
        edu = random.choice(education_fields)
        
        # Job Details
        dept = random.choice(list(departments.keys()))
        role = random.choice(list(departments[dept].keys()))
        min_sal, max_sal, base_level = departments[dept][role]
        
        # Add slight variation to job level based on role baseline
        job_level = base_level
        if job_level < 5 and random.random() > 0.7:
            job_level += 1
            
        salary = random.randint(min_sal, max_sal)
        monthly_income = round(salary / 12, 2)
        
        # Tenure
        # Bound years at company by age
        max_tenure = min(age - 21, 20)
        years_at_company = random.randint(0, max_tenure) if max_tenure > 0 else 0
        
        # Years since last promotion should be <= years at company
        years_since_promotion = random.randint(0, min(years_at_company, 8)) if years_at_company > 0 else 0
        
        # Training hours
        training_hours = random.randint(10, 60)
        
        # Overtime (highly correlated with sales and tech, and lower levels)
        ot_prob = 0.25
        if dept in ["Sales", "Technology"]:
            ot_prob += 0.15
        if job_level <= 2:
            ot_prob += 0.10
        overtime = "Yes" if random.random() < ot_prob else "No"
        
        # Satisfaction ratings (1 to 5)
        # Default distribution skewed towards satisfied (3 or 4)
        job_sat = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.15, 0.35, 0.3, 0.1])[0]
        env_sat = random.choices([1, 2, 3, 4, 5], weights=[0.08, 0.12, 0.35, 0.35, 0.1])[0]
        wlb = random.choices([1, 2, 3, 4, 5], weights=[0.07, 0.15, 0.4, 0.28, 0.1])[0]
        
        # Adjust satisfaction based on overtime
        if overtime == "Yes" and random.random() > 0.4:
            wlb = max(1, wlb - 1)
            job_sat = max(1, job_sat - 1)
            
        # Performance
        perf = random.choices(performance_ratings, weights=[0.05, 0.55, 0.3, 0.1])[0]
        
        # Salary hike - tied to performance
        if perf == 4:
            pct_hike = random.randint(18, 25)
        elif perf == 3:
            pct_hike = random.randint(14, 18)
        elif perf == 2:
            pct_hike = random.randint(10, 14)
        else:
            pct_hike = random.randint(5, 9)

        # ----------------------------------------------------
        # ATTRITION PROBABILITY MODEL (The Core Business Logic)
        # ----------------------------------------------------
        attrition_prob = 0.05  # Base probability of resigning
        
        # Attrition triggers:
        # 1. Low Job Satisfaction
        if job_sat == 1:
            attrition_prob += 0.30
        elif job_sat == 2:
            attrition_prob += 0.15
            
        # 2. Overtime without high satisfaction
        if overtime == "Yes":
            attrition_prob += 0.20
            
        # 3. Work Life Balance is poor
        if wlb <= 2:
            attrition_prob += 0.15
            
        # 4. Low Tenure (first 2 years are high turnover)
        if years_at_company <= 2:
            attrition_prob += 0.10
            
        # 5. Stagnation: Top performers who haven't been promoted in a while
        if perf >= 3 and years_since_promotion >= 4:
            attrition_prob += 0.25
            
        # 6. Underpaid compared to median of role
        median_for_role = (min_sal + max_sal) / 2
        if salary < median_for_role:
            attrition_prob += 0.12

        # Bound probability between 2% and 95%
        attrition_prob = max(0.02, min(0.95, attrition_prob))
        
        # Decide Attrition status
        attrition = "Yes" if random.random() < attrition_prob else "No"
        
        # Adjust records to show realistic outcomes:
        # If someone has resigned, their metrics might have reflected their dissatisfaction
        if attrition == "Yes":
            # Force low satisfaction for 70% of resigned to show clear patterns
            if random.random() < 0.7:
                job_sat = min(job_sat, 2)
                wlb = min(wlb, 2)

        records.append([
            emp_id, age, gender, marital, edu,
            dept, role, job_level, salary, monthly_income,
            years_at_company, years_since_promotion, training_hours,
            overtime, job_sat, env_sat, wlb,
            perf, pct_hike, attrition
        ])

    # Ensure target output folder exists
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    
    with open(output_filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        writer.writerows(records)

    print(f"Successfully generated {num_records} rows of HR Data at {output_filepath}")

if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), "hr_employee_data.csv")
    generate_hr_data(output_path)
