import importlib
import os
from typing import Optional, Tuple


class PromptManager:
    """Manages loading database-specific prompts."""
    
    def __init__(self):
        self.prompts_dir = "prompts"
        self.current_db = None
        self.sql_prompt = None
        self.summary_prompt = None
        self._load_default_prompts()
    
    def _load_default_prompts(self) -> None:
        """Load default prompts as fallback."""
        try:
            from prompts import default_prompt
            self.sql_prompt = default_prompt.SQL_PROMPT
            self.summary_prompt = default_prompt.SUMMARY_PROMPT
        except ImportError:
            # Hardcoded fallback if default_prompt doesn't exist
            self.sql_prompt = """You are an AI assistant that converts user questions into SQLite-compatible SQL.

Guidelines:
- Only return SELECT statements
- Do not include markdown formatting or explanations

{column_descriptions}

{context}

User Question: {user_question}

Generate only the SQL query:"""
            self.summary_prompt = """Summarize the following data for the user's question: "{user_question}"

{context}

Current result:
{data_preview}

Summary:"""
    
    @staticmethod
    def get_prompt_module_name(db_name: str) -> str:
        """Generate prompt module name from database name."""
        # Remove extension and create module name
        base_name = db_name.replace('.db', '').replace('.sqlite', '').replace('.sqlite3', '')
        return f"{base_name}_prompt"
    
    def load_prompts_for_db(self, db_name: str) -> Tuple[str, str]:
        """
        Load prompts specific to the given database.
        Falls back to default prompts if no specific prompt file exists.
        
        Args:
            db_name: Name of the database file (e.g., 'soil_pollution.db')
            
        Returns:
            Tuple of (sql_prompt, summary_prompt)
        """
        if db_name == self.current_db:
            return self.sql_prompt, self.summary_prompt
        
        module_name = self.get_prompt_module_name(db_name)
        
        try:
            # Try to import database-specific prompt module
            prompt_module = importlib.import_module(f"prompts.{module_name}")
            
            # Reload in case file was modified
            importlib.reload(prompt_module)
            
            self.sql_prompt = getattr(prompt_module, 'SQL_PROMPT', None)
            self.summary_prompt = getattr(prompt_module, 'SUMMARY_PROMPT', None)
            
            # Fall back to defaults if attributes missing
            if not self.sql_prompt or not self.summary_prompt:
                self._load_default_prompts()
            
            self.current_db = db_name
            
        except ImportError:
            # No specific prompt file, use defaults
            self._load_default_prompts()
            self.current_db = db_name
        
        return self.sql_prompt, self.summary_prompt
    
    def get_sql_prompt(self) -> str:
        """Get the current SQL prompt template."""
        return self.sql_prompt
    
    def get_summary_prompt(self) -> str:
        """Get the current summary prompt template."""
        return self.summary_prompt
    
    @staticmethod
    def get_available_prompt_files() -> list:
        """List all available prompt files."""
        prompts_dir = "prompts"
        if not os.path.exists(prompts_dir):
            return []
        
        prompt_files = []
        for file in os.listdir(prompts_dir):
            if file.endswith('_prompt.py') and file != 'default_prompt.py':
                prompt_files.append(file)
        return prompt_files
