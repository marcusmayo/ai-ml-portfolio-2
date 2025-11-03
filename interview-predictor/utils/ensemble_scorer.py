"""
Ensemble Scorer - PRODUCTION VERSION (Fixed)
Uses segment-level aggregation for better accuracy
"""

from typing import Dict, Any, List


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Safe clamp with NaN handling"""
    try:
        v = float(x)
    except Exception:
        return 50.0
    if v != v:  # NaN check
        return 50.0
    return max(lo, min(hi, v))


class EnsembleScorer:
    """Combines sentiment, toxicity, competency, keywords"""
    
    def calculate_ensemble_score(
        self,
        sentiment_scores: Dict[str, float],
        toxicity_score: float,
        competency_scores: Dict[str, float],
        keyword_match: Dict[str, Any],
        segment_sentiments: List[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate final score
        
        NEW: Can use segment-level sentiment aggregation for better accuracy
        """
        
        # ---- Component 1: Sentiment (25%)
        if segment_sentiments and len(segment_sentiments) > 0:
            # Use segment aggregation (more accurate)
            pos_scores = [_clamp(s.get("positive", 50.0)) for s in segment_sentiments]
            sentiment_component = sum(pos_scores) / len(pos_scores)
            print(f"[SCORER] Using segment sentiment avg: {sentiment_component:.2f}% from {len(pos_scores)} segments", flush=True)
        else:
            # Fallback to full-text sentiment
            pos = _clamp(sentiment_scores.get("positive", 50.0))
            neu = _clamp(sentiment_scores.get("neutral", 0.0))
            # Don't let formula exceed 100
            sentiment_component = min(100.0, pos + 0.3 * neu)
            print(f"[SCORER] Using full-text sentiment: pos={pos:.2f}%, neu={neu:.2f}%, component={sentiment_component:.2f}%", flush=True)
        
        # ---- Component 2: Toxicity (25%) - INVERTED
        toxic_raw = _clamp(toxicity_score)
        toxicity_component = 100.0 - toxic_raw
        
        # ---- Component 3: Competency (30%)
        comp_vals = [_clamp(v) for v in (competency_scores or {}).values()]
        competency_component = sum(comp_vals) / len(comp_vals) if comp_vals else 50.0
        
        # ---- Component 4: Keywords (20%)
        keyword_component = _clamp((keyword_match or {}).get("score", 50.0))
        
        # ---- Weights
        w_sent, w_tox, w_comp, w_key = 0.25, 0.25, 0.30, 0.20
        
        # ---- Weighted sum
        final_score = (
            sentiment_component * w_sent +
            toxicity_component * w_tox +
            competency_component * w_comp +
            keyword_component * w_key
        )
        
        final_score = _clamp(final_score)
        
        print(f"[SCORER] Final components: sent={sentiment_component:.2f}, tox={toxicity_component:.2f}, comp={competency_component:.2f}, key={keyword_component:.2f}", flush=True)
        print(f"[SCORER] Final score: {final_score:.2f}", flush=True)
        
        # ---- Prediction thresholds
        if final_score >= 70:
            prediction = "Strong"
            confidence = "High"
        elif final_score >= 50:
            prediction = "Moderate"
            confidence = "Medium"
        else:
            prediction = "Weak"
            confidence = "Low"
        
        return {
            "prediction": prediction,
            "score": round(final_score, 2),
            "confidence": confidence,
            "component_scores": {
                "sentiment": round(sentiment_component, 2),
                "toxicity": round(toxicity_component, 2),
                "competency": round(competency_component, 2),
                "keywords": round(keyword_component, 2)
            },
            "component_contributions": {
                "sentiment": 25.0,
                "toxicity": 25.0,
                "competency": 30.0,
                "keywords": 20.0
            }
        }
