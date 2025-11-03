"""
FastAPI Interview Predictor with Timeline Analysis (cleaned)
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import tempfile, os, traceback, asyncio, json
from datetime import datetime

# GPU check (non-fatal if torch missing)
try:
    import torch
    print(f"[STARTUP] PyTorch {torch.__version__} loaded, CUDA: {torch.cuda.is_available()}", flush=True)
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False
    torch = None
    print("[STARTUP] PyTorch not available", flush=True)

from utils.asr_processor import ASRProcessor
from utils.nlp_analyzer import NLPAnalyzer
from utils.ensemble_scorer import EnsembleScorer
from utils.timeline_analyzer import TimelineAnalyzer
from utils.llm_feedback import LLMFeedbackGenerator

# ----------------- Global progress -----------------
ASR_SINGLETON = None
_progress = {"percent": 0, "stage": "idle", "message": "Waiting…"}

def set_progress(percent: float | None = None, stage: str | None = None, message: str | None = None):
    if percent is not None:
        _progress["percent"] = max(0, min(100, float(percent)))
    if stage is not None:
        _progress["stage"] = stage
    if message is not None:
        _progress["message"] = message
    print(f"[PROGRESS] {_progress['percent']}% - {_progress['stage']}: {_progress['message']}", flush=True)

app = FastAPI(title="Interview Predictor")

# ----------------- Warmup -----------------
@app.on_event("startup")
async def warmup_models():
    """Preload whisper tiny to reduce TTFB on first request."""
    global ASR_SINGLETON
    try:
        print("[WARMUP] Initializing ASR + caching tiny model…", flush=True)
        ASR_SINGLETON = ASRProcessor()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, ASR_SINGLETON.load_model, "tiny")
        print("[WARMUP] ✅ ASR ready.", flush=True)
    except Exception as e:
        print(f"[WARMUP] ⚠️  Warmup skipped: {e}", flush=True)

@app.get("/health")
async def health_check():
    gpu = False
    try:
        gpu = TORCH_AVAILABLE and torch is not None and torch.cuda.is_available()
    except Exception:
        gpu = False
    return {"status":"healthy","service":"interview-predictor","gpu_available":gpu,"warmup_complete":ASR_SINGLETON is not None}

# CORS + static
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    for path in ["static/index.html","index.html"]:
        if os.path.exists(path):
            return open(path, "r", encoding="utf-8").read()
    return HTMLResponse("<h1>Interview Predictor</h1><p>index.html not found</p>", status_code=500)

# ----------------- Model info -----------------
@app.get("/api/model-info")
async def model_info():
    return {
        "models":[
            {"value":"tiny","display":"Tiny - Fastest","size":"39M params","accuracy":"⭐⭐⭐ Good","time_30min":"3-5 min","time_60min":"8-12 min","best_for":"Quick demos, testing"},
            {"value":"base","display":"Base - Balanced (Recommended)","size":"74M params","accuracy":"⭐⭐⭐⭐ Very Good","time_30min":"5-8 min","time_60min":"15-20 min","best_for":"Balanced accuracy/speed"},
            {"value":"small","display":"Small - Higher Accuracy","size":"244M params","accuracy":"⭐⭐⭐⭐⭐ Excellent","time_30min":"10-15 min","time_60min":"30-40 min","best_for":"Higher accuracy needed"},
            {"value":"medium","display":"Medium - Maximum Accuracy","size":"769M params","accuracy":"⭐⭐⭐⭐⭐ Excellent","time_30min":"20-30 min","time_60min":"50-70 min","best_for":"Maximum accuracy"}
        ],
        "component_explanations":{
            "sentiment":"Measures positive vs negative emotional tone in responses",
            "toxicity":"Detects unprofessional language or inappropriate content (higher is better)",
            "competency":"Evaluates technical skills and role-specific fit based on answers",
            "keywords":"Identifies positive interviewer signals and professional language use"
        }
    }

# ----------------- Progress (SSE + JSON) -----------------
@app.get("/api/progress")
async def sse_progress(request: Request):
    async def eventgen():
        last = None
        yield f"data: {json.dumps(_progress)}\n\n"
        while True:
            if await request.is_disconnected(): break
            payload = json.dumps(_progress)
            if payload != last:
                last = payload
                yield f"data: {payload}\n\n"
            else:
                yield ": ping\n\n"
            await asyncio.sleep(1.0)
    headers = {"Content-Type":"text/event-stream","Cache-Control":"no-cache","Connection":"keep-alive","X-Accel-Buffering":"no"}
    return StreamingResponse(eventgen(), headers=headers, media_type="text/event-stream")

@app.get("/api/progress-now")
async def progress_now():
    return JSONResponse(_progress)

# ----------------- Helpers -----------------
def _approximate_word_timestamps(segments):
    for seg in segments:
        start = float(seg.get("start", 0.0) or 0.0)
        end   = float(seg.get("end", start) or start)
        text  = (seg.get("text") or "").strip()
        duration = max(0.0, end - start)
        tokens = [w for w in text.split() if w]
        words = []
        if duration > 0 and tokens:
            step = duration / len(tokens)
            for i, w in enumerate(tokens):
                words.append({"word": w, "start": round(start + step*i,3), "end": round(start + step*(i+1),3)})
        seg["words"] = words
    return segments

# ----------------- Analyze Audio -----------------
@app.post("/api/analyze-audio")
async def analyze_audio(file: UploadFile = File(...), model_select: str = Form("base", alias="model_size")):
    print(f"\n[API] ========== NEW ANALYZE REQUEST ==========", flush=True)
    print(f"[API] File: {file.filename}, Model: {model_select}", flush=True)
    set_progress(1, "start", "Starting…")

    # size guard (best-effort; UploadFile may not expose .size)
    try:
        if getattr(file, "size", 0) and file.size > 200*1024*1024:
            raise HTTPException(400, "File too large. Max 200MB.")
    except Exception: pass

    temp_file = None
    try:
        # Save upload
        set_progress(5, "uploading", "Saving upload…")
        suffix = os.path.splitext(file.filename or "")[1] or ".bin"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file = tmp.name
            while True:
                chunk = await file.read(1024*1024)
                if not chunk: break
                tmp.write(chunk)
        print(f"[API] File saved: {temp_file}", flush=True)

        # Init processors
        set_progress(15, "init", "Loading models…")
        asr = ASR_SINGLETON or ASRProcessor()
        nlp = NLPAnalyzer()
        scorer = EnsembleScorer()
        timeline_analyzer = TimelineAnalyzer()

        # Transcribe
        set_progress(30, "transcribing", "Transcribing audio…")
        print(f"[API] Starting transcription with model: {model_select}", flush=True)
        transcription = asr.transcribe_audio(temp_file, model_name=model_select)
        print("[API] Transcription complete!", flush=True)
        set_progress(55, "transcribed", "Transcription complete")

        transcript_text = transcription.get("text", "") or ""
        segments = transcription.get("segments", []) or []
        duration = float(transcription.get("duration", 0) or 0)

        # No speech case
        if not transcript_text and not segments:
            warning = transcription.get("warning", "No speech detected")
            print(f"[API] ⚠️  Empty transcription: {warning}", flush=True)
            set_progress(100, "done", "No speech detected")
            return JSONResponse({
                "success": True,
                "prediction": "Insufficient Audio",
                "score": 0.0,
                "confidence": "Low",
                "component_scores": {"sentiment":0.0,"toxicity":0.0,"competency":0.0,"keywords":0.0},
                "component_contributions": {},
                "transcript": "",
                "transcript_length": 0,
                "timeline": [],
                "segments": [],
                "warning": warning,
                "note": "No speech was detected in the uploaded audio. Please ensure the audio file contains clear speech."
            })

        print(f"[API] Transcript length: {len(transcript_text)}, Segments: {len(segments)}, Duration: {duration}s", flush=True)

        # duration fallback from segments
        if duration <= 0 and segments:
            try:
                duration = max(float(s.get("end", 0) or 0) for s in segments if s.get("end") is not None)
                print(f"[API] Calculated duration from segments: {duration}s", flush=True)
            except Exception:
                print("[API] WARNING: Could not calculate duration", flush=True)
                duration = 0.0

        segments = _approximate_word_timestamps(segments)

        # NLP - Load models ONCE
        set_progress(60, "nlp", "Running NLP analysis…")
        nlp.load_models()
        
        # Full-text analysis (for toxicity, competency, keywords)
        sentiment = nlp.analyze_sentiment(transcript_text)
        set_progress(70, "nlp", "Toxicity…")
        toxicity = nlp.analyze_toxicity(transcript_text)
        set_progress(75, "nlp", "Competency…")
        competencies = nlp.analyze_competency(
            transcript_text,
            candidate_labels=["technical skills","communication","problem solving","leadership"]
        )
        set_progress(80, "nlp", "Keywords…")
        keywords = nlp.detect_keywords(
            transcript_text,
            positive_keywords=["experienced","led","achieved","improved","solved"],
            negative_keywords=["maybe","i think","i guess","not sure"]
        )

        # Timeline (this also does segment sentiment analysis internally)
        set_progress(86, "timeline", "Building performance timeline…")
        scored_segments = timeline_analyzer.analyze_segments(segments)
        timeline_data = timeline_analyzer.create_timeline_data(scored_segments, duration)
        
        # Extract segment sentiments from timeline analysis
        segment_sentiments = []
        for seg in scored_segments:
            if "sentiment" in seg:
                segment_sentiments.append(seg["sentiment"])
                # Debug: print first 3 segments
                if len(segment_sentiments) <= 3:
                    print(f"[DEBUG] Segment {len(segment_sentiments)}: {seg['sentiment']}", flush=True)
        
        print(f"[API] Extracted {len(segment_sentiments)} segment sentiments from timeline", flush=True)

        # Score - Use timeline's segment sentiments
        set_progress(92, "scoring", "Calculating interview score…")
        results = scorer.calculate_ensemble_score(
            sentiment_scores=sentiment,
            toxicity_score=toxicity["toxic"],
            competency_scores=competencies,
            keyword_match=keywords,
            segment_sentiments=segment_sentiments  # Use timeline's analysis
        )
        print("[API] Components (outgoing):", results["component_scores"], flush=True)

        # Done
        set_progress(100, "done", "Complete")
        response = {
            "success": True,
            "prediction": results["prediction"],
            "score": results["score"],
            "confidence": results["confidence"],
            "component_scores": results["component_scores"],
            "component_contributions": results["component_contributions"],
            "transcript": transcript_text[:500] + "..." if len(transcript_text) > 500 else transcript_text,
            "transcript_length": len(transcript_text),
            "timeline": timeline_data,
            "segments": segments
        }
        print("[API] ========== REQUEST COMPLETE ==========\n", flush=True)
        return JSONResponse(response)

    except Exception as e:
        print(f"[API] ERROR:\n{traceback.format_exc()}", flush=True)
        set_progress(100, "error", f"Error: {e}")
        raise HTTPException(500, f"Analysis failed: {e}")
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
                print(f"[API] Cleaned up temp file: {temp_file}", flush=True)
            except Exception as ce:
                print(f"[API] Temp cleanup failed: {ce}", flush=True)

# ----------------- Analyze Text -----------------
@app.post("/api/analyze-text")
async def analyze_text(text: str = Form(...)):
    try:
        nlp = NLPAnalyzer(); nlp.load_models()
        scorer = EnsembleScorer()
        sentiment = nlp.analyze_sentiment(text)
        toxicity  = nlp.analyze_toxicity(text)
        competencies = nlp.analyze_competency(
            text,
            candidate_labels=["technical skills","communication","problem solving","leadership"]
        )
        keywords = nlp.detect_keywords(
            text,
            positive_keywords=["experienced","led","achieved","improved","solved"],
            negative_keywords=["maybe","i think","i guess","not sure"]
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
        print(f"[API] analyze-text error:\n{traceback.format_exc()}", flush=True)
        raise HTTPException(500, f"Analysis failed: {e}")

# ----------------- Feedback -----------------
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
    try:
        feedback_generator = LLMFeedbackGenerator()
        api_configured = feedback_generator.configure_api()
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
        feedback_result = feedback_generator.generate_feedback(analysis_results)
        return JSONResponse({
            "success": True,
            "feedback": feedback_result["feedback"],
            "model": feedback_result["model_used"] if api_configured else "fallback"
        })
    except Exception as e:
        print(f"[API] Feedback error: {e}", flush=True)
        return JSONResponse({"success": False, "error": f"Feedback generation failed: {e}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

