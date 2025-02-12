import os
from openai import AzureOpenAI
from common_app_files.logger import log_request

OPENAI_MODEL = "Modulr-Data4o"
OPENAI_KEY = os.getenv("OPENAI_KEY")
AZURE_ENDPOINT = "https://data-gpt.openai.azure.com/"

def create_openai_client():
    return AzureOpenAI(
        api_key=OPENAI_KEY,
        api_version="2024-05-01-preview",
        azure_endpoint=AZURE_ENDPOINT,
    )

client = create_openai_client()

def create_assistant(DEFAULT_SYSTEM_PROMPT):
    """Create an assistant in OpenAI."""
    return client.beta.assistants.create(
        instructions=DEFAULT_SYSTEM_PROMPT,
        name="Data Analyst",
        tools=[{"type": "code_interpreter"}],
        model=OPENAI_MODEL,
    )

def create_file_with_assistants(file_obj):
    """Create a file in OpenAI's assistant."""
    return client.files.create(file=file_obj, purpose='assistants')

def create_thread():
    """Create a new thread in OpenAI's assistant."""
    return client.beta.threads.create()

def add_files_to_thread(thread_id, file_ids):
    """Add files to an existing thread."""
    client.beta.threads.update(
        thread_id=thread_id,
        tool_resources={"code_interpreter": {"file_ids": file_ids}}
    )

def add_message_to_thread(thread_id, prompt):
    """Add a user message to the thread."""
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

def create_stream(assistant_id, thread_id):
    """Create a stream for a thread."""
    return client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        tool_choice={"type": "code_interpreter"},
        stream=True,
    )

def get_image_content(image_file_id):
    """Get content of an image file."""
    return client.files.content(image_file_id)

def delete_file(file_id):
    """Delete a file from OpenAI."""
    client.files.delete(file_id)

def fetch_all_files():
    """Fetch all files from OpenAI."""
    return client.files.list()