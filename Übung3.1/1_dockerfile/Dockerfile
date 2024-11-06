# https://hub.docker.com/_/python
FROM python:3.9

# create app directory
WORKDIR /code

# bundle app source
COPY . .

# our application will listen on port 5000 inside the container
EXPOSE 8080

# run the application
CMD ["python3","-u", "Simple_Server.py"]