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
        openjdk-17-jdk \
        wget \
        unzip \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the latest version of pip for Python 3.10
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# Upgrade pip to the latest version
RUN python3 -m pip install --upgrade pip

# Install the grpcio library and required dependencies
RUN python3 -m pip install grpcio grpcio-tools protobuf stomp.py

# Install ActiveMQ
ENV ACTIVEMQ_VERSION=6.1.4
ENV ACTIVEMQ_HOME=/opt/activemq

RUN wget https://dlcdn.apache.org/activemq/${ACTIVEMQ_VERSION}/apache-activemq-${ACTIVEMQ_VERSION}-bin.tar.gz -O /tmp/activemq.tar.gz && \
    tar -xzf /tmp/activemq.tar.gz -C /opt/ && \
    mv /opt/apache-activemq-${ACTIVEMQ_VERSION} ${ACTIVEMQ_HOME} && \
    rm /tmp/activemq.tar.gz && \
    ln -s ${ACTIVEMQ_HOME}/bin/activemq /usr/local/bin/activemq

# Expose ActiveMQ default ports
EXPOSE 61616 8161

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
