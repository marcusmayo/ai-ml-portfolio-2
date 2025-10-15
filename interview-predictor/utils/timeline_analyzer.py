"""
Timeline Analyzer - Uses Real NLP Models for Segment Scoring
"""

from typing import List, Dict
from utils.nlp_analyzer import NLPAnalyzer
from utils.ensemble_scorer import EnsembleScorer


class TimelineAnalyzer:
    """Creates timeline with real NLP-based segment scores"""
    
    def __init__(self):
        self.nlp = NLPAnalyzer()
        self.scorer = EnsembleScorer()
        
    def analyze_segments(self, segments: List[Dict]) -> List[Dict]:
        """
        Analyze each segment with real NLP models
        
        Args:
            segments: List of transcript segments with timestamps
            
        Returns:
            List of scored segments with NLP analysis
        """
        if not segments:
            return []
        
        # Load NLP models once
        self.nlp.load_models()
        
        scored_segments = []
        
        for segment in segments:
            segment_text = segment.get('text', '')
            
            if not segment_text or len(segment_text.strip()) < 10:
                # Skip very short segments
                continue
            
            # Run real NLP analysis on this segment
            sentiment = self.nlp.analyze_sentiment(segment_text)
            toxicity = self.nlp.analyze_toxicity(segment_text)
            
            # Simplified competency for segments (faster)
            competencies = {"general": 50.0}  # Default
            if len(segment_text) > 50:
                try:
                    competencies = self.nlp.analyze_competency(
                        segment_text,
                        candidate_labels=["professional", "competent"]
                    )
                except:
                    pass
            
            # Simple keyword detection for segment
            keywords = self.nlp.detect_keywords(
                segment_text,
                positive_keywords=["yes", "definitely", "experience", "achieved", "successfully"],
                negative_keywords=["um", "uh", "maybe", "I guess"]
            )
            
            # Calculate ensemble score for this segment
            results = self.scorer.calculate_ensemble_score(
                sentiment_scores=sentiment,
                toxicity_score=toxicity["toxic"],
                competency_scores=competencies,
                keyword_match=keywords
            )
            
            print(f'Segment {len(scored_segments)+1}: text="{segment_text[:50]}..." score={results["score"]:.1f}%')
            scored_segments.append({
                'start': segment.get('start', 0),
                'end': segment.get('end', 0),
                'text': segment_text,
                'score': results['score'],
                'sentiment': sentiment,
                'toxicity': toxicity,
                'prediction': results['prediction']
            })
        
        return scored_segments
    
    def create_timeline_data(self, scored_segments: List[Dict], duration: float) -> Dict:
        """
        Create timeline visualization data from scored segments
        
        Args:
            scored_segments: Segments with NLP scores
            duration: Total audio duration in seconds
            
        Returns:
            Timeline data with bins for visualization
        """
        if not scored_segments or duration <= 0:
            return {'bins': [], 'duration': 0, 'bin_size': 0}
        
        # Use 30-second bins for timeline
        bin_size = 30
        num_bins = int(duration / bin_size) + 1
        
        bins = []
        
        for i in range(num_bins):
            bin_start = i * bin_size
            bin_end = min((i + 1) * bin_size, duration)
            
            # Find segments in this time bin
            bin_segments = [
                seg for seg in scored_segments
                if seg['start'] >= bin_start and seg['start'] < bin_end
            ]
            
            if bin_segments:
                # Average real NLP scores for this bin
                avg_score = sum(seg['score'] for seg in bin_segments) / len(bin_segments)
                
                # Color coding based on real scores
                if avg_score >= 70:
                    color, label = 'green', 'Strong'
                elif avg_score >= 40:
                    color, label = 'yellow', 'Okay'
                else:
                    color, label = 'red', 'Weak'
                
                bins.append({
                    'start': bin_start,
                    'end': bin_end,
                    'score': round(avg_score, 1),
                    'color': color,
                    'label': label,
                    'segment_count': len(bin_segments),
                    'segments': [
                        {
                            'text': seg['text'][:100] + '...' if len(seg['text']) > 100 else seg['text'],
                            'score': seg['score'],
                            'start': seg['start'],
                            'end': seg['end']
                        }
                        for seg in bin_segments
                    ]
                })
        
        return {
            'bins': bins,
            'duration': duration,
            'bin_size': bin_size
        }
