# Skilly Universal Docker Container
# Run anywhere with zero dependencies:
#   docker run --rm -v $(pwd):/project ghcr.io/arastuthakur/skilly /project

FROM python:3.11-slim

LABEL maintainer="Arastu Thakur <arustuthakur@gmail.com>"
LABEL description="Autonomous LLM-free project capability analyzer and interactive knowledge graph synthesizer."

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY pyproject.toml setup.py README.md ./
COPY skilly_core/ ./skilly_core/
COPY skilly.py ./

# Install skilly
RUN pip install --no-cache-dir .

WORKDIR /project

ENTRYPOINT ["skilly"]
CMD ["."]
