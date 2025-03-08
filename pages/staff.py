import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.auth import Auth

data_manager = DataManager()
auth = Auth()

def render():
    st.title("Staff Management")
    
    # Add new staff member
    with st.expander("Add New Staff Member"):
        with st.form("add_staff"):
            name = st.text_input("Name")
            role = st.selectbox("Role", 
                              ["Doctor", "Nurse", "Receptionist", "Administrator", "Other"])
            contact = st.text_input("Contact")
            schedule = st.text_area("Schedule")
            
            if st.form_submit_button("Add Staff Member"):
                if name and contact:
                    new_staff = {
                        "id": pd.util.hash_pandas_object(pd.Series([name, contact])).sum(),
                        "name": name,
                        "role": role,
                        "contact": contact,
                        "schedule": schedule
                    }
                    data_manager.add_record("staff", new_staff)
                    auth.log_activity(f"Added new staff member: {name}")
                    st.success("Staff member added successfully!")
                else:
                    st.error("Please fill in required fields")
    
    # View/Manage staff
    st.subheader("Staff Records")
    
    staff_df = data_manager.load_data("staff")
    if not staff_df.empty:
        # Filter by role
        role_filter = st.selectbox("Filter by Role", 
                                 ["All"] + staff_df['role'].unique().tolist())
        
        filtered_df = staff_df if role_filter == "All" else staff_df[staff_df['role'] == role_filter]
        
        for _, staff in filtered_df.iterrows():
            with st.expander(f"{staff['name']} - {staff['role']}"):
                with st.form(f"edit_staff_{staff['id']}"):
                    edit_name = st.text_input("Name", staff['name'])
                    edit_role = st.selectbox("Role", 
                                           ["Doctor", "Nurse", "Receptionist", "Administrator", "Other"],
                                           index=["Doctor", "Nurse", "Receptionist", "Administrator", "Other"].index(staff['role']))
                    edit_contact = st.text_input("Contact", staff['contact'])
                    edit_schedule = st.text_area("Schedule", staff['schedule'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update"):
                            updated_staff = {
                                "id": staff['id'],
                                "name": edit_name,
                                "role": edit_role,
                                "contact": edit_contact,
                                "schedule": edit_schedule
                            }
                            data_manager.update_record("staff", staff['id'], updated_staff)
                            auth.log_activity(f"Updated staff member: {edit_name}")
                            st.success("Staff member updated successfully!")
                    
                    with col2:
                        if st.form_submit_button("Delete"):
                            data_manager.delete_record("staff", staff['id'])
                            auth.log_activity(f"Deleted staff member: {staff['name']}")
                            st.success("Staff member deleted successfully!")
                            st.rerun()
    else:
        st.info("No staff members registered")
