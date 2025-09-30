"""
Ensemble Scorer
Combines multiple analysis signals into a single prediction
"""

from typing import Dict, Tuple


class EnsembleScorer:
    """Combines sentiment, toxicity, competency, and keyword signals into a prediction"""
    
    def __init__(self):
        """Initialize scorer with weights"""
        # Weights for each component (must sum to 1.0)
        self.weights = {
            "sentiment": 0.30,      # 30% - Overall conversation tone
            "toxicity": 0.25,       # 25% - Professional communication
            "competency": 0.30,     # 30% - Demonstrated skills/fit
            "keywords": 0.10,       # 10% - Interviewer cues
            "filler_penalty": 0.05  # 5% - Speech clarity penalty
        }
        
        # Thresholds for classification
        self.thresholds = {
            "likely": 0.70,      # >= 70% = Likely to advance
            "unlikely": 0.40     # < 40% = Unlikely to advance
        }
    
    def calculate_sentiment_score(self, sentiment: Dict[str, float]) -> float:
        """
        Convert sentiment analysis to a 0-1 score
        
        Args:
            sentiment: Dict with 'positive', 'neutral', 'negative' scores
            
        Returns:
            Score from 0 (very negative) to 1 (very positive)
        """
        # Positive is good, negative is bad, neutral is middle
        score = sentiment.get("positive", 0) - sentiment.get("negative", 0) * 0.5
        
        # Normalize to 0-1 range
        return max(0, min(1, (score + 0.5)))
    
    def calculate_toxicity_score(self, toxicity: Dict[str, float]) -> float:
        """
        Convert toxicity analysis to a 0-1 score
        
        Args:
            toxicity: Dict with 'toxic' and 'non_toxic' scores
            
        Returns:
            Score from 0 (toxic) to 1 (professional)
        """
        # Non-toxic is good
        return toxicity.get("non_toxic", 0.5)
    
    def calculate_competency_score(self, competency: Dict[str, float]) -> float:
        """
        Convert competency analysis to a 0-1 score
        
        Args:
            competency: Dict with competency dimension scores
            
        Returns:
            Average competency score
        """
        if not competency:
            return 0.5
        
        # Average all competency dimensions
        return sum(competency.values()) / len(competency)
    
    def calculate_keyword_score(self, keywords: Dict[str, any]) -> float:
        """
        Convert keyword detection to a 0-1 score
        
        Args:
            keywords: Dict with positive/negative keyword counts
            
        Returns:
            Score based on keyword balance
        """
        positive = keywords.get("positive_keywords", 0)
        negative = keywords.get("negative_keywords", 0)
        
        if positive == 0 and negative == 0:
            return 0.5  # Neutral if no keywords
        
        # More positive than negative is good
        net_score = (positive - negative) / max(positive + negative, 1)
        
        # Normalize to 0-1
        return max(0, min(1, (net_score + 1) / 2))
    
    def calculate_filler_penalty(self, filler_words: Dict[str, any]) -> float:
        """
        Calculate penalty for excessive filler words
        
        Args:
            filler_words: Dict with filler word statistics
            
        Returns:
            Penalty score (0 = heavy penalty, 1 = no penalty)
        """
        filler_rate = filler_words.get("filler_rate", 0)
        
        # Penalize if filler rate > 3%
        if filler_rate < 0.03:
            return 1.0  # No penalty
        elif filler_rate > 0.10:
            return 0.0  # Maximum penalty
        else:
            # Linear penalty between 3% and 10%
            return 1.0 - ((filler_rate - 0.03) / 0.07)
    
    def calculate_ensemble_score(self, analysis: Dict[str, any]) -> Dict[str, any]:
        """
        Calculate final ensemble score from all analyses
        
        Args:
            analysis: Complete analysis dictionary from NLPAnalyzer
            
        Returns:
            Dict with score, prediction, and component breakdown
        """
        # Calculate individual component scores
        sentiment_score = self.calculate_sentiment_score(analysis["sentiment"])
        toxicity_score = self.calculate_toxicity_score(analysis["toxicity"])
        competency_score = self.calculate_competency_score(analysis["competency"])
        keyword_score = self.calculate_keyword_score(analysis["keywords"])
        filler_score = self.calculate_filler_penalty(analysis["filler_words"])
        
        # Calculate weighted ensemble score
        ensemble_score = (
            sentiment_score * self.weights["sentiment"] +
            toxicity_score * self.weights["toxicity"] +
            competency_score * self.weights["competency"] +
            keyword_score * self.weights["keywords"] +
            filler_score * self.weights["filler_penalty"]
        )
        
        # Classify based on thresholds
        if ensemble_score >= self.thresholds["likely"]:
            prediction = "Likely"
            confidence = "High"
        elif ensemble_score < self.thresholds["unlikely"]:
            prediction = "Unlikely"
            confidence = "High"
        else:
            prediction = "Inconclusive"
            confidence = "Medium"
        
        # Calculate component contributions (for visualization)
        total_weighted = (
            sentiment_score * self.weights["sentiment"] +
            toxicity_score * self.weights["toxicity"] +
            competency_score * self.weights["competency"] +
            keyword_score * self.weights["keywords"] +
            filler_score * self.weights["filler_penalty"]
        )
        
        component_contributions = {
            "sentiment": (sentiment_score * self.weights["sentiment"] / total_weighted * 100) if total_weighted > 0 else 0,
            "toxicity": (toxicity_score * self.weights["toxicity"] / total_weighted * 100) if total_weighted > 0 else 0,
            "competency": (competency_score * self.weights["competency"] / total_weighted * 100) if total_weighted > 0 else 0,
            "keywords": (keyword_score * self.weights["keywords"] / total_weighted * 100) if total_weighted > 0 else 0,
            "filler_penalty": (filler_score * self.weights["filler_penalty"] / total_weighted * 100) if total_weighted > 0 else 0
        }
        
        return {
            "score": round(ensemble_score * 100, 2),  # Convert to percentage
            "prediction": prediction,
            "confidence": confidence,
            "component_scores": {
                "sentiment": round(sentiment_score * 100, 2),
                "toxicity": round(toxicity_score * 100, 2),
                "competency": round(competency_score * 100, 2),
                "keywords": round(keyword_score * 100, 2),
                "filler_penalty": round(filler_score * 100, 2)
            },
            "component_contributions": {
                k: round(v, 2) for k, v in component_contributions.items()
            }
        }
    
    def get_explanation(self, result: Dict[str, any]) -> str:
        """
        Generate human-readable explanation of the prediction
        
        Args:
            result: Result dictionary from calculate_ensemble_score
            
        Returns:
            Explanation string
        """
        score = result["score"]
        prediction = result["prediction"]
        components = result["component_scores"]
        
        explanation = f"Overall Score: {score}% - {prediction}\n\n"
        explanation += "Component Breakdown:\n"
        explanation += f"- Sentiment: {components['sentiment']}% (conversation tone)\n"
        explanation += f"- Professional Communication: {components['toxicity']}% (non-toxic)\n"
        explanation += f"- Competency Signals: {components['competency']}% (skills/fit)\n"
        explanation += f"- Interviewer Cues: {components['keywords']}% (positive keywords)\n"
        explanation += f"- Speech Clarity: {components['filler_penalty']}% (low filler words)\n"
        
        return explanation
