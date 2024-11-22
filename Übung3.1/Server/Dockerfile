# https://hub.docker.com/_/alpine
FROM alpine:latest

# install pip
RUN apk add --update-cache \
    py3-pip \
  && rm -rf /var/cache/apk/*

# create app directory
WORKDIR /code

# bundle app source
COPY . .

# our application will listen on port 5000 inside the container
# EXPOSE 8080

# add -u flag to avoid buffering (print output immediately in the docker console)
# run the application
CMD ["python3","-u", "Simple_Server.py"]