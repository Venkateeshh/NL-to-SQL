# 🌱 NL-SQL: Natural Language to SQL Query System

A Streamlit-based application that converts natural language questions into SQL queries using Google's Gemini AI. The system is designed to query environmental data about soil pollution and its impact on human health.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [File Descriptions](#file-descriptions)
- [How It Works](#how-it-works)

## ✨ Features

- **Natural Language Queries**: Ask questions in plain English and get SQL queries automatically generated
- **AI-Powered**: Uses Google Gemini AI for intelligent SQL generation and result summarization
- **SQL Validation**: Multi-layer SQL validation including safety checks, semantic validation, and execution verification
- **Conversation Memory**: Maintains context from previous interactions for more accurate query generation
- **Interactive UI**: Clean Streamlit interface with real-time results and data visualization
- **Export Results**: Download query results as CSV files

## 📁 Project Structure

```
NL-SQL/
├── main.py                 # Main Streamlit application
├── create_db.py            # Database creation script
├── databse_manager.py      # Database operations manager
├── gemini_class.py         # Gemini AI integration
├── memory_management.py    # Conversation memory handler
├── sql_validation.py       # SQL query validation
├── memory.json             # Persistent memory storage
├── pyproject.toml          # Project dependencies
├── README.md               # This file
├── db/                     # SQLite database directory
│   └── soil_pollution.db   # SQLite database file
└── inputs/                 # Input CSV files
    ├── global_air_pollution_dataset.csv
    └── soil_pollution_diseases.csv
```

## 📦 Prerequisites

- Python 3.12 or higher
- Google Gemini API key

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NL-SQL
   ```

2. **Install dependencies using pip**
   ```bash
   pip install -r requirements.txt
   ```

   Or using `uv` (recommended):
   ```bash
   uv sync
   ```

3. **Create the database**
   ```bash
   python create_db.py
   ```

## ⚙️ Configuration

1. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

2. **Get a Gemini API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key
   - Copy the key to your `.env` file

## 🎯 Usage

1. **Start the application**
   ```bash
   streamlit run main.py
   ```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Ask questions** in natural language, for example:
   - "What are the highest lead concentrations by country?"
   - "Show me the top 10 regions with the most soil pollution"
   - "What diseases are linked to cadmium exposure?"

## 📄 File Descriptions

### `main.py`
The main entry point for the Streamlit application. It:
- Sets up the web interface with custom styling
- Initializes session state for database, memory, and AI assistant
- Handles user input and displays query results
- Manages query history and provides CSV export functionality

### `create_db.py`
A utility script to initialize the SQLite database:
- Creates the `db/` directory if it doesn't exist
- Reads CSV data from `inputs/soil_pollution_diseases.csv`
- Creates the `soil_pollution_diseases` table with appropriate columns
- Imports all rows from the CSV file

### `databse_manager.py`
Manages all SQLite database operations through the `DatabaseManager` class:
- `execute_query()`: Executes SQL queries and returns results as dictionaries
- `get_schema()`: Retrieves database schema information for AI context

### `gemini_class.py`
Handles Google Gemini AI integration through the `GeminiAssistant` class:
- `build_sql_prompt()`: Constructs prompts with schema context and guidelines
- `generate_sql()`: Converts natural language to SQL queries
- `generate_summary()`: Creates human-readable summaries of query results

### `memory_management.py`
Manages conversation context through the `MemoryManager` class:
- `add()`: Stores new interactions (question, SQL, result, summary)
- `get_recent_context()`: Retrieves recent interactions for AI context
- `clear()`: Clears all stored memory
- Persists data to `memory.json` for session continuity

### `sql_validation.py`
Provides SQL security and validation through the `SQLValidator` class:
- `safety_check()`: Blocks DDL/DML operations (DROP, DELETE, INSERT, etc.)
- `semantic_check()`: Validates tables and columns against the database schema
- `execution_check()`: Tests query execution in a safe environment

### `memory.json`
JSON file storing conversation history with:
- User questions
- Generated SQL queries
- Query results
- AI-generated summaries
- Timestamps

### `pyproject.toml`
Project configuration and dependencies:
- `google-generativeai`: Google Gemini AI SDK
- `python-dotenv`: Environment variable management
- `sqlalchemy`: SQL toolkit for Python
- `sqlglot`: SQL parser for validation
- `streamlit`: Web application framework

## 🔄 How It Works

1. **User Input**: User enters a natural language question in the Streamlit interface

2. **Context Building**: The system retrieves:
   - Database schema (tables, columns, data types)
   - Recent conversation history for context

3. **SQL Generation**: Gemini AI generates an SQLite-compatible query based on:
   - The user's question
   - Database schema
   - Previous interactions

4. **Validation**: The generated SQL passes through multiple validation layers:
   - Safety check (blocks harmful operations)
   - Semantic check (validates tables/columns exist)
   - Execution check (ensures query runs successfully)

5. **Execution**: The validated query is executed against the SQLite database

6. **Summary**: Gemini AI generates a natural language summary of the results

7. **Memory Storage**: The interaction is saved for future context

## 🛡️ Security Features

- **Read-Only Queries**: Only SELECT statements are allowed
- **DDL/DML Blocking**: DROP, DELETE, INSERT, UPDATE, CREATE, ALTER operations are blocked
- **Schema Validation**: Queries are validated against actual database schema
- **SQL Injection Prevention**: Uses parameterized queries and AST parsing

## 📝 License

This project is open source. See the LICENSE file for details.
