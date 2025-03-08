import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.data_dir = "data"
        self.initialize_data_files()
        
    def initialize_data_files(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        files = {
            "patients": ["id", "name", "age", "gender", "contact", "medical_history"],
            "appointments": ["id", "patient_id", "date", "time", "doctor", "status"],
            "inventory": ["id", "item", "quantity", "category", "last_updated"],
            "staff": ["id", "name", "role", "contact", "schedule"],
            "billing": ["id", "patient_id", "amount", "date", "status"]
        }
        
        for file, columns in files.items():
            filepath = f"{self.data_dir}/{file}.csv"
            if not os.path.exists(filepath):
                df = pd.DataFrame(columns=columns)
                df.to_csv(filepath, index=False)
                
    def load_data(self, file):
        return pd.read_csv(f"{self.data_dir}/{file}.csv")
    
    def save_data(self, file, data):
        data.to_csv(f"{self.data_dir}/{file}.csv", index=False)
        
    def add_record(self, file, record):
        df = self.load_data(file)
        df = df.append(record, ignore_index=True)
        self.save_data(file, df)
        
    def update_record(self, file, record_id, record):
        df = self.load_data(file)
        df.loc[df['id'] == record_id] = record
        self.save_data(file, df)
        
    def delete_record(self, file, record_id):
        df = self.load_data(file)
        df = df[df['id'] != record_id]
        self.save_data(file, df)
