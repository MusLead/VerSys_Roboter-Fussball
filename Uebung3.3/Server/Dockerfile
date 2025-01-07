# Use the official Ubuntu base image
FROM ubuntu:20.04

# Set environment variables to avoid user prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
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

# Install required Python libraries
RUN python3 -m pip install grpcio grpcio-tools protobuf stomp.py

# Verify installations
RUN python3 --version && pip --version && python3 -m pip show grpcio

# Install ActiveMQ 6.1.4
ENV ACTIVEMQ_VERSION=6.1.4
ENV ACTIVEMQ_HOME=/opt/activemq

# Install ActiveMQ 6.1.4
ENV ACTIVEMQ_VERSION=6.1.4
ENV ACTIVEMQ_HOME=/opt/activemq

ADD https://dlcdn.apache.org/activemq/${ACTIVEMQ_VERSION}/apache-activemq-${ACTIVEMQ_VERSION}-bin.tar.gz /tmp/activemq.tar.gz
RUN tar -xzf /tmp/activemq.tar.gz -C /opt/ && \
    mv /opt/apache-activemq-${ACTIVEMQ_VERSION} ${ACTIVEMQ_HOME} && \
    rm /tmp/activemq.tar.gz && \
    ln -s ${ACTIVEMQ_HOME}/bin/activemq /usr/local/bin/activemq && \
    # Modify jetty.xml to set host to 0.0.0.0 for external access
    # https://knowledge.informatica.com/s/article/000220326?language=en_US 
    sed -i 's\127.0.0.1\0.0.0.0\g' ${ACTIVEMQ_HOME}/conf/jetty.xml

# Expose ActiveMQ default ports
EXPOSE 61613 8161

# Set the working directory inside the container
WORKDIR /code

# Copy the Controller directory (for gRPC definitions)
COPY Controller /code/Controller

# Copy the Server directory (including server.py)
COPY Server /code/Server

# Set the default working directory for the server
WORKDIR /code/Server

# Start ActiveMQ and the Python server
CMD ["/bin/sh", "-c", "activemq start && exec python3 -u server.py"]
