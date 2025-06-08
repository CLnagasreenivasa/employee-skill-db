import streamlit as st
import sqlite3
import os

# Database setup
conn = sqlite3.connect("employee_data.db")
c = conn.cursor()

# Create uploads directory
UPLOAD_DIR = "resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create table if not exists
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

# Database operations
def add_employee(data):
    c.execute('''INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()

def update_employee(emp_id, field, new_value):
    c.execute(f"UPDATE employees SET {field} = ? WHERE employee_id = ?", (new_value, emp_id))
    conn.commit()

def get_employee(emp_id):
    c.execute("SELECT * FROM employees WHERE employee_id = ?", (emp_id,))
    return c.fetchone()

# App UI
st.title("🧠 Employee Skill Database")

# Top-aligned tabs
tab1, tab2, tab3 = st.tabs(["➕ Add Employee", "✏️ Update Employee", "🔍 Search Employee"])

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

with tab2:
    st.header("Update Employee Information")

    search_query = st.text_input("🔍 Search by any field value")

    if st.button("Search Records"):
        if search_query.strip():
            c.execute("SELECT * FROM employees")
            all_records = c.fetchall()
            matching = []
            for record in all_records:
                if any(search_query.lower() in str(field).lower() for field in record):
                    matching.append(record)

            if matching:
                keys = ["Employee ID", "Name", "Email", "Role", "Primary Skills", "Secondary Skills",
                        "Certifications", "Total Exp", "Relevant Exp", "Location", "Aspiration",
                        "Action Plan", "Target Date", "Resume Path"]

                selected = st.selectbox("Select Record to Edit (by Employee ID)", [r[0] for r in matching])

                selected_record = next((r for r in matching if r[0] == selected), None)

                if selected_record:
                    st.markdown("### ✏️ Edit Employee Details")

                    emp_id = selected_record[0]
                    name = st.text_input("Name", selected_record[1])
                    email = st.text_input("Email", selected_record[2])
                    role = st.text_input("Role", selected_record[3])
                    primary_skills = st.text_input("Primary Skills", selected_record[4])
                    secondary_skills = st.text_input("Secondary Skills", selected_record[5])
                    certifications = st.text_input("Certifications", selected_record[6])
                    total_exp = st.number_input("Total Experience", value=selected_record[7], step=0.1)
                    relevant_exp = st.number_input("Relevant Experience", value=selected_record[8], step=0.1)
                    location = st.text_input("Location", selected_record[9])
                    aspiration = st.text_area("Career Aspiration", selected_record[10])
                    plan = st.text_area("Action Plan", selected_record[11])
                    target_date = st.date_input("Target Date", selected_record[12])

                    if st.button("Update Employee"):
                        try:
                            c.execute("""
                                UPDATE employees SET 
                                    name = ?, email = ?, role = ?, primary_skills = ?, secondary_skills = ?,
                                    certifications = ?, total_experience = ?, relevant_experience = ?,
                                    current_location = ?, career_aspiration = ?, action_plan = ?, target_date = ?
                                WHERE employee_id = ?
                            """, (name, email, role, primary_skills, secondary_skills, certifications,
                                  total_exp, relevant_exp, location, aspiration, plan, str(target_date), emp_id))
                            conn.commit()
                            st.success(f"✅ Employee '{emp_id}' updated successfully!")
                        except Exception as e:
                            st.error(f"❌ Error updating employee: {e}")
            else:
                st.warning("No matching records found.")
        else:
            st.info("Please enter a value to search.")

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
