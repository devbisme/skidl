"""Module for LLM provider implementations for circuit analysis."""

from abc import ABC, abstractmethod
import os
from typing import Dict, Optional, Any
import anthropic
from openai import OpenAI
from anthropic import Anthropic
import requests
from datetime import datetime

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self) -> Any:
        """Initialize the API client."""
        pass
    
    @abstractmethod
    def generate_analysis(self, prompt: str, **kwargs) -> Dict:
        """Generate analysis using the LLM."""
        pass

class AnthropicProvider(LLMProvider):
    """Provider for Anthropic's Claude models."""
    
    def _initialize_client(self) -> Anthropic:
        api_key = self.api_key or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("Anthropic API key not provided")
        return Anthropic(api_key=api_key)
    
    def generate_analysis(self, prompt: str, **kwargs) -> Dict:
        try:
            # Use the specified model or default to claude-3-sonnet
            model = kwargs.get('model') or "claude-3-sonnet-20240229"
            max_tokens = kwargs.get('max_tokens', 12000)  # Increased from 8000
            
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return {
                "success": True,
                "analysis": response.content[0].text,
                "timestamp": int(datetime.now().timestamp()),
                "provider": "anthropic"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "anthropic"
            }

class OpenAIProvider(LLMProvider):
    """Provider for OpenAI's GPT models."""
    
    def _initialize_client(self) -> OpenAI:
        api_key = self.api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not provided")
        return OpenAI(api_key=api_key)
    
    def generate_analysis(self, prompt: str, **kwargs) -> Dict:
        try:
            model = kwargs.get('model', 'gpt-4-turbo-preview')
            max_tokens = kwargs.get('max_tokens', 4000)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=max_tokens
            )
            
            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "timestamp": response.created,
                "provider": "openai"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "openai"
            }

class OpenRouterProvider(LLMProvider):
    """Provider for OpenRouter API access to various LLMs."""
    
    def _initialize_client(self) -> None:
        self.api_key = self.api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided")
        # OpenRouter uses direct HTTP requests, so no client initialization needed
        return None
    
    def generate_analysis(self, prompt: str, **kwargs) -> Dict:
        try:
            model = kwargs.get('model', 'anthropic/claude-3-opus-20240229')
            max_tokens = kwargs.get('max_tokens', 4000)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": kwargs.get('referer', 'https://skidl.org'),  # Replace with your domain
                "X-Title": kwargs.get('title', 'SKiDL Circuit Analysis')
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [{
                        "role": "user",
                        "content": prompt
                    }],
                    "max_tokens": max_tokens
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "analysis": result['choices'][0]['message']['content'],
                "timestamp": result['created'],
                "provider": "openrouter"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": "openrouter"
            }

def get_provider(provider_name: str, api_key: Optional[str] = None) -> LLMProvider:
    """Factory function to get the appropriate LLM provider."""
    providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "openrouter": OpenRouterProvider
    }
    
    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}")
        
    return providers[provider_name](api_key=api_key)