# Use Alpine Linux 3.15 as the base image
FROM eclipse-temurin:21

# Set the working directory inside the container
WORKDIR /code

# Copy application source code to the container
COPY ClientGradle .

# # Compile the Java application with preview features enabled
RUN ./gradlew build

# Run the Java application
# To avoid this message: 
# "Starting a Gradle Daemon, 1 incompatible and 1 stopped Daemons could not be reused"
# We add the --no-daemon flag
# The server IP is 192.168.1.100

# Run the Java application
CMD ["sh", "-c", "./gradlew run --no-daemon --args='192.168.1.100' & tail -f /dev/null"]
