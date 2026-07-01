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

# Expose server port (server.py) and Streamlit port (app.py)
EXPOSE 8000 8501

# Default entrypoint: main web server
CMD ["python", "server.py"]
