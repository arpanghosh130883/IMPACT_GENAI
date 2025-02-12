import streamlit as st
import time
from common_app_files.openai import get_openai_response, get_app_name
from common_app_files.functions import process_docx_file
from meeting_bot.common.agenda_constants import (
    MESSAGE_VAR,
    DEFAULT_SYSTEM_PROMPT,
    WELCOME_MESSAGE,
)
from meeting_bot.common.media_path import LOGO_FILE_PATH, FAVICON_FILE_PATH
from meeting_bot.common.constants import APP_NAME, FOOTER_HTML

get_app_name(APP_NAME)

st.set_page_config(page_title="Agenda", layout = "centered", page_icon=FAVICON_FILE_PATH)

# config:
st.logo(LOGO_FILE_PATH)

st.markdown(FOOTER_HTML, unsafe_allow_html=True)

# system prompt functions:
def get_system_prompt():
    return st.session_state[MESSAGE_VAR][0]["content"]


def set_system_prompt(updated_system_prompt):
    st.session_state[MESSAGE_VAR][0]["content"] = updated_system_prompt


# Initialise the streamlit session state:
if MESSAGE_VAR not in st.session_state:
    st.session_state[MESSAGE_VAR] = [
        {
            "role": "system",
            "content": DEFAULT_SYSTEM_PROMPT,
        }
    ]

st.session_state["system_prompt_input"] = get_system_prompt()


# file uploader dialog:
@st.experimental_dialog("Upload a file")
def upload_a_file():

    uploaded_file = st.file_uploader(
        label="Upload a file", type=["docx"], label_visibility="collapsed"
    )
    content_description = st.text_input(
        label="Description of the contents",
        value="Notes about the meeting",
        help="Enter a description of the contents that will help the chatbot understand what's in the file",
    )
    if st.button("Upload", disabled=uploaded_file is None):
        file_name = uploaded_file.name
        text_data = process_docx_file(uploaded_file)
        st.session_state[MESSAGE_VAR].append(
            {
                "role": "user",
                "content": f"{file_name} uploaded by user with description: {content_description}.\n\n File contents:\n\n {text_data}",
                "type": "file_upload",
                "file_name": file_name,
            }
        )
        st.rerun()


# System prompt editor dialog:
@st.experimental_dialog("Modify System Prompt", width="large")
def modify_system_prompt():
    updated_system_prompt = st.text_area(
        label="Edit the system prompt",
        value=get_system_prompt(),
        height=600,
    )
    if st.button("Update System Prompt", disabled=updated_system_prompt is None):
        set_system_prompt(updated_system_prompt)
        st.info("System prompt updated!")
        time.sleep(1)
        st.rerun()
    if st.button(":red[Reset to default]"):
        set_system_prompt(DEFAULT_SYSTEM_PROMPT)
        st.info("System prompt reset!")
        time.sleep(1)
        st.rerun()


with st.sidebar:

    if st.button(
        label="Modify System Prompt",
        help="Modify the system instructions that control the behaviour of the chatbot",
    ):
        modify_system_prompt()

    if st.button(
        label="Upload a file",
        help="Upload notes or other supporting documents",
    ):
        upload_a_file()

    if st.button(
        label="Reset",
        help="This will clear the chat history and delete any uploaded files",
    ):
        st.session_state[MESSAGE_VAR] = [
            {
                "role": "system",
                "content": get_system_prompt(),
            }
        ]
        st.rerun()

# Headings and page links:
st.title("The Modulr Meeting Way")

# Chat Interface
with st.chat_message("assistant"):
    st.markdown(WELCOME_MESSAGE)

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
