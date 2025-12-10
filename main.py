import pandas as pd
import streamlit as st
from custom_db import CustomDatabase
from databse_manager import DatabaseManager
from datetime import datetime
from gemini_class import GeminiAssistant
from memory_management import MemoryManager
from sql_validation import SQLValidator

st.set_page_config(
    page_title="NL-SQL Query System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'memory_manager' not in st.session_state:
        st.session_state.memory_manager = MemoryManager()
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    if 'assistant' not in st.session_state:
        st.session_state.assistant = GeminiAssistant()
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'custom_db' not in st.session_state:
        st.session_state.custom_db = CustomDatabase()
    if 'selected_db' not in st.session_state:
        st.session_state.selected_db = 'soil_pollution.db'


def main():
    """Main Streamlit application."""
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1976D2;
            text-align: center;
            margin-bottom: 1rem;
        }
        .stButton>button {
            width: 100%;
        }
        .success-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #E3F2FD;
            border-left: 5px solid #1976D2;
        }
        .db-badge {
            background-color: #E3F2FD;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.875rem;
            color: #1976D2;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize
    initialize_session_state()
    
    # Ensure db_manager is using the selected database
    if st.session_state.db_manager.db_path != f"db/{st.session_state.selected_db}":
        st.session_state.db_manager.switch_database(st.session_state.selected_db)
    
    # Ensure memory_manager is using the correct memory file for selected database
    expected_memory_file = MemoryManager.get_memory_file_for_db(st.session_state.selected_db)
    if st.session_state.memory_manager.memory_file != expected_memory_file:
        st.session_state.memory_manager.switch_memory_file(st.session_state.selected_db)
    
    # Ensure assistant is using the correct prompts for selected database
    st.session_state.assistant.set_database(st.session_state.selected_db)
    
    # Generate dynamic title from selected database
    db_display_name = st.session_state.selected_db.replace('.db', '').replace('_', ' ').title()
    
    # Header
    st.markdown('<h1 class="main-header">🔍 NL-SQL Query System</h1>', unsafe_allow_html=True)
    st.markdown(f"### Ask questions about your data in natural language")
    st.markdown(f'<span class="db-badge">📊 Current Database: {db_display_name}</span>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Memory management
        st.subheader("💾 Memory Management")
        memory_count = len(st.session_state.memory_manager.memory)
        st.info(f"Stored interactions: {memory_count}")
        
        if st.button("🗑️ Clear Memory", type="secondary"):
            st.session_state.memory_manager.clear()
            st.success("Memory cleared!")
            st.rerun()
        
        st.divider()
        
        # Database Info
        st.subheader("🗄️ Database Info")
        schema = st.session_state.db_manager.get_schema()
        if schema:
            for table_name, columns in schema.items():
                with st.expander(f"Table: {table_name}"):
                    for col in columns:
                        st.text(f"• {col['name']} ({col['datatype']})")
        
        st.divider()
        
        # Database Management in sidebar
        st.subheader("📂 Database Management")
        
        db_action = st.selectbox(
            "Choose action:",
            ["Select an action...", "Upload SQLite Database", "Create Database from CSV"],
            index=0
        )
        
        if db_action == "Upload SQLite Database":
            uploaded_file = st.file_uploader(
                "Choose SQLite file", 
                type=["db", "sqlite", "sqlite3"],
                key="db_uploader"
            )
            if uploaded_file:
                if st.button("⬆️ Upload Database", type="primary", use_container_width=True):
                    st.session_state.custom_db.upload_database(uploaded_file)
        
        elif db_action == "Create Database from CSV":
            csv_file = st.file_uploader(
                "Upload CSV file", 
                type=["csv"], 
                help="Upload a CSV file to create a new database",
                key="csv_uploader"
            )
            db_name = st.text_input("Database Name:", placeholder="e.g., soil_pollution")
            table_name = st.text_input("Table Name:", placeholder="e.g., pollution_data")
            
            if csv_file and db_name and table_name:
                if st.button("🆕 Create Database", type="primary", use_container_width=True):
                    st.session_state.custom_db.create_database(csv_file, db_name, table_name)
            elif csv_file or db_name or table_name:
                st.info("Please fill in all fields to create a database.")
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Database selector row
        db_col1, db_col2 = st.columns([3, 1])
        with db_col1:
            # Database selector
            available_dbs = st.session_state.db_manager.get_available_databases()
            if available_dbs:
                # Find current index
                current_idx = 0
                if st.session_state.selected_db in available_dbs:
                    current_idx = available_dbs.index(st.session_state.selected_db)
                
                selected_db = st.selectbox(
                    "🗄️ Select Database:",
                    available_dbs,
                    index=current_idx,
                    key="db_selector",
                    label_visibility="collapsed"
                )
                
                # Switch database if selection changed
                if selected_db != st.session_state.selected_db:
                    st.session_state.selected_db = selected_db
                    st.session_state.db_manager.switch_database(selected_db)
                    st.rerun()
            else:
                st.warning("No databases found. Please create or upload a database.")
        
        # Query input
        user_question = st.text_area(
            "Enter your question:",
            height=100,
            placeholder="E.g., Show me the top 10 records, What is the average value by category?"
        )
        
        # Buttons row - aligned properly
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            query_button = st.button("🔍 Run Query", type="primary", use_container_width=True)
        
        with col_btn2:
            clear_button = st.button("🔄 Clear", type="secondary", use_container_width=True)
        
        with col_btn3:
            st.empty()  # Spacer for alignment
    
    with col2:
        st.metric("Total Queries", len(st.session_state.query_history))
        # Show current database
        st.caption(f"📁 Active: {st.session_state.selected_db}")
    
    # Process query
    if query_button and user_question:
        
        with st.spinner("🤔 Generating SQL query..."):
            # Get schema and context
            schema = st.session_state.db_manager.get_schema()
            context = st.session_state.memory_manager.get_recent_context(3)
            
            # Generate SQL
            prompt = st.session_state.assistant.build_sql_prompt(schema, user_question, context)
            sql_query = st.session_state.assistant.generate_sql(prompt)
            
            # Validate SQL using SQLValidator
            validator = SQLValidator(db_path=st.session_state.db_manager.db_path)
            is_safe, safety_msg = validator.validate(sql_query)

            if not is_safe:
                st.error(f"❌ SQL Safety Error: {safety_msg}")
                st.warning("Query execution blocked for security reasons.")
                # Optionally show the problematic query for debugging
                with st.expander("View Generated Query (Not Executed)"):
                    st.code(sql_query, language="sql")
                return 

            if not sql_query:
                st.error("Failed to generate SQL query")
                return
            
            # Display generated SQL
            st.subheader("📝 Generated SQL Query")
            st.code(sql_query, language="sql")
        
        with st.spinner("⚡ Executing query..."):
            # Execute query
            result = st.session_state.db_manager.execute_query(sql_query)
            
            if result is None:
                st.error("Query execution failed")
                return
            
            if not result:
                st.warning("No results found")
                summary = "No data found for the given query."
            else:
                # Generate summary
                summary = st.session_state.assistant.generate_summary(
                    user_question, result, context
                )
                
                # Display results
                st.subheader("📊 Query Results")
                df = pd.DataFrame(result)
                st.dataframe(df, use_container_width=True, width="stretch")
                
                # Display summary
                st.subheader("💬 Natural Language Summary")
                st.markdown(f'<div class="success-box">{summary}</div>', unsafe_allow_html=True)
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # Save to memory
            st.session_state.memory_manager.add(user_question, sql_query, result, summary)
            st.session_state.query_history.append({
                "question": user_question,
                "timestamp": datetime.now(),
                "summary": summary
            })
    
    # Clear button action
    if clear_button:
        st.rerun()
    
    # Query history
    if st.session_state.query_history:
        st.divider()
        st.subheader("📜 Recent Queries")
        
        for i, query in enumerate(reversed(st.session_state.query_history[-5:])):
            with st.expander(f"Query {len(st.session_state.query_history) - i}: {query['question'][:50]}..."):
                st.write(f"**Question:** {query['question']}")
                st.write(f"**Time:** {query['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Summary:** {query['summary']}")


if __name__ == "__main__":
    main()