
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

st.title("🧠 Employee Skill Database")

tab1, tab2, tab3 = st.tabs(["➕ Add Employee", "✏️ Update / Delete", "🔍 Search Employees"])

# Add employee
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

# Update/Delete employee
with tab2:
    st.header("Update or Delete Employees")
    keyword = st.text_input("Search by keyword (name, skills, etc.):", key="search_update")
    update_message = ""

    if st.button("Search", key="btn_search_update"):
        results = flexible_search(keyword)
        if results:
            for idx, row in enumerate(results):
                with st.expander(f"🔧 Edit: {row[0]} - {row[1]}"):
                    name = st.text_input("Name", row[1], key=f"edit_name_{idx}")
                    email = st.text_input("Email", row[2], key=f"edit_email_{idx}")
                    role = st.text_input("Role", row[3], key=f"edit_role_{idx}")
                    primary_skills = st.text_input("Primary Skills", row[4], key=f"edit_primary_{idx}")
                    secondary_skills = st.text_input("Secondary Skills", row[5], key=f"edit_secondary_{idx}")
                    certifications = st.text_input("Certifications", row[6], key=f"edit_cert_{idx}")
                    total_exp = st.number_input("Total Exp", value=row[7], key=f"edit_total_{idx}")
                    relevant_exp = st.number_input("Relevant Exp", value=row[8], key=f"edit_relevant_{idx}")
                    location = st.text_input("Location", row[9], key=f"edit_location_{idx}")
                    aspiration = st.text_area("Aspiration", row[10], key=f"edit_aspiration_{idx}")
                    plan = st.text_area("Action Plan", row[11], key=f"edit_plan_{idx}")
                    target = st.date_input("Target Date", pd.to_datetime(row[12]), key=f"edit_target_{idx}")
                    resume = st.file_uploader("Upload Resume", type=["pdf", "docx"], key=f"edit_resume_{idx}")

                    resume_path = row[13]
                    if resume:
                        resume_path = os.path.join(UPLOAD_DIR, f"{row[0]}_{resume.name}")
                        with open(resume_path, "wb") as f:
                            f.write(resume.read())

                    if st.button("Update", key=f"btn_update_{idx}"):
                        update_employee(row[0], (
                            name, email, role, primary_skills, secondary_skills,
                            certifications, total_exp, relevant_exp,
                            location, aspiration, plan, str(target), resume_path
                        ))
                        update_message = f"✅ Record for {row[0]} updated successfully."

                    if st.button("❌ Delete", key=f"btn_delete_{idx}"):
                        delete_employee(row[0])
                        update_message = f"⚠️ Record for {row[0]} deleted."

            if update_message:
                st.success(update_message)
        else:
            st.warning("No matching records found.")

# Search tab
with tab3:
    st.header("Search Employees (by ID, Name, Skills, etc.)")
    keyword = st.text_input("Enter any search keyword", key="search_tab")
    if st.button("Search", key="btn_search_tab"):
        results = flexible_search(keyword)
        if results:
            columns = ["Employee ID", "Name", "Email", "Role", "Primary Skills", "Secondary Skills",
                       "Certifications", "Total Exp", "Relevant Exp", "Location", "Aspiration",
                       "Action Plan", "Target Date", "Resume Download"]
            rows = []
            for row in results:
                download_button = ""
                if row[13] and os.path.exists(row[13]):
                    with open(row[13], "rb") as f:
                        st.download_button(label=f"📄 Download Resume for {row[0]}", data=f,
                                           file_name=os.path.basename(row[13]),
                                           mime="application/octet-stream", key=f"dl_{row[0]}")
                rows.append(row[:13] + (row[13],))
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df.drop(columns=["Resume Download"]))  # Hide path column
        else:
            st.warning("No records matched your search.")
