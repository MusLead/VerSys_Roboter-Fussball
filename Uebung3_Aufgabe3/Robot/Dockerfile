# Use the official Ubuntu base image
FROM ubuntu:20.04

# Set environment variables to avoid user prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        # For Ubuntu/Debian 
        mosquitto-clients \  
        openjdk-17-jdk \
        python3 \
        python3-pip \
        unzip \
        wget \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the latest version of pip for Python 3.10
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# Upgrade pip to the latest version
RUN python3 -m pip install --upgrade pip

# Install the grpcio library and required dependencies
# https://stackoverflow.com/questions/77984857/paho-mqtt-unsupported-callback-api-version-error
RUN python3 -m pip install grpcio grpcio-tools "paho-mqtt<2.0.0" protobuf 

# Set the working directory inside the container
WORKDIR /code

# Copy the Controller directory (for gRPC definitions)
COPY Controller /code/Controller

# Copy the Server directory (including server.py)
COPY Robot /code/Robot

# Set the default working directory for the server
WORKDIR /code/Robot

# Use the virtual environment when running the application
CMD ["python3", "robot.py", "dummy_robot"]
