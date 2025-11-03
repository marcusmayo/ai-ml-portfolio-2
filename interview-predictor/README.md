# 🎯 Interview Predictor - AI-Powered Interview Analysis

Real-time interview performance prediction using speech-to-text, NLP sentiment analysis, and machine learning.

![Demo](static/demo.gif)

## ✨ Features

- **Multi-Model ASR**: Supports Whisper Tiny, Base, Small, and Medium models
- **Real-time Analysis**: Live progress tracking with SSE
- **Component Scoring**: Sentiment, toxicity, competency, and keyword analysis
- **Performance Timeline**: Visualize performance across interview duration
- **AI Feedback**: Gemini-powered actionable feedback generation
- **GPU Acceleration**: CUDA support for faster processing

## 🚀 Quick Start (Local)

### Prerequisites

- Ubuntu 22.04+ (or similar Debian-based system)
- Python 3.11+
- NVIDIA GPU with CUDA 12.1+ (optional, for acceleration)
- 8GB+ RAM
- 20GB+ disk space

### One-Command Install
```bash
sudo bash install_local.sh
```

### Manual Setup

See [README_LOCAL.md](README_LOCAL.md) for detailed local deployment instructions.

## 🐳 Docker Deployment (Recommended)

### Quick Start
```bash
# Clone repository
git clone <your-repo-url>
cd interview-predictor

# Create .env file
echo "GEMINI_API_KEY=your-key-here" > .env

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Docker Configuration

- **Port**: 8080 (configurable in `docker-compose.yml`)
- **GPU Support**: Automatically detected
- **Volume**: Data persists in `./data`

## 📊 Architecture
```
┌─────────────┐
│   Frontend  │ (Streamlit/HTML)
│  (Browser)  │
└──────┬──────┘
       │ HTTP
┌──────▼──────┐
│   FastAPI   │ (API Server)
│   Backend   │
└──────┬──────┘
       │
┌──────▼──────────────────────────────┐
│        Core Components               │
├──────────────┬──────────────────────┤
│ ASR          │ Faster-Whisper       │
│ NLP          │ Transformers         │
│ Scoring      │ Ensemble ML          │
│ Timeline     │ Temporal Analysis    │
│ Feedback     │ Gemini API           │
└──────────────┴──────────────────────┘
```

## 🧪 Testing
```bash
# Test audio analysis
curl -X POST http://localhost:8080/api/analyze-audio \
  -F "file=@sample.mp3" \
  -F "model_size=base"

# Test text analysis
curl -X POST http://localhost:8080/api/analyze-text \
  -F "text=I have 5 years of experience in Python"

# Health check
curl http://localhost:8080/health
```

## 📈 Component Scoring

| Component | Weight | Description |
|-----------|--------|-------------|
| Sentiment | 25% | Positive vs negative emotional tone |
| Toxicity | 25% | Professional language (inverted toxicity) |
| Competency | 30% | Technical skills and role fit |
| Keywords | 20% | Interview signals and professionalism |

**Overall Score Ranges**:
- **70-100%**: Strong (High confidence)
- **50-69%**: Moderate (Medium confidence)
- **0-49%**: Weak (Low confidence)

## 🛠️ Development

### Project Structure
```
interview-predictor/
├── app.py                      # FastAPI main application
├── static/
│   └── index.html             # Web interface
├── utils/
│   ├── asr_processor.py       # Audio transcription
│   ├── nlp_analyzer.py        # Sentiment/toxicity analysis
│   ├── ensemble_scorer.py     # Score calculation
│   ├── timeline_analyzer.py   # Performance timeline
│   └── llm_feedback.py        # AI feedback generation
├── requirements-local.txt      # Python dependencies
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Docker orchestration
├── install_local.sh           # Local installation script
└── start_local.sh             # Local startup script
```

### Key Dependencies

- **FastAPI**: Modern web framework
- **PyTorch**: Deep learning (CUDA 12.1)
- **Transformers**: NLP models
- **Faster-Whisper**: Efficient ASR
- **Gemini API**: AI feedback generation

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
GEMINI_API_KEY=your-api-key-here
```

### Model Selection

| Model | Size | Accuracy | Speed | Best For |
|-------|------|----------|-------|----------|
| Tiny | 39M | ⭐⭐⭐ | 3-5 min/30min | Quick demos |
| Base | 74M | ⭐⭐⭐⭐ | 5-8 min/30min | Balanced (recommended) |
| Small | 244M | ⭐⭐⭐⭐⭐ | 10-15 min/30min | Higher accuracy |
| Medium | 769M | ⭐⭐⭐⭐⭐ | 20-30 min/30min | Maximum accuracy |

## 📝 API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

### Key Endpoints

- `POST /api/analyze-audio` - Analyze audio file
- `POST /api/analyze-text` - Analyze text input
- `POST /api/generate-feedback` - Generate AI feedback
- `GET /api/model-info` - Get model information
- `GET /api/progress` - SSE progress stream
- `GET /health` - Health check

## ⚠️ Known Issues & Solutions

### NumPy Version
**Issue**: ImportError with transformers
**Solution**: Ensure `numpy<2.0` (critical for transformers 4.44.2)

### PyTorch Version Mismatch
**Issue**: torchvision::nms errors
**Solution**: Use PyTorch 2.5.1 with torchvision 0.20.1

### GPU Not Detected
**Issue**: CUDA not available
**Solution**: Verify NVIDIA drivers and CUDA 12.1+ installation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- **OpenAI Whisper**: Speech recognition
- **Hugging Face**: NLP models
- **Anthropic**: Claude AI assistance
- **Google Gemini**: Feedback generation

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for better interview experiences**
