FROM python:3.12-slim

# Use args
ARG MINIMUM_BUILD
ARG USE_CUDA
ARG USE_CUDA_VER

RUN apt-get update && \
    apt-get install -y gcc build-essential curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

## Basis ##
ENV ENV=prod \
    MINIMUM_BUILD=${MINIMUM_BUILD} \ 
    USE_CUDA_DOCKER=${USE_CUDA} \
    USE_CUDA_DOCKER_VER=${USE_CUDA_VER}



RUN pip3 install uv
RUN if [ "$MINIMUM_BUILD" != "true" ]; then \
        if [ "$USE_CUDA_DOCKER" = "true" ]; then \
            pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/$USE_CUDA_DOCKER_VER --no-cache-dir; \
        else \
            pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --no-cache-dir; \    
        fi \
    fi

# Installer curl
RUN apt-get update && apt-get install -y curl && apt-get clean
RUN apt-get update && apt-get install -y git && apt-get clean
RUN apt-get update && apt-get install -y iputils-ping
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    gcc \
    cmake \
    make \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN curl -sSL https://install.python-poetry.org | python3.12 -
RUN    export PATH="/root/.local/bin:$PATH" 
ENV PATH="/root/.local/bin:$PATH"