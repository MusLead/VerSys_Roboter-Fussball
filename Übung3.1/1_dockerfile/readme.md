# Introduction to Containerization with Docker

In this exercise, we will build a Docker image with a web application, run it, and terminate it finally. This can be done in a local VM or in a Cloud.

 1. Have a look to the steps in the Dockerfile to see what happens during the build process.
 2. Build an image with name `controller`:

  ```sh
    docker build . -t controller
  ```
  
 3. List the images available on your host and verify that there is a `controller` image:

  ```sh
  docker images
  ```

 4. Launch a container from the image. We expose the port from the container to port 80 on the local machine:
  
  ```sh
  docker run -p 80:8080 -d controller
  ```

 5. Check that the container is running and get the id:
  
  ```sh
  docker ps -a
  ```

 6. Now we check that the service we just created by opening `http://hostname` in a webbrowser.
 7. Let's enter the container:

  ```sh
  docker exec -it <container id> /bin/bash
  ```

or if it does not work, then

  ```sh
  docker exec -it <container id> /bin/sh
  ```

 8. Stop the container:

  ```sh
  docker stop <container id>
  ```

 9. Remove the containers:
  
  ```sh
  docker rm <container id>
  ```

 10. Remove the images from your host:
  
  ```sh
  docker rmi controller
  ```

References:

- <https://www.kirilv.com/canvas-confetti/>
- <https://www.docker.com/>
- <https://hub.docker.com>
- <https://alpinelinux.org/>
- <https://pkgs.alpinelinux.org/packages>
