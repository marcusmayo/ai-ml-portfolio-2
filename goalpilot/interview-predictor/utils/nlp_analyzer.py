"""
NLP Analyzer
Performs sentiment analysis, toxicity detection, and competency assessment
"""

import re
from typing import Dict, List
from transformers import pipeline
import torch


class NLPAnalyzer:
    """Analyzes text using multiple NLP models"""
    
    def __init__(self):
        self.sentiment_analyzer = None
        self.toxicity_analyzer = None
        self.zero_shot_classifier = None
        
    def load_models(self):
        """Load all NLP models"""
        if self.sentiment_analyzer is None:
            print("Loading sentiment analysis model...")
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=-1
            )
            
        if self.toxicity_analyzer is None:
            print("Loading toxicity detection model...")
            self.toxicity_analyzer = pipeline(
                "text-classification",
                model="unitary/toxic-bert",
                device=-1
            )
            
        if self.zero_shot_classifier is None:
            print("Loading zero-shot classifier...")
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
                device=-1
            )
        
        print("All NLP models loaded successfully")
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""
        self.load_models()
        
        # Truncate text if too long
        text = text[:512] if len(text) > 512 else text
        
        result = self.sentiment_analyzer(text)[0]
        label = result['label']
        score = result['score']
        
        # Convert to standard format
        sentiment_scores = {
            'positive': 0.0,
            'neutral': 0.0,
            'negative': 0.0
        }
        
        if 'positive' in label.lower():
            sentiment_scores['positive'] = score * 100
        elif 'negative' in label.lower():
            sentiment_scores['negative'] = score * 100
        else:
            sentiment_scores['neutral'] = score * 100
            
        return sentiment_scores
    
    def analyze_toxicity(self, text: str) -> Dict[str, float]:
        """Analyze toxicity of text"""
        self.load_models()
        
        text = text[:512] if len(text) > 512 else text
        
        result = self.toxicity_analyzer(text)[0]
        
        # Return toxicity score (lower is better)
        toxic_score = result['score'] if result['label'] == 'toxic' else (1 - result['score'])
        
        return {
            'toxic': toxic_score * 100,
            'non_toxic': (1 - toxic_score) * 100
        }
    
    def analyze_competency(self, text: str, candidate_labels: List[str]) -> Dict[str, float]:
        """Analyze competencies using zero-shot classification"""
        self.load_models()
        
        text = text[:512] if len(text) > 512 else text
        
        result = self.zero_shot_classifier(text, candidate_labels)
        
        # Convert to dict
        competency_scores = {}
        for label, score in zip(result['labels'], result['scores']):
            competency_scores[label] = score * 100
            
        return competency_scores
    
    def detect_keywords(self, text: str, positive_keywords: List[str], negative_keywords: List[str]) -> Dict[str, any]:
        """Detect presence of positive and negative keywords"""
        
        text_lower = text.lower()
        
        positive_count = sum(1 for keyword in positive_keywords if keyword.lower() in text_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword.lower() in text_lower)
        
        total_keywords = len(positive_keywords) + len(negative_keywords)
        
        # Calculate score (positive keywords boost, negative keywords reduce)
        if total_keywords > 0:
            score = ((positive_count - negative_count) / total_keywords) * 100
            score = max(0, min(100, score + 50))  # Normalize to 0-100
        else:
            score = 50.0
        
        return {
            'score': score,
            'positive_found': positive_count,
            'negative_found': negative_count
        }
