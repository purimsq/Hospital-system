import streamlit as st
from datetime import datetime
from database import get_db, Patient, AuditLog

# Initialize database session
db = next(get_db())

def log_patient_activity(user_id, action, details):
    new_log = AuditLog(
        user_id=user_id,
        action=action,
        details=details
    )
    db.add(new_log)
    db.commit()

def patient_registration():
    st.header("Patient Registration")
    
    with st.form("patient_registration"):
        name = st.text_input("Full Name")
        dob = st.date_input("Date of Birth")
        contact = st.text_input("Contact Number")
        address = st.text_area("Address")
        medical_history = st.text_area("Medical History")
        
        if st.form_submit_button("Register Patient"):
            if name and dob and contact:
                try:
                    new_patient = Patient(
                        name=name,
                        date_of_birth=dob,
                        contact_number=contact,
                        address=address,
                        medical_history=medical_history,
                        created_at=datetime.utcnow()
                    )
                    db.add(new_patient)
                    db.commit()
                    
                    log_patient_activity(
                        st.session_state.user_id,
                        "Patient Registration",
                        f"Registered new patient: {name}"
                    )
                    
                    st.success("Patient registered successfully!")
                except Exception as e:
                    st.error(f"Error registering patient: {str(e)}")
            else:
                st.error("Please fill in all required fields")

def view_patients():
    st.header("View Patients")
    
    patients = db.query(Patient).all()
    
    if not patients:
        st.info("No patients registered yet")
        return
        
    for patient in patients:
        with st.expander(f"Patient: {patient.name}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Personal Information**")
                st.write(f"Date of Birth: {patient.date_of_birth}")
                st.write(f"Contact: {patient.contact_number}")
                st.write(f"Address: {patient.address}")
            with col2:
                st.write("**Medical Information**")
                st.write(f"Medical History: {patient.medical_history}")
                st.write(f"Registration Date: {patient.created_at}")
            
            if st.button(f"Edit Patient #{patient.id}"):
                st.session_state.editing_patient = patient.id
                st.rerun()

def edit_patient(patient_id):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        st.error("Patient not found")
        return
        
    st.header(f"Edit Patient: {patient.name}")
    
    with st.form("edit_patient"):
        name = st.text_input("Full Name", value=patient.name)
        dob = st.date_input("Date of Birth", value=patient.date_of_birth)
        contact = st.text_input("Contact Number", value=patient.contact_number)
        address = st.text_area("Address", value=patient.address)
        medical_history = st.text_area("Medical History", value=patient.medical_history)
        
        if st.form_submit_button("Update Patient"):
            try:
                patient.name = name
                patient.date_of_birth = dob
                patient.contact_number = contact
                patient.address = address
                patient.medical_history = medical_history
                
                db.commit()
                
                log_patient_activity(
                    st.session_state.user_id,
                    "Patient Update",
                    f"Updated patient information: {name}"
                )
                
                st.success("Patient information updated successfully!")
                st.session_state.editing_patient = None
                st.rerun()
            except Exception as e:
                st.error(f"Error updating patient information: {str(e)}")

def main():
    if 'editing_patient' not in st.session_state:
        st.session_state.editing_patient = None

    # Tabs for different patient management functions
    tab1, tab2 = st.tabs(["Register New Patient", "View/Edit Patients"])
    
    with tab1:
        patient_registration()
    
    with tab2:
        if st.session_state.editing_patient:
            edit_patient(st.session_state.editing_patient)
        else:
            view_patients()

if __name__ == "__main__":
    main()
