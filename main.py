import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
from pathlib import Path
import bcrypt #added import for bcrypt

# Create necessary directories if they don't exist
Path("data").mkdir(exist_ok=True)
Path("styles").mkdir(exist_ok=True)

# Initialize session state
def initialize_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False

# Authentication functions
def load_admin_credentials():
    try:
        if os.path.exists('admin.json'):
            with open('admin.json', 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        if os.path.exists('admin.json'):
            os.remove('admin.json')  # Remove corrupted file
    return None

def save_admin_credentials(username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    admin_data = {
        'username': username,
        'password': hashed.decode('utf-8')
    }
    with open('admin.json', 'w') as f:
        json.dump(admin_data, f)

def load_staff_credentials():
    try:
        if os.path.exists('staff.json'):
            with open('staff.json', 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        if os.path.exists('staff.json'):
            os.remove('staff.json')
    return {'staff': []}

def save_staff_credentials(username, password, role):
    staff_data = load_staff_credentials()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    staff_data['staff'].append({
        'username': username,
        'password': hashed.decode('utf-8'),
        'role': role
    })
    with open('staff.json', 'w') as f:
        json.dump(staff_data, f)

def verify_credentials(username, password):
    # Check admin credentials first
    admin_data = load_admin_credentials()
    if admin_data and admin_data['username'] == username:
        try:
            if bcrypt.checkpw(password.encode('utf-8'), 
                            admin_data['password'].encode('utf-8')):
                return True, True  # authenticated, is_admin
        except Exception as e:
            st.error(f"Error verifying admin credentials: {str(e)}")
            return False, False

    # Check staff credentials
    staff_data = load_staff_credentials()
    for staff in staff_data['staff']:
        if staff['username'] == username:
            try:
                if bcrypt.checkpw(password.encode('utf-8'), 
                                staff['password'].encode('utf-8')):
                    return True, False  # authenticated, not admin
            except Exception as e:
                st.error(f"Error verifying staff credentials: {str(e)}")
                return False, False

    return False, False

def log_activity(action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("audit_log.txt", "a") as f:
        f.write(f"{timestamp} - {st.session_state.username}: {action}\n")

# Page functions
def login_page():
    st.title("🏥 Hospital Management System")

    # Check if admin exists
    admin_data = load_admin_credentials()

    if not admin_data:
        st.warning("Welcome! Please create an admin account to get started.")
        with st.form("create_admin"):
            new_username = st.text_input("Create Admin Username")
            new_password = st.text_input("Create Admin Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            if st.form_submit_button("Create Admin Account"):
                if not new_username or not new_password:
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    save_admin_credentials(new_username, new_password)
                    st.success("Admin account created successfully! Please log in.")
                    st.rerun()
    else:
        # Add tabs for login/signup
        tab1, tab2 = st.tabs(["Login", "Create Staff Account"])

        with tab1:
            with st.form("login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    authenticated, is_admin = verify_credentials(username, password)
                    if authenticated:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.is_admin = is_admin
                        log_activity("Logged in as " + ("admin" if is_admin else "staff"))
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

        with tab2:
            with st.form("create_staff"):
                st.subheader("Create New Staff Account")
                staff_username = st.text_input("Staff Username")
                staff_password = st.text_input("Staff Password", type="password")
                confirm_staff_password = st.text_input("Confirm Password", type="password")
                role = st.selectbox("Staff Role", 
                    ["Doctor", "Nurse", "Receptionist", "Pharmacist", "Lab Technician"])

                if st.form_submit_button("Create Staff Account"):
                    if not staff_username or not staff_password:
                        st.error("Please fill in all fields")
                    elif staff_password != confirm_staff_password:
                        st.error("Passwords do not match")
                    else:
                        try:
                            save_staff_credentials(staff_username, staff_password, role)
                            st.success("Staff account created successfully! Please log in.")
                            log_activity(f"New staff account created: {staff_username} ({role})")
                        except Exception as e:
                            st.error(f"Error creating staff account: {str(e)}")

def main_page():
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        st.session_state.current_page = st.radio(
            "Go to",
            ["Dashboard", "Patients", "Appointments", "Staff",
             "Inventory", "Pharmacy", "Billing", "Reports", "Audit Log"]
        )

        if st.button("Logout"):
            log_activity("Logged out")
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.is_admin = False
            st.rerun()

    # Main content
    if st.session_state.current_page == "Dashboard":
        st.title("Hospital Dashboard")

        # Example metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Patients", "150")
        with col2:
            st.metric("Today's Appointments", "25")
        with col3:
            st.metric("Available Staff", "45")
        with col4:
            st.metric("Bed Occupancy", "75%")

    elif st.session_state.current_page == "Audit Log":
        if st.session_state.is_admin:
            st.title("System Audit Log")
            if os.path.exists("audit_log.txt"):
                with open("audit_log.txt", "r") as f:
                    logs = f.readlines()
                for log in reversed(logs):  # Show most recent first
                    st.text(log.strip())
            else:
                st.info("No audit logs found")
        else:
            st.error("Access Denied: Only administrators can view the audit log")

def main():
    st.set_page_config(
        page_title="Hospital Management System",
        page_icon="🏥",
        layout="wide"
    )

    initialize_session()

    if not st.session_state.logged_in:
        login_page()
    else:
        main_page()

if __name__ == "__main__":
    main()