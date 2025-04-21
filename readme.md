# Docker
## Comando para levantar el docker

docker run -d --mount type=bind,source=/home/ubuntu/meta,target=/app/data --restart always -e USERNAME='sheryl.ter34@gmail.com' -e PASSWORD='Blueocean-299' -v /dev/shm:/dev/shm jjvnhi/sheryl

## Comando para levantar el docker de prueba

docker run -it --mount type=bind,source="$(pwd)",target=/app/data --restart always -e USERNAME='sheryl.ter34@gmail.com' -e PASSWORD='Blueocean-299' jjvnhi/sheryl