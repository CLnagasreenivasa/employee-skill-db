
import streamlit as st
import sqlite3
import os
import pandas as pd

# Database setup
conn = sqlite3.connect("employee_data.db")
c = conn.cursor()

UPLOAD_DIR = "resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

def add_employee(data):
    c.execute('''INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()

def update_employee(emp_id, field, new_value):
    c.execute(f"UPDATE employees SET {field} = ? WHERE employee_id = ?", (new_value, emp_id))
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
    rows = c.fetchall()
    return rows

st.title("🧠 Employee Skill Database")

tab1, tab2, tab3 = st.tabs(["➕ Add Employee", "✏️ Update Employee", "🔍 Search Employees"])

with tab1:
    st.header("Add New Employee")
    emp_id = st.text_input("Employee ID")
    name = st.text_input("Employee Name")
    email = st.text_input("E-Mail ID")
    role = st.text_input("Role")
    primary_skills = st.text_input("Primary Skills")
    secondary_skills = st.text_input("Secondary Skills")
    certifications = st.text_input("Certifications")
    total_exp = st.number_input("Total Years of Experience", step=0.1)
    relevant_exp = st.number_input("Relevant Years of Experience", step=0.1)
    location = st.text_input("Current Location")
    aspiration = st.text_area("Career Aspiration")
    plan = st.text_area("Action Plan")
    target = st.date_input("Target Date")
    resume = st.file_uploader("Upload Resume", type=["pdf", "docx"])

    if st.button("Submit", key="submit_add"):
        if emp_id and name:
            resume_path = ""
            if resume:
                resume_path = os.path.join(UPLOAD_DIR, f"{emp_id}_{resume.name}")
                with open(resume_path, "wb") as f:
                    f.write(resume.read())

            data = (emp_id, name, email, role, primary_skills, secondary_skills, certifications,
                    total_exp, relevant_exp, location, aspiration, plan, str(target), resume_path)
            try:
                add_employee(data)
                st.success(f"Employee {name} added successfully!")
            except sqlite3.IntegrityError:
                st.error("Employee ID already exists!")
        else:
            st.warning("Employee ID and Name are mandatory!")

with tab2:
    st.header("Update Employee Record")
    emp_id = st.text_input("Enter Employee ID", key="update_id")
    field = st.selectbox("Field to Update", ["name", "email", "role", "primary_skills",
                                             "secondary_skills", "certifications", "total_experience",
                                             "relevant_experience", "current_location",
                                             "career_aspiration", "action_plan", "target_date"])
    new_value = st.text_input(f"New Value for {field}")

    if st.button("Update", key="submit_update"):
        if emp_id and new_value:
            try:
                update_employee(emp_id, field, new_value)
                st.success("Employee data updated.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("All fields required!")

with tab3:
    st.header("Search Employees (by ID, Name, Skills, etc.)")
    keyword = st.text_input("Enter any search keyword")
    if st.button("Search", key="submit_search"):
        results = flexible_search(keyword)
        if results:
            columns = ["Employee ID", "Name", "Email", "Role", "Primary Skills", "Secondary Skills", "Certifications",
                       "Total Exp", "Relevant Exp", "Location", "Aspiration", "Action Plan", "Target Date", "Resume Path"]
            df = pd.DataFrame(results, columns=columns)
            st.dataframe(df)
        else:
            st.warning("No records matched your search.")
