# AI Interview Predictor

AI-powered interview analysis system using WhisperX, transformer models, and Google Gemini.

## 🚀 Features

- **Audio Transcription**: WhisperX with GPU acceleration for fast, accurate transcription
- **NLP Analysis**: Sentiment, toxicity, and competency assessment using RoBERTa models
- **AI Feedback**: Context-aware feedback generation using Google Gemini
- **Real-time Processing**: FastAPI backend with async processing
- **Modern UI**: Clean, responsive interface with progress tracking

## 📋 System Requirements

- Python 3.12+
- CUDA 12.8 (for GPU acceleration)
- 16GB RAM minimum
- NVIDIA GPU (T4 or better recommended)

## 🛠️ Installation

### Local Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd interview-predictor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install PyTorch with CUDA 12.8
pip install torch==2.8.0 torchaudio==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cu128

# Install other dependencies
pip install -r requirements-minimal.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Docker Setup
```bash
# Build and run with docker-compose
docker-compose up --build

# Or build manually
docker build -t interview-predictor .
docker run -p 8080:8080 -e GEMINI_API_KEY=your_key interview-predictor
```

## 🚀 Quick Start
```bash
# Start the server
uvicorn app:app --host 0.0.0.0 --port 8080

# Open in browser
http://localhost:8080
```

## 📦 Tech Stack

- **Backend**: FastAPI, Python 3.12
- **ML/AI**: 
  - WhisperX 3.7.4 (speech recognition)
  - Transformers 4.48+ (NLP models)
  - PyTorch 2.8.0 (CUDA 12.8)
  - Google Gemini (feedback generation)
- **Frontend**: HTML5, JavaScript, CSS3
- **Deployment**: Docker, AWS EC2

## 📁 Project Structure
```
interview-predictor/
├── app.py                      # FastAPI main application
├── utils/
│   ├── asr_processor.py       # WhisperX audio transcription
│   ├── nlp_analyzer.py        # NLP analysis (sentiment, toxicity, competency)
│   ├── ensemble_scorer.py     # Score aggregation
│   └── timeline_analyzer.py   # Timeline processing
├── static/
│   ├── css/
│   └── js/
├── templates/
│   └── index.html
├── requirements.txt           # Full dependencies
├── requirements-minimal.txt   # Clean dependencies
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8080
```

### Whisper Model Options

- `tiny`: Fastest (39M params, ~5 min for 80MB audio)
- `base`: Balanced (74M params, ~8 min for 30min audio) ⭐ Recommended
- `small`: Higher accuracy (244M params, ~15 min)
- `medium`: Maximum accuracy (769M params, ~30 min)

## 📊 Analysis Components

1. **Sentiment Analysis**: Emotional tone detection (86% weight)
2. **Toxicity Detection**: Inappropriate content screening (100% weight)
3. **Competency Assessment**: Technical skill evaluation (25% weight)
4. **Keyword Matching**: Industry-specific term detection (50% weight)
5. **Filler Word Penalty**: Speech fluency scoring (variable weight)

## 🎯 Prediction Thresholds

- **Likely** (70%+): Strong interview performance
- **Inconclusive** (40-70%): Mixed signals, review needed
- **Unlikely** (<40%): Significant improvement areas

## 🐛 Troubleshooting

### PyTorch Version Issues
If you see "torch.load vulnerability" errors:
```bash
pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128
```

### CUDA Not Available
Check CUDA installation:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

### Memory Issues
Reduce batch size or use smaller model:
```python
# In asr_processor.py
batch_size = 8  # Reduce from 16
```

## 📝 License

MIT License

## 👥 Contributing

Contributions welcome! Please open an issue or PR.

## 🙏 Acknowledgments

- WhisperX by Max Bain
- Hugging Face Transformers
- Google Gemini API
