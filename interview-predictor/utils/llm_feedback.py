"""
LLM Feedback Generator using Google Gemini (Fixed)
"""

import google.generativeai as genai
import os
from typing import Dict, Any


class LLMFeedbackGenerator:
    """Generates actionable feedback using Google Gemini"""
    
    def __init__(self):
        # Use correct model names from API documentation
        self.models_to_try = [
            "gemini-2.0-flash",      # Latest model
            "gemini-1.5-flash-001",  # Stable versioned model
            "gemini-1.5-flash",      # Base model
            "gemini-pro"             # Fallback
        ]
        self.client = None
        self.working_model = None
        
    def configure_api(self, api_key: str = None):
        """Configure Gemini API and find working model"""
        if api_key:
            genai.configure(api_key=api_key)
        else:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("Warning: No Gemini API key found. Set GEMINI_API_KEY env var.")
                return False
            genai.configure(api_key=api_key)
        
        # Try to find a working model
        for model_name in self.models_to_try:
            try:
                print(f"Trying model: {model_name}")
                test_client = genai.GenerativeModel(model_name)
                
                # Test with a simple prompt
                response = test_client.generate_content("Say 'test successful'")
                if response and response.text:
                    self.client = test_client
                    self.working_model = model_name
                    print(f"✅ Successfully configured with model: {model_name}")
                    return True
                    
            except Exception as e:
                print(f"❌ Model {model_name} failed: {str(e)}")
                continue
        
        print("❌ No working Gemini models found")
        return False
    
    def list_available_models(self):
        """List available models (for debugging)"""
        try:
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    print(f"Available model: {model.name}")
        except Exception as e:
            print(f"Error listing models: {e}")
    
    def generate_feedback(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable interview feedback"""
        if not self.client or not self.working_model:
            return self._generate_fallback_feedback(analysis_results)
        
        try:
            score = analysis_results.get('score', 0)
            prediction = analysis_results.get('prediction', 'Unknown')
            components = analysis_results.get('component_scores', {})
            transcript = analysis_results.get('transcript', '')
            
            prompt = f"""You are an expert interview coach. Analyze this interview performance and provide specific, actionable feedback.

INTERVIEW METRICS:
- Overall Score: {score}%
- Prediction: {prediction}
- Sentiment Score: {components.get('sentiment', 0):.1f}%
- Communication Quality: {components.get('toxicity', 0):.1f}%
- Technical Competency: {components.get('competency', 0):.1f}%
- Professional Language: {components.get('keywords', 0):.1f}%

TRANSCRIPT SAMPLE:
{transcript[:500]}...

Provide feedback in this EXACT format:

**STRENGTHS (3 specific items):**
- [Specific strength based on the data]
- [Another strength with evidence]
- [Third strength]

**AREAS FOR IMPROVEMENT (3 specific items):**
- [Specific area with actionable advice]
- [Another area with clear guidance]  
- [Third area]

**NEXT STEPS (2 actionable items):**
- [Specific action to take before next interview]
- [Another concrete next step]

Keep each point concise (1-2 sentences)."""

            response = self.client.generate_content(prompt)
            
            if response and response.text:
                return {
                    "success": True,
                    "feedback": response.text.strip(),
                    "model_used": self.working_model
                }
            else:
                return self._generate_fallback_feedback(analysis_results)
                
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return self._generate_fallback_feedback(analysis_results)
    
    def _generate_fallback_feedback(self, analysis_results):
        """Generate simple fallback feedback when Gemini fails"""
        score = analysis_results.get('score', 0)
        components = analysis_results.get('component_scores', {})
        prediction = analysis_results.get('prediction', 'Unknown')
        
        feedback = f"""**ANALYSIS SUMMARY**

Overall Performance: {score:.1f}% ({prediction})

**STRENGTHS:**
- Sentiment analysis shows {components.get('sentiment', 0):.0f}% positive emotional tone
- Communication quality rated at {components.get('toxicity', 0):.0f}%  
- Technical competency assessed at {components.get('competency', 0):.0f}%

**AREAS FOR IMPROVEMENT:**
"""
        
        if components.get('sentiment', 0) < 70:
            feedback += "• Work on maintaining a more positive and confident tone\n"
        if components.get('toxicity', 0) < 90:
            feedback += "• Focus on professional language and communication clarity\n"
        if components.get('competency', 0) < 60:
            feedback += "• Strengthen technical explanations with specific examples\n"
        if components.get('keywords', 0) < 50:
            feedback += "• Use more positive action words and professional terminology\n"
        
        feedback += """
**NEXT STEPS:**
- Practice answering questions with the STAR method (Situation, Task, Action, Result)
- Prepare 2-3 detailed stories showcasing specific achievements and measurable outcomes"""

        return {
            "success": True,
            "feedback": feedback,
            "model_used": "Fallback Rule-Based Generator"
        }
