import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.data_manager import DataManager
from utils.auth import Auth

data_manager = DataManager()
auth = Auth()

def render():
    st.title("Appointment Management")
    
    # Add new appointment
    with st.expander("Schedule New Appointment"):
        with st.form("add_appointment"):
            patients_df = data_manager.load_data("patients")
            staff_df = data_manager.load_data("staff")
            
            patient = st.selectbox("Patient", 
                                 patients_df['name'].tolist() if not patients_df.empty else ["No patients available"])
            date = st.date_input("Date", min_value=datetime.now().date())
            time = st.time_input("Time")
            doctor = st.selectbox("Doctor", 
                                staff_df[staff_df['role'] == 'Doctor']['name'].tolist() if not staff_df.empty else ["No doctors available"])
            
            if st.form_submit_button("Schedule Appointment"):
                if patient != "No patients available" and doctor != "No doctors available":
                    new_appointment = {
                        "id": pd.util.hash_pandas_object(pd.Series([patient, date, time])).sum(),
                        "patient_id": patients_df[patients_df['name'] == patient]['id'].iloc[0],
                        "date": date.strftime("%Y-%m-%d"),
                        "time": time.strftime("%H:%M"),
                        "doctor": doctor,
                        "status": "Scheduled"
                    }
                    data_manager.add_record("appointments", new_appointment)
                    auth.log_activity(f"Scheduled appointment for patient: {patient}")
                    st.success("Appointment scheduled successfully!")
                else:
                    st.error("Please ensure patients and doctors are available")
    
    # View/Manage appointments
    st.subheader("Appointment Schedule")
    
    appointments_df = data_manager.load_data("appointments")
    if not appointments_df.empty:
        appointments_df['date'] = pd.to_datetime(appointments_df['date'])
        appointments_df = appointments_df.sort_values('date')
        
        # Filter appointments
        filter_date = st.date_input("Filter by date", datetime.now().date())
        filtered_df = appointments_df[appointments_df['date'].dt.date == filter_date]
        
        if not filtered_df.empty:
            for _, appointment in filtered_df.iterrows():
                patient_name = patients_df[patients_df['id'] == appointment['patient_id']]['name'].iloc[0]
                with st.expander(f"Appointment: {patient_name} - {appointment['time']}"):
                    with st.form(f"edit_appointment_{appointment['id']}"):
                        status = st.selectbox("Status", 
                                            ["Scheduled", "Completed", "Cancelled"],
                                            index=["Scheduled", "Completed", "Cancelled"].index(appointment['status']))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Update Status"):
                                appointment['status'] = status
                                data_manager.update_record("appointments", appointment['id'], appointment)
                                auth.log_activity(f"Updated appointment status for patient: {patient_name}")
                                st.success("Appointment updated successfully!")
                        
                        with col2:
                            if st.form_submit_button("Cancel Appointment"):
                                data_manager.delete_record("appointments", appointment['id'])
                                auth.log_activity(f"Cancelled appointment for patient: {patient_name}")
                                st.success("Appointment cancelled successfully!")
                                st.rerun()
        else:
            st.info(f"No appointments scheduled for {filter_date}")
    else:
        st.info("No appointments scheduled")
