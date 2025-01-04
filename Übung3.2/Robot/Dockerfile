# https://hub.docker.com/_/alpine
FROM alpine:latest

# install pip
RUN apk add --update-cache \
    py3-pip \
  && rm -rf /var/cache/apk/*

# Copy the Controller directory (for gRPC definitions)
COPY Controller /code/Controller

# Copy the Robot directory
COPY Robot /code/Robot

# Install dependencies
RUN pip install grpcio grpcio-tools

# Set the default working directory for the robot
WORKDIR /app/Robot

# add -u flag to avoid buffering (print output immediately in the docker console)
# run the application
ENTRYPOINT ["python3","-u", "robot.py"]