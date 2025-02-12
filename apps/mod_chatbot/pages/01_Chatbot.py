import streamlit as st
import time
from common_app_files.openai import get_openai_response, get_app_name
from common_app_files.functions import process_docx_file, process_pdf_file
from mod_chatbot.common.mod_chatbot_constants import (
    MESSAGE_VAR,
    DEFAULT_SYSTEM_PROMPT,
    WELCOME_MESSAGE,
)
from mod_chatbot.common.media_path import LOGO_FILE_PATH, FAVICON_FILE_PATH
from mod_chatbot.common.constants import APP_NAME, FOOTER_HTML

# Initialize application name
get_app_name(APP_NAME)

# Set page configuration
st.set_page_config(page_title="ChatBot", layout="centered", page_icon=FAVICON_FILE_PATH)

# Display logo and footer
st.logo(LOGO_FILE_PATH)
st.markdown(FOOTER_HTML, unsafe_allow_html=True)

# System prompt functions
def get_system_prompt():
    return st.session_state[MESSAGE_VAR][0]["content"]

# Initialize session state for chat history and context
if MESSAGE_VAR not in st.session_state:
    st.session_state[MESSAGE_VAR] = [
        {
            "role": "system",
            "content": DEFAULT_SYSTEM_PROMPT,
        }
    ]

# Function to append messages to session memory
def append_message(role, content, message_type=None, file_name=None):
    message = {
        "role": role,
        "content": content,
    }
    if message_type:
        message["type"] = message_type
    if file_name:
        message["file_name"] = file_name
    st.session_state[MESSAGE_VAR].append(message)

st.session_state["system_prompt_input"] = get_system_prompt()

########## File uploader dialog:
@st.experimental_dialog("Upload a file")
def upload_a_file():
    uploaded_file = st.file_uploader(
        label="Upload a file", type=["docx", "pdf"], label_visibility="collapsed"
    )
    content_description = st.text_input(
        label="Description of the contents",
        value="General notes or supporting documents",
        help="Provide a description of the uploaded file to help the chatbot process the contents.",
    )
    if st.button("Upload", disabled=uploaded_file is None):
        file_name = uploaded_file.name
        file_extension = file_name.split(".")[-1].lower()

        if file_extension == "docx":
            text_data = process_docx_file(uploaded_file)
        elif file_extension == "pdf":
            text_data = process_pdf_file(uploaded_file)
        else:
            text_data = "Unsupported file type"

        append_message(
            role="user",
            content=f"{file_name} uploaded by user with description: {content_description}.\n\n File contents:\n\n {text_data}",
            message_type="file_upload",
            file_name=file_name,
        )
        st.rerun()

########## Dynamic Contextual Suggestions
def generate_suggestions():
    """
    Dynamically generate suggestions based on the user's latest query
    by analyzing the context of the conversation.
    """
    # Get the last user message
    last_user_message = next(
        (msg for msg in reversed(st.session_state[MESSAGE_VAR]) if msg["role"] == "user"),
        None,
    )

    # If no user message exists, return default suggestions
    #if not last_user_message:
        #return ["Ask me about uploading documents.", "How to summarize a report?"]
    if not last_user_message:
        return ["Review and suggest changes to improve my drafting", "Summarize this document for me","Brainstorm solutions or approaches for this task."]


    user_query = last_user_message["content"]

    # Craft a prompt for suggestion generation
    suggestion_prompt = f"""
    You are an intelligent assistant. Based on the following user query, generate 3 relevant follow-up questions or actions the user might be interested in. 
    Keep the suggestions concise and actionable.

    User Query: "{user_query}"

    Suggestions:
    """

    # Call the OpenAI API for suggestion generation
    suggestions_response = get_openai_response(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": suggestion_prompt},
        ]
    )

    # Parse and clean the response into a list of suggestions
    suggestions = suggestions_response.strip().split("\n")
    return [suggestion.strip("- ").strip() for suggestion in suggestions if suggestion]

########## Sidebar with Search Functionality and Other Actions
with st.sidebar:
    # Search input for chat history
    search_query = st.text_input("Search Chat History", placeholder="Enter keyword...")
    if search_query:
        st.markdown(f"### Search Results for: `{search_query}`")
        # Filter chat history based on search query
        search_results = [
            message
            for message in st.session_state[MESSAGE_VAR]
            if search_query.lower() in message["content"].lower()
        ]
        if search_results:
            for result in search_results:
                st.markdown(f"- **{result['role'].capitalize()}**: {result['content']}")
        else:
            st.markdown("No results found.")
        st.markdown("---")  # Separator for search results

    if st.button(
        label="Upload a file",
        help="Upload documents or notes for chatbot context.",
    ):
        upload_a_file()

    if st.button(
        label="Reset",
        help="Clear chat history and uploaded files.",
    ):
        st.session_state[MESSAGE_VAR] = [
            {
                "role": "system",
                "content": get_system_prompt(),
            }
        ]
        st.rerun()

########## Main chatbot title and greeting
st.title("Welcome to ModBot2.0 🤖")

with st.chat_message("assistant"):
    st.markdown(WELCOME_MESSAGE)

# Display chat history
for message in st.session_state[MESSAGE_VAR]:
    if message["role"] == "system":
        continue
    # Check for 'type' key and handle file uploads
    if message.get("type") == "file_upload":
        with st.expander(":page_with_curl: **" + message.get("file_name", "Unknown File") + "**"):
            st.write(message.get("content", "No content available"))
    else:
        # Render other messages (e.g., user and assistant messages)
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User input for questions
if prompt := st.chat_input(placeholder="Ask me anything..."):
    append_message(role="user", content=prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
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
        append_message(role="assistant", content=assistant_response)

# Generate Contextual Suggestions
st.markdown("### Suggested Actions:")
for suggestion in generate_suggestions():
    if st.button(suggestion):
        append_message(role="user", content=suggestion)
        with st.chat_message("user"):
            st.markdown(suggestion)

        # Generate AI response for the suggestion
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                assistant_response = get_openai_response(
                    messages=[
                        {"role": message["role"], "content": message["content"]}
                        for message in st.session_state[MESSAGE_VAR]
                    ]
                )
                st.markdown(assistant_response)
        append_message(role="assistant", content=assistant_response)
