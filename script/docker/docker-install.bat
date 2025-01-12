REM batch file to install docker on windows
REM docker compose up -d
cd ../../
docker build -t meshing-around .
REM docker-compose up -d
docker run -it --entrypoint /bin/bash meshing-around -c "nano /app/config.ini"