"""
Safe NLP model loader that uses safetensors format
Bypasses PyTorch version requirements
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from typing import Optional

def create_safe_pipeline(
    model_name: str,
    task: str = "text-classification",
    **kwargs
):
    """
    Create pipeline using ONLY safetensors format.
    This bypasses the torch>=2.6 requirement.
    """
    device = 0 if torch.cuda.is_available() else -1
    
    print(f"[NLP] Loading {model_name} with safetensors...", flush=True)
    
    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        
        # Load model with SAFETENSORS ONLY
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            use_safetensors=True,  # CRITICAL: Forces safetensors format
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )
        
        # Create pipeline
        pipe = pipeline(
            task,
            model=model,
            tokenizer=tokenizer,
            device=device,
            **kwargs
        )
        
        print(f"[NLP] ✅ Loaded {model_name} successfully", flush=True)
        return pipe
        
    except Exception as e:
        print(f"[NLP] ❌ Failed to load {model_name}: {e}", flush=True)
        raise
