FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libsqlite3-dev zlib1g-dev curl unzip \
    && git clone --depth 1 --branch 2.79.0 https://github.com/felt/tippecanoe.git /tmp/tippecanoe \
    && make -C /tmp/tippecanoe -j2 \
    && make -C /tmp/tippecanoe install \
    && curl -fsSL https://github.com/duckdb/duckdb/releases/download/v1.5.5/duckdb_cli-linux-amd64.zip -o /tmp/duckdb.zip \
    && echo '08c0ca117111fcede14239d0093792352befdc174218c344d232c13279643d05  /tmp/duckdb.zip' | sha256sum -c - \
    && unzip -p /tmp/duckdb.zip duckdb > /usr/local/bin/duckdb \
    && chmod +x /usr/local/bin/duckdb \
    && curl -fsSL https://github.com/protomaps/go-pmtiles/releases/download/v1.31.2/go-pmtiles_1.31.2_Linux_x86_64.tar.gz -o /tmp/pmtiles.tar.gz \
    && echo '3ed7dbf4ec2e6dfe5e25b6f70d1ffc932729f93c86db353bf514dd71010a312f  /tmp/pmtiles.tar.gz' | sha256sum -c - \
    && tar -xzOf /tmp/pmtiles.tar.gz pmtiles > /usr/local/bin/pmtiles \
    && chmod +x /usr/local/bin/pmtiles \
    && duckdb -c 'SELECT 1' \
    && pmtiles version \
    && rm -rf /tmp/tippecanoe /tmp/duckdb.zip /tmp/pmtiles.tar.gz /var/lib/apt/lists/*
