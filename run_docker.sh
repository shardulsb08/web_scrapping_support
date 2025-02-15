#!/bin/bash

# Build the Docker image and tag it as 'scrapping_tool'
docker build -t scrapping_tool .

# Check if a URL argument was provided; if not, prompt the user
if [ "$#" -eq 0 ]; then
    read -p "Enter the URL to analyze: " url
else
    url="$1"
fi

# Run the container, passing the URL as an argument
docker run --rm scrapping_tool "$url"
