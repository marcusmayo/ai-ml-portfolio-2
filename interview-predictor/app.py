"""
FastAPI backend for Interview Predictor
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import traceback
from datetime import datetime

from utils.asr_processor import ASRProcessor
from utils.nlp_analyzer import NLPAnalyzer
from utils.ensemble_scorer import EnsembleScorer

app = FastAPI(title="Interview Predictor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html", "r") as f:
        return f.read()


@app.post("/api/analyze-audio")
async def analyze_audio(
    file: UploadFile = File(...),
    model_size: str = Form("base")
):
    """Analyze uploaded audio file"""
    
    if file.size > 200 * 1024 * 1024:
        raise HTTPException(400, "File too large. Max 200MB.")
    
    temp_file = None
    
    try:
        # Save uploaded file
        suffix = os.path.splitext(file.filename)[1]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        
        content = await file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Transcribe
        print(f"Transcribing with model: {model_size}")
        asr = ASRProcessor(model_size=model_size)
        transcription_result = asr.transcribe_audio(temp_file.name)
        transcript_text = transcription_result["text"]
        print(f"Transcription complete: {len(transcript_text)} characters")
        
        # Analyze
        print("Starting NLP analysis")
        nlp_analyzer = NLPAnalyzer()
        analysis = nlp_analyzer.analyze_all(transcript_text)
        print("NLP analysis complete")
        
        # Score
        print("Calculating ensemble score")
        scorer = EnsembleScorer()
        results = scorer.calculate_ensemble_score(analysis)
        print(f"Score calculated: {results['score']}%")
        
        return JSONResponse({
            "success": True,
            "transcript": transcript_text[:500] + "..." if len(transcript_text) > 500 else transcript_text,
            "prediction": results["prediction"],
            "score": results["score"],
            "confidence": results["confidence"],
            "component_scores": results["component_scores"],
            "component_contributions": results["component_contributions"],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(500, f"Analysis failed: {str(e)}")
        
    finally:
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


@app.post("/api/analyze-text")
async def analyze_text(transcript: str = Form(...)):
    """Analyze text transcript"""
    
    try:
        nlp_analyzer = NLPAnalyzer()
        analysis = nlp_analyzer.analyze_all(transcript)
        
        scorer = EnsembleScorer()
        results = scorer.calculate_ensemble_score(analysis)
        
        return JSONResponse({
            "success": True,
            "prediction": results["prediction"],
            "score": results["score"],
            "confidence": results["confidence"],
            "component_scores": results["component_scores"],
            "component_contributions": results["component_contributions"],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@app.get("/health")
async def health():
    return {"status": "healthy"}
