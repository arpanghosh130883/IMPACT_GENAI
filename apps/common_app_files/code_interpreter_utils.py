import base64
from io import BytesIO
import streamlit as st
import pandas as pd

from openai.types.beta.assistant_stream_event import (
    ThreadRunStepCreated,
    ThreadRunStepDelta,
    ThreadRunStepCompleted,
    ThreadMessageCreated,
    ThreadMessageDelta
)
from openai.types.beta.threads.text_delta_block import TextDeltaBlock 
from openai.types.beta.threads.runs.tool_calls_step_details import ToolCallsStepDetails
from openai.types.beta.threads.runs.code_interpreter_tool_call import (
    CodeInterpreterOutputImage,
    CodeInterpreterOutputLogs
)

from common_app_files.openai_code_interpreter import (
    create_file_with_assistants,
    create_stream,
    get_image_content,
    delete_file
)

def init_session_state():
    if "file_uploaded" not in st.session_state:
        st.session_state["file_uploaded"] = False
    if "file_id" not in st.session_state:
        st.session_state["file_id"] = []
    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

@st.experimental_dialog("Upload a file")
def upload_a_file():
    file_upload_box = st.empty()
    upload_btn = st.empty()
    
    if not st.session_state["file_uploaded"]:
        st.session_state["files"] = file_upload_box.file_uploader(
            "Please upload your dataset(s)",
            label_visibility="collapsed",
            accept_multiple_files=True,
            type=["csv"]
        )

    print("files: ",st.session_state["files"])

    if st.button(
        label="Upload",
        disabled=file_upload_box is None
    ):
        st.session_state["file_id"] = []

        for file in st.session_state["files"]:
            oai_file = create_file_with_assistants(file)
            st.session_state["file_id"].append(oai_file.id)
            print(f"Uploaded new file: \t {oai_file.id}")

        st.toast("File(s) uploaded successfully", icon="🚀")
        st.session_state["file_uploaded"] = True
        file_upload_box.empty()
        upload_btn.empty()
        st.rerun()

def upload_dataframe(dataset_df):
    file_upload_box = False
    files = BytesIO()
    dataset_df.to_csv(files, index=False)
    files.seek(0)
    
    print("before file_uploaded")
    if not st.session_state["file_uploaded"]:
        print("inside file_uploaded")
        st.session_state["files"] = [files]
    
    # print("files: ", st.session_state["files"])

    file_upload_box = True
    # print("before file_upload_box")
    if file_upload_box:
        # print("inside file_upload_box")
        st.session_state["file_id"] = []
        for file in st.session_state["files"]:    
            oai_file = create_file_with_assistants(file)
            st.session_state["file_id"].append(oai_file.id)
            print(f"Uploaded new file: \t {oai_file.id}")

        st.toast("Dataset uploaded successfully", icon="🚀")
        st.session_state["file_uploaded"] = True
        file_upload_box = False
        # st.rerun()

def delete_uploaded_files(file_list):
        for file_id in file_list:
            print(f"Delete file: \t {file_id}")
            delete_file(file_id)

def display_message_content(items):
    for item in items:
        item_type = item["type"]
        if item_type == "text":
            st.markdown(item["content"])
        elif item_type == "image":
            for image in item["content"]:
                st.html(image)
        elif item_type == "code_input":
            with st.status("Code", state="complete"):
                st.code(item["content"])
        elif item_type == "code_output":
            with st.status("Results", state="complete"):
                st.code(item["content"])

def handle_assistant_response(assistant_id, thread_id, messages):
    stream = create_stream(assistant_id, thread_id)
    assistant_output = []         

    # print("stream: ", stream)
    # print("stream dir: ", dir(stream))
    # print("stream.response dir: ", dir(stream.response))
    # print("usage: ", stream.response.request)

    for event in stream:
        if isinstance(event, ThreadRunStepCreated):
            if event.data.step_details.type == "tool_calls":
                assistant_output.append({"type": "code_input", "content": ""})
                code_input_expander = st.status("Writing code ...", expanded=False)
                code_input_block = code_input_expander.empty()

        elif isinstance(event, ThreadRunStepDelta):
            handle_run_step_delta(event, assistant_output, code_input_block)

        elif isinstance(event, ThreadRunStepCompleted):
            handle_run_step_completed(event, assistant_output)

        elif isinstance(event, ThreadMessageCreated):
            assistant_output.append({"type": "text", "content": ""})
            assistant_text_box = st.empty()

        elif isinstance(event, ThreadMessageDelta):
            handle_message_delta(event, assistant_output, assistant_text_box)

    st.session_state[messages].append({"role": "assistant", "items": assistant_output})
    print("messages: ", messages)

def handle_run_step_delta(event, assistant_output, code_input_block):
    if event.data.delta.step_details.tool_calls[0].code_interpreter is not None:
        code_interpretor = event.data.delta.step_details.tool_calls[0].code_interpreter
        code_input_delta = code_interpretor.input
        if code_input_delta:
            assistant_output[-1]["content"] += code_input_delta
            code_input_block.empty()
            code_input_block.code(assistant_output[-1]["content"])

def handle_run_step_completed(event, assistant_output):
    if isinstance(event.data.step_details, ToolCallsStepDetails):
        code_interpretor = event.data.step_details.tool_calls[0].code_interpreter
        if code_interpretor.outputs:
            if len(code_interpretor.outputs) > 0:
                process_code_interpreter_outputs(code_interpretor.outputs, assistant_output)
            else:
                print("No outputs found in code_interpretor.")
        else:
            print("code_interpretor.outputs is None or empty.")

def process_code_interpreter_outputs(outputs, assistant_output):
    for output in outputs:
        if isinstance(output, CodeInterpreterOutputImage):
            process_image_output(output, assistant_output)
        elif isinstance(output, CodeInterpreterOutputLogs):
            process_logs_output(output, assistant_output)

def process_image_output(output, assistant_output):
    image_file_id = output.image.file_id
    image_data = get_image_content(image_file_id)
    image_data_bytes = BytesIO(image_data.read())
    data_url = base64.b64encode(image_data_bytes.getvalue()).decode("utf-8")
    image_html = f'<p align="center"><img src="data:image/png;base64,{data_url}" width=600></p>'
    st.html(image_html)
    assistant_output.append({"type": "image", "content": [image_html]})

def process_logs_output(output, assistant_output):
    assistant_output.append({"type": "code_output", "content": ""})
    code_output = output.logs
    with st.status("Results", state="complete"):
        st.code(code_output)    
        assistant_output[-1]["content"] = code_output

def handle_message_delta(event, assistant_output, assistant_text_box):
    if isinstance(event.data.delta.content[0], TextDeltaBlock):
        assistant_text_box.empty()
        assistant_output[-1]["content"] += event.data.delta.content[0].text.value
        assistant_text_box.markdown(assistant_output[-1]["content"])
