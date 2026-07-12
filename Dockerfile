FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Environment variables (override at runtime)
ENV FIREWORKS_API_KEY=""
ENV FIREWORKS_MODEL="accounts/fireworks/models/minimax-m3"
ENV LOCAL_MODEL="gemma2:2b"
ENV COMPLEXITY_THRESHOLD=3
ENV OLLAMA_BASE_URL="http://host.docker.internal:11434"

# Start server
CMD ["python", "server.py"]

HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["python", "server.py"]