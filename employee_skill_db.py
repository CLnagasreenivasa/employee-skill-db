
import streamlit as st
import sqlite3
import os
import pandas as pd

# Database setup
conn = sqlite3.connect("employee_data.db", check_same_thread=False)
c = conn.cursor()

UPLOAD_DIR = "resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

with tab3:
    st.header("Search Employees (by ID, Name, Skills, etc.)")
    keyword = st.text_input("Enter any search keyword", key="search_keyword")
    selected_id = None
    employee_data = []

    if st.button("Search", key="search_button"):
        employee_data = flexible_search(keyword)
        if employee_data:
            options = [f"{row[0]} - {row[1]} ({row[2]})" for row in employee_data]
            selected_option = st.selectbox("Select an employee to view details", options)
            selected_id = selected_option.split(" - ")[0]

    if selected_id:
        row = next(emp for emp in employee_data if emp[0] == selected_id)
        st.markdown(f"**🆔 {row[0]} | 👤 {row[1]} | 📧 {row[2]} | 🧰 {row[4]} | 📍 {row[9]}**")
        st.markdown(f"🔖 **Certifications:** {row[6]}")
        st.markdown(f"🎯 **Career Aspiration:** {row[10]}")
        st.markdown(f"📅 **Target Date:** {row[12]}")
        if row[13] and os.path.exists(row[13]):
            with open(row[13], "rb") as file:
                st.download_button(
                    label="📎 Download Resume",
                    data=file,
                    file_name=os.path.basename(row[13]),
                    mime="application/octet-stream"
                )
        else:
            st.markdown("❌ No resume uploaded.")
