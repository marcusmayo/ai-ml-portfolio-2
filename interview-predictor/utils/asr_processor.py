"""
ASR Processor using faster-whisper (Fixed to return segments)
"""

import whisper


class ASRProcessor:
    """Handles audio-to-text transcription with segments"""
    
    def __init__(self, model_size="base"):
        self.model_size = model_size
        self.model = None
    
    def load_model(self):
        """Load Whisper model"""
        if self.model is None:
            print(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            print("Model loaded")
    
    def transcribe_audio(self, audio_path):
        """Transcribe audio file and return segments"""
        self.load_model()
        
        results = self.model.transcribe(audio_path)
        transcription_text = results["text"]
        
        segments = results.get("segments", [])
        
        # Convert segments to list (important!)
        segment_list = []
        full_text = ""
        
        for segment in segments:
            segment_data = {
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip()
            }
            segment_list.append(segment_data)
            full_text += segment["text"] + " "
        
        # Calculate duration from segments if available
        duration = segments[-1]["end"] if segments else 0
        
        print(f"ASR: Transcribed {len(segment_list)} segments, duration: {duration:.1f}s")
        
        return {
            "text": full_text.strip(),
            "language": results.get("language", "unknown"),
            "duration": duration,
            "segments": segment_list
        }
