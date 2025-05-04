# Use an older official Python image compatible with leek (and likely your app)
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies needed for building some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file and install first to leverage Docker cache
COPY ./celery_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./celery_app /app/

ENV PYTHONPATH=/app:$PYTHONPATH

# Default command can be set here or in docker-compose.yml
# CMD ["celery", "-A", "celery_app.celery_instance:app", "worker", "--loglevel=INFO"] 