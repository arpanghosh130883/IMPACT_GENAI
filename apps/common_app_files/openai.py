import os
import time
from openai import AzureOpenAI
from common_app_files.logger import log_request


OPENAI_MODEL = "Modulr-Data4o"
OPENAI_KEY = os.getenv("OPENAI_KEY")

app_name = None

def get_app_name(name: str) -> str:
    global app_name
    app_name = name


def get_openai_response(messages: dict) -> str:

    client = AzureOpenAI(
        api_key=OPENAI_KEY,
        api_version="2024-02-15-preview",
        azure_endpoint="https://data-gpt.openai.azure.com/",
    )

    try:

        request_time = time.time()
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.2,
        )

        response_time = time.time()

        elapsed_time_ms = round((response_time - request_time) * 1000)

        first_choice = response.choices[0]

        reply_message = first_choice.message.content

        usage = response.usage

        log_info_dict = {
            "status": "SUCCESS",
            "finish_reason": first_choice.finish_reason,
            "completion_tokens": usage.completion_tokens,
            "prompt_tokens": usage.prompt_tokens,
            "total_tokens": usage.total_tokens,
            "response_time": elapsed_time_ms,
            "app_name": app_name
        }

    except Exception as e:
        log_info_dict = {
            "status": "FAILURE",
            "error_message": str(e),
            "app_name": app_name
        }
        reply_message = f"Error: {e}"

    log_request(**log_info_dict) #commented on 05-11-2024

    return reply_message
