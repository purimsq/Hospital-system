import streamlit as st
import hashlib
import json
import os
from datetime import datetime

class Auth:
    def __init__(self):
        self.admin_file = "admin.json"
        self.audit_file = "audit_log.txt"
        
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def save_admin(self, username, password):
        admin_data = {
            "username": username,
            "password": self.hash_password(password)
        }
        with open(self.admin_file, "w") as f:
            json.dump(admin_data, f)
            
    def verify_admin(self, username, password):
        if not os.path.exists(self.admin_file):
            return False
        with open(self.admin_file, "r") as f:
            admin_data = json.load(f)
        return (admin_data["username"] == username and 
                admin_data["password"] == self.hash_password(password))
    
    def log_activity(self, activity):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        username = st.session_state.get("username", "Unknown")
        log_entry = f"[{timestamp}] {username}: {activity}\n"
        with open(self.audit_file, "a") as f:
            f.write(log_entry)
            
    def admin_exists(self):
        return os.path.exists(self.admin_file)
