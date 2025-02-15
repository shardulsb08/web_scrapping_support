#!/bin/bash

# Build the Docker image and tag it as 'scrapping_tool'
docker build -t scrapping_tool .

# Run the container and remove it after exit
docker run -it --rm scrapping_tool
