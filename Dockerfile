# Use Ubuntu 24.04 as the base image
FROM ubuntu:24.04

# Disable interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and extra libraries for Chrome.
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    curl \
    gnupg \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    libgtk-3-0 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (stable)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Create a symlink so that 'python' points to 'python3'
RUN ln -s /usr/bin/python3 /usr/bin/python

# Copy your application files
COPY recommend_scrapping_tool.py /app/recommend_scrapping_tool.py
COPY selenium_utils.py /app/selenium_utils.py

# Set working directory
WORKDIR /app

# Install Python dependencies. We add webdriver-manager to manage the ChromeDriver.
RUN pip3 install --break-system-packages --no-cache-dir requests beautifulsoup4 selenium webdriver-manager

# Run the application in unbuffered mode
CMD ["python3", "-u", "recommend_scrapping_tool.py"]
