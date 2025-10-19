# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ ./src/

# Expose port 8080 (Cloud Run expects this)
EXPOSE 8080

# Set environment variable for production
ENV APP_ENV=production

# Run the application
# Note: We use src as the working directory for imports to work
CMD ["uvicorn", "src.app.api:app", "--host", "0.0.0.0", "--port", "8080"]
