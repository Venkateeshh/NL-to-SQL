import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
from typing import List, Dict, Optional


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

class GeminiAssistant:
    """Handles Gemini AI interactions such as SQL generation and result summarization."""
    if not api_key:
            st.error("⚠️ Please configure your GOOGLE_API_KEY in the .env file")
            
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
    
    def build_sql_prompt(self, schema: Dict, user_question: str, context: str = "") -> str:
        """
            Build prompt for SQL generation.
            Args:
                schema (Dict): Database schema information.
                user_question (str): User's natural language question.
                context (str): Recent interaction context.
            Returns:
                str: Formatted prompt for Gemini AI.
        """
        
        # Build column descriptions
        column_descriptions = ""
        for table_name, columns in schema.items():
            column_descriptions += f"\nTable: {table_name}\nColumns:\n"
            for col in columns:
                column_descriptions += f"- {col['name']} ({col['datatype']}): {col['description']}\n"
        
        prompt = f"""
            You are an AI assistant that converts user questions into SQLite-compatible SQL.
            You work with environmental data about soil pollution and its impact on human health.

            Guidelines:
            - For string filtering, use LOWER(TRIM(column)) LIKE '%value%' for case-insensitive partial matches
            - Use AVG only when explicitly asked for averages
            - Use MAX for highest values, MIN for lowest values
            - Use COUNT, SUM for totals and aggregations
            - Use GROUP BY when aggregating data
            - Use ORDER BY for ranking queries
            - Use EXTRACT or strftime for date filtering
            - Normalize country names (e.g., "United States" → "usa")
            - Only return SELECT statements
            - Do not include markdown formatting or explanations

            {column_descriptions}

            {context}

            User Question: {user_question}

            Generate only the SQL query:"""
        
        return prompt.strip()
    
    def generate_sql(self, prompt: str) -> Optional[str]:
        """
        Generate SQL query from prompt.
        Args:
            prompt (str): Prompt for SQL generation.
        Returns:
            Optional[str]: Generated SQL query or None if error occurs.
        """
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            sql = response.text.strip()
            
            # Clean up markdown formatting
            if sql.startswith("```"):
                sql = sql.strip("```").replace("sql", "").strip()
            
            return sql
        except Exception as e:
            st.error(f"Error generating SQL: {e}")
            return None
    
    def generate_summary(self, user_question: str, result: List[Dict], context: str = "") -> str:
        """Generate natural language summary of results."""
        if not result:
            return "No data available for this question."
        
        try:
            model = genai.GenerativeModel(self.model_name)
            
            # Limit result preview
            preview_rows = result[:10]
            data_preview = "\n".join([json.dumps(row) for row in preview_rows])
            
            prompt = f"""
                You are a helpful assistant analyzing environmental data about soil pollution.
                User asked: "{user_question}"

                Based on the following query result and previous interactions, write a user-friendly summary.
                If a similar result is already available in memory, summarize that instead.

                {context}

                Current result:
                {data_preview}
                
                Summary:"""
            
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            st.error(f"Error generating summary: {e}")
            return "Unable to generate summary."
