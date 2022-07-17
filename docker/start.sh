cd ..

docker rmi automod-docker -f

docker build -t automod-docker -f ./docker/Dockerfile .
docker run  --network="bridge" -p 5050:5000 automod-docker