# Use Alpine Linux 3.15 as the base image
FROM alpine:3.15

# Install necessary packages and dependencies
RUN apk update && \
    apk add --no-cache \
        openjdk16-jdk \
        tzdata \
        curl \
        unzip \
        bash \
        coreutils \
        ca-certificates && \
    update-ca-certificates

# Set the working directory inside the container
WORKDIR /code

# Copy application source code to the container
COPY . .

# Compile the Java application with preview features enabled
RUN javac --release 16 --enable-preview Simple_Client.java

# Expose the application port
# EXPOSE 8080

# Command to run the Java application with preview features enabled
CMD ["sh", "-c", "sleep 10 && java --enable-preview Simple_Client 192.168.1.100 & tail -f /dev/null"]
