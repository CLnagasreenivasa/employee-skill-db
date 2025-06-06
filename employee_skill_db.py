
import streamlit as st
import sqlite3
import os
import pandas as pd

# DB setup
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

def update_employee(emp_id, field_values):
    query = """
    UPDATE employees SET
        name=?, email=?, role=?, primary_skills=?, secondary_skills=?,
        certifications=?, total_experience=?, relevant_experience=?,
        current_location=?, career_aspiration=?, action_plan=?, target_date=?, resume_path=?
    WHERE employee_id=?
    """
    c.execute(query, (*field_values, emp_id))
    conn.commit()

def delete_employee(emp_id):
    c.execute("DELETE FROM employees WHERE employee_id=?", (emp_id,))
    conn.commit()

# UI
st.set_page_config(layout="wide")
st.title("🧠 Employee Skill Database - Update / Delete Only")

keyword = st.text_input("Search by keyword (e.g., mw admin)", key="search_update")

if st.button("Search", key="btn_search_update"):
    results = flexible_search(keyword)
    if results:
        for idx, row in enumerate(results):
            with st.expander(f"{row[0]} - {row[1]}", expanded=True):
                with st.form(key=f"form_{row[0]}"):
                    name = st.text_input("Name", row[1])
                    email = st.text_input("Email", row[2])
                    role = st.text_input("Role", row[3])
                    primary_skills = st.text_input("Primary Skills", row[4])
                    secondary_skills = st.text_input("Secondary Skills", row[5])
                    certifications = st.text_input("Certifications", row[6])
                    total_exp = st.number_input("Total Exp", value=row[7])
                    relevant_exp = st.number_input("Relevant Exp", value=row[8])
                    location = st.text_input("Location", row[9])
                    aspiration = st.text_area("Aspiration", row[10])
                    plan = st.text_area("Action Plan", row[11])
                    target = st.date_input("Target Date", pd.to_datetime(row[12]))
                    resume_path = row[13]

                    submitted = st.form_submit_button("Update Record")
                    if submitted:
                        update_employee(row[0], (
                            name, email, role, primary_skills, secondary_skills,
                            certifications, total_exp, relevant_exp,
                            location, aspiration, plan, str(target), resume_path
                        ))
                        st.success(f"✅ Employee {name} (ID: {row[0]}) updated successfully!")

                if st.button("❌ Delete This Employee", key=f"delete_{row[0]}"):
                    delete_employee(row[0])
                    st.warning(f"⚠️ Employee ID {row[0]} deleted.")
    else:
        st.warning("No matching records found.")
