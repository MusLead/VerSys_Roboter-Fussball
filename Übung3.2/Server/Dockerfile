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

# add -u flag to avoid buffering (print output immediately in the docker console)
# run the application
CMD ["python3","-u", "server.py"]