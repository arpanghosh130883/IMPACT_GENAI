import os
import streamlit as st
import snowflake.connector
from snowflake.snowpark.session import Session


@st.cache_resource
def _get_cached_snowflake_session(token: str) -> Session:
    SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_HOST = os.getenv("SNOWFLAKE_HOST")

    if SNOWFLAKE_ACCOUNT and SNOWFLAKE_HOST:

        connection = snowflake.connector.connect(
            host=SNOWFLAKE_HOST,
            account=SNOWFLAKE_ACCOUNT,
            token=token,
            authenticator="oauth",
            warehouse="GENAI_WH",
        )

    else:
        # Running locally - get connection to dev
        connection = snowflake.connector.connect(
            connection_name="prd", warehouse="GENAI_WH", role="CONTAINER_SERVICE_ROLE"
            #connection_name="dev", warehouse="ANALYST_WH", role="ANALYSTS" #changed on 05-11-2024
            #connection_name="prd", warehouse="ANALYST_WH", role="ANALYSTS" #changed on 05-11-2024
            # connection_name="prd", warehouse="COMPUTE_WH", role="ENGINEERS"
        )
    

    return Session.builder.configs({"connection": connection}).create()


def get_session_token():
    try:
        with open("/snowflake/session/token", "r") as f:
            token = f.read()
    except FileNotFoundError:
        # Running locally - no token available
        token = None
    return token


def get_snowflake_session() -> Session:

    return _get_cached_snowflake_session(get_session_token())
