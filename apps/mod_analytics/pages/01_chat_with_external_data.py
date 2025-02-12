import streamlit as st
from common_app_files.snowflake import get_snowflake_session
from common_app_files.code_interpreter_utils import (
    init_session_state,
    upload_a_file,
    upload_dataframe,
    display_message_content,
    handle_assistant_response
)
from common_app_files.openai_code_interpreter import (
    create_assistant,
    create_thread,
    add_files_to_thread,
    add_message_to_thread,
)
from mod_analytics.common.media_path import LOGO_FILE_PATH, FAVICON_FILE_PATH
from mod_analytics.common.html_constants import FOOTER_HTML 
from mod_analytics.common.mod_analytics_constants import CI_PROMPT, session_state_page1
from mod_analytics.common.code_interpreter_constants import DEFAULT_SYSTEM_PROMPT


# Set page config
st.set_page_config(page_title="Code Interpreter", layout="centered", page_icon=FAVICON_FILE_PATH)

# Config
st.logo(LOGO_FILE_PATH)
st.markdown(FOOTER_HTML, unsafe_allow_html=True)

# Initialize session state
init_session_state()

# Upload a file
with st.sidebar:
    if st.button(
        label="Upload a file",
        help="Upload notes or other supporting documents"
    ):
        upload_a_file()
    
if st.session_state["file_uploaded"]:

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

    messages = messages = session_state_page1
    if messages not in st.session_state:
        st.session_state[messages] = []

    for message in st.session_state[messages]:
        # print('st.session_state[messages]: ', st.session_state[messages])
        with st.chat_message(message["role"]):
            display_message_content(message["items"])

    if st.session_state[messages] == []:
        add_message_to_thread(st.session_state.thread_id, CI_PROMPT)
        with st.chat_message("assistant"):
            handle_assistant_response(st.session_state.assistant_id, st.session_state.thread_id, messages)

    if prompt := st.chat_input("Ask me a question about your dataset"):
        st.session_state[messages].append({"role": "user", "items": [{"type": "text", "content": prompt}]})
        add_message_to_thread(st.session_state.thread_id, prompt)

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            handle_assistant_response(st.session_state.assistant_id, st.session_state.thread_id, messages)