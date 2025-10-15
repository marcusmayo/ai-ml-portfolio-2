"""
ASR Processor using faster-whisper (Fixed to return segments)
"""

from faster_whisper import WhisperModel


class ASRProcessor:
    """Handles audio-to-text transcription with segments"""
    
    def __init__(self, model_size="base"):
        self.model_size = model_size
        self.model = None
        
    def load_model(self):
        """Load Whisper model"""
        if self.model is None:
            print(f"Loading Whisper model: {self.model_size}")
            self.model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8"
            )
            print("Model loaded")
    
    def transcribe_audio(self, audio_path):
        """Transcribe audio file and return segments"""
        self.load_model()
        
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
            language="en"
        )
        
        # Convert segments to list (important!)
        segment_list = []
        full_text = ""
        
        for segment in segments:
            segment_data = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
            segment_list.append(segment_data)
            full_text += segment.text + " "
        
        print(f"ASR: Transcribed {len(segment_list)} segments, duration: {info.duration:.1f}s")
        
        return {
            "text": full_text.strip(),
            "language": info.language,
            "duration": info.duration,
            "segments": segment_list  # This is the key fix!
        }
