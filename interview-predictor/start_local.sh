#!/bin/bash
set -e

echo "========================================"
echo "  Interview Predictor - Local Startup"
echo "========================================"

# Change to project directory
cd /home/ubuntu/ai-ml-portfolio-2/interview-predictor

# Check if API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set!"
    echo "Please export GEMINI_API_KEY before running this script"
    exit 1
fi

echo "✓ API key configured"

# Verify key packages are installed
echo "Checking dependencies..."
python3 -c "import fastapi, torch, transformers, faster_whisper, google.generativeai" 2>/dev/null || {
    echo "❌ Missing dependencies. Please run: sudo bash install_local.sh"
    exit 1
}

echo "✓ All dependencies present"

# Show versions
echo ""
echo "Package Versions:"
python3 -c "import fastapi, torch, transformers, numpy; print(f'  FastAPI: {fastapi.__version__}'); print(f'  PyTorch: {torch.__version__}'); print(f'  Transformers: {transformers.__version__}'); print(f'  NumPy: {numpy.__version__}'); print(f'  CUDA Available: {torch.cuda.is_available()}')"

echo ""
echo "Starting server on http://0.0.0.0:8080"
echo "Press CTRL+C to stop"
echo "========================================"
echo ""

# Start uvicorn
python3 -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
