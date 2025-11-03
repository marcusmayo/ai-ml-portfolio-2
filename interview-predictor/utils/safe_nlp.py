"""
Safe NLP Loader - FIXED with reliable toxicity model
"""

import torch
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("safe_nlp")

_SENTIMENT_PIPE = None
_TOXICITY_PIPE = None
_DEVICE = None


def get_device():
    """Get device once and cache it"""
    global _DEVICE
    if _DEVICE is None:
        try:
            _DEVICE = 0 if torch.cuda.is_available() else -1
            logger.info(f"[SAFE_NLP] Device: {'GPU' if _DEVICE >= 0 else 'CPU'}")
        except Exception:
            _DEVICE = -1
    return _DEVICE


def sentiment_pipeline():
    """Load sentiment model"""
    global _SENTIMENT_PIPE
    
    if _SENTIMENT_PIPE is not None:
        return _SENTIMENT_PIPE
    
    logger.info("[SAFE_NLP] Loading sentiment model...")
    
    device = get_device()
    model_name = "distilbert-base-uncased-finetuned-sst-2-english"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        use_safetensors=True,
        torch_dtype=torch.float16 if device >= 0 else torch.float32,
    )
    
    _SENTIMENT_PIPE = pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tokenizer,
        device=device,
        framework="pt"
    )
    
    # Test
    test = _SENTIMENT_PIPE("This is good")[0]
    logger.info(f"[SAFE_NLP] ✅ Sentiment loaded: {test['label']}")
    
    return _SENTIMENT_PIPE


def toxicity_pipeline():
    """
    Load toxicity model - FIXED to use unitary/toxic-bert
    This model is more reliable and has proper safetensors support
    """
    global _TOXICITY_PIPE
    
    if _TOXICITY_PIPE is not None:
        return _TOXICITY_PIPE
    
    logger.info("[SAFE_NLP] Loading toxicity model (unitary/toxic-bert)...")
    
    try:
        device = get_device()
        model_name = "unitary/toxic-bert"
        
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device >= 0 else torch.float32,
        )
        
        _TOXICITY_PIPE = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            device=device,
            framework="pt",
            top_k=None  # Return all labels
        )
        
        # Test
        test = _TOXICITY_PIPE("This is a test")
        logger.info(f"[SAFE_NLP] ✅ Toxicity loaded: {len(test[0])} labels")
        
        return _TOXICITY_PIPE
        
    except Exception as e:
        logger.error(f"[SAFE_NLP] ❌ Toxicity load failed: {e}")
        logger.info("[SAFE_NLP] Trying alternative: roberta-hate-speech-dynabench-r4")
        
        # Fallback to another reliable model
        try:
            model_name = "facebook/roberta-hate-speech-dynabench-r4-target"
            
            tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if device >= 0 else torch.float32,
            )
            
            _TOXICITY_PIPE = pipeline(
                "text-classification",
                model=model,
                tokenizer=tokenizer,
                device=device,
                framework="pt"
            )
            
            logger.info("[SAFE_NLP] ✅ Alternative toxicity model loaded")
            return _TOXICITY_PIPE
            
        except Exception as e2:
            logger.error(f"[SAFE_NLP] ❌ Alternative also failed: {e2}")
            raise RuntimeError("All toxicity models failed")


def warmup_models():
    """Load all models at startup"""
    logger.info("[SAFE_NLP] Starting warmup...")
    try:
        sentiment_pipeline()
        toxicity_pipeline()
        logger.info("[SAFE_NLP] ✅ All models warmed up")
    except Exception as e:
        logger.error(f"[SAFE_NLP] ❌ Warmup failed: {e}")
        raise
