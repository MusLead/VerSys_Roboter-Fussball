# Use the official Ubuntu base image
FROM ubuntu:20.04

# Set environment variables to avoid user prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        curl \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the latest version of pip for Python 3.10
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# Upgrade pip to the latest version
RUN python3 -m pip install --upgrade pip

# Install the grpcio library
RUN python3 -m pip install grpcio grpcio-tools protobuf

# Verify installations
RUN python3 --version && pip --version && python3 -m pip show grpcio

# Set the working directory inside the container
WORKDIR /code

# Copy the Controller directory (for gRPC definitions)
COPY Controller /code/Controller

# Copy the Server directory (including server.py)
COPY Server /code/Server

# Set the default working directory for the server
WORKDIR /code/Server

# Use the virtual environment when running the application
CMD ["python3", "-u", "server.py"]

