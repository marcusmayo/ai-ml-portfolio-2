"""
Safe model loader that forces safetensors format
Bypasses PyTorch 2.6 requirement by avoiding pickle-based weights
"""

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Optional

def load_classification_pipeline(
    model_name: str,
    task: str = "text-classification",
    **pipeline_kwargs
):
    """
    Load a text classification pipeline using ONLY safetensors.
    
    Args:
        model_name: HuggingFace model ID
        task: Pipeline task type
        **pipeline_kwargs: Additional pipeline arguments
    
    Returns:
        Loaded pipeline
    """
    device_idx = 0 if torch.cuda.is_available() else -1
    
    # Models known to have safetensors support
    SAFETENSORS_MODELS = {
        "sentiment": [
            "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "distilbert-base-uncased-finetuned-sst-2-english",
            "finiteautomata/bertweet-base-sentiment-analysis"
        ],
        "toxicity": [
            "s-nlp/roberta_toxicity_classifier",
            "unitary/unbiased-toxic-roberta",  # Has safetensors
            "martin-ha/toxic-comment-model"
        ]
    }
    
    # Try requested model first, then fallbacks
    models_to_try = [model_name]
    
    # Add fallbacks based on task
    if "sentiment" in task.lower():
        models_to_try.extend(SAFETENSORS_MODELS["sentiment"])
    elif "toxic" in model_name.lower() or "toxic" in task.lower():
        models_to_try.extend(SAFETENSORS_MODELS["toxicity"])
    
    last_error = None
    
    for model_id in models_to_try:
        try:
            print(f"[NLP] Loading {model_id} with safetensors...", flush=True)
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                use_fast=True
            )
            
            # Load model with SAFETENSORS ONLY
            model = AutoModelForSequenceClassification.from_pretrained(
                model_id,
                use_safetensors=True,  # CRITICAL: Forces safetensors
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )
            
            # Create pipeline
            pipe = pipeline(
                task,
                model=model,
                tokenizer=tokenizer,
                device=device_idx,
                **pipeline_kwargs
            )
            
            print(f"[NLP] ✅ Successfully loaded {model_id}", flush=True)
            return pipe
            
        except Exception as e:
            print(f"[NLP] ⚠️  Failed to load {model_id}: {str(e)[:100]}", flush=True)
            last_error = e
            continue
    
    # If all models failed
    raise RuntimeError(
        f"Failed to load any model with safetensors. Last error: {last_error}"
    )


def create_sentiment_pipeline():
    """Create sentiment analysis pipeline with safetensors"""
    return load_classification_pipeline(
        "cardiffnlp/twitter-roberta-base-sentiment-latest",
        task="sentiment-analysis"
    )


def create_toxicity_pipeline():
    """Create toxicity classification pipeline with safetensors"""
    return load_classification_pipeline(
        "s-nlp/roberta_toxicity_classifier",
        task="text-classification",
        return_all_scores=True
    )
