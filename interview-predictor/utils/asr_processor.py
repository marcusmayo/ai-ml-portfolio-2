"""
ASR Processor - Dual Mode (WhisperX or faster-whisper)
Works in both local (WhisperX) and Docker (faster-whisper) environments
"""

import os
import uuid
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Try to import torch for GPU detection
try:
    import torch
    HAS_CUDA = torch.cuda.is_available()  # RESTORED GPU DETECTION
    print(f"[ASR] CUDA available: {HAS_CUDA}", flush=True)
except Exception:
    HAS_CUDA = False
    torch = None
    print("[ASR] CUDA not available", flush=True)

# Try WhisperX first (for local), fall back to faster-whisper (for Docker)
WHISPERX_AVAILABLE = False
FASTER_WHISPER_AVAILABLE = False

try:
    import whisperx
    WHISPERX_AVAILABLE = True
    print("[ASR] Using WhisperX backend", flush=True)
except ImportError:
    print("[ASR] WhisperX not available, trying faster-whisper...", flush=True)
    try:
        from faster_whisper import WhisperModel
        FASTER_WHISPER_AVAILABLE = True
        print("[ASR] Using faster-whisper backend", flush=True)
    except ImportError:
        print("[ASR] ERROR: Neither WhisperX nor faster-whisper available!", flush=True)

# Import soundfile for duration check
try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False
    print("[ASR] soundfile not available, skipping duration checks", flush=True)

FFMPEG_BIN = "ffmpeg"

def _wav_duration_seconds(path: str) -> float:
    """Get WAV file duration in seconds"""
    if not HAS_SOUNDFILE:
        return 0.0
    try:
        info = sf.info(path)
        if info.samplerate > 0:
            duration = info.frames / float(info.samplerate)
            return duration
    except Exception as e:
        print(f"[ASR] Could not determine duration: {e}", flush=True)
    return 0.0

def _to_wav_mono_16k(src_path: str) -> str:
    """Convert any audio to 16kHz mono WAV using FFmpeg CLI"""
    dst = Path(tempfile.gettempdir()) / f"ip_{uuid.uuid4().hex}.wav"
    
    cmd = [
        FFMPEG_BIN,
        "-hide_banner",
        "-loglevel", "error",
        "-nostdin",
        "-y",
        "-i", src_path,
        "-vn",
        "-sn",
        "-ac", "1",
        "-ar", "16000",
        "-f", "wav",
        str(dst)
    ]
    
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=300
        )
        print(f"[ASR] Audio converted: {src_path} -> {dst}", flush=True)
        return str(dst)
    except subprocess.TimeoutExpired:
        print(f"[ASR] FFmpeg conversion timeout after 5min", flush=True)
        raise
    except subprocess.CalledProcessError as e:
        print(f"[ASR] FFmpeg conversion failed: {e.stderr.decode()}", flush=True)
        raise
    except Exception as e:
        print(f"[ASR] FFmpeg conversion error: {e}", flush=True)
        raise

class ASRProcessor:
    """Handles automatic speech recognition using available backend"""
    
    def __init__(self):
        self.device = "cuda" if HAS_CUDA else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        self.model = None
        self.model_name = None
        self.backend = None
        
        if WHISPERX_AVAILABLE:
            self.backend = "whisperx"
            print(f"[ASR] Backend: WhisperX on {self.device}", flush=True)
        elif FASTER_WHISPER_AVAILABLE:
            self.backend = "faster-whisper"
            print(f"[ASR] Backend: faster-whisper on {self.device}", flush=True)
        else:
            raise RuntimeError("No ASR backend available! Install whisperx or faster-whisper")
        
        if self.device == "cuda" and torch:
            try:
                gpu_name = torch.cuda.get_device_name(0)
                print(f"[ASR] GPU: {gpu_name}", flush=True)
            except:
                pass
    
    def _load_fw_model(self, model_name: str):
        """Load faster-whisper model with GPU fallback"""
        try:
            print(f"[ASR] Trying GPU (cuda) for faster-whisper...", flush=True)
            model = WhisperModel(
                model_name,
                device="cuda",
                compute_type="float16",
                cpu_threads=0,
            )
            print(f"[ASR] ✅ Using GPU for faster-whisper", flush=True)
            return model
        except Exception as e:
            print(f"[ASR] GPU init failed, falling back to CPU: {e}", flush=True)
            try:
                model = WhisperModel(
                    model_name,
                    device="cpu",
                    compute_type="int8",
                    cpu_threads=4,
                )
                print(f"[ASR] ✅ Using CPU for faster-whisper", flush=True)
                return model
            except Exception as e2:
                print(f"[ASR] ❌ CPU init also failed: {e2}", flush=True)
                raise
    
    def load_model(self, model_name: str = "base"):
        """Load ASR model (backend-agnostic)"""
        model_name = (model_name or "base").lower()
        if model_name not in {"tiny", "base", "small", "medium", "large", "large-v2"}:
            model_name = "base"
        
        if self.model is not None and self.model_name == model_name:
            print(f"[ASR] Model {model_name} already loaded", flush=True)
            return
        
        print(f"[ASR] Loading {self.backend} model: {model_name}", flush=True)
        
        if self.backend == "whisperx":
            self.model = whisperx.load_model(
                model_name,
                self.device,
                compute_type=self.compute_type
            )
        elif self.backend == "faster-whisper":
            self.model = self._load_fw_model(model_name)
        
        self.model_name = model_name
        print(f"[ASR] Model {model_name} loaded successfully", flush=True)
    
    def transcribe_audio(
        self,
        audio_path: str,
        model_name: str = "base",
        batch_size: int = 16
    ) -> Dict:
        """Transcribe audio file using available backend"""
        try:
            self.load_model(model_name)
            print(f"[ASR] Transcribing: {audio_path}", flush=True)
            
            if self.backend == "whisperx":
                return self._transcribe_whisperx(audio_path, batch_size)
            elif self.backend == "faster-whisper":
                return self._transcribe_faster_whisper(audio_path)
            else:
                raise RuntimeError("No backend available")
                
        except Exception as e:
            print(f"[ASR] Error during transcription: {str(e)}", flush=True)
            raise
    
    def _transcribe_whisperx(self, audio_path: str, batch_size: int) -> Dict:
        """Transcribe using WhisperX"""
        audio = whisperx.load_audio(audio_path)
        result = self.model.transcribe(audio, batch_size=batch_size)
        
        if "segments" in result and len(result["segments"]) > 0:
            transcription_text = " ".join([seg["text"].strip() for seg in result["segments"]])
        else:
            transcription_text = ""
        
        words = []
        duration = 0.0
        for segment in result.get("segments", []):
            duration = max(duration, segment.get("end", 0.0))
            for word in segment.get("words", []):
                words.append({
                    "word": word.get("word", ""),
                    "start": word.get("start", 0.0),
                    "end": word.get("end", 0.0),
                    "score": word.get("score", 0.0)
                })
        
        return {
            "text": transcription_text,
            "segments": result.get("segments", []),
            "words": words,
            "duration": duration,
            "language": result.get("language", "en")
        }
    
    def _transcribe_faster_whisper(self, audio_path: str) -> Dict:
        """Transcribe using faster-whisper with robust empty audio handling"""
        print(f"[ASR] Converting audio to WAV...", flush=True)
        wav_path = _to_wav_mono_16k(audio_path)
        
        try:
            dur = _wav_duration_seconds(wav_path)
            print(f"[ASR] WAV duration: {dur:.3f}s", flush=True)
            
            if dur < 0.2:
                print("[ASR] ⚠️  Audio too short or empty, returning empty transcript", flush=True)
                return {
                    "text": "",
                    "segments": [],
                    "words": [],
                    "duration": 0.0,
                    "language": "en",
                    "warning": "Audio duration too short for transcription"
                }
            
            print(f"[ASR] Starting transcription (this may take a while)...", flush=True)
            
            try:
                segments_iter, info = self.model.transcribe(
                    wav_path,
                    vad_filter=True,
                    beam_size=5,
                    word_timestamps=False
                )
            except ValueError as e:
                if "empty sequence" in str(e).lower():
                    print(f"[ASR] ⚠️  No speech detected (VAD returned no segments)", flush=True)
                    return {
                        "text": "",
                        "segments": [],
                        "words": [],
                        "duration": dur,
                        "language": "en",
                        "warning": "No speech detected in audio"
                    }
                else:
                    raise
            
            output_segments = []
            text_parts = []
            duration = 0.0
            segment_count = 0
            
            for seg in segments_iter:
                start = float(getattr(seg, "start", 0.0) or 0.0)
                end = float(getattr(seg, "end", start) or start)
                txt = (getattr(seg, "text", "") or "").strip()
                
                if end > 0:
                    duration = max(duration, end)
                segment_count += 1
                
                if txt:
                    text_parts.append(txt)
                    output_segments.append({
                        "start": start,
                        "end": end,
                        "text": txt
                    })
            
            if segment_count == 0:
                print(f"[ASR] ⚠️  No segments generated", flush=True)
                return {
                    "text": "",
                    "segments": [],
                    "words": [],
                    "duration": dur,
                    "language": "en",
                    "warning": "No transcribable content found"
                }
            
            print(f"[ASR] ✅ Transcription complete: {segment_count} segments, {duration:.1f}s", flush=True)
            
            return {
                "text": " ".join(text_parts).strip(),
                "segments": output_segments,
                "words": [],
                "duration": duration if duration > 0 else dur,
                "language": getattr(info, "language", "en")
            }
            
        finally:
            try:
                os.unlink(wav_path)
                print(f"[ASR] Cleaned up temp WAV: {wav_path}", flush=True)
            except:
                pass
    
    def get_speaker_timeline(self, result: Dict) -> List[Dict]:
        """Extract speaker timeline from transcription result"""
        timeline = []
        
        for segment in result.get("segments", []):
            timeline.append({
                "start": segment.get("start", 0.0),
                "end": segment.get("end", 0.0),
                "text": segment.get("text", "").strip(),
                "speaker": segment.get("speaker", "Unknown")
            })
        
        return timeline
