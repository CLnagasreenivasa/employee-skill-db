import streamlit as st
import sqlite3
import os

# ------------------ DB Setup ------------------
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

# ------------------ Helper Functions ------------------
def add_employee(data):
    c.execute('''INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()

def update_full_employee(data):
    try:
        st.write("🚧 Update called with the following data:")
        st.json({
            "employee_id": data[-1],
            "name": data[0],
            "email": data[1],
            "role": data[2],
            "primary_skills": data[3],
            "secondary_skills": data[4],
            "certifications": data[5],
            "total_experience": data[6],
            "relevant_experience": data[7],
            "current_location": data[8],
            "career_aspiration": data[9],
            "action_plan": data[10],
            "target_date": data[11]
        })

        c.execute("""
            UPDATE employees SET 
                name = ?, email = ?, role = ?, primary_skills = ?, secondary_skills = ?,
                certifications = ?, total_experience = ?, relevant_experience = ?,
                current_location = ?, career_aspiration = ?, action_plan = ?, target_date = ?
            WHERE employee_id = ?
        """, data)

        conn.commit()

        if c.rowcount == 0:
            st.error("⚠️ No record was updated. Please check if the Employee ID exists.")
        else:
            st.success(f"✅ {c.rowcount} record(s) updated successfully for Employee ID: {data[-1]}")

    except Exception as e:
        st.exception(f"❌ Exception occurred while updating the employee record: {e}")


def get_all_employees():
    c.execute("SELECT * FROM employees")
    return c.fetchall()

def get_employee(emp_id):
    c.execute("SELECT * FROM employees WHERE employee_id = ?", (emp_id,))
    return c.fetchone()

# ------------------ UI ------------------
st.set_page_config(page_title="Employee Skill DB", layout="wide")
st.title("🧠 Employee Skill Database")

tab1, tab2, tab3 = st.tabs(["➕ Add Employee", "✏️ Update Employee", "🔍 Search Employee"])

# ------------------ Add Employee ------------------
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

# ------------------ Update Employee ------------------
with tab2:
    st.header("Update Employee Information")

    search_query = st.text_input("🔍 Search by any field value", key="update_search_input")

    if st.button("Search Records", key="update_search_button"):
        if search_query.strip():
            all_records = get_all_employees()
            matching = [r for r in all_records if any(search_query.lower() in str(f).lower() for f in r)]

            if matching:
                st.markdown("### 🔎 Matching Employee Records")

                for record in matching:
                    emp_id = record[0]

                    with st.expander(f"📋 {emp_id} — {record[1]}", expanded=False):
                        with st.form(key=f"form_{emp_id}"):
                            name = st.text_input("Name", record[1], key=f"name_{emp_id}")
                            email = st.text_input("Email", record[2], key=f"email_{emp_id}")
                            role = st.text_input("Role", record[3], key=f"role_{emp_id}")
                            primary_skills = st.text_input("Primary Skills", record[4], key=f"primary_{emp_id}")
                            secondary_skills = st.text_input("Secondary Skills", record[5], key=f"secondary_{emp_id}")
                            certifications = st.text_input("Certifications", record[6], key=f"certs_{emp_id}")
                            total_exp = st.number_input("Total Experience", value=record[7], step=0.1, key=f"total_{emp_id}")
                            relevant_exp = st.number_input("Relevant Experience", value=record[8], step=0.1, key=f"relevant_{emp_id}")
                            location = st.text_input("Current Location", record[9], key=f"location_{emp_id}")
                            aspiration = st.text_area("Career Aspiration", record[10], key=f"asp_{emp_id}")
                            plan = st.text_area("Action Plan", record[11], key=f"plan_{emp_id}")
                            target_date = st.date_input("Target Date", record[12], key=f"target_{emp_id}")

                            submitted = st.form_submit_button("Update Employee", type="primary")

                            if submitted:
                                update_full_employee((
                                    name, email, role, primary_skills, secondary_skills,
                                    certifications, total_exp, relevant_exp, location,
                                    aspiration, plan, str(target_date), emp_id
                                ))
                                st.success(f"✅ Employee '{emp_id}' updated successfully.")
            else:
                st.warning("No matching records found.")
        else:
            st.info("Please enter a value to search.")

# ------------------ Search Employee ------------------
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
