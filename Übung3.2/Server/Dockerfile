# Use a lightweight Alpine-based image
FROM alpine:latest

# Install system dependencies
RUN apk add --no-cache \
    build-base \
    linux-headers \
    python3-dev \
    py3-pip \
    git \
    elogind-dev \
    py3-virtualenv

# Set environment variable for systemd
ENV GRPC_PYTHON_BUILD_WITH_SYSTEMD=1

# Create a virtual environment
RUN python3 -m venv /code/venv

# Activate the virtual environment and upgrade pip
RUN /code/venv/bin/pip install --upgrade pip

# Set the repository root environment variable
ENV REPO_ROOT=/grpc

# Clone the gRPC repository at a specific release tag
RUN git clone -b v1.69.0 https://github.com/grpc/grpc $REPO_ROOT

# Navigate to the repository root
WORKDIR $REPO_ROOT

# Initialize and update submodules
RUN git submodule update --init

# Install required Python packages
RUN /code/venv/bin/pip install -r requirements.txt

# Build and install grpcio and grpcio-tools with Cython
RUN GRPC_PYTHON_BUILD_WITH_CYTHON=1 /code/venv/bin/pip install .

# Set the working directory for your application
WORKDIR /code

# Copy the Controller directory (for gRPC definitions)
COPY Controller /code/Controller

# Copy the Server directory
COPY Server /code/Server

# Set the default working directory for the server
WORKDIR /code/Server

# Run the application using the virtual environment's Python interpreter
CMD ["/code/venv/bin/python3", "-u", "server.py"]
