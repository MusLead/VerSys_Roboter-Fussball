# https://hub.docker.com/_/alpine
FROM alpine:latest

# install pip
RUN apk add --update-cache \
    py3-pip \
    build-base \
    linux-headers \
  && rm -rf /var/cache/apk/*

# Copy the Controller directory (for gRPC definitions)
COPY Controller /code/Controller

# Copy the Robot directory
COPY Robot /code/Robot

# Create a virtual environment
RUN python3 -m venv /code/venv

# Activate the virtual environment and install dependencies
RUN /code/venv/bin/pip install --upgrade pip
RUN /code/venv/bin/pip install grpcio grpcio-tools

# Set the default working directory for the robot
WORKDIR /app/Robot

# add -u flag to avoid buffering (print output immediately in the docker console)
# run the application
ENTRYPOINT ["python3","-u", "robot.py", "dummy_robot"]