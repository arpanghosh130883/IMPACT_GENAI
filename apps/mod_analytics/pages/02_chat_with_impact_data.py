import streamlit as st
import time
import pandas as pd
import re

from snowflake.snowpark.functions import col, concat, lit
from common_app_files.openai import get_openai_response, get_app_name
from common_app_files.snowflake import get_snowflake_session
from common_app_files.code_interpreter_utils import (
    init_session_state,
    upload_dataframe,
    display_message_content,
    handle_assistant_response,
    delete_uploaded_files
)
from common_app_files.openai_code_interpreter import (
    create_assistant,
    create_thread,
    add_files_to_thread,
    add_message_to_thread,
    fetch_all_files,
)
from mod_analytics.common.media_path import LOGO_FILE_PATH, FAVICON_FILE_PATH
from mod_analytics.common.html_constants import APP_NAME, FOOTER_HTML
from mod_analytics.common.code_interpreter_constants import DEFAULT_SYSTEM_PROMPT
from mod_analytics.common.mod_analytics_constants import CI_PROMPT, session_state_page2

# Set page config (First Streamlit call)
st.set_page_config(page_title="Code Interpreter", layout="centered", page_icon=FAVICON_FILE_PATH)

# Default Prompts
DEFAULT_CI_PROMPT = CI_PROMPT

def get_prompt(SESSION_VAR, PROMPT):
    return st.session_state.get({SESSION_VAR}, PROMPT)

def set_prompt(SESSION_VAR, PROMPT):
    st.session_state[{SESSION_VAR}] = PROMPT

def check_limit_clause(sql_query, limit_threshold=10000):
    sql_query_upper = sql_query.upper()

    if 'LIMIT' not in sql_query_upper:
        st.warning("Warning: Your SQL query does not contain a LIMIT clause. This may result in processing a large amount of data.")
        return False

    limit_match = re.search(r'\bLIMIT\s+(\d+)', sql_query_upper)
    
    if limit_match:
        limit_value = int(limit_match.group(1))
        if limit_value > limit_threshold:
            st.warning(f"Warning: Your SQL query has a LIMIT clause with a value greater than {limit_threshold} ({limit_value}). This may result in processing a large amount of data.")
            return False
    else:
        st.warning("Warning: Your SQL query must include a LIMIT clause with a specified value to limit the number of rows returned.")
        return False

    return True

# System prompt editor dialog
@st.experimental_dialog("Modify Prompts", width="large")
def modify_prompts():
    updated_system_prompt = st.text_area(
        label="Edit the code interpreter prompt",
        value=get_prompt("modified_ci_prompt", CI_PROMPT),
        height=300,
    )

    # Update buttons for prompts
    if st.button("Update Prompts", updated_system_prompt is None):
        set_prompt("modified_ci_prompt", updated_system_prompt)
        st.info("Prompts updated!")
        time.sleep(1)
        st.rerun()

    if st.button(":red[Reset to default]"):
        set_prompt("modified_ci_prompt", DEFAULT_CI_PROMPT)
        st.info("Prompts reset to default!")
        time.sleep(1)
        st.rerun()    

@st.experimental_dialog("Modify Prompts", width="large")
def analyze_dataset():
    analyze_sql_query = st.text_area(
        label="Enter the SQL query to analyze the dataset",
        height=300,
    )

    if st.button("Analyze Dataset"):
        if check_limit_clause(analyze_sql_query):            
            st.session_state.analyze_sql_query = analyze_sql_query
            st.info("Analyzing the dataset...")
            time.sleep(1)
            st.rerun()            

# Sidebar for System Prompt and Client Summary Prompt Editor
with st.sidebar:
    if st.button(
        label="Modify Prompts",
        help="Modify the system prompt for the code interpreter",
    ):
        modify_prompts()

    if st.button(
        label="Analyze Dataset",
        help="Analyze the data by providing the sql query",
    ):
        analyze_dataset()

    if st.button(
        label="Reset",
        help="This will clear the chat history and delete any uploaded files",
    ):
        set_prompt("modified_ci_prompt", DEFAULT_CI_PROMPT)
        st.rerun()

# Initialize App
def init_app():
    get_app_name(APP_NAME)
    st.logo(LOGO_FILE_PATH)
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)

# Initialize Session State
def init_session_variables():
    init_session_state()
    if "selected_object" not in st.session_state:
        st.session_state.selected_object = None
    if "analyze_sql_query" not in st.session_state:
        st.session_state.analyze_sql_query = None
    if "analyze_sql_query_old" not in st.session_state:
        st.session_state.analyze_sql_query_old = None

@st.experimental_dialog("Raw Data", width="large")
def show_raw_data(selected_object, raw_data):
    with st.expander("Data for " + selected_object):
        st.dataframe(raw_data.head(100))

def fetch_table_names(session):
    views_df = session.table('SNOWFLAKE.ACCOUNT_USAGE.VIEWS') \
            .filter(col("DELETED").is_null()) \
            .filter(col("TABLE_CATALOG") == 'CORE') \
            .filter(col("TABLE_SCHEMA") == 'DWH') \
            .select(concat(col("TABLE_CATALOG"), lit('.'), 
                        col("TABLE_SCHEMA"), lit('.'), 
                        col("TABLE_NAME")).alias("object_name"))
    
    tables_df = session.table('SNOWFLAKE.ACCOUNT_USAGE.TABLES') \
        .filter(col("DELETED").is_null()) \
        .filter(col("TABLE_CATALOG") == 'CORE') \
        .filter(col("TABLE_SCHEMA") == 'DWH') \
        .select(concat(col("TABLE_CATALOG"), lit('.'), 
                       col("TABLE_SCHEMA"), lit('.'), 
                       col("TABLE_NAME")).alias("object_name"))
    
    union_df = views_df.union_all(tables_df)
    union_df = union_df.order_by(col("object_name"))
    return union_df

# Main Function
def main():
    init_app()
    init_session_variables()
    session = get_snowflake_session()

    table_options = fetch_table_names(session)
    
    selected_object = st.selectbox("Select Object", 
                                    table_options,
                                    index=None,
                                    placeholder="Please select a object",)

    # print("selected_object: ", selected_object)
    # print("st.session_state.selected_object: ", st.session_state.selected_object)
    # print("02: st.session_state.analyze_sql_query: ", st.session_state.analyze_sql_query)

    if selected_object or st.session_state.analyze_sql_query:
        if (selected_object != st.session_state.selected_object) or (st.session_state.analyze_sql_query != st.session_state.analyze_sql_query_old):

            if "chat_with_external_data_messages" not in st.session_state:
                chat_with_external_data_messages=[]
            else:
                chat_with_external_data_messages = st.session_state.chat_with_external_data_messages
            
            if "analyze_sql_query" not in st.session_state:
                analyze_sql_query=[]
            else:
                analyze_sql_query = st.session_state.analyze_sql_query       
                # print("03: st.session_state.analyze_sql_query: ", st.session_state.analyze_sql_query) 

            st.session_state.clear()
            st.cache_data.clear()

            # Initialize session state
            init_session_variables()  
            st.session_state.chat_with_external_data_messages = chat_with_external_data_messages
            st.session_state.selected_object = selected_object          
            st.session_state.analyze_sql_query = analyze_sql_query
            st.session_state.analyze_sql_query_old = st.session_state.analyze_sql_query

            if st.session_state.analyze_sql_query:
                sql_query = st.session_state.analyze_sql_query
                print("01: sql_query: ", sql_query)
            elif st.session_state.selected_object:
                sql_query = f"""Select * from {st.session_state.selected_object} limit 10000""" 
            else:
                raise ValueError("No object selected or sql query provided")            

            try:
                snowflake_df = session.sql(sql_query).collect()
                object_df = pd.DataFrame([row.asDict() for row in snowflake_df])                

            except Exception as e:
                st.warning(f"Error with data collection: {e}")

                try:
                    object_df = session.sql(sql_query).to_pandas()

                except Exception as e:
                    raise ValueError(f"Error with data collection: {e}")

            row_count = len(object_df)
            st.write(f"Row count: {row_count}")

            if row_count > 10000:
                st.warning(f"Dataset exceeds 10,000 rows. Limiting to first 10,000 rows.")
                object_df = object_df.head(10000)

            # Delete existing files before uploading a new one
            data = fetch_all_files()
            fil_ids = [file_object.id for file_object in data]    
            delete_uploaded_files(fil_ids)
            # print("after delete_uploaded_files: ", fetch_all_files(), "\n")

            upload_dataframe(object_df)
            # print("after upload_dataframe: ", fetch_all_files(), "\n")

            st.session_state.object_df = object_df

            # print("before rerun :- st.session_state.selected_object: ", st.session_state.selected_object)
            # print("before rerun :- st.session_state.analyze_sql_query: ", st.session_state.analyze_sql_query)                           
            if not st.session_state.analyze_sql_query:
                st.rerun()

        # print("st.session_state.selected_object: ", st.session_state.selected_object)
        # print("05: st.session_state.analyze_sql_query: ", st.session_state.analyze_sql_query)
        if st.session_state.selected_object or st.session_state.analyze_sql_query:            

            if "assistant_id" not in st.session_state:
                st.session_state["assistant_id"] = None
                assistant = create_assistant(DEFAULT_SYSTEM_PROMPT)
                st.session_state.assistant_id = assistant.id
                # print(st.session_state.assistant_id)

            if st.session_state.thread_id is None:
                thread = create_thread()
                st.session_state.thread_id = thread.id
                # print(st.session_state.thread_id)

            add_files_to_thread(st.session_state.thread_id, st.session_state.file_id)

            messages = session_state_page2
            if messages not in st.session_state:
                st.session_state[messages] = []

            for message in st.session_state[messages]:
                with st.chat_message(message["role"]):
                    display_message_content(message["items"])

            if st.session_state[messages] == []:
                add_message_to_thread(st.session_state.thread_id, CI_PROMPT)
                with st.chat_message("assistant"):
                    handle_assistant_response(st.session_state.assistant_id, st.session_state.thread_id, messages)

            with st.sidebar:
                if st.button("Show Raw Data"):
                    show_raw_data(st.session_state.selected_object, st.session_state.object_df)

        if prompt := st.chat_input("Ask me a question about your dataset"):
                    st.session_state[messages].append({"role": "user", "items": [{"type": "text", "content": prompt}]})
                    # print("prompt: ", prompt)
                    add_message_to_thread(st.session_state.thread_id, prompt)

                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        handle_assistant_response(st.session_state.assistant_id, st.session_state.thread_id, messages)


if __name__ == "__main__":
    main()

