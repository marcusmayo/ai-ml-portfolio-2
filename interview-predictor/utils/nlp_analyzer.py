"""
NLP Analyzer - FINAL PRODUCTION VERSION
Handles ALL sentiment label formats
"""

import re
from typing import Dict, List
import torch

try:
    from utils.safe_nlp import sentiment_pipeline, toxicity_pipeline, warmup_models
    HAS_SAFE_NLP = True
    print("[NLP] Safe loader imported")
except ImportError as e:
    HAS_SAFE_NLP = False
    print(f"[NLP] WARNING: safe_nlp not available: {e}")

try:
    from transformers import pipeline as tf_pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class NLPAnalyzer:
    """NLP analysis with robust label handling"""
    
    def __init__(self):
        self.sentiment_analyzer = None
        self.toxicity_analyzer = None
        self.zero_shot_classifier = None
        self._models_loaded = False
        
    def load_models(self):
        """Load models"""
        if self._models_loaded:
            return
            
        print("[NLP] Loading models...")
        
        if not HAS_SAFE_NLP:
            print("[NLP] ERROR: safe_nlp not available!")
            return
        
        try:
            self.sentiment_analyzer = sentiment_pipeline()
            self.toxicity_analyzer = toxicity_pipeline()
            
            if TRANSFORMERS_AVAILABLE:
                device = 0 if torch.cuda.is_available() else -1
                self.zero_shot_classifier = tf_pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli",
                    device=device
                )
                print("[NLP] ✅ Zero-shot loaded")
            
            self._models_loaded = True
            print("[NLP] ✅ All models loaded")
            
        except Exception as e:
            print(f"[NLP] ❌ Failed: {e}")
            self._models_loaded = False
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Return 0-100 scaled dict: {positive, negative, neutral}
        ROBUST to all label formats:
        - "POSITIVE", "positive", "pos"
        - "NEGATIVE", "negative", "neg"  
        - "NEUTRAL", "neutral", "neu"
        - "LABEL_0", "LABEL_1", "LABEL_2"
        """
        def clamp01(x: float) -> float:
            try:
                v = float(x)
                if v != v:  # NaN
                    return 0.0
                return max(0.0, min(1.0, v))
            except:
                return 0.0
        
        if not text or not text.strip():
            return {"positive": 50.0, "negative": 10.0, "neutral": 40.0}
        
        if self.sentiment_analyzer is None:
            return self._fallback_sentiment(text)
        
        try:
            raw = self.sentiment_analyzer(text[:512])
            
            # Normalize to list of {label, score} dicts
            if isinstance(raw, dict):
                items = [raw]
            elif isinstance(raw, list):
                # Could be [[{...}]] or [{...}]
                items = raw[0] if (len(raw) > 0 and isinstance(raw[0], list)) else raw
            else:
                items = []
            
            # Parse labels
            p = n = u = 0.0
            
            if len(items) == 1:
                # Single top label
                label = str(items[0].get("label", "")).lower()
                score = clamp01(items[0].get("score", 0.0))
                
                print(f"[NLP] Sentiment raw: label='{label}', score={score:.3f}", flush=True)
                
                # Map label to sentiment
                if "pos" in label or "label_2" in label:
                    p = score
                    n = 0.0
                    u = max(0.0, 1.0 - score)
                elif "neg" in label or "label_0" in label:
                    p = 0.0
                    n = score
                    u = max(0.0, 1.0 - score)
                elif "neu" in label or "label_1" in label:
                    p = 0.0
                    n = 0.0
                    u = score
                else:
                    # Unknown label - treat as neutral
                    print(f"[NLP] WARNING: Unknown sentiment label '{label}'", flush=True)
                    p = 0.0
                    n = 0.0
                    u = score
                    
            else:
                # Multiple labels (return_all_scores=True)
                for item in items:
                    label = str(item.get("label", "")).lower()
                    score = clamp01(item.get("score", 0.0))
                    
                    if "pos" in label or "label_2" in label:
                        p = max(p, score)
                    elif "neg" in label or "label_0" in label:
                        n = max(n, score)
                    elif "neu" in label or "label_1" in label:
                        u = max(u, score)
                
                # Normalize if needed
                total = p + n + u
                if total > 0:
                    p, n, u = p/total, n/total, u/total
            
            result = {
                "positive": round(p * 100.0, 2),
                "negative": round(n * 100.0, 2),
                "neutral": round(u * 100.0, 2)
            }
            
            print(f"[NLP] Sentiment parsed: {result}", flush=True)
            return result
            
        except Exception as e:
            print(f"[NLP] Sentiment error: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return self._fallback_sentiment(text)
    
    def _fallback_sentiment(self, text: str) -> Dict[str, float]:
        """Keyword fallback"""
        positive = ['good', 'great', 'excellent', 'happy', 'love', 'best', 'amazing', 'success', 'excited']
        negative = ['bad', 'terrible', 'hate', 'worst', 'awful', 'poor', 'horrible', 'failed', 'difficult']
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive if w in text_lower)
        neg_count = sum(1 for w in negative if w in text_lower)
        total = pos_count + neg_count
        
        if total == 0:
            return {"positive": 50.0, "negative": 10.0, "neutral": 40.0}
        
        pos_pct = (pos_count / total) * 100
        neg_pct = (neg_count / total) * 100
        
        return {
            "positive": round(pos_pct, 2),
            "negative": round(neg_pct, 2),
            "neutral": round(max(0, 100 - pos_pct - neg_pct), 2)
        }
    
    def analyze_toxicity(self, text: str) -> Dict[str, float]:
        """Toxicity (0-100, higher = more toxic)"""
        if not text or not text.strip():
            return {"toxic": 5.0, "non_toxic": 95.0}
        
        if self.toxicity_analyzer is None:
            return self._fallback_toxicity(text)
        
        try:
            out = self.toxicity_analyzer(text[:512])
            toxic_score = 0.0
            
            first = out[0] if isinstance(out, list) else out
            
            if isinstance(first, list):
                # Multi-label
                for item in first:
                    label = str(item.get("label", "")).lower()
                    score = float(item.get("score", 0.0))
                    if "toxic" in label or "hate" in label:
                        toxic_score = max(toxic_score, score)
                        
            elif isinstance(first, dict):
                # Single label
                label = str(first.get("label", "")).lower()
                score = float(first.get("score", 0.0))
                
                if "toxic" in label or "hate" in label:
                    toxic_score = score
                else:
                    toxic_score = 1.0 - score
            
            toxic_pct = max(0.0, min(100.0, toxic_score * 100.0))
            
            print(f"[NLP] Toxicity: {toxic_pct:.2f}%", flush=True)
            
            return {
                "toxic": round(toxic_pct, 2),
                "non_toxic": round(100.0 - toxic_pct, 2)
            }
            
        except Exception as e:
            print(f"[NLP] Toxicity error: {e}", flush=True)
            return self._fallback_toxicity(text)
    
    def _fallback_toxicity(self, text: str) -> Dict[str, float]:
        """Profanity check"""
        profanity = ['damn', 'hell', 'crap', 'shit', 'fuck', 'ass', 'bitch']
        count = sum(1 for w in profanity if w in text.lower())
        toxic = min(count * 20.0, 100.0)
        return {"toxic": round(toxic, 2), "non_toxic": round(100 - toxic, 2)}
    
    def analyze_competency(self, text: str, candidate_labels: List[str]) -> Dict[str, float]:
        """Zero-shot (0-100)"""
        if not text or not candidate_labels:
            return {l: 50.0 for l in candidate_labels}
        
        if self.zero_shot_classifier is None:
            return {l: 50.0 for l in candidate_labels}
        
        try:
            result = self.zero_shot_classifier(
                text[:512],
                candidate_labels=candidate_labels,
                multi_label=True
            )
            return {
                l: round(float(s) * 100, 2)
                for l, s in zip(result['labels'], result['scores'])
            }
        except Exception as e:
            print(f"[NLP] Competency error: {e}", flush=True)
            return {l: 50.0 for l in candidate_labels}
    
    def detect_keywords(
        self,
        text: str,
        positive_keywords: List[str],
        negative_keywords: List[str]
    ) -> Dict[str, any]:
        """Keywords (0-100)"""
        if not text:
            return {
                "positive_count": 0,
                "negative_count": 0,
                "positive_keywords": [],
                "negative_keywords": [],
                "score": 50.0
            }
        
        text_lower = text.lower()
        pos_matches = [k for k in positive_keywords if k.lower() in text_lower]
        neg_matches = [k for k in negative_keywords if k.lower() in text_lower]
        
        total = len(pos_matches) + len(neg_matches)
        score = (len(pos_matches) / total) * 100 if total > 0 else 50.0
        
        return {
            "positive_count": len(pos_matches),
            "negative_count": len(neg_matches),
            "positive_keywords": pos_matches,
            "negative_keywords": neg_matches,
            "score": round(score, 2)
        }
