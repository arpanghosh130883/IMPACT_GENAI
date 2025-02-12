import os
import subprocess
from time import sleep
import snowflake
from snowflake.snowpark import Session
from project_path import PROJECT_ROOT_DIR
import argparse
import yaml

SERVICE_ROLE = "container_service_role"
COMPUTE_POOL = "genai_compute_pool"
DATABASE = "impact_genai"
WAREHOUSE = "genai_wh"


class AppConfig:

    def __init__(self, app_name: str, environment: str):

        self.app_name = app_name
        self.app_dir = os.path.join(PROJECT_ROOT_DIR, "apps")  
        self.rbac_dir = os.path.join(PROJECT_ROOT_DIR, "apps", app_name)  
        self.database = DATABASE
        self.service_role = SERVICE_ROLE
        self.compute_pool = COMPUTE_POOL
        self.warehouse = WAREHOUSE
        self.schema = self.app_name
        self.image_repository = f"{self.app_name}_image_repository"
        self.image = f"{self.app_name}_image"
        self.image_tag = f"{self.image}:latest"
        self.remote_image_tag = (
            f"{self.database}/{self.schema}/{self.image_repository}/{self.image}:latest"
        )
        self.service_spec_stage = f"{self.database}.{self.schema}.{app_name}_spec_stage"
        self.service_spec_file = f"{app_name}_service_spec.yaml"
        self.service_spec_file_path = os.path.join(self.app_dir, self.service_spec_file)
        self.service_name = f"{app_name}_service"

        with open(os.path.join(PROJECT_ROOT_DIR, "snowflake_config.yaml")) as f:
            snowflake_config = yaml.safe_load(f)
            snowflake_env = snowflake_config.get("environments").get(environment)

        self.snowflake_org_identifier = snowflake_env.get("org_identifier")
        self.snowflake_account_identifier = snowflake_env.get("account_identifier")
        self.snowflake_registry_url = f"{self.snowflake_org_identifier}-{self.snowflake_account_identifier}.registry.snowflakecomputing.com"

        # check the app_dir for a file called snowflake_rbac.yaml:
        rbac_file_path = os.path.join(self.rbac_dir, "snowflake_rbac.yaml")
        if os.path.exists(rbac_file_path):
            with open(rbac_file_path) as f:
                self.snowflake_rbac = yaml.safe_load(f)
        else:
            self.snowflake_rbac = None

        self._endpoint_name = None
        self._endpoint_url = None

    @property
    def endpoint_name(self):
        return self._endpoint_name

    @endpoint_name.setter
    def endpoint_name(self, value):
        self._endpoint_name = value

    @property
    def endpoint_url(self):
        return self._endpoint_url

    @endpoint_url.setter
    def endpoint_url(self, value):
        self._endpoint_url = value

    @property
    def endpoint_role(self):
        return f"{self.database}.{self.schema}.{self.service_name}!{self.endpoint_name}_endpoint_role"

    @property
    def fq_service_name(self):
        return f"{self.database}.{self.schema}.{self.service_name}"


def deploy_app(app_name, environment, deployment_stages):

    # deployment control logic:
    build = True if deployment_stages in ["build", "all"] else False
    deploy = True if deployment_stages in ["deploy", "all"] else False
    print(f"app: {app_name} in environment: {environment}")
    if build and deploy:
        print("Building docker image and deploying to snowflake")
    elif build:
        print("Building docker image locally only")
    elif deploy:
        print("Deploying prebuilt image to snowflake")

    # get config:
    config = AppConfig(app_name, environment)

    if build:

        docker_build(
            image_tag=config.image_tag,
            snowflake_registry_url=config.snowflake_registry_url,
            remote_image_tag=config.remote_image_tag,
            dockerfile_path=os.path.join(config.app_dir, f'Dockerfile.{app_name}'),
            build_context=config.app_dir
        )

    if deploy:

        connection = snowflake.connector.connect(connection_name=environment)
        session = Session.builder.configs({"connection": connection}).create()

        for statement in [
            f"use role {config.service_role}",
            f"use warehouse {config.warehouse}",
            f"create schema if not exists {config.database}.{config.schema}",
            f"create image repository if not exists {config.database}.{config.schema}.{config.image_repository}",
            f"create stage if not exists {config.service_spec_stage} directory = (enable = True)",
        ]:
            session.sql(statement).collect()

        # put the service config file in the stage:

        session.file.put(
            config.service_spec_file_path,
            f"{config.service_spec_stage}",
            auto_compress=False,
            overwrite=True,
        )

        docker_push(
            environment=environment,
            snowflake_registry_url=config.snowflake_registry_url,
            remote_image_tag=config.remote_image_tag,
        )

        for statement in [
            f"alter compute pool {config.compute_pool} resume if suspended",
            (
                f"create service if not exists {config.database}.{config.schema}.{app_name}_service "
                f"in compute pool {config.compute_pool} "
                f"from @{config.service_spec_stage} "
                f"specification_file={config.service_spec_file} "
                f"external_access_integrations=(openai_ext_access) "
                f"min_instances=1 "
                f"max_instances=1 "
            ),
            (
                f"alter service {config.database}.{config.schema}.{app_name}_service "
                f"from @{config.service_spec_stage} "
                f"specification_file={config.service_spec_file} "
            ),
        ]:
            session.sql(statement).collect()

        endpoint = get_service_endpoint(session, config.fq_service_name)

        config.endpoint_name = endpoint.get("name")
        config.endpoint_url = endpoint.get("url")

        print(f"service endpoint url: {config.endpoint_url}")

        if config.snowflake_rbac:
            print(f"Applying snowflake RBAC permissions")
            apply_snowflake_rbac(session, config.snowflake_rbac, config)

        print(f"Deployment Complete")


def apply_snowflake_rbac(session: Session, snowflake_rbac: dict, config):

    for role in snowflake_rbac.get("roles"):
        session.sql("use role accountadmin").collect()
        role_name = role.get("role_name")
        session.sql(f"create role if not exists {role_name}").collect()
        session.sql(
            f"grant usage on database {config.database} to role {role_name}"
        ).collect()
        session.sql(
            f"grant usage on schema {config.database}.{config.schema} to role {role_name}"
        ).collect()
        for username in role.get("users") or []:
            user_exists = session.sql(
                f"select * from snowflake.account_usage.users where name = '{username}'"
            ).count()
            if user_exists == 1:
                session.sql(f'grant role {role_name} to user "{username}"').collect()

        session.sql(f"use role {config.service_role}")
        session.sql(
            f"grant usage on service {config.database}.{config.schema}.{config.service_name} to role {role_name}"
        ).collect()
        session.sql(
            f"grant service role {config.endpoint_role} to role {role_name}"
        ).collect()


def docker_build(
    image_tag: str,
    snowflake_registry_url: str,
    remote_image_tag: str,
    dockerfile_path: str,
    build_context: str,
):

    subprocess.run(
        [
            "sh",
            os.path.join(PROJECT_ROOT_DIR, "app_deployment/docker_build.sh"),
            image_tag,
            snowflake_registry_url,
            remote_image_tag,
            dockerfile_path,
            build_context,
        ]
    )


def docker_push(environment: str, snowflake_registry_url: str, remote_image_tag: str):

    subprocess.run(
        [
            "sh",
            os.path.join(PROJECT_ROOT_DIR, "app_deployment/docker_push.sh"),
            environment,
            snowflake_registry_url,
            remote_image_tag,
        ]
    )


def get_service_endpoint(session: Session, fq_service_name: str) -> dict:

    print("Getting service endpoint from snowflake")
    while True:
        session.sql(f"show endpoints in SERVICE {fq_service_name}").collect()
        result = session.sql(
            "select NAME, INGRESS_URL from table(result_scan(LAST_QUERY_ID()))"
        ).first(1)[0]
        endpoint_name = result["NAME"]
        ingress_url = result["INGRESS_URL"]
        if not ingress_url.startswith("Endpoints provisioning in progress"):
            endpoint = {
                "name": endpoint_name,
                "url": ingress_url,
            }
            return endpoint
        print("Provisioning still in progress. Retrying in 5 seconds...")
        sleep(5)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--app_name", help="Name of the application")
    parser.add_argument("--environment", help="Environment for deployment")
    parser.add_argument(
        "--deployment_stages", help="Deployment Stages [build | deploy | all]"
    )
    args = parser.parse_args()

    app_name = args.app_name or input("Application to deploy: ")
    environment = args.environment or input("Environment ([dev | prd]): ") or "dev"
    deployment_stages = (
        args.deployment_stages
        or input("Deployment Stages ([build | deploy | all]):")
        or "all"
    )

    deploy_app(app_name, environment, deployment_stages)
    # deploy_app("echo_service", "dev")
