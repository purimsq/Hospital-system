import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_manager import DataManager
from utils.auth import Auth

data_manager = DataManager()
auth = Auth()

def render():
    st.title("Inventory Management")
    
    # Add new item
    with st.expander("Add New Item"):
        with st.form("add_item"):
            item = st.text_input("Item Name")
            quantity = st.number_input("Quantity", min_value=0)
            category = st.selectbox("Category", 
                                  ["Medicines", "Equipment", "Supplies", "Other"])
            
            if st.form_submit_button("Add Item"):
                if item and quantity >= 0:
                    new_item = {
                        "id": pd.util.hash_pandas_object(pd.Series([item, category])).sum(),
                        "item": item,
                        "quantity": quantity,
                        "category": category,
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    data_manager.add_record("inventory", new_item)
                    auth.log_activity(f"Added new inventory item: {item}")
                    st.success("Item added successfully!")
                else:
                    st.error("Please fill in all fields correctly")
    
    # View/Manage inventory
    st.subheader("Current Inventory")
    
    inventory_df = data_manager.load_data("inventory")
    if not inventory_df.empty:
        # Filter by category
        category_filter = st.selectbox("Filter by Category", 
                                     ["All"] + inventory_df['category'].unique().tolist())
        
        filtered_df = inventory_df if category_filter == "All" else inventory_df[inventory_df['category'] == category_filter]
        
        for _, item in filtered_df.iterrows():
            with st.expander(f"{item['item']} - {item['quantity']} units"):
                with st.form(f"edit_item_{item['id']}"):
                    edit_quantity = st.number_input("Update Quantity", 
                                                  min_value=0, 
                                                  value=int(item['quantity']))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update"):
                            item['quantity'] = edit_quantity
                            item['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            data_manager.update_record("inventory", item['id'], item)
                            auth.log_activity(f"Updated inventory item: {item['item']}")
                            st.success("Item updated successfully!")
                    
                    with col2:
                        if st.form_submit_button("Delete"):
                            data_manager.delete_record("inventory", item['id'])
                            auth.log_activity(f"Deleted inventory item: {item['item']}")
                            st.success("Item deleted successfully!")
                            st.rerun()
                
                # Low stock warning
                if item['quantity'] < 10:
                    st.warning("⚠️ Low stock alert!")
    else:
        st.info("No items in inventory")
