"""
Audio Helper - FFmpeg CLI + SoundFile (NO PyAV)
Provides PyAV-free audio loading for Whisper
"""
import subprocess
import tempfile
import uuid
from pathlib import Path
import soundfile as sf
import numpy as np

FFMPEG_BIN = "ffmpeg"

def transcode_to_wav_mono16k(src_path: str) -> str:
    """
    Transcode any audio to 16kHz mono WAV using FFmpeg CLI.
    No PyAV compilation needed!
    
    Args:
        src_path: Path to input audio file
        
    Returns:
        Path to transcoded WAV file
    """
    dst = Path(tempfile.gettempdir()) / f"ip_{uuid.uuid4().hex}.wav"
    
    cmd = [
        FFMPEG_BIN, "-y",
        "-i", src_path,
        "-ac", "1",           # mono
        "-ar", "16000",       # 16kHz
        "-f", "wav",
        str(dst)
    ]
    
    try:
        subprocess.run(
            cmd, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=300
        )
        return str(dst)
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg transcode timeout (>5 minutes)")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}")

def load_wav(path: str) -> tuple[np.ndarray, int]:
    """
    Load WAV as float32 PCM array and sample rate via libsndfile.
    
    Args:
        path: Path to WAV file
        
    Returns:
        Tuple of (audio_array, sample_rate)
    """
    audio, sr = sf.read(path, dtype="float32", always_2d=False)
    return audio, sr

def prepare_audio_for_whisper(input_path: str) -> str:
    """
    Prepare any audio file for Whisper (16kHz mono WAV).
    
    Args:
        input_path: Path to input audio
        
    Returns:
        Path to prepared WAV file
    """
    return transcode_to_wav_mono16k(input_path)
