# Übung 3.1

## Deployment and Server

In this exercise we have two containers `Server` and `Client`.
They are a simple HTTP server-client communication that will be used for the future Task.
The configuration within the docker-compose allows the Server to be accessed within a Web-Browser.
To deploy these containers, two command needs to be executed:

1. Build the image (You only need once, as long as the image has been created loacally)

For MacOS

```sh
docker compose build
```

For Linux

```sh
docker-compose build
```

2. Deploy the Containers

For MacOS

```sh
docker compose up -d
```

For Linux

```sh
docker-compose up -d
```

3. You could Check the containers are running and get the id and the port:
  
```sh
docker ps -a
```

You could also try to request GET HTTP using `http://localhost:8080` on your local computer.

## Client

After the deployment, the Client will execute the java program after 10 Seconds.
This will make sure that the Server is properly running after the deployment
and the communication can be established. Without this naive approach (execute after 10 seconds),
the connection might be failed, and the deployment of Client could be disturbed.

With this command below you could see the result of the Client deployment:

```sh
docker logs <container_name_or_id>
```

You shoudl see such a result below

```sh
Actual Host: 192.168.1.100
Starting Host: 192.168.1.100
POST /:
Expected Status: 200, Actual Status: 200
Expected Response: Server is running, Actual Response:  Server is running

Pass
```

## Closing Deployment

To shutdown the containers it could be easily done using a simple line of code below.
The containers will also be deleted by default

For MacOS

```sh
docker compose down -d
```

For Linux

```sh
docker-compose down -d
```

## Additional Information

- List the images available on your host and verify that there is a `controller` image:

  ```sh
  docker images
  ```

- Check that the container is running and get the id:
  
  ```sh
  docker ps -a
  ```

- Entering the container:

  ```sh
  docker exec -it <container id> /bin/bash
  ```

  or if it does not work, then

  ```sh
  docker exec -it <container id> /bin/sh
  ```

- Stop the container:

  ```sh
  docker stop <container id>
  ```

- Remove the container:
  
  ```sh
  docker rm <container id>
  ```

- Remove the images from your host:
  
  ```sh
  docker rmi <name of the image>
  ```

## References

- <https://www.kirilv.com/canvas-confetti/>
- <https://www.docker.com/>
- <https://hub.docker.com>
- <https://alpinelinux.org/>
- <https://pkgs.alpinelinux.org/packages>
- <https://www.baeldung.com/gradle-command-line-arguments>
- <https://hub.docker.com/_/eclipse-temurin>
