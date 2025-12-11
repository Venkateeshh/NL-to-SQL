import google.generativeai as genai
import os
import streamlit as st
from dotenv import load_dotenv
from typing import Optional


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)


class QueryExplainer:
    """Generates explanations for SQL queries using Gemini AI."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
    
    def explain_query(self, sql_query: str) -> Optional[str]:
        """
        Generate a plain English explanation of an SQL query.
        
        Args:
            sql_query: The SQL query to explain
            
        Returns:
            A human-readable explanation of the query
        """
        if not sql_query:
            return "No query to explain."
        
        try:
            model = genai.GenerativeModel(self.model_name)
            
            prompt = f"""You are a helpful assistant that explains SQL queries in plain English.
Explain the following SQL query in simple, easy-to-understand terms.
Break down what each part of the query does and what the overall result will be.
Use bullet points for clarity.

SQL Query:
```sql
{sql_query}
```

Explanation:"""
            
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            st.error(f"Error explaining query: {e}")
            return "Unable to generate explanation."