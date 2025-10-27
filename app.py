import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
import pandas as pd
import re
from langchain_groq import ChatGroq

st.set_page_config(page_title="Chat with SQL DB", page_icon="🖥️")
st.title("🖥️Chat with SQL DB")

LOCALDB="USE_LOCALDB"
MYSQL="USE_MYSQL"

radio_opt=["Use SQLLite 3 Database- Student.db","Connect to your MySQL Database"]

selected_opt=st.sidebar.radio(label="Choose the DB which you want to chat with",options=radio_opt)

if radio_opt.index(selected_opt)==1:
    db_uri=MYSQL
    mysql_host=st.sidebar.text_input("Provide MySQL Host")
    mysql_user=st.sidebar.text_input("MYSQL User")
    mysql_password=st.sidebar.text_input("MYSQL password",type="password")
    mysql_db=st.sidebar.text_input("MySQL database")
else:
    db_uri=LOCALDB

api_key=st.sidebar.text_input(label="Groq API Key",type="password")

if not db_uri:
    st.info("Please enter the database information and uri")

if not api_key:
    st.info("Please add the groq api key")

## LLM model
llm=ChatGroq(groq_api_key=api_key,model_name="Llama3-8b-8192",streaming=True)

def parse_and_display_response(response):
    """
    Parse the agent response and display tabular data as tables if available.
    Returns the text content without the table data.
    """
    # Pattern to match pipe-separated tables or markdown tables
    # Looks for patterns like: Col1|Col2|Col3\n---\nVal1|Val2|Val3
    table_pattern = r'(\|.+\|\n\|[-:\s\|]+\|\n(?:\|.+\|\n?)+)'
    
    matches = re.findall(table_pattern, response)
    
    if matches:
        # Display each table found
        for table_match in matches:
            lines = table_match.strip().split('\n')
            
            # Parse header
            header = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
            
            # Parse rows (skip separator line and header)
            rows = []
            for line in lines[2:]:
                if line.strip() and '---' not in line:
                    row = [cell.strip() for cell in line.split('|') if cell.strip()]
                    if row:  # Only add non-empty rows
                        rows.append(row)
            
            if header and rows:
                # Create DataFrame for better display
                try:
                    # Handle cases where rows might have different lengths
                    max_cols = max(len(row) for row in rows) if rows else len(header)
                    if max_cols > len(header):
                        header.extend([f'Column{i+1}' for i in range(len(header), max_cols)])
                    
                    # Pad rows to match header length
                    padded_rows = []
                    for row in rows:
                        padded_row = row + [''] * (len(header) - len(row))
                        padded_rows.append(padded_row[:len(header)])
                    
                    df = pd.DataFrame(padded_rows, columns=header)
                    st.dataframe(df, use_container_width=True)
                    
                    # Remove the table from the response text
                    response = response.replace(table_match, '').strip()
                except Exception as e:
                    st.warning(f"Could not parse table: {e}")
    else:
        # Try to detect simple tabular data without markdown formatting
        # Look for patterns with multiple lines that might be a table
        # Check if we have multiple lines with similar structure
        lines = response.split('\n')
        if len(lines) > 2:
            # Check if we have pipe-separated values (even without markdown header)
            potential_table_lines = []
            for line in lines:
                if '|' in line and line.count('|') >= 2 and '---' not in line:
                    potential_table_lines.append(line)
            
            if len(potential_table_lines) >= 2:
                try:
                    # Try to parse as a table
                    all_rows = []
                    for line in potential_table_lines:
                        row = [cell.strip() for cell in line.split('|') if cell.strip()]
                        if row:
                            all_rows.append(row)
                    
                    if all_rows:
                        # Find the row with the most columns (likely the header)
                        max_cols = max(len(row) for row in all_rows)
                        # Check if first row could be a header (all strings, reasonable length)
                        if all_rows and len(all_rows[0]) >= 2:
                            header = all_rows[0] if len(all_rows[0]) == max_cols else [f'Column{i+1}' for i in range(max_cols)]
                            
                            # Add padding if needed
                            if len(header) < max_cols:
                                header.extend([f'Column{i+1}' for i in range(len(header), max_cols)])
                            
                            # Create DataFrame from remaining rows or all rows if no clear header
                            data_rows = all_rows[1:] if len(all_rows) > 1 and len(all_rows[0]) == max_cols else all_rows
                            
                            padded_rows = []
                            for row in data_rows:
                                padded_row = row + [''] * (max_cols - len(row))
                                padded_rows.append(padded_row[:max_cols])
                            
                            df = pd.DataFrame(padded_rows, columns=header[:max_cols])
                            st.dataframe(df, use_container_width=True)
                            
                            # Remove the table lines from response
                            for line in potential_table_lines:
                                response = response.replace(line, '', 1).strip()
                except Exception as e:
                    # If parsing fails, just continue with original response
                    pass
    
    return response

@st.cache_resource(ttl="2h")
def configure_db(db_uri,mysql_host=None,mysql_user=None,mysql_password=None,mysql_db=None):
    if db_uri==LOCALDB:
        dbfilepath=(Path(__file__).parent/"student.db").absolute()
        print(dbfilepath)
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_uri==MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))   
    
if db_uri==MYSQL:
    db=configure_db(db_uri,mysql_host,mysql_user,mysql_password,mysql_db)
else:
    db=configure_db(db_uri)

## toolkit
toolkit=SQLDatabaseToolkit(db=db,llm=llm)

agent=create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query=st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback=StreamlitCallbackHandler(st.container())
        response=agent.run(user_query,callbacks=[streamlit_callback])
        
        # Parse and display tabular data as formatted tables
        remaining_text = parse_and_display_response(response)
        
        # Display any remaining text content
        if remaining_text.strip():
            st.write(remaining_text)
        
        # Store the full response in session state
        st.session_state.messages.append({"role":"assistant","content":response})