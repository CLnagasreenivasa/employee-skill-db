
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
                safe_name = resume.name.replace(" ", "_")
                resume_path = os.path.join(UPLOAD_DIR, f"{emp_id}_{safe_name}")
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
    keyword = st.text_input("Search by any field (ID, Name, Skills, etc.)", key="update_search")
    matched_rows = []
    selected = None

    if st.button("Search", key="update_search_btn"):
        matched_rows = flexible_search(keyword)
        if matched_rows:
            df = pd.DataFrame(matched_rows, columns=["Employee ID", "Name", "Email", "Role", "Primary Skills", "Secondary Skills",
                                                      "Certifications", "Total Exp", "Relevant Exp", "Location", "Aspiration",
                                                      "Action Plan", "Target Date", "Resume Path"])
            st.dataframe(df)
            emp_ids = [row[0] for row in matched_rows]
            selected = st.selectbox("Select an Employee ID to Edit", emp_ids, key="edit_select")

    if selected:
        row = next(row for row in matched_rows if row[0] == selected)
        st.subheader(f"Editing Record for {selected}")
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
                safe_name = resume.name.replace(" ", "_")
                resume_path = os.path.join(UPLOAD_DIR, f"{selected}_{safe_name}")
                with open(resume_path, "wb") as f:
                    f.write(resume.read())

            updated_data = (name, email, role, primary_skills, secondary_skills,
                            certifications, total_exp, relevant_exp, location,
                            aspiration, plan, str(target), resume_path)
            update_employee_record(selected, updated_data)
            st.success("Record updated successfully!")

with tab3:
    st.header("Search Employees (by ID, Name, Skills, etc.)")
    keyword = st.text_input("Enter any search keyword", key="search_generic")
    if st.button("Search", key="submit_search"):
        results = flexible_search(keyword)
        if results:
            st.write("### Results")
            for row in results:
                st.markdown(f"**🆔 {row[0]} | 👤 {row[1]} | 📧 {row[2]} | 🧰 {row[4]} | 📍 {row[9]}**")
                st.markdown(f"🔖 **Certifications:** {row[6]}")
                st.markdown(f"🎯 **Career Aspiration:** {row[10]}")
                st.markdown(f"📅 **Target Date:** {row[12]}")
                if row[13] and os.path.exists(row[13]):
                    with open(row[13], "rb") as file:
                        btn = st.download_button(
                            label="📎 Download Resume",
                            data=file,
                            file_name=os.path.basename(row[13]),
                            mime="application/octet-stream"
                        )
                else:
                    st.markdown("❌ No resume uploaded.")
                st.markdown("---")
