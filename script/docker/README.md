# How do I use this thing?
This is not a full turnkey setup for Docker yet


## other info
1. Ensure your serial port is properly shared.
2. Run the Docker container:
    ```sh
    docker run --rm -it --device=/dev/ttyUSB0 meshing-around
    ```