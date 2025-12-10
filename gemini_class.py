import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
from typing import List, Dict, Optional
from prompt_manager import PromptManager


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
        self.prompt_manager = PromptManager()
        self.current_db = None
    
    def set_database(self, db_name: str) -> None:
        """Set the current database and load appropriate prompts."""
        if db_name != self.current_db:
            self.prompt_manager.load_prompts_for_db(db_name)
            self.current_db = db_name
    
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
        
        # Get the SQL prompt template from prompt manager
        sql_template = self.prompt_manager.get_sql_prompt()
        
        # Format the prompt with the actual values
        prompt = sql_template.format(
            column_descriptions=column_descriptions,
            context=context,
            user_question=user_question
        )
        
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
            
            # Get the summary prompt template from prompt manager
            summary_template = self.prompt_manager.get_summary_prompt()
            
            # Format the prompt with the actual values
            prompt = summary_template.format(
                user_question=user_question,
                context=context,
                data_preview=data_preview
            )
            
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            st.error(f"Error generating summary: {e}")
            return "Unable to generate summary."
