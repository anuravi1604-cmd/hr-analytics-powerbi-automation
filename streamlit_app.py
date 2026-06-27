import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Set page configurations
st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling (glassmorphism/slate dark theme mock)
st.markdown("""
    <style>
        .reportview-container {
            background: #0F172A;
        }
        div[data-testid="stMetricValue"] {
            font-size: 28px;
            color: #F8FAFC;
        }
        .main-header {
            font-size: 32px;
            font-weight: bold;
            color: #F8FAFC;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Load dataset
@st.cache_data
def load_data():
    # Load from local folder
    csv_path = os.path.join(os.path.dirname(__file__), "hr_employee_data.csv")
    df = pd.read_csv(csv_path)
    # Create attrition numeric flag
    df['Attrition_Flag'] = df['Attrition'].apply(lambda x: 1 if x == 'Yes' else 0)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filter Analytics")

# Department Filter
departments = ["All"] + list(df['Department'].unique())
selected_dept = st.sidebar.selectbox("Select Department", departments)

# Overtime Filter
overtime_options = ["All", "Yes", "No"]
selected_ot = st.sidebar.selectbox("Filter Overtime Status", overtime_options)

# Filter dataframe based on selections
filtered_df = df.copy()
if selected_dept != "All":
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
if selected_ot != "All":
    filtered_df = filtered_df[filtered_df['Overtime'] == selected_ot]

# --- MAIN DASHBOARD INTERFACE ---
st.markdown('<div class="main-header">📊 HR Attrition & People Analytics Dashboard</div>', unsafe_allow_html=True)
st.write("This interactive Python dashboard monitors voluntary departures and attrition drivers in real-time.")

# --- KPI METRICS ---
total_staff = len(filtered_df)
resigned = len(filtered_df[filtered_df['Attrition'] == 'Yes'])
attrition_rate = (resigned / total_staff) * 100 if total_staff > 0 else 0
avg_salary = filtered_df['Annual_Salary'].mean() if total_staff > 0 else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="Total Headcount", value=f"{total_staff:,}")
with kpi2:
    st.metric(label="Resignations", value=f"{resigned:,}")
with kpi3:
    st.metric(label="Attrition Rate", value=f"{attrition_rate:.1f}%")
with kpi4:
    st.metric(label="Avg Annual Salary", value=f"${avg_salary:,.0f}")

st.markdown("---")

# --- CHARTS AND VISUALS ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("🏢 Attrition Rate by Department")
    # Group by Department and calculate attrition rate
    dept_stats = df.groupby('Department').agg(
        Total=('Employee_ID', 'count'),
        Resigned=('Attrition_Flag', 'sum')
    ).reset_index()
    dept_stats['Attrition Rate (%)'] = round((dept_stats['Resigned'] / dept_stats['Total']) * 100, 1)
    
    # Render horizontal bar chart
    fig_dept = px.bar(
        dept_stats.sort_values(by='Attrition Rate (%)', ascending=True),
        x='Attrition Rate (%)',
        y='Department',
        orientation='h',
        color='Attrition Rate (%)',
        color_continuous_scale=px.colors.sequential.Tealgrn,
        text='Attrition Rate (%)'
    )
    fig_dept.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#F8FAFC',
        height=350,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_dept, use_container_width=True)

with chart_col2:
    st.subheader("⏰ Overtime Impact on Turnover")
    # Group by Overtime status and Attrition
    ot_stats = filtered_df.groupby(['Overtime', 'Attrition']).size().reset_index(name='Employee Count')
    
    # Render stacked column chart
    fig_ot = px.bar(
        ot_stats,
        x='Overtime',
        y='Employee Count',
        color='Attrition',
        color_discrete_map={'Yes': '#F43F5E', 'No': '#0D9488'},
        barmode='stack'
    )
    fig_ot.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#F8FAFC',
        height=350,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_ot, use_container_width=True)

# --- DETAILED DATA TABLE ---
st.subheader("📋 Filtered Employee Database Preview")
st.dataframe(
    filtered_df[[
        "Employee_ID", "Age", "Gender", "Department", "Job_Role", 
        "Annual_Salary", "Overtime", "Job_Satisfaction", "Work_Life_Balance", "Attrition"
    ]].head(100),
    use_container_width=True
)
