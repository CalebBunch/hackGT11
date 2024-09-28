CONTAINER_NAME=test_container
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Starting existing container $CONTAINER_NAME..."
    docker start $CONTAINER_NAME
else
    echo "Building the Docker image..."
    docker build -t test .

    echo "Running a new container..."
    docker run --name $CONTAINER_NAME -p 8001:8001 -it test
fi

