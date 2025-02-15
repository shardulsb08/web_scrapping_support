# Use Ubuntu 24.04 as the base image
FROM ubuntu:24.04

# Disable interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    chromium-browser \
    chromium-chromedriver \
    wget \
    curl \
    gnupg \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    libgtk-3-0 \
    libgbm1 \
    libasound2t64 \
    && rm -rf /var/lib/apt/lists/*

# (Optional) Create a symlink so that 'python' points to 'python3'
RUN ln -s /usr/bin/python3 /usr/bin/python

# Copy your scraping script into the container.
# Ensure your file is named 'recommend_scrapping_tool.py' and located in the same directory as this Dockerfile.
COPY recommend_scrapping_tool.py /app/recommend_scrapping_tool.py
COPY selenium_utils.py /app/selenium_utils.py

# Set the working directory
WORKDIR /app

# Install required Python packages with override flag.
RUN pip3 install --break-system-packages --no-cache-dir requests beautifulsoup4 selenium

RUN chromium-browser --version && chromedriver --version

# (Optional) Set the DISPLAY variable if needed (for headless operation, this is usually not required)
ENV DISPLAY=:99

# By default, run the script when the container starts.
CMD ["python3", "recommend_scrapping_tool.py"]
