FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch 2.8.0 (CUDA 12.8) - WORKING VERSION
RUN pip install --no-cache-dir \
    torch==2.8.0 \
    torchaudio==2.8.0 \
    torchvision==0.23.0 \
    --index-url https://download.pytorch.org/whl/cu128

# Install NumPy 2.0.x (WhisperX requirement)
RUN pip install --no-cache-dir 'numpy>=2.0.2,<2.1.0'

# Install transformers >=4.48.0
RUN pip install --no-cache-dir 'transformers>=4.48.0' tokenizers sentencepiece

# Install WhisperX and dependencies
RUN pip install --no-cache-dir whisperx faster-whisper

# Install ML libraries
RUN pip install --no-cache-dir scipy pandas scikit-learn accelerate

# Install audio libraries
RUN pip install --no-cache-dir soundfile librosa audioread decorator lazy-loader msgpack numba pooch soxr

# Install Google API
RUN pip install --no-cache-dir google-generativeai google-api-core google-auth

# Install web framework
RUN pip install --no-cache-dir fastapi==0.115.0 uvicorn==0.32.0 starlette python-multipart pydantic typing-extensions

# Copy application
COPY app.py .
COPY utils/ ./utils/
COPY static/ ./static/

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8080

# Run app
CMD ["python", "app.py"]
