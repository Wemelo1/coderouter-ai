FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck use in compose
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Default entrypoint: batch runner for evaluation
CMD ["python", "batch_runner.py"]
