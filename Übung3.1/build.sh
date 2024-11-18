#!/bin/bash

# Function to build Docker Compose in a given directory
build_docker_compose() {
    local dir=$1
    if [ -f "$dir/docker-compose.yml" ]; then
        echo "Building Docker Compose in $dir"
        docker compose -f "$dir/docker-compose.yml" build
    else
        echo "No docker-compose.yml found in $dir"
    fi
}

# Build Docker Compose in Client directory
build_docker_compose "Client"

# Build Docker Compose in Server directory
build_docker_compose "Server"