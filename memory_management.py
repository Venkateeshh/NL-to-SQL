import json
import os
import streamlit as st
from datetime import datetime
from typing import List, Dict


class MemoryManager:
    """Manages conversation memory and uses it as context for generating SQL queries."""
    
    def __init__(self, memory_file: str = "memory.json"):
        self.memory_file = memory_file
        self.memory = self._load()
    
    def _load(self) -> List[Dict]:
        """Load memory from JSON file."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return []
        return []
    
    def save(self) -> None:
        """Save memory to JSON file."""
        try:
            with open(self.memory_file, "w") as file:
                json.dump(self.memory, file, indent=2)
        except IOError as e:
            st.error(f"Error saving memory: {e}")
    
    def add(self, question: str, sql: str, result: List, summary: str) -> None:
        """Add a new interaction to memory."""
        self.memory.append({
            "question": question,
            "sql": sql,
            "result": result,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        })
        self.save()
    
    def get_recent_context(self, n: int = 3) -> str:
        """Get formatted context from recent interactions."""
        if not self.memory:
            return ""
        
        context = ""
        for turn in self.memory[-n:]:
            context += f"Previous question: '{turn['question']}'\n"
            context += f"Generated SQL: {turn['sql']}\n"
            if 'summary' in turn:
                context += f"Summary: {turn['summary']}\n"
            context += "\n"
        return context
    
    def clear(self) -> None:
        """Clear all memory."""
        self.memory = []
        self.save()