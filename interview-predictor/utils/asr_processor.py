"""
ASR (Automatic Speech Recognition) Processor
Handles speech-to-text conversion using faster-whisper
"""

import os
from typing import Optional, Dict
from faster_whisper import WhisperModel


class ASRProcessor:
    """Processes audio files and converts them to text transcriptions"""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize the ASR processor
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large-v3)
                       - tiny: fastest, least accurate
                       - base: good balance (recommended for demo)
                       - large-v3: most accurate, slowest
        """
        self.model_size = model_size
        self.model = None
        
    def load_model(self):
        """Load the Whisper model (lazy loading to save memory)"""
        if self.model is None:
            print(f"Loading Whisper model: {self.model_size}...")
            self.model = WhisperModel(
                self.model_size,
                device="cpu",  # Use CPU for compatibility
                compute_type="int8"  # Quantized for speed
            )
            print("Model loaded successfully")
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, any]:
        """
        Transcribe an audio file to text
        
        Args:
            audio_path: Path to audio file (mp3, wav, m4a, etc.)
            
        Returns:
            Dictionary containing:
                - text: Full transcription
                - language: Detected language
                - segments: List of timestamped segments
        """
        self.load_model()
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print(f"Transcribing: {audio_path}")
        
        # Transcribe with faster-whisper
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True,  # Voice activity detection
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Collect all segments
        full_text = ""
        segment_list = []
        
        for segment in segments:
            full_text += segment.text + " "
            segment_list.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
        
        return {
            "text": full_text.strip(),
            "language": info.language,
            "segments": segment_list,
            "duration": info.duration
        }
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the loaded model"""
        return {
            "model_size": self.model_size,
            "device": "cpu",
            "compute_type": "int8"
        }
