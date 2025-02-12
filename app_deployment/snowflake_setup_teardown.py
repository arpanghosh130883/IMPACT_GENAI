import os
import argparse
from project_path import PROJECT_ROOT_DIR
import snowflake.connector


def run_setup_teardown(run_type: str, environment: str) -> None:

    connection = snowflake.connector.connect(connection_name=environment)

    with open(
        os.path.join(PROJECT_ROOT_DIR, "snowflake_setup", f"{run_type}.sql"), "r"
    ) as f:
        connection.execute_string(f.read())


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--run_type", help="Type to run [setup | teardown]")
    parser.add_argument("--environment", help="Environment for deployment")

    args = parser.parse_args()

    run_type = args.run_type or input("Type to run:  [setup | teardown]:")
    environment = args.environment or input("Environment [dev | prd]:")

    run_setup_teardown(run_type, environment)
