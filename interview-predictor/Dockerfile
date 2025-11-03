# Start with Python 3.11 (smaller, faster version)
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies
# FFmpeg = needed for audio processing
# libsndfile1 = needed for audio files
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first (for caching)
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Create directories for uploads and data
RUN mkdir -p uploads data/raw data/processed data/models

# Expose port 8080 (where app will run)
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Command to run when container starts
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
