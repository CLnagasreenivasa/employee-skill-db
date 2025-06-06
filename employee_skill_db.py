
import streamlit as st
import sqlite3
import os
import pandas as pd

# Database setup
conn = sqlite3.connect("employee_data.db", check_same_thread=False)
c = conn.cursor()

UPLOAD_DIR = "resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Fetch all unique values for filters
def get_unique_values(column):
    c.execute(f"SELECT DISTINCT {column} FROM employees")
    return sorted([row[0] for row in c.fetchall() if row[0]])

c.execute("""
CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT,
    role TEXT,
    primary_skills TEXT,
    secondary_skills TEXT,
    certifications TEXT,
    total_experience REAL,
    relevant_experience REAL,
    current_location TEXT,
    career_aspiration TEXT,
    action_plan TEXT,
    target_date TEXT,
    resume_path TEXT
)
""")
conn.commit()

def flexible_search(keyword):
    keyword = f"%{keyword.lower()}%"
    query = """
    SELECT * FROM employees WHERE
    LOWER(employee_id) LIKE ? OR
    LOWER(name) LIKE ? OR
    LOWER(email) LIKE ? OR
    LOWER(role) LIKE ? OR
    LOWER(primary_skills) LIKE ? OR
    LOWER(secondary_skills) LIKE ? OR
    LOWER(certifications) LIKE ? OR
    LOWER(current_location) LIKE ?
    """
    c.execute(query, (keyword,)*8)
    return c.fetchall()

def search_with_filters(skill, location):
    query = "SELECT * FROM employees WHERE 1=1"
    conditions = []
    params = []

    if skill:
        conditions.append("(primary_skills LIKE ? OR secondary_skills LIKE ?)")
        params.extend((f"%{skill}%", f"%{skill}%"))
    if location:
        conditions.append("current_location LIKE ?")
        params.append(f"%{location}%")

    if conditions:
        query += " AND " + " AND ".join(conditions)

    c.execute(query, tuple(params))
    return c.fetchall()

st.title("🧠 Employee Skill Database")

tab1, tab2, tab3 = st.tabs(["➕ Add Employee", "🔍 Search + Export", "⚙️ Filters"])

# Search tab with export
with tab2:
    st.header("Search Employees")
    keyword = st.text_input("Enter any search keyword", key="search_tab")
    if st.button("Search", key="btn_search_tab"):
        results = flexible_search(keyword)
        if results:
            columns = ["Employee ID", "Name", "Email", "Role", "Primary Skills", "Secondary Skills", "Certifications",
                       "Total Exp", "Relevant Exp", "Location", "Aspiration", "Action Plan", "Target Date", "Resume Path"]
            df = pd.DataFrame(results, columns=columns)
            st.dataframe(df)

            st.download_button("📥 Export as CSV", df.to_csv(index=False), "employee_data.csv", "text/csv")
            excel_bytes = df.to_excel(index=False, engine='openpyxl')
            st.download_button("📥 Export as Excel", excel_bytes, "employee_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning("No records matched your search.")

# Filter tab
with tab3:
    st.header("🎯 Filter by Skill or Location")
    skill_options = get_unique_values("primary_skills")
    location_options = get_unique_values("current_location")

    selected_skill = st.selectbox("Select Primary Skill", [""] + skill_options)
    selected_location = st.selectbox("Select Location", [""] + location_options)

    if st.button("Apply Filters", key="btn_filter"):
        filtered = search_with_filters(selected_skill, selected_location)
        if filtered:
            columns = ["Employee ID", "Name", "Email", "Role", "Primary Skills", "Secondary Skills", "Certifications",
                       "Total Exp", "Relevant Exp", "Location", "Aspiration", "Action Plan", "Target Date", "Resume Path"]
            df = pd.DataFrame(filtered, columns=columns)
            st.dataframe(df)

            st.download_button("📥 Export Filtered Data (CSV)", df.to_csv(index=False), "filtered_employee_data.csv", "text/csv")
        else:
            st.warning("No data found for selected filters.")
