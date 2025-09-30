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
        """Initialize the NLP analyzer with model pipelines"""
        self.sentiment_analyzer = None
        self.toxicity_analyzer = None
        self.zero_shot_classifier = None
        
    def load_models(self):
        """Load all NLP models (lazy loading)"""
        if self.sentiment_analyzer is None:
            print("Loading sentiment analysis model...")
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=-1  # CPU
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
        """
        Analyze sentiment of text
        
        Returns:
            Dict with 'positive', 'neutral', 'negative' scores
        """
        self.load_models()
        
        # Split into chunks (model has token limits)
        chunks = self._split_text(text, max_length=500)
        
        sentiment_scores = {"positive": 0, "neutral": 0, "negative": 0}
        
        for chunk in chunks:
            result = self.sentiment_analyzer(chunk)[0]
            label = result['label'].lower()
            score = result['score']
            
            if label in sentiment_scores:
                sentiment_scores[label] += score
        
        # Average across chunks
        num_chunks = len(chunks)
        for key in sentiment_scores:
            sentiment_scores[key] /= num_chunks
        
        return sentiment_scores
    
    def analyze_toxicity(self, text: str) -> Dict[str, float]:
        """
        Analyze toxicity of text
        
        Returns:
            Dict with 'toxic' and 'non_toxic' scores
        """
        self.load_models()
        
        chunks = self._split_text(text, max_length=500)
        
        toxic_score = 0
        
        for chunk in chunks:
            result = self.toxicity_analyzer(chunk)[0]
            if result['label'].lower() == 'toxic':
                toxic_score += result['score']
        
        toxic_score /= len(chunks)
        
        return {
            "toxic": toxic_score,
            "non_toxic": 1 - toxic_score
        }
    
    def analyze_competency(self, text: str) -> Dict[str, float]:
        """
        Analyze competency signals using zero-shot classification
        
        Returns:
            Dict with scores for different competency dimensions
        """
        self.load_models()
        
        # Define competency labels
        competency_labels = [
            "clear communication",
            "technical knowledge",
            "problem solving ability",
            "enthusiasm and motivation",
            "cultural fit",
            "relevant experience"
        ]
        
        # Analyze text
        result = self.zero_shot_classifier(
            text,
            candidate_labels=competency_labels,
            multi_label=True
        )
        
        # Convert to dict
        competency_scores = {}
        for label, score in zip(result['labels'], result['scores']):
            competency_scores[label] = score
        
        return competency_scores
    
    def detect_keywords(self, text: str) -> Dict[str, any]:
        """
        Detect positive and negative keyword signals
        
        Returns:
            Dict with keyword counts and flags
        """
        text_lower = text.lower()
        
        # Positive interviewer cues
        positive_keywords = [
            "next steps", "we're excited", "move forward", "great fit",
            "impressed", "strong candidate", "hr will reach out",
            "we'll be in touch", "looking forward", "perfect match"
        ]
        
        # Negative cues
        negative_keywords = [
            "not a fit", "unfortunately", "other candidates",
            "don't think", "concerns about", "lacking experience"
        ]
        
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
        
        return {
            "positive_keywords": positive_count,
            "negative_keywords": negative_count,
            "has_positive_signals": positive_count > 0,
            "has_negative_signals": negative_count > 0
        }
    
    def count_filler_words(self, text: str) -> Dict[str, any]:
        """
        Count filler words (um, uh, like, you know, etc.)
        
        Returns:
            Dict with filler word statistics
        """
        fillers = ["um", "uh", "like", "you know", "i mean", "sort of", "kind of"]
        
        text_lower = text.lower()
        word_count = len(text.split())
        
        filler_count = 0
        for filler in fillers:
            filler_count += len(re.findall(r'\b' + filler + r'\b', text_lower))
        
        filler_rate = filler_count / word_count if word_count > 0 else 0
        
        return {
            "filler_count": filler_count,
            "word_count": word_count,
            "filler_rate": filler_rate,
            "excessive_fillers": filler_rate > 0.05  # >5% is excessive
        }
    
    def analyze_all(self, text: str) -> Dict[str, any]:
        """
        Run all analyses on text
        
        Returns:
            Comprehensive analysis dictionary
        """
        print("Running comprehensive NLP analysis...")
        
        return {
            "sentiment": self.analyze_sentiment(text),
            "toxicity": self.analyze_toxicity(text),
            "competency": self.analyze_competency(text),
            "keywords": self.detect_keywords(text),
            "filler_words": self.count_filler_words(text)
        }
    
    def _split_text(self, text: str, max_length: int = 500) -> List[str]:
        """Split text into chunks for processing"""
        words = text.split()
        chunks = []
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            if len(' '.join(current_chunk)) >= max_length:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks if chunks else [text]
