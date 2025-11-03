#!/bin/bash
set -e

echo "========================================"
echo "  Interview Predictor - Local Setup"
echo "========================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo: sudo bash install_local.sh"
    exit 1
fi

echo "Step 1/4: Installing system dependencies..."
apt-get update
apt-get install -y \
    python3-scipy \
    ffmpeg \
    libavformat-dev libavcodec-dev libavdevice-dev \
    libavutil-dev libavfilter-dev libswscale-dev \
    libswresample-dev pkg-config \
    libopenblas-dev liblapack-dev gfortran build-essential

echo "✓ System dependencies installed"

echo ""
echo "Step 2/4: Installing Python packages..."
pip3 install --break-system-packages \
    fastapi==0.115.0 \
    'uvicorn[standard]==0.30.6' \
    pydantic==2.9.2 \
    python-multipart==0.0.12 \
    httpx==0.27.2 \
    python-dotenv==1.0.0 \
    transformers==4.44.2 \
    safetensors==0.4.3 \
    tokenizers==0.19.1 \
    accelerate==0.20.0 \
    scikit-learn==1.3.0 \
    'numpy>=1.26,<2.0' \
    pandas==2.0.0 \
    faster-whisper==1.0.3 \
    librosa \
    soundfile==0.12.1 \
    google-generativeai==0.8.5 \
    tqdm==4.66.0 \
    requests==2.31.0

echo "✓ Python packages installed"

echo ""
echo "Step 3/4: Installing PyTorch with CUDA support..."
pip3 install --break-system-packages \
    --extra-index-url https://download.pytorch.org/whl/cu121 \
    torch==2.5.1 \
    torchvision==0.20.1 \
    torchaudio==2.5.1

echo "✓ PyTorch installed"

echo ""
echo "Step 4/4: Verifying installation..."
python3 << 'PYEOF'
import fastapi, torch, transformers, faster_whisper, google.generativeai, numpy
print(f"✓ FastAPI {fastapi.__version__}")
print(f"✓ PyTorch {torch.__version__}")
print(f"✓ Transformers {transformers.__version__}")
print(f"✓ NumPy {numpy.__version__}")
print(f"✓ CUDA Available: {torch.cuda.is_available()}")
PYEOF

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Export your API key:"
echo "   export GEMINI_API_KEY='your-key-here'"
echo ""
echo "2. Start the server:"
echo "   cd /home/ubuntu/ai-ml-portfolio-2/interview-predictor"
echo "   ./start_local.sh"
echo ""
