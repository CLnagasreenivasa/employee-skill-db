
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

def add_employee(data):
    c.execute("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()

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

st.set_page_config(layout="wide")
st.title("🧠 Employee Skill Database")

tab1, tab2, tab3 = st.tabs(["➕ Add Employee", "✏️ Update / Delete", "🔍 Search Employees"])

# ➕ Add
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

# ✏️ Update/Delete
with tab2:
    st.header("Update or Delete Employees")
    keyword = st.text_input("Search by keyword (name, skills, etc.):", key="search_update")
    result_msg = st.empty()

    if st.button("Search", key="btn_search_update"):
        results = flexible_search(keyword)
        if results:
            for idx, row in enumerate(results):
                with st.expander(f"{row[0]} - {row[1]}"):
                    name = st.text_input("Name", row[1], key=f"name_{idx}")
                    email = st.text_input("Email", row[2], key=f"email_{idx}")
                    role = st.text_input("Role", row[3], key=f"role_{idx}")
                    primary_skills = st.text_input("Primary Skills", row[4], key=f"pskills_{idx}")
                    secondary_skills = st.text_input("Secondary Skills", row[5], key=f"sskills_{idx}")
                    certifications = st.text_input("Certifications", row[6], key=f"certs_{idx}")
                    total_exp = st.number_input("Total Exp", value=row[7], key=f"texp_{idx}")
                    relevant_exp = st.number_input("Relevant Exp", value=row[8], key=f"rexp_{idx}")
                    location = st.text_input("Location", row[9], key=f"loc_{idx}")
                    aspiration = st.text_area("Aspiration", row[10], key=f"asp_{idx}")
                    plan = st.text_area("Action Plan", row[11], key=f"plan_{idx}")
                    target = st.date_input("Target Date", pd.to_datetime(row[12]), key=f"tgt_{idx}")
                    resume_path = row[13]

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Update", key=f"update_{idx}"):
                            update_employee(row[0], (
                                name, email, role, primary_skills, secondary_skills,
                                certifications, total_exp, relevant_exp, location,
                                aspiration, plan, str(target), resume_path
                            ))
                            result_msg.success(f"✅ Record for {row[0]} updated successfully.")

                    with col2:
                        if st.button("❌ Delete", key=f"delete_{idx}"):
                            delete_employee(row[0])
                            result_msg.warning(f"⚠️ Record for {row[0]} deleted.")

        else:
            st.warning("No matching records found.")

# 🔍 Search
with tab3:
    st.header("Search Employees (by ID, Name, Skills, etc.)")
    keyword = st.text_input("Enter any search keyword", key="search_tab")
    if st.button("Search", key="btn_search_tab"):
        results = flexible_search(keyword)
        if results:
            df = pd.DataFrame(results, columns=[
                "Employee ID", "Name", "Email", "Role", "Primary Skills", "Secondary Skills",
                "Certifications", "Total Exp", "Relevant Exp", "Location", "Aspiration",
                "Action Plan", "Target Date", "Resume Path"
            ])
            st.dataframe(df.drop(columns=["Resume Path"]))
        else:
            st.warning("No records matched your search.")
