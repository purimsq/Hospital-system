import streamlit as st
import pandas as pd
from datetime import datetime
import os
import bcrypt
from sqlalchemy.orm import Session
from database import get_db, User, AuditLog, Patient, Appointment, Inventory

# Initialize database session
db = next(get_db())

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
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

# Authentication functions
def save_user_credentials(username, password, role='staff'):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(
        username=username,
        password=hashed.decode('utf-8'),
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def verify_credentials(username, password):
    user = db.query(User).filter(User.username == username).first()
    if user:
        try:
            if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                user.last_login = datetime.utcnow()
                db.commit()
                return True, user.role == 'admin', user.id
        except Exception as e:
            st.error(f"Error verifying credentials: {str(e)}")
    return False, False, None

def log_activity(action, details=None):
    new_log = AuditLog(
        user_id=st.session_state.user_id,
        action=action,
        details=details
    )
    db.add(new_log)
    db.commit()

def login_page():
    st.title("🏥 Hospital Management System")

    # Check if admin exists
    admin_exists = db.query(User).filter(User.role == 'admin').first() is not None

    if not admin_exists:
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
                    try:
                        save_user_credentials(new_username, new_password, role='admin')
                        st.success("Admin account created successfully! Please log in.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating admin account: {str(e)}")
    else:
        # Add tabs for login/signup
        tab1, tab2 = st.tabs(["Login", "Create Staff Account"])

        with tab1:
            with st.form("login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    authenticated, is_admin, user_id = verify_credentials(username, password)
                    if authenticated:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.is_admin = is_admin
                        st.session_state.user_id = user_id
                        log_activity("Logged in", f"User logged in as {username}")
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
                            save_user_credentials(staff_username, staff_password, role)
                            st.success("Staff account created successfully! Please log in.")
                            log_activity("Staff account created", f"New staff account created: {staff_username} ({role})")
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
            st.session_state.user_id = None
            st.rerun()

    # Main content
    if st.session_state.current_page == "Dashboard":
        st.title("Hospital Dashboard")

        # Real metrics from database
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            patient_count = db.query(Patient).count()
            st.metric("Total Patients", patient_count)
        with col2:
            today_appointments = db.query(Appointment).filter(
                Appointment.appointment_date >= datetime.now().date()
            ).count()
            st.metric("Today's Appointments", today_appointments)
        with col3:
            staff_count = db.query(User).filter(User.role != 'admin').count()
            st.metric("Available Staff", staff_count)
        with col4:
            low_stock_count = db.query(Inventory).filter(
                Inventory.quantity <= Inventory.reorder_level
            ).count()
            st.metric("Low Stock Items", low_stock_count)

    elif st.session_state.current_page == "Audit Log":
        if st.session_state.is_admin:
            st.title("System Audit Log")
            audit_logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
            for log in audit_logs:
                user = db.query(User).filter(User.id == log.user_id).first()
                st.text(f"{log.timestamp} - {user.username if user else 'Unknown User'}: {log.action} - {log.details if log.details else ''}")
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