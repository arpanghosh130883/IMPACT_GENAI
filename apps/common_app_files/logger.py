from snowflake.snowpark.functions import current_timestamp
from common_app_files.functions import get_logged_in_user
from common_app_files.snowflake import get_snowflake_session


def log_request(**kwargs):

    user_name = get_logged_in_user()
    log_info = {
        "page_name": "Summarise",
    }
    log_info.update(kwargs)

    APP_NAME = kwargs["app_name"]

    session = get_snowflake_session()

    df = (
        session.create_dataframe(
            [(APP_NAME, user_name, log_info)],
            schema=["app_name", "user_name", "log_info"],
        )
        .with_column("log_timestamp", current_timestamp())
        .select("log_timestamp", "app_name", "user_name", "log_info")
    )

    # Write the DataFrame to the table
    df.write.save_as_table("impact_genai.metadata.genai_usage_log", mode="append")
