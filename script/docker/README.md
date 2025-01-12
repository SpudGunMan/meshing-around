# How do I use this thing?
This is not a full turnkey setup for Docker yet but gets you most of the way there!

## Setup New Image
`docker build -t meshing-around .`

## Ollama Image with compose
still a WIP
`docker compose up -d`

## Edit the config.ini in the docker
To edit the config.ini in the docker you can
`docker run -it --entrypoint /bin/bash meshing-around -c "nano /app/config.ini"`

## other info
1. Ensure your serial port is properly shared.
2. Run the Docker container:
    ```sh
    docker run --rm -it --device=/dev/ttyUSB0 meshing-around
    ```