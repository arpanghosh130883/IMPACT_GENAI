import streamlit as st
import pandas as pd
from common_app_files.openai import get_openai_response, get_app_name
from mod_aioncall.common.mod_review_constants import (
    MESSAGE_VAR,
    DEFAULT_SYSTEM_PROMPT,
    WELCOME_MESSAGE
)
from mod_aioncall.common.media_path import LOGO_FILE_PATH, FAVICON_FILE_PATH
from mod_aioncall.common.constants import APP_NAME, FOOTER_HTML

# Load historical data
data_path = '/home/arpan_ghosh/impact-genai/apps/mod_aioncall/data/Service_desk_Jira_Tickets_Refined.csv'
data = pd.read_csv(data_path, encoding='ISO-8859-1')

def find_resolution_in_history(query, data, max_results=3):
    """
    Searches the historical data for resolutions matching the query.

    Args:
        query (str): The user's query to search for in the 'Summary' column.
        data (pd.DataFrame): The historical data DataFrame.
        max_results (int): Maximum number of results to return.

    Returns:
        list[dict] | None: A list of dictionaries with relevant records, or None if no results found.
    """
    # Perform case-insensitive search for the query in the 'Summary' column
    results = data[data['Summary'].str.contains(query, case=False, na=False)]
    
    # If matches are found, return up to 'max_results' as dictionaries
    if not results.empty:
        sorted_results = results.sort_values(by='Priority', ascending=False)  # Example sort by priority
        return sorted_results.head(max_results).to_dict(orient='records')
    
    # If no matches, return None
    return None

def generate_llm_response_from_history(query, historical_data):
    """
    Generates a detailed response using the LLM, referencing historical data.

    Args:
        query (str): The user's query.
        historical_data (dict): The historical data record to use as context.

    Returns:
        str: Generated narrative response based on the historical resolution.
    """
    # Construct context from historical data
    context = f"""
    Incident Summary: {historical_data.get('Summary', 'No summary available')}.
    Resolution: {historical_data.get('Custom field (Incident Resolution)', 'No resolution available')}.
    Priority: {historical_data.get('Priority', 'No priority specified')}.
    Reporter: {historical_data.get('Reporter', 'No reporter available')}.
    Description: {historical_data.get('Description', 'No description provided')}.
    Change/Service Owning Squad: {historical_data.get('Custom field (Change / Service Owning Squad)', 'Not specified')}.
    Customer Impact: {historical_data.get('Custom field (Customer(s) Impacted)', 'Not specified')}.
    Root Cause: {historical_data.get('Custom field (Incident Root Cause)', 'No root cause provided')}.
    """

    # Query the LLM
    response = get_openai_response(messages=[
        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Generate a detailed response based on the following incident data: {context}"}
    ])

    return response

def generate_generic_resolution(query, escalation_department):
    """
    Generates a generic resolution and escalation details when no historical match is found.

    Args:
        query (str): The user's query.
        escalation_department (str): Department to escalate the query.

    Returns:
        str: Generated generic resolution.
    """
    response = get_openai_response(messages=[
        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
        {"role": "user", "content": f"No historical match found for the query: '{query}'. Please provide a generic resolution and mention escalation to {escalation_department}."}
    ])
    return response

# App Configuration
get_app_name(APP_NAME)
st.set_page_config(page_title="Mod-AIonCall", layout="centered", page_icon=FAVICON_FILE_PATH)

# UI Elements
st.logo(LOGO_FILE_PATH)
st.markdown(FOOTER_HTML, unsafe_allow_html=True)
st.title("Mod-AIonCall")

# Display Welcome Message
with st.chat_message("assistant"):
    st.markdown(WELCOME_MESSAGE)

# Separate Input for Query
st.subheader("Query Input")
query = st.text_area("Paste your query here:")

if st.button("Analyze"):
    if query.strip():
        with st.spinner("Searching historical resolutions..."):
            historical_resolutions = find_resolution_in_history(query, data)
            if historical_resolutions:
                st.success("Generating a response based on historical data...")
                # Use the first match to generate a response
                llm_response = generate_llm_response_from_history(query, historical_resolutions[0])
                st.markdown(f"**Response:** {llm_response}")
            else:
                st.error("No relevant historical resolutions found. Generating a resolution...")
                escalation_department = data['Custom field (Department)'].dropna().unique()[0]
                generic_resolution = generate_generic_resolution(query, escalation_department)
                st.markdown(f"**Generated Resolution:** {generic_resolution}")
    else:
        st.warning("Please enter a query before clicking 'Analyze'.")

# Chat Interface
if MESSAGE_VAR not in st.session_state:
    st.session_state[MESSAGE_VAR] = [
        {
            "role": "system", "content": DEFAULT_SYSTEM_PROMPT,
        }
    ]

for message in st.session_state[MESSAGE_VAR]:
    if message["role"] == "system":
        continue
    if message.get("type") == "file_upload":
        with st.expander(":page_with_curl: **" + message["file_name"] + "**"):
            st.write(message["content"])
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input():
    st.session_state[MESSAGE_VAR].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

if st.session_state[MESSAGE_VAR][-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            assistant_response = get_openai_response(
                messages=[
                    {"role": message["role"], "content": message["content"]}
                    for message in st.session_state[MESSAGE_VAR]
                ]
            )
            st.markdown(assistant_response)
    st.session_state[MESSAGE_VAR].append(
        {"role": "assistant", "content": assistant_response}
    )
