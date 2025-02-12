#!/bin/bash

# Accept command line arguments for Snowflake URL, Docker image tag, and Dockerfile path
environment=$1
snowflake_registry_url=$2
remote_image_tag=$3

# Get the Snowflake token and login to the Docker registry
snow spcs image-registry token --connection $environment --format=JSON | docker login "$snowflake_registry_url" --username 0sessiontoken --password-stdin

# Push the Docker image to the registry
docker push "$snowflake_registry_url/$remote_image_tag"