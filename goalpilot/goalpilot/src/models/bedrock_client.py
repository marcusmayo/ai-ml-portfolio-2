"""
AWS Bedrock Client for Claude AI
"""
import json
import boto3
from typing import List, Dict, Any
from src.utils.config import settings
from src.utils.logger import logger

class BedrockClient:
    """Client for invoking Claude via AWS Bedrock"""
    
    def __init__(self):
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=settings.aws_region
        )
        self.model_id = settings.bedrock_model
        logger.info(f"Initialized Bedrock client with model: {self.model_id}")
    
    def invoke(
        self,
        messages: List[Dict[str, str]],
        system: str = None,
        max_tokens: int = 2000,
        temperature: float = 0.2
    ) -> str:
        """
        Invoke Claude model
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system: System prompt (optional)
            max_tokens: Max tokens to generate
            temperature: Sampling temperature (0-1)
            
        Returns:
            Generated text from Claude
        """
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        if system:
            request_body["system"] = system
        
        try:
            logger.debug(f"Invoking Bedrock model: {self.model_id}")
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            if 'content' in response_body and len(response_body['content']) > 0:
                text = response_body['content'][0]['text']
                logger.debug(f"Received response: {len(text)} characters")
                return text
            else:
                logger.error("No content in Bedrock response")
                return ""
                
        except Exception as e:
            logger.error(f"Bedrock invocation error: {e}")
            raise

# Global instance
bedrock_client = BedrockClient()

__all__ = ["bedrock_client", "BedrockClient"]
