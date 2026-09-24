FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libsqlite3-dev zlib1g-dev \
    && git clone --depth 1 https://github.com/felt/tippecanoe.git /tmp/tippecanoe \
    && make -C /tmp/tippecanoe -j2 \
    && make -C /tmp/tippecanoe install \
    && rm -rf /tmp/tippecanoe /var/lib/apt/lists/*
