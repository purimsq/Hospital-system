import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_manager import DataManager
from utils.auth import Auth

data_manager = DataManager()
auth = Auth()

def render():
    st.title("Reports and Analytics")
    
    # Load all required data
    patients_df = data_manager.load_data("patients")
    appointments_df = data_manager.load_data("appointments")
    inventory_df = data_manager.load_data("inventory")
    billing_df = data_manager.load_data("billing")
    staff_df = data_manager.load_data("staff")

    # Report selection
    report_type = st.selectbox(
        "Select Report Type",
        ["Patient Demographics", "Appointment Analytics", "Financial Reports", "Inventory Status", "Staff Overview"]
    )

    if report_type == "Patient Demographics":
        st.subheader("Patient Demographics Analysis")
        
        if not patients_df.empty:
            # Age distribution
            fig_age = px.histogram(
                patients_df,
                x="age",
                title="Age Distribution",
                labels={"age": "Age", "count": "Number of Patients"},
                nbins=20,
                color_discrete_sequence=['#F5F5DC']
            )
            st.plotly_chart(fig_age)

            # Gender distribution
            gender_counts = patients_df['gender'].value_counts()
            fig_gender = px.pie(
                values=gender_counts.values,
                names=gender_counts.index,
                title="Gender Distribution",
                color_discrete_sequence=['#F5F5DC', '#F0EAD6', '#DEB887']
            )
            st.plotly_chart(fig_gender)
        else:
            st.info("No patient data available for analysis")

    elif report_type == "Appointment Analytics":
        st.subheader("Appointment Analytics")
        
        if not appointments_df.empty:
            # Convert date to datetime
            appointments_df['date'] = pd.to_datetime(appointments_df['date'])
            
            # Appointments by date
            daily_appointments = appointments_df.groupby('date').size().reset_index(name='count')
            fig_appointments = px.line(
                daily_appointments,
                x="date",
                y="count",
                title="Daily Appointment Trends",
                labels={"date": "Date", "count": "Number of Appointments"},
                color_discrete_sequence=['#F5F5DC']
            )
            st.plotly_chart(fig_appointments)

            # Appointment status distribution
            status_counts = appointments_df['status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Appointment Status Distribution",
                color_discrete_sequence=['#F5F5DC', '#F0EAD6', '#DEB887']
            )
            st.plotly_chart(fig_status)
        else:
            st.info("No appointment data available for analysis")

    elif report_type == "Financial Reports":
        st.subheader("Financial Analysis")
        
        if not billing_df.empty:
            # Convert date to datetime
            billing_df['date'] = pd.to_datetime(billing_df['date'])
            
            # Total revenue by date
            daily_revenue = billing_df.groupby('date')['amount'].sum().reset_index()
            fig_revenue = px.line(
                daily_revenue,
                x="date",
                y="amount",
                title="Daily Revenue",
                labels={"date": "Date", "amount": "Revenue ($)"},
                color_discrete_sequence=['#F5F5DC']
            )
            st.plotly_chart(fig_revenue)

            # Payment status distribution
            payment_status = billing_df['status'].value_counts()
            fig_payment = px.pie(
                values=payment_status.values,
                names=payment_status.index,
                title="Payment Status Distribution",
                color_discrete_sequence=['#F5F5DC', '#F0EAD6', '#DEB887']
            )
            st.plotly_chart(fig_payment)

            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Revenue", f"${billing_df['amount'].sum():,.2f}")
            with col2:
                pending_amount = billing_df[billing_df['status'] == 'Pending']['amount'].sum()
                st.metric("Pending Payments", f"${pending_amount:,.2f}")
            with col3:
                overdue_amount = billing_df[billing_df['status'] == 'Overdue']['amount'].sum()
                st.metric("Overdue Payments", f"${overdue_amount:,.2f}")
        else:
            st.info("No billing data available for analysis")

    elif report_type == "Inventory Status":
        st.subheader("Inventory Analysis")
        
        if not inventory_df.empty:
            # Items by category
            category_counts = inventory_df.groupby('category')['quantity'].sum().reset_index()
            fig_category = px.bar(
                category_counts,
                x="category",
                y="quantity",
                title="Inventory by Category",
                labels={"category": "Category", "quantity": "Total Quantity"},
                color_discrete_sequence=['#F5F5DC']
            )
            st.plotly_chart(fig_category)

            # Low stock items
            st.subheader("Low Stock Items (Quantity < 10)")
            low_stock = inventory_df[inventory_df['quantity'] < 10]
            if not low_stock.empty:
                fig_low_stock = px.bar(
                    low_stock,
                    x="item",
                    y="quantity",
                    title="Low Stock Items",
                    labels={"item": "Item", "quantity": "Quantity"},
                    color_discrete_sequence=['#DEB887']
                )
                st.plotly_chart(fig_low_stock)
            else:
                st.info("No items are currently low in stock")
        else:
            st.info("No inventory data available for analysis")

    elif report_type == "Staff Overview":
        st.subheader("Staff Analysis")
        
        if not staff_df.empty:
            # Staff distribution by role
            role_counts = staff_df['role'].value_counts()
            fig_roles = px.pie(
                values=role_counts.values,
                names=role_counts.index,
                title="Staff Distribution by Role",
                color_discrete_sequence=['#F5F5DC', '#F0EAD6', '#DEB887', '#D2B48C']
            )
            st.plotly_chart(fig_roles)

            # Staff list by role
            for role in staff_df['role'].unique():
                with st.expander(f"{role}s"):
                    role_staff = staff_df[staff_df['role'] == role]
                    st.dataframe(role_staff[['name', 'contact', 'schedule']])
        else:
            st.info("No staff data available for analysis")

    # Export reports
    st.subheader("Export Reports")
    export_type = st.selectbox("Select report to export", 
                              ["Patient List", "Appointment Schedule", "Financial Summary", "Inventory Status"])
    
    if st.button("Generate Report"):
        if export_type == "Patient List":
            data = patients_df
        elif export_type == "Appointment Schedule":
            data = appointments_df
        elif export_type == "Financial Summary":
            data = billing_df
        else:
            data = inventory_df
            
        # Convert DataFrame to CSV string
        csv = data.to_csv(index=False)
        
        # Create download button
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{export_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        auth.log_activity(f"Generated {export_type} report")
        st.success(f"{export_type} report generated successfully!")
