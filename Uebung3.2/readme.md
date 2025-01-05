# Übung 3.2

## Deployment

The configuration within `docker-compose.yml` allows the server to be accessed within a web browser.
To deploy these containers, two commands must be executed:

1. Build the image and deploy the container

    For UNIX Based OS

    ```sh
    docker compose up --build -d
    ```

    For Linux

    ```sh
    docker-compose up --build -d
    ```

2. You can also scale the robot with the command below i.e 5 robot containers

    For UNIX Based OS

    ```sh
    docker compose up --scale robot=5 --build -d
    ```

    For Linux

    ```sh
    docker-compose up --scale robot=5 --build -d
    ```

3. You could check the containers are running, get the id and the port:
  
    ```sh
    docker ps -a
    ```

## Interactive Mode

To accesss the robot i.e. sending health status you could use this command below. After that write 'h' or 'help' to get information for access

```sh
docker attach <name of robot>
```

## gRPC

- Create proto API files:

```sh
python -m grpc_tools.protoc --proto_path=./controller --python_out=./Controller --grpc_python_out=./Controller robot_controller.proto
```

References:

- <https://www.kirilv.com/canvas-confetti/>
- <https://www.docker.com/>
- <https://hub.docker.com>
- <https://alpinelinux.org/>
- <https://pkgs.alpinelinux.org/packages>
