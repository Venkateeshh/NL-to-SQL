# 🔍 NL-SQL: Natural Language to SQL Query System

A Streamlit-based application that converts natural language questions into SQL queries using Google's Gemini AI. The system supports **multiple databases** with database-specific prompts and memory management.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [File Descriptions](#file-descriptions)
- [How It Works](#how-it-works)
- [Adding New Databases](#adding-new-databases)

## ✨ Features

- **Natural Language Queries**: Ask questions in plain English and get SQL queries automatically generated
- **AI-Powered**: Uses Google Gemini AI for intelligent SQL generation and result summarization
- **Multi-Database Support**: Switch between multiple databases seamlessly
- **Database-Specific Prompts**: Custom AI prompts tailored for each database type
- **Database-Specific Memory**: Separate conversation history for each database
- **SQL Validation**: Multi-layer SQL validation including safety checks, semantic validation, and execution verification
- **Conversation Memory**: Maintains context from previous interactions for more accurate query generation
- **Interactive UI**: Clean Streamlit interface with real-time results and data visualization
- **Database Management**: Upload SQLite databases or create new ones from CSV files
- **Export Results**: Download query results as CSV files

## 📁 Project Structure

```
NL-SQL/
├── main.py                 # Main Streamlit application
├── create_db.py            # Database creation utility
├── custom_db.py            # Custom database upload/creation handler
├── databse_manager.py      # Database operations manager
├── gemini_class.py         # Gemini AI integration
├── memory_management.py    # Conversation memory handler
├── prompt_manager.py       # Database-specific prompt loader
├── sql_validation.py       # SQL query validation
├── pyproject.toml          # Project dependencies
├── README.md               # This file
├── db/                     # SQLite database directory
│   ├── soil_pollution.db   # Soil pollution database
│   └── air_pollution.db    # Air pollution database
├── inputs/                 # Input CSV files
│   ├── global_air_pollution_dataset.csv
│   └── soil_pollution_diseases.csv
├── memory/                 # Database-specific memory files
│   ├── soil_pollution_memory.json
│   └── air_pollution_memory.json
└── prompts/                # Database-specific prompt templates
    ├── __init__.py
    ├── default_prompt.py   # Default/fallback prompts
    ├── soil_pollution_prompt.py
    └── air_pollution_prompt.py
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

3. **Select a database** from the dropdown menu

4. **Ask questions** in natural language, for example:
   - "Show me the top 10 records"
   - "What is the average value by category?"
   - "List all unique countries in the dataset"

5. **Manage databases** via the sidebar:
   - Upload existing SQLite databases
   - Create new databases from CSV files

## 📄 File Descriptions

### `main.py`
The main entry point for the Streamlit application. It:
- Sets up the web interface with custom styling
- Initializes session state for database, memory, and AI assistant
- Handles database switching and syncs memory/prompts accordingly
- Handles user input and displays query results
- Manages query history and provides CSV export functionality

### `create_db.py`
A utility function to create SQLite databases from CSV files:
- Creates the `db/` directory if it doesn't exist
- Reads CSV data and creates tables with appropriate columns
- Imports all rows from the CSV file

### `custom_db.py`
Handles custom database operations through the `CustomDatabase` class:
- `upload_database()`: Upload existing SQLite database files
- `create_database()`: Create new databases from uploaded CSV files

### `databse_manager.py`
Manages all SQLite database operations through the `DatabaseManager` class:
- `execute_query()`: Executes SQL queries and returns results as dictionaries
- `get_schema()`: Retrieves database schema information for AI context
- `get_available_databases()`: Lists all available database files
- `switch_database()`: Switches to a different database

### `gemini_class.py`
Handles Google Gemini AI integration through the `GeminiAssistant` class:
- `set_database()`: Loads appropriate prompts for the selected database
- `build_sql_prompt()`: Constructs prompts with schema context and guidelines
- `generate_sql()`: Converts natural language to SQL queries
- `generate_summary()`: Creates human-readable summaries of query results

### `prompt_manager.py`
Manages database-specific prompts through the `PromptManager` class:
- `load_prompts_for_db()`: Loads prompts specific to a database
- `get_sql_prompt()`: Returns the SQL generation prompt template
- `get_summary_prompt()`: Returns the summary generation prompt template
- Falls back to default prompts if no specific prompt file exists

### `memory_management.py`
Manages conversation context through the `MemoryManager` class:
- `add()`: Stores new interactions (question, SQL, result, summary)
- `get_recent_context()`: Retrieves recent interactions for AI context
- `switch_memory_file()`: Switches to memory file for a different database
- `clear()`: Clears all stored memory for the current database
- Each database has its own memory file in the `memory/` directory

### `sql_validation.py`
Provides SQL security and validation through the `SQLValidator` class:
- `safety_check()`: Blocks DDL/DML operations (DROP, DELETE, INSERT, etc.)
- `semantic_check()`: Validates tables and columns against the database schema
- `execution_check()`: Tests query execution in a safe environment

### `prompts/` Directory
Contains database-specific prompt templates:
- `default_prompt.py`: Generic prompts used as fallback
- `soil_pollution_prompt.py`: Prompts tailored for soil pollution data
- `air_pollution_prompt.py`: Prompts tailored for air quality data
- Each file exports `SQL_PROMPT` and `SUMMARY_PROMPT` templates

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

## ➕ Adding New Databases

### Adding a Database File

1. **Option A: Upload via UI**
   - Go to the sidebar → Database Management
   - Select "Upload SQLite Database"
   - Upload your `.db`, `.sqlite`, or `.sqlite3` file

2. **Option B: Create from CSV**
   - Go to the sidebar → Database Management
   - Select "Create Database from CSV"
   - Upload your CSV file and specify database/table names

3. **Option C: Manual placement**
   - Place your SQLite database file in the `db/` directory
   - Restart the application

### Adding Custom Prompts (Optional)

To add database-specific prompts for better AI responses:

1. Create a new file in `prompts/` named `<database_name>_prompt.py`
   - For `my_data.db`, create `prompts/my_data_prompt.py`

2. Add two template variables:
   ```python
   SQL_PROMPT = """Your custom SQL generation prompt here...
   
   {column_descriptions}
   {context}
   User Question: {user_question}
   
   Generate only the SQL query:"""

   SUMMARY_PROMPT = """Your custom summary prompt here...
   
   User asked: "{user_question}"
   {context}
   Current result:
   {data_preview}
   
   Summary:"""
   ```

3. The system will automatically use these prompts when the database is selected

## 📝 License

This project is open source. See the LICENSE file for details.
