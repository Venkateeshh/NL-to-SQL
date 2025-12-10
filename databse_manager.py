import os
import sqlite3
import streamlit as st
from typing import List, Dict, Optional


class DatabaseManager:
    """Manages SQLite database operations."""
    
    def __init__(self, db_path: str = "db/soil_pollution.db"):
        self.db_path = db_path
        self.db_dir = "db"
        self._ensure_db_exists()
    
    def _ensure_db_exists(self) -> None:
        """Ensure database directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create sample table if database doesn't exist
        if not os.path.exists(self.db_path):
            self._create_sample_database()
    
    def get_available_databases(self) -> List[str]:
        """Get list of available database files in the db directory."""
        if not os.path.exists(self.db_dir):
            return []
        
        db_files = []
        for file in os.listdir(self.db_dir):
            if file.endswith(('.db', '.sqlite', '.sqlite3')):
                db_files.append(file)
        return sorted(db_files)
    
    def switch_database(self, db_name: str) -> bool:
        """Switch to a different database."""
        new_path = os.path.join(self.db_dir, db_name)
        if os.path.exists(new_path):
            self.db_path = new_path
            return True
        return False
    
    
    def execute_query(self, sql_query: str) -> Optional[List[Dict]]:
        """Execute SQL query and return results as list of dictionaries."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            result = [dict(row) for row in rows]
            return result
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            return None
    
    def get_schema(self) -> Optional[Dict]:
        """Get database schema information to assist in SQL query generation."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            schema = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                schema[table_name] = [
                    {
                        "name": col[1],
                        "datatype": col[2],
                        "description": f"{col[1]} column"
                    }
                    for col in columns
                ]
            
            conn.close()
            return schema
        except sqlite3.Error as e:
            st.error(f"Error retrieving schema: {e}")
            return None