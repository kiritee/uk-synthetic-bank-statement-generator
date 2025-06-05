FROM python:3.12-slim

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    build-essential libffi-dev libssl-dev curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools


# Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -e .

# Set default command
ENTRYPOINT ["bankgen"]
