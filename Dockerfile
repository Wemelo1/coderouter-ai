# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that the application runs on
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the backend server
CMD ["python", "server.py"]
