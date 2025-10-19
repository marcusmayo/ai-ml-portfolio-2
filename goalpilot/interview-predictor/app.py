"""
FastAPI Interview Predictor with Timeline Analysis
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
from utils.timeline_analyzer import TimelineAnalyzer

app = FastAPI(title="Interview Predictor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main HTML page"""
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>Interview Predictor</h1><p>index.html not found</p>", status_code=500)

@app.get("/api/model-info")
async def model_info():
    """Get information about available models"""
    return {
        "models": [
            {
                "value": "tiny",
                "display": "Tiny - Fastest",
                "size": "39M params",
                "accuracy": "⭐⭐⭐ Good",
                "time_30min": "3-5 min",
                "time_60min": "8-12 min",
                "best_for": "Quick demos, testing"
            },
            {
                "value": "base",
                "display": "Base - Balanced (Recommended)",
                "size": "74M params", 
                "accuracy": "⭐⭐⭐⭐ Very Good",
                "time_30min": "5-8 min",
                "time_60min": "15-20 min",
                "best_for": "Balanced accuracy/speed"
            },
            {
                "value": "small",
                "display": "Small - Higher Accuracy",
                "size": "244M params",
                "accuracy": "⭐⭐⭐⭐⭐ Excellent", 
                "time_30min": "10-15 min",
                "time_60min": "30-40 min",
                "best_for": "Higher accuracy needed"
            },
            {
                "value": "medium",
                "display": "Medium - Maximum Accuracy",
                "size": "769M params",
                "accuracy": "⭐⭐⭐⭐⭐ Excellent",
                "time_30min": "20-30 min", 
                "time_60min": "50-70 min",
                "best_for": "Maximum accuracy"
            }
        ],
        "component_explanations": {
            "sentiment": "Measures positive vs negative emotional tone in responses",
            "toxicity": "Detects unprofessional language or inappropriate content (higher is better)",
            "competency": "Evaluates technical skills and role-specific fit based on answers",
            "keywords": "Identifies positive interviewer signals and professional language use"
        }
    }

@app.post("/api/analyze-audio")
async def analyze_audio(
    file: UploadFile = File(...),
    model_size: str = Form("base")
):
    """Analyze uploaded audio file with timeline"""
    
    if file.size and file.size > 200 * 1024 * 1024:
        raise HTTPException(400, "File too large. Maximum 200MB.")
    
    temp_file = None
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp:
            content = await file.read()
            temp.write(content)
            temp_file = temp.name
        
        # Initialize processors
        asr = ASRProcessor(model_size=model_size)
        nlp = NLPAnalyzer()
        scorer = EnsembleScorer()
        timeline_analyzer = TimelineAnalyzer()
        
        # Transcribe
        asr.load_model()
        transcription = asr.transcribe_audio(temp_file)
        transcript_text = transcription["text"]
        segments = transcription.get("segments", [])
        duration = transcription.get("duration", 0)
        
        # Analyze with NLP
        nlp.load_models()
        sentiment = nlp.analyze_sentiment(transcript_text)
        toxicity = nlp.analyze_toxicity(transcript_text)
        competencies = nlp.analyze_competency(
            transcript_text,
            candidate_labels=["technical skills", "communication", "problem solving", "leadership"]
        )
        keywords = nlp.detect_keywords(
            transcript_text,
            positive_keywords=["experienced", "led", "achieved", "improved", "solved"],
            negative_keywords=["maybe", "I think", "I guess", "not sure"]
        )
        
        # Calculate ensemble score
        results = scorer.calculate_ensemble_score(
            sentiment_scores=sentiment,
            toxicity_score=toxicity["toxic"],
            competency_scores=competencies,
            keyword_match=keywords
        )
        
        # NEW: Generate timeline with real NLP analysis
        print(f"Analyzing {len(segments)} segments for timeline...")
        scored_segments = timeline_analyzer.analyze_segments(segments)
        timeline_data = timeline_analyzer.create_timeline_data(scored_segments, duration)
        print(f"Timeline created with {len(timeline_data.get('bins', []))} bins")
        
        # Return response with timeline data
        return JSONResponse({
            "success": True,
            "prediction": results["prediction"],
            "score": results["score"],
            "confidence": results["confidence"],
            "component_scores": results["component_scores"],
            "component_contributions": results["component_contributions"],
            "transcript": transcript_text[:500] + "..." if len(transcript_text) > 500 else transcript_text,
            "transcript_length": len(transcript_text),
            "timeline": timeline_data  # NEW: Include timeline data
        })
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(500, error_msg)
        
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except:
                pass

@app.post("/api/analyze-text")
async def analyze_text(text: str = Form(...)):
    """Analyze plain text (no timeline for text-only)"""
    
    try:
        nlp = NLPAnalyzer()
        scorer = EnsembleScorer()
        nlp.load_models()
        
        sentiment = nlp.analyze_sentiment(text)
        toxicity = nlp.analyze_toxicity(text)
        competencies = nlp.analyze_competency(
            text,
            candidate_labels=["technical skills", "communication", "problem solving", "leadership"]
        )
        keywords = nlp.detect_keywords(
            text,
            positive_keywords=["experienced", "led", "achieved", "improved", "solved"],
            negative_keywords=["maybe", "I think", "I guess", "not sure"]
        )
        
        results = scorer.calculate_ensemble_score(
            sentiment_scores=sentiment,
            toxicity_score=toxicity["toxic"],
            competency_scores=competencies,
            keyword_match=keywords
        )
        
        return JSONResponse({
            "success": True,
            "prediction": results["prediction"],
            "score": results["score"],
            "confidence": results["confidence"],
            "component_scores": results["component_scores"],
            "component_contributions": results["component_contributions"],
            "text_length": len(text)
        })
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(500, error_msg)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

from utils.llm_feedback import LLMFeedbackGenerator


from utils.llm_feedback import LLMFeedbackGenerator

@app.post("/api/generate-feedback")
async def generate_feedback(
    score: float = Form(...),
    prediction: str = Form(...),
    sentiment: float = Form(...),
    toxicity: float = Form(...), 
    competency: float = Form(...),
    keywords: float = Form(...),
    transcript: str = Form(...)
):
    """Generate AI feedback using Gemini (with fallback)"""
    try:
        feedback_generator = LLMFeedbackGenerator()
        
        # Try to configure API (will automatically test models)
        api_configured = feedback_generator.configure_api()
        if not api_configured:
            print("Gemini API not configured, using fallback")
        
        # Prepare analysis results
        analysis_results = {
            "score": score,
            "prediction": prediction,
            "component_scores": {
                "sentiment": sentiment,
                "toxicity": toxicity,
                "competency": competency,
                "keywords": keywords
            },
            "transcript": transcript
        }
        
        # Generate feedback (will use fallback if Gemini fails)
        feedback_result = feedback_generator.generate_feedback(analysis_results)
        
        return JSONResponse({
            "success": True,
            "feedback": feedback_result["feedback"],
            "model": feedback_result["model_used"]
        })
            
    except Exception as e:
        print(f"Feedback generation error: {e}")
        return JSONResponse({
            "success": False,
            "error": f"Feedback generation failed: {str(e)}"
        })
