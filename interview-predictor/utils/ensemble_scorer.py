"""
Ensemble Scorer
Combines multiple analysis signals into a single prediction
"""

from typing import Dict


class EnsembleScorer:
    """Combines sentiment, toxicity, competency, and keyword signals"""
    
    def calculate_ensemble_score(
        self,
        sentiment_scores: Dict[str, float],
        toxicity_score: float,
        competency_scores: Dict[str, float],
        keyword_match: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Calculate final ensemble score
        
        Args:
            sentiment_scores: Dict with 'positive', 'neutral', 'negative'
            toxicity_score: Toxicity score (0-100, lower is better)
            competency_scores: Dict of competency scores
            keyword_match: Dict with 'score', 'positive_found', 'negative_found'
        
        Returns:
            Dict with prediction, score, confidence, components
        """
        
        # Component 1: Sentiment (25% weight)
        sentiment_score = sentiment_scores.get('positive', 0)
        
        # Component 2: Toxicity (25% weight) - invert so higher is better
        toxicity_component = 100 - toxicity_score
        
        # Component 3: Competency (30% weight) - average of all competencies
        competency_values = list(competency_scores.values())
        competency_score = sum(competency_values) / len(competency_values) if competency_values else 50.0
        
        # Component 4: Keywords (20% weight)
        keyword_score = keyword_match.get('score', 50.0)
        
        # Calculate weighted ensemble score
        final_score = (
            sentiment_score * 0.25 +
            toxicity_component * 0.25 +
            competency_score * 0.30 +
            keyword_score * 0.20
        )
        
        # Determine prediction
        if final_score >= 70:
            prediction = "Likely"
            confidence = "High"
        elif final_score >= 40:
            prediction = "Inconclusive"
            confidence = "Medium"
        else:
            prediction = "Unlikely"
            confidence = "Low"
        
        # Component scores for display
        component_scores = {
            "sentiment": round(sentiment_score, 2),
            "toxicity": round(toxicity_component, 2),
            "competency": round(competency_score, 2),
            "keywords": round(keyword_score, 2)
        }
        
        # Component contributions (percentage of final score)
        component_contributions = {
            "sentiment": 25.0,
            "toxicity": 25.0,
            "competency": 30.0,
            "keywords": 20.0
        }
        
        return {
            "prediction": prediction,
            "score": round(final_score, 2),
            "confidence": confidence,
            "component_scores": component_scores,
            "component_contributions": component_contributions
        }
