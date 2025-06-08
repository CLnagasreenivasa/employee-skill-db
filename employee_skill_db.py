import streamlit as st
import sqlite3
import os

# Database setup
conn = sqlite3.connect("employee_data.db", check_same_thread=False)
c = conn.cursor()

# Create uploads directory
UPLOAD_DIR = "resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Table creation
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

# Helper functions
def add_employee(data):
    c.execute('''INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()

def update_full_employee(data):
    c.execute("""
        UPDATE employees SET 
            name = ?, email = ?, role = ?, primary_skills = ?, secondary_skills = ?,
            certifications = ?, total_experience = ?, relevant_experience = ?,
            current_location = ?, career_aspiration = ?, action_plan = ?, target_date = ?
        WHERE employee_id = ?
    """, data)
    conn.commit()

def get_all_employees():
    c.execute("SELECT * FROM employees")
    return c.fetchall()

def get_employee(emp_id):
    c.execute("SELECT * FROM employees WHERE employee_id = ?", (emp_id,))
    return c.fetchone()

# UI
st.set_page_config(page_title="Employee Skill DB", layout="wide")
st.title("🧠 Employee Skill Database")

tab1, tab2, tab3 = st.tabs(["➕ Add Employee", "✏️ Update Employee", "🔍 Search Employee"])

# ------------------- ADD EMPLOYEE -------------------
with tab1:
    st.header("Add New Employee")

    emp_id = st.text_input("Employee ID")
    name = st.text_input("Employee Name")
    email = st.text_input("E-Mail ID")
    role = st.text_input("Role")
    primary_skills = st.text_input("Primary Skills")
    secondary_skills = st.text_input("Secondary Skills")
    certifications = st.text_input("Certifications")
    total_exp = st.number_input("Total Experience (years)", step=0.1)
    relevant_exp = st.number_input("Relevant Experience (years)", step=0.1)
    location = st.text_input("Current Location")
    aspiration = st.text_area("Career Aspiration")
    plan = st.text_area("Action Plan")
    target_date = st.date_input("Target Date")
    resume = st.file_uploader("Upload Resume", type=["pdf", "docx"])

    if st.button("Submit Employee"):
        if emp_id and name:
            resume_path = ""
            if resume:
                resume_path = os.path.join(UPLOAD_DIR, f"{emp_id}_{resume.name}")
                with open(resume_path, "wb") as f:
                    f.write(resume.read())
            data = (emp_id, name, email, role, primary_skills, secondary_skills, certifications,
                    total_exp, relevant_exp, location, aspiration, plan, str(target_date), resume_path)
            try:
                add_employee(data)
                st.success(f"✅ Employee {name} added successfully!")
            except sqlite3.IntegrityError:
                st.error("❌ Employee ID already exists!")
        else:
            st.warning("⚠️ Employee ID and Name are required!")

# ------------------- UPDATE EMPLOYEE -------------------
with tab2:
    st.header("Update Employee Information")

    search_query = st.text_input("🔍 Search by any field value", key="update_search_input")

    if st.button("Search Records", key="update_search_button"):
        if search_query.strip():
            all_records = get_all_employees()
            matching = [r for r in all_records if any(search_query.lower() in str(f).lower() for f in r)]

            if matching:
                selected_id = st.selectbox("Select Employee to Edit", [r[0] for r in matching], key="update_select_emp")
                selected_record = next((r for r in matching if r[0] == selected_id), None)

                if selected_record:
                    st.markdown("### ✏️ Edit Details")

                    name = st.text_input("Name", selected_record[1], key="update_name")
                    email = st.text_input("Email", selected_record[2], key="update_email")
                    role = st.text_input("Role", selected_record[3], key="update_role")
                    primary_skills = st.text_input("Primary Skills", selected_record[4], key="update_primary_skills")
                    secondary_skills = st.text_input("Secondary Skills", selected_record[5], key="update_secondary_skills")
                    certifications = st.text_input("Certifications", selected_record[6], key="update_certifications")
                    total_exp = st.number_input("Total Experience", value=selected_record[7], step=0.1, key="update_total_exp")
                    relevant_exp = st.number_input("Relevant Experience", value=selected_record[8], step=0.1, key="update_relevant_exp")
                    location = st.text_input("Current Location", selected_record[9], key="update_location")
                    aspiration = st.text_area("Career Aspiration", selected_record[10], key="update_aspiration")
                    plan = st.text_area("Action Plan", selected_record[11], key="update_plan")
                    target_date = st.date_input("Target Date", selected_record[12], key="update_target_date")

                    if st.button("Update Employee", key="update_submit_button"):
                        try:
                            update_full_employee((
                                name, email, role, primary_skills, secondary_skills,
                                certifications, total_exp, relevant_exp, location,
                                aspiration, plan, str(target_date), selected_id
                            ))
                            st.success(f"✅ Employee '{selected_id}' updated successfully!")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
            else:
                st.warning("No matching records found.")
        else:
            st.info("Please enter a value to search.")


# ------------------- SEARCH EMPLOYEE -------------------
with tab3:
    st.header("Search Employee")
    emp_id = st.text_input("Enter Employee ID to Search")
    if st.button("Search"):
        record = get_employee(emp_id)
        if record:
            keys = ["Employee ID", "Name", "Email", "Role", "Primary Skills", "Secondary Skills",
                    "Certifications", "Total Exp", "Relevant Exp", "Location", "Aspiration",
                    "Action Plan", "Target Date", "Resume Path"]
            st.write(dict(zip(keys, record)))
            if record[-1]:
                st.markdown(f"[📄 Download Resume]({record[-1]})")
        else:
            st.warning("❗ Employee not found.")
