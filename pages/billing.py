import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_manager import DataManager
from utils.auth import Auth

data_manager = DataManager()
auth = Auth()

def render():
    st.title("Billing Management")

    # Load required data
    patients_df = data_manager.load_data("patients")

    if patients_df.empty:
        st.warning("⚠️ No patients registered in the system. Please add patients before creating bills.")
        if st.button("Go to Patient Management"):
            st.session_state.current_page = "Patients"
            st.rerun()
        return

    # Create new bill
    with st.expander("Create New Bill"):
        with st.form("create_bill"):
            patient = st.selectbox("Patient", 
                               patients_df['name'].tolist())
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            status = st.selectbox("Status", ["Pending", "Paid", "Overdue"])

            if st.form_submit_button("Create Bill"):
                if amount > 0:
                    new_bill = {
                        "id": pd.util.hash_pandas_object(pd.Series([patient, datetime.now()])).sum(),
                        "patient_id": patients_df[patients_df['name'] == patient]['id'].iloc[0],
                        "amount": amount,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "status": status
                    }
                    data_manager.add_record("billing", new_bill)
                    auth.log_activity(f"Created new bill for patient: {patient}")
                    st.success("Bill created successfully!")
                else:
                    st.error("Please enter a valid amount")

    # View/Manage bills
    st.subheader("Billing Records")

    billing_df = data_manager.load_data("billing")
    if not billing_df.empty:
        # Filter by status
        status_filter = st.selectbox("Filter by Status", 
                                 ["All"] + billing_df['status'].unique().tolist())

        filtered_df = billing_df if status_filter == "All" else billing_df[billing_df['status'] == status_filter]

        for _, bill in filtered_df.iterrows():
            patient_name = patients_df[patients_df['id'] == bill['patient_id']]['name'].iloc[0]
            with st.expander(f"Bill: {patient_name} - ${bill['amount']} ({bill['status']})"):
                with st.form(f"edit_bill_{bill['id']}"):
                    edit_amount = st.number_input("Amount", 
                                              min_value=0.0, 
                                              value=float(bill['amount']), 
                                              format="%.2f")
                    edit_status = st.selectbox("Status", 
                                           ["Pending", "Paid", "Overdue"],
                                           index=["Pending", "Paid", "Overdue"].index(bill['status']))

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update"):
                            bill['amount'] = edit_amount
                            bill['status'] = edit_status
                            data_manager.update_record("billing", bill['id'], bill)
                            auth.log_activity(f"Updated bill for patient: {patient_name}")
                            st.success("Bill updated successfully!")

                    with col2:
                        if st.form_submit_button("Delete"):
                            data_manager.delete_record("billing", bill['id'])
                            auth.log_activity(f"Deleted bill for patient: {patient_name}")
                            st.success("Bill deleted successfully!")
                            st.rerun()
    else:
        st.info("No billing records found. Create a new bill using the form above.")