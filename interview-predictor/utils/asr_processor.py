"""
ASR Processor using WhisperX
Handles audio transcription with word-level timestamps
"""

import os
import torch
import whisperx
from typing import Dict, List, Optional


class ASRProcessor:
    """Handles automatic speech recognition using WhisperX"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        self.model = None
        self.model_name = None
        
        print(f"[ASR] Device: {self.device}")
        if self.device == "cuda":
            print(f"[ASR] GPU: {torch.cuda.get_device_name(0)}")
    
    def load_model(self, model_name: str = "base"):
        """Load WhisperX model"""
        if self.model is None or self.model_name != model_name:
            print(f"[ASR] Loading WhisperX model: {model_name} on {self.device}")
            self.model = whisperx.load_model(
                model_name,
                self.device,
                compute_type=self.compute_type
            )
            self.model_name = model_name
            print(f"[ASR] Model loaded successfully")
    
    def transcribe_audio(
        self,
        audio_path: str,
        model_name: str = "base",
        batch_size: int = 16
    ) -> Dict:
        """
        Transcribe audio file using WhisperX
        
        Args:
            audio_path: Path to audio file
            model_name: WhisperX model size (tiny, base, small, medium, large-v2)
            batch_size: Batch size for inference
            
        Returns:
            Dictionary with transcription results
        """
        try:
            # Load model
            self.load_model(model_name)
            
            # Load audio
            print(f"[ASR] Transcribing: {audio_path}")
            audio = whisperx.load_audio(audio_path)
            
            # Transcribe
            result = self.model.transcribe(audio, batch_size=batch_size)
            
            # Extract text from segments
            if "segments" in result and len(result["segments"]) > 0:
                transcription_text = " ".join([seg["text"].strip() for seg in result["segments"]])
            else:
                transcription_text = ""
            
            # Get word-level timestamps if available
            words = []
            for segment in result.get("segments", []):
                for word in segment.get("words", []):
                    words.append({
                        "word": word.get("word", ""),
                        "start": word.get("start", 0.0),
                        "end": word.get("end", 0.0),
                        "score": word.get("score", 0.0)
                    })
            
            output = {
                "text": transcription_text,
                "segments": result.get("segments", []),
                "words": words,
                "language": result.get("language", "en")
            }
            
            print(f"[ASR] Transcription completed")
            return output
            
        except Exception as e:
            print(f"[ASR] Error during transcription: {str(e)}")
            raise
    
    def get_speaker_timeline(self, result: Dict) -> List[Dict]:
        """
        Extract speaker timeline from transcription result
        
        Args:
            result: WhisperX transcription result
            
        Returns:
            List of timeline events with speaker and text
        """
        timeline = []
        
        for segment in result.get("segments", []):
            timeline.append({
                "start": segment.get("start", 0.0),
                "end": segment.get("end", 0.0),
                "text": segment.get("text", "").strip(),
                "speaker": segment.get("speaker", "Unknown")
            })
        
        return timeline
