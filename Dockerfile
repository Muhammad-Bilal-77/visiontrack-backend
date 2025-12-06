# Use Python 3.11 slim image with better binary wheel support
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV, face-recognition, and build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    libopenblas-dev \
    liblapack-dev \
    libx11-6 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# Run via entrypoint (handles collectstatic/migrate at runtime with env vars available)
ENTRYPOINT ["/entrypoint.sh"]
