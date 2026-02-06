# Use official Python runtime as base image
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set environment variables
ENV PATH="/root/.cargo/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Create workspace directory
WORKDIR /workspace

# Install initial dependencies will be done by postCreateCommand
CMD ["/bin/bash"]
