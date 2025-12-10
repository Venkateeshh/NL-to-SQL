import os
import streamlit as st
from typing import List, Dict, Optional
from create_db import create_db_from_csv

class CustomDatabase:
    """Lets user upload and manage a custom SQLite database."""
    
    def __init__(self, upload_dir: str = "inputs"):
        self.upload_dir = upload_dir
        self.db_path = "./db"
        os.makedirs(self.upload_dir, exist_ok=True)
        self.db_path: Optional[str] = None
    
    def upload_database(self, uploaded_file) -> Optional[str]:
        """Handle database file upload and save it to the upload directory."""
        if uploaded_file is not None:
            file_path = os.path.join(self.upload_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            self.db_path = file_path
            st.success(f"Database uploaded to: {file_path}")
            return file_path
        else:
            st.error("No file uploaded.")
            return None
        
    def create_database(self, uploaded_csv, db_name: str, table_name: str) -> str:
        """Create a new SQLite database from an uploaded CSV file."""
        # Save the uploaded CSV file first
        if uploaded_csv is not None:
            csv_path = os.path.join(self.upload_dir, uploaded_csv.name)
            with open(csv_path, "wb") as f:
                f.write(uploaded_csv.getbuffer())
            
            # Create database from the saved CSV
            create_db_from_csv(csv_path, db_name, table_name)
            db_path = os.path.join("db", f"{db_name}.db")
            self.db_path = db_path
            st.success(f"New database created at: {db_path}")
            return db_path
        else:
            st.error("No CSV file uploaded.")
            return None