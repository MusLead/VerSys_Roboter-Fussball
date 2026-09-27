# Stage 1: Build the application using a minimal JDK
FROM amazoncorretto:21-alpine AS builder

# Set the working directory inside the container
WORKDIR /build

# Install dependencies required for Gradle
RUN apk add --no-cache bash curl

# Copy application source code
COPY ClientGradle .

# Grant execution permission to Gradle wrapper
RUN chmod +x ./gradlew

# Build the application
RUN ./gradlew build --no-daemon

# Stage 2: Create a minimal runtime environment
FROM alpine:3.15

# Enable Alpine Edge Testing Repository (for OpenJDK 21)
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories && \
    apk add --no-cache bash curl openjdk21

# Set the working directory
WORKDIR /app

# Copy application source code and Gradle wrapper from builder stage
COPY --from=builder /build .

# Grant execution permission to Gradle wrapper again (in case it's reset)
RUN chmod +x ./gradlew

# Run the Java application
# To avoid this message: 
# "Starting a Gradle Daemon, 1 incompatible and 1 stopped Daemons could not be reused"
# We add the --no-daemon flag

# Run the Java application using Gradle
CMD ["sh", "-c", "./gradlew run --no-daemon & tail -f /dev/null"]
