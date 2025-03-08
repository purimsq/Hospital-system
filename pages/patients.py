import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.auth import Auth

data_manager = DataManager()
auth = Auth()

def render():
    st.title("Patient Management")
    
    # Add new patient
    with st.expander("Add New Patient"):
        with st.form("add_patient"):
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=0, max_value=120)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            contact = st.text_input("Contact")
            medical_history = st.text_area("Medical History")
            
            if st.form_submit_button("Add Patient"):
                if name and contact:
                    new_patient = {
                        "id": pd.util.hash_pandas_object(pd.Series([name, contact])).sum(),
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "contact": contact,
                        "medical_history": medical_history
                    }
                    data_manager.add_record("patients", new_patient)
                    auth.log_activity(f"Added new patient: {name}")
                    st.success("Patient added successfully!")
                else:
                    st.error("Please fill in required fields")
    
    # View/Edit patients
    st.subheader("Patient Records")
    patients_df = data_manager.load_data("patients")
    
    if not patients_df.empty:
        for _, patient in patients_df.iterrows():
            with st.expander(f"Patient: {patient['name']}"):
                with st.form(f"edit_patient_{patient['id']}"):
                    edit_name = st.text_input("Name", patient['name'])
                    edit_age = st.number_input("Age", min_value=0, max_value=120, value=int(patient['age']))
                    edit_gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                             index=["Male", "Female", "Other"].index(patient['gender']))
                    edit_contact = st.text_input("Contact", patient['contact'])
                    edit_history = st.text_area("Medical History", patient['medical_history'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update"):
                            updated_patient = {
                                "id": patient['id'],
                                "name": edit_name,
                                "age": edit_age,
                                "gender": edit_gender,
                                "contact": edit_contact,
                                "medical_history": edit_history
                            }
                            data_manager.update_record("patients", patient['id'], updated_patient)
                            auth.log_activity(f"Updated patient: {edit_name}")
                            st.success("Patient updated successfully!")
                    
                    with col2:
                        if st.form_submit_button("Delete"):
                            data_manager.delete_record("patients", patient['id'])
                            auth.log_activity(f"Deleted patient: {patient['name']}")
                            st.success("Patient deleted successfully!")
                            st.rerun()
    else:
        st.info("No patients registered yet")
