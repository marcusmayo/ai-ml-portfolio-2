"""
Simple in-memory metrics tracker for API performance
Tracks: total requests, successful plans, eval scores
"""
from datetime import datetime
from typing import Dict, List
import threading

class MetricsTracker:
    """Thread-safe metrics collection for plan generation"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._data = {
            'total_requests': 0,
            'successful_plans': 0,
            'failed_plans': 0,
            'eval_scores': [],  # Quality scores from evaluator
            'start_time': datetime.utcnow().isoformat()
        }
    
    def record_request(self, success: bool, eval_score: float = None):
        """Record a plan generation attempt"""
        with self._lock:
            self._data['total_requests'] += 1
            
            if success:
                self._data['successful_plans'] += 1
                if eval_score is not None:
                    self._data['eval_scores'].append(eval_score)
            else:
                self._data['failed_plans'] += 1
    
    def get_metrics(self) -> Dict:
        """Return current metrics snapshot"""
        with self._lock:
            total = self._data['total_requests']
            success_rate = (
                (self._data['successful_plans'] / total * 100) 
                if total > 0 else 0.0
            )
            
            avg_eval_score = (
                sum(self._data['eval_scores']) / len(self._data['eval_scores'])
                if self._data['eval_scores'] else 0.0
            )
            
            return {
                'total_requests': total,
                'successful_plans': self._data['successful_plans'],
                'failed_plans': self._data['failed_plans'],
                'success_rate_percent': round(success_rate, 1),
                'average_quality_score': round(avg_eval_score, 2),
                'uptime_since': self._data['start_time']
            }

# Global singleton instance
metrics = MetricsTracker()
