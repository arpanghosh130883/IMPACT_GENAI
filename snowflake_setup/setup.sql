-- Account level objects:
use role accountadmin;
create role if not exists container_service_role;
grant create database on account to role container_service_role;
grant create warehouse on account to role container_service_role;
grant create compute pool on account to role container_service_role;
grant monitor usage on account to role container_service_role;
grant bind service endpoint on account to role container_service_role;
grant imported privileges on database snowflake to role container_service_role;

grant role container_service_role to role accountadmin;

grant usage on database core to role container_service_role;
grant usage on schema core.impact_etl to role container_service_role;
GRANT USAGE, READ ON SECRET core.impact_etl.sf_openapi_key TO container_service_role;
GRANT USAGE ON INTEGRATION openai_ext_access TO container_service_role;

use role container_service_role;

create database if not exists impact_genai;

CREATE WAREHOUSE if not exists genai_wh WITH
  WAREHOUSE_SIZE='X-SMALL'
  MAX_CLUSTER_COUNT = 1
  MIN_CLUSTER_COUNT = 1
  SCALING_POLICY = STANDARD
  AUTO_SUSPEND = 120
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  ENABLE_QUERY_ACCELERATION = FALSE
;

CREATE COMPUTE POOL IF NOT EXISTS genai_compute_pool
  MIN_NODES = 1
  MAX_NODES = 1
  INSTANCE_FAMILY = CPU_X64_XS
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE
  AUTO_SUSPEND_SECS = 60;

create schema if not exists impact_genai.metadata;

create table if not exists impact_genai.metadata.genai_usage_log
(
    log_timestamp timestamp,
    app_name varchar,
    user_name varchar,
    log_info variant    
);
