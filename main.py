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
    if os.path.exists('admin.json'):
        with open('admin.json', 'r') as f:
            return json.load(f)
    return None

def save_admin_credentials(username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    admin_data = {
        'username': username,
        'password': hashed.decode('utf-8')
    }
    with open('admin.json', 'w') as f:
        json.dump(admin_data, f)

def verify_admin(username, password):
    admin_data = load_admin_credentials()
    if admin_data and admin_data['username'] == username:
        return bcrypt.checkpw(password.encode('utf-8'), 
                            admin_data['password'].encode('utf-8'))
    return False

def log_activity(action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("audit_log.txt", "a") as f:
        f.write(f"{timestamp} - {st.session_state.username}: {action}\n")

# Page functions
def login_page():
    st.title("🏥 Hospital Management System")

    # Check if admin exists
    admin_exists = os.path.exists('admin.json')

    if not admin_exists:
        st.warning("Welcome! No admin account exists. Please create one now.")
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
                    if verify_admin(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.is_admin = True
                        log_activity("Logged in as admin")
                        st.rerun()
                    else:
                        # Here we would check staff credentials
                        st.error("Invalid credentials")

        with tab2:
            st.info("Staff account creation feature coming soon...")
            # We'll implement staff account creation in the next iteration

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
        st.title("System Audit Log")
        if os.path.exists("audit_log.txt"):
            with open("audit_log.txt", "r") as f:
                logs = f.readlines()
            for log in reversed(logs):  # Show most recent first
                st.text(log.strip())
        else:
            st.info("No audit logs found")

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