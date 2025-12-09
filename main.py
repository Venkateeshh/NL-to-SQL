import streamlit as st
from databse_manager import DatabaseManager
from datetime import datetime
from gemini_class import GeminiAssistant
from memory_management import MemoryManager
import pandas as pd
from sql_validation import SQLValidator

st.set_page_config(
    page_title="Soil Pollution Query System",
    page_icon="🌱",
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


def main():
    """Main Streamlit application."""
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #2E7D32;
            text-align: center;
            margin-bottom: 1rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
        }
        .success-box {
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #E8F5E9;
            border-left: 5px solid #4CAF50;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🌱 Soil Pollution Query System</h1>', unsafe_allow_html=True)
    st.markdown("### Ask questions about soil pollution data in natural language")
    
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
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Query input
        user_question = st.text_area(
            "Enter your question:",
            height=100,
            placeholder="E.g., What are the highest lead concentrations by country?"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            query_button = st.button("🔍 Run Query", type="primary")
        
        with col_btn2:
            clear_button = st.button("🔄 Clear", type="secondary")
    
    with col2:
        st.metric("Total Queries", len(st.session_state.query_history))
    
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