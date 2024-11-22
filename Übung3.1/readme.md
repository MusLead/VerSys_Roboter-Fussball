# Übung 3.1

In this exercise we have two containers, `Server` and `Client`. They are a simple HTTP server-client communication that will be used for the future task.

## Deployment

The configuration within `docker-compose.yml` allows the server to be accessed within a web browser.
To deploy these containers, two commands must be executed:

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

3. You could check the containers are running, get the id and the port:
  
    ```sh
    docker ps -a
    ```

## Server and Client

The server is deployed first, followed by the client. Since the server must be online before the client can send an HTTP request, and considering the client's build, testing, and execution time using Gradle, there is no need to wait after starting the server before running the client.

With this command below you could see the result of the client deployment:

```sh
docker logs client_container
```

You should see such a result below from the `client_container`

```sh
POST /:
Expected Status: 200, Actual Status: 200
Expected Response: Server is running, Actual Response:  Server is running

Pass
```

Also, with this command below you could see the requests and the logs of the server deployment:

```sh
docker logs server_container
```

You could also try to request GET HTTP to the server using `http://localhost:8080` on your local computer.

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
