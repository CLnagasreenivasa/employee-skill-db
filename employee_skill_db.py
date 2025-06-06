
import streamlit as st
import sqlite3
import os
import pandas as pd

# Database setup
conn = sqlite3.connect("employee_data.db", check_same_thread=False)
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

def update_employee_record(emp_id, updated_data):
    query = """
    UPDATE employees SET
        name=?, email=?, role=?, primary_skills=?, secondary_skills=?,
        certifications=?, total_experience=?, relevant_experience=?,
        current_location=?, career_aspiration=?, action_plan=?, target_date=?, resume_path=?
    WHERE employee_id=?
    """
    c.execute(query, (*updated_data, emp_id))
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
    st.header("Search and Update Employee Record")

    if "matched_rows" not in st.session_state:
        st.session_state.matched_rows = []
    if "selected_emp_id" not in st.session_state:
        st.session_state.selected_emp_id = ""

    keyword = st.text_input("Search by any field (ID, Name, Skills, etc.)", key="update_search")

    if st.button("Search", key="update_search_btn"):
        matched = flexible_search(keyword)
        if matched:
            st.session_state.matched_rows = matched
            st.session_state.selected_emp_id = ""
        else:
            st.warning("No records found.")
            st.session_state.matched_rows = []
            st.session_state.selected_emp_id = ""

    if st.session_state.matched_rows:
        st.write("### Select an employee to update:")
        selected = st.radio(
            "Matching Employees",
            [f"{row[0]} - {row[1]} ({row[2]})" for row in st.session_state.matched_rows],
            key="radio_select"
        )
        st.session_state.selected_emp_id = selected.split(" - ")[0]

    if st.session_state.selected_emp_id:
        row = next(row for row in st.session_state.matched_rows if row[0] == st.session_state.selected_emp_id)
        st.subheader(f"Editing Record for {row[0]}")
        name = st.text_input("Name", row[1], key="edit_name")
        email = st.text_input("Email", row[2], key="edit_email")
        role = st.text_input("Role", row[3], key="edit_role")
        primary_skills = st.text_input("Primary Skills", row[4], key="edit_primary")
        secondary_skills = st.text_input("Secondary Skills", row[5], key="edit_secondary")
        certifications = st.text_input("Certifications", row[6], key="edit_certs")
        total_exp = st.number_input("Total Exp", value=row[7], key="edit_total_exp")
        relevant_exp = st.number_input("Relevant Exp", value=row[8], key="edit_relevant_exp")
        location = st.text_input("Location", row[9], key="edit_location")
        aspiration = st.text_area("Aspiration", row[10], key="edit_aspiration")
        plan = st.text_area("Action Plan", row[11], key="edit_plan")
        target = st.date_input("Target Date", pd.to_datetime(row[12]), key="edit_date")
        resume = st.file_uploader("Update Resume", type=["pdf", "docx"], key="edit_resume")

        if st.button("Update Record", key="submit_record_update"):
            resume_path = row[13]
            if resume:
                resume_path = os.path.join(UPLOAD_DIR, f"{row[0]}_{resume.name}")
                with open(resume_path, "wb") as f:
                    f.write(resume.read())

            updated_data = (name, email, role, primary_skills, secondary_skills,
                            certifications, total_exp, relevant_exp, location,
                            aspiration, plan, str(target), resume_path)
            update_employee_record(row[0], updated_data)
            st.success("Record updated successfully!")
