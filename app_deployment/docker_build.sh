#!/bin/bash

# Accept command line arguments for Snowflake URL, Docker image tag, and Dockerfile path
image_tag=$1
snowflake_registry_url=$2
remote_image_tag=$3
dockerfile_path=$4
build_context=$5

# Build the Docker image
docker buildx build --rm --platform linux/amd64 -t "$image_tag" -t "$snowflake_registry_url/$remote_image_tag" -f "$dockerfile_path" "$build_context"

