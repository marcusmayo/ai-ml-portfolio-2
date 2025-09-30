# Interview Predictor - AI-Powered Interview Analysis

**An intelligent system that analyzes interview transcripts and recordings to predict interview outcomes using ensemble ML techniques.**

## Overview

This application combines speech-to-text (ASR), natural language processing, and ensemble scoring to provide insights into interview performance. It's designed as a self-coaching tool to help candidates understand their interview strengths and areas for improvement.

## Features

- **Multi-Input Support**: Upload audio files (mp3, wav, m4a) or text transcripts
- **Automatic Speech-to-Text**: Uses faster-whisper for efficient transcription
- **Multi-Dimensional Analysis**:
  - Sentiment analysis (positive/negative tone)
  - Toxicity detection (professional language screening)
  - Competency assessment (zero-shot classification)
  - Keyword detection (interviewer cues)
  - Filler word analysis
- **Ensemble Prediction**: Combines multiple signals into a single outcome: Likely / Unlikely / Inconclusive
- **Interactive Dashboard**: Streamlit-based UI with visual breakdowns
- **Production Monitoring**: Prometheus metrics for tracking model health

## Tech Stack

- **ASR**: faster-whisper (CTranslate2 optimized)
- **NLP Models**: cardiffnlp/twitter-roberta-base-sentiment-latest, unitary/toxic-bert, MoritzLaurer/mDeBERTa-v3-base-mnli-xnli
- **Framework**: Streamlit
- **Cloud**: Google Cloud Platform (Cloud Run ready)
- **Monitoring**: Prometheus

## Quick Start

Local Development: pip install -r requirements.txt, then streamlit run dashboard.py

Cloud Deployment: gcloud run deploy interview-predictor --source . --platform managed --region us-central1 --allow-unauthenticated

## Sample Data

Try the app with pre-loaded sample transcripts in data/sample/

## Responsible AI

This tool is for self-coaching and learning purposes only. NOT for hiring decisions. Predictions are guidance, not truth. Human judgment remains essential.

## Author

Marcus Mayo - GitHub: marcusmayo

## License

MIT License
