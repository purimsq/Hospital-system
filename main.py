import streamlit as st
import pandas as pd
from utils.auth import Auth
from utils.data_manager import DataManager
import os

# Initialize authentication and data management
auth = Auth()
data_manager = DataManager()

# Configure page
st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide"
)

# Load custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def initialize_session():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None

def login_page():
    st.title("🏥 Hospital Management System")
    
    if not auth.admin_exists():
        st.warning("No admin account exists. Create one now.")
        with st.form("create_admin"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            if st.form_submit_button("Create Admin"):
                if new_username and new_password:
                    auth.save_admin(new_username, new_password)
                    st.success("Admin account created successfully!")
                    auth.log_activity("Admin account created")
                else:
                    st.error("Please fill in all fields")
    else:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if auth.verify_admin(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    auth.log_activity("Admin logged in")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

def main_page():
    st.sidebar.title("Navigation")
    
    # Sidebar navigation
    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Patients", "Appointments", "Inventory", 
         "Staff", "Billing", "Reports", "Audit Log"]
    )
    
    # Logout button
    if st.sidebar.button("Logout"):
        auth.log_activity("Admin logged out")
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    
    # Page content
    if page == "Dashboard":
        st.title("Hospital Dashboard")
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        patients_df = data_manager.load_data("patients")
        appointments_df = data_manager.load_data("appointments")
        staff_df = data_manager.load_data("staff")
        inventory_df = data_manager.load_data("inventory")
        
        with col1:
            st.metric("Total Patients", len(patients_df))
        with col2:
            st.metric("Today's Appointments", 
                     len(appointments_df[appointments_df['date'] == pd.Timestamp.now().date().strftime("%Y-%m-%d")]))
        with col3:
            st.metric("Staff Members", len(staff_df))
        with col4:
            st.metric("Low Stock Items", 
                     len(inventory_df[inventory_df['quantity'] < 10]))
    
    elif page == "Audit Log":
        st.title("System Audit Log")
        if os.path.exists("audit_log.txt"):
            with open("audit_log.txt", "r") as f:
                logs = f.readlines()
            for log in logs:
                st.text(log.strip())
        else:
            st.info("No audit logs found")

def main():
    initialize_session()
    
    if not st.session_state.logged_in:
        login_page()
    else:
        main_page()

if __name__ == "__main__":
    main()
