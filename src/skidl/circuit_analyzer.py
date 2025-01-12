"""Module for circuit analysis using LLMs."""

from typing import Dict, Optional
from datetime import datetime
import time
import os
import json
import requests
from typing import Dict, Any, List, Optional, Union

class LLMInterface:
    """
    A flexible interface for interacting with various LLM providers.
    Supports custom prompts, logging, and different response formats.
    """
    
    def __init__(self,
                 provider: str = "openrouter",
                 model: str = None,
                 api_key: str = None,
                 base_url: str = None,
                 logging_enabled: bool = True,
                 max_length: int = 8000,
                 **kwargs):
        """
        Initialize LLM Interface
        """
        self.provider = provider.lower()
        self.model = model or self._get_default_model()
        # Support both OPENROUTER_API_KEY and ANTHROPIC_API_KEY for backward compatibility
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = base_url or self._get_default_base_url()
        self.max_length = max_length
        self.kwargs = kwargs

    def _get_default_model(self) -> str:
        """Get default model based on provider"""
        defaults = {
            "openrouter": "anthropic/claude-3.5-haiku",
            "ollama": "llama3.2",
            "anthropic": "claude-3-opus-20240229"
        }
        return defaults.get(self.provider, "")

    def _get_default_base_url(self) -> str:
        """Get default base URL based on provider"""
        defaults = {
            "openrouter": "https://openrouter.ai/api/v1",
            "ollama": "http://localhost:11434",
            "anthropic": "https://api.anthropic.com/v1"
        }
        return defaults.get(self.provider, "")

    def process(self,
                messages: List[Dict[str, str]],
                options: Optional[Dict[str, Any]] = None,
                **kwargs) -> Dict[str, Any]:
        """Process a request through the LLM"""
        if not messages:
            raise ValueError("Messages list cannot be empty")
            
        # Apply content length limit if specified
        if self.max_length:
            messages = self._truncate_messages(messages)
            
        # Merge options with instance kwargs
        request_options = {**self.kwargs, **(options or {}), **kwargs}
        
        # Process based on provider
        processor = getattr(self, f"_process_{self.provider}", None)
        if not processor:
            raise ValueError(f"Unsupported provider: {self.provider}")
            
        try:
            return processor(messages, request_options)
        except Exception as e:
            raise

    def _truncate_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Truncate message content to max_length"""
        truncated = []
        for msg in messages:
            content = msg.get('content', '')
            if len(content) > self.max_length:
                msg = dict(msg)
                msg['content'] = content[:self.max_length] + "..."
            truncated.append(msg)
        return truncated

    def _process_openrouter(self, 
                           messages: List[Dict[str, str]], 
                           options: Dict[str, Any]) -> Dict[str, Any]:
        """Process request through OpenRouter"""
        if not self.api_key:
            raise ValueError("API key required for OpenRouter")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/devbisme/skidl",  # Required
            "X-Title": "SKiDL Circuit Analyzer",  # Optional, shown in OpenRouter dashboard
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096,
            "headers": {  # OpenRouter-specific headers in the request body
                "HTTP-Referer": "https://github.com/devbisme/skidl",
                "X-Title": "SKiDL Circuit Analyzer"
            }
        }
        
        url = f"{self.base_url}/chat/completions"
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=30  # Add timeout to prevent hanging
        )
        response.raise_for_status()
        return response.json()

    def quick_prompt(self,
                    content: str,
                    system_prompt: Optional[str] = None,
                    temperature: float = 0.7) -> str:
        """Simplified interface for quick prompts"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": content})
        
        response = self.process(messages, {"temperature": temperature})
        return response['choices'][0]['message']['content']

class SkidlCircuitAnalyzer:
    """Circuit analyzer using Large Language Models."""
    
    def __init__(
        self,
        model: str = "anthropic/claude-3.5-haiku",
        api_key: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        analysis_flags: Optional[Dict[str, bool]] = None,
        **kwargs
    ):
        """
        Initialize the circuit analyzer.

        Args:
            model: Name of the LLM model to use
            api_key: API key for the LLM service
            custom_prompt: Additional custom prompt template to append
            analysis_flags: Dict of analysis sections to enable/disable
            **kwargs: Additional configuration options
        """
        self.llm = LLMInterface(
            provider="openrouter",
            model=model,
            api_key=api_key,
            **kwargs
        )
        
        self.custom_prompt = custom_prompt
        self.analysis_flags = analysis_flags or {
            "system_overview": True,
            "design_review": True,
            "power_analysis": True,
            "signal_integrity": True,
            "thermal_analysis": True,
            "noise_analysis": True,
            "testing_verification": True
        }
        self.config = kwargs

    def _generate_analysis_prompt(self, circuit_description: str) -> str:
        """
        Generate the complete analysis prompt.
        
        Args:
            circuit_description: Description of the circuit to analyze
            
        Returns:
            Complete prompt string for the LLM
        """
        from .analysis_prompts import ANALYSIS_SECTIONS, BASE_ANALYSIS_PROMPT
        
        # Build enabled analysis sections
        enabled_sections = []
        for section, content in ANALYSIS_SECTIONS.items():
            if self.analysis_flags.get(section, True):
                enabled_sections.append(content)
                
        analysis_sections = "\n".join(enabled_sections)
        
        # Format base prompt with circuit description and sections
        prompt = BASE_ANALYSIS_PROMPT.format(
            circuit_description=circuit_description,
            analysis_sections=analysis_sections
        )
        
        # Append custom prompt if provided
        if self.custom_prompt:
            prompt += f"\n\nAdditional Analysis Requirements:\n{self.custom_prompt}"
            
        return prompt

    def analyze_circuit(
        self,
        circuit_description: str,
        output_file: Optional[str] = "circuit_llm_analysis.txt",
        verbose: bool = True
    ) -> Dict:
        """
        Analyze the circuit using the configured LLM.
        
        Args:
            circuit_description: Description of the circuit to analyze
            output_file: File to save analysis results (None to skip saving)
            verbose: Whether to print progress messages
            
        Returns:
            Dictionary containing:
                - success: Whether analysis completed successfully
                - analysis: The analysis text if successful
                - error: Error message if failed
                - timestamp: Analysis timestamp
                - request_time_seconds: Time taken for LLM request
                - total_time_seconds: Total analysis time
                - enabled_analyses: List of enabled analysis sections
        """
        start_time = time.time()
        
        if verbose:
            print(f"\n=== Starting Circuit Analysis with {self.llm.model} ===")
        
        try:
            # Generate the analysis prompt
            prompt = self._generate_analysis_prompt(circuit_description)
            
            if verbose:
                print("\nGenerating analysis...")
            
            # Get analysis from LLM
            request_start = time.time()
            analysis_text = self.llm.quick_prompt(prompt)
            request_time = time.time() - request_start
            
            # Prepare results
            results = {
                "success": True,
                "analysis": analysis_text,
                "timestamp": int(datetime.now().timestamp()),
                "request_time_seconds": request_time,
                "total_time_seconds": time.time() - start_time,
                "enabled_analyses": [
                    k for k, v in self.analysis_flags.items() if v
                ]
            }
            
            # Save to file if requested
            if output_file:
                if verbose:
                    print(f"\nSaving analysis to {output_file}...")
                with open(output_file, "w") as f:
                    f.write(analysis_text)
                if verbose:
                    print("Analysis saved successfully")
            
            if verbose:
                print(f"\n=== Analysis completed in {results['total_time_seconds']:.2f} seconds ===")
            
            return results
            
        except Exception as e:
            error_results = {
                "success": False,
                "error": str(e),
                "timestamp": int(datetime.now().timestamp()),
                "total_time_seconds": time.time() - start_time
            }
            
            if verbose:
                print(f"\nERROR: Analysis failed: {str(e)}")
            
            if output_file:
                if verbose:
                    print(f"\nSaving error message to {output_file}...")
                with open(output_file, "w") as f:
                    f.write(f"Analysis failed: {error_results['error']}")
                if verbose:
                    print("Error message saved")
            
            if verbose:
                print("\n=== Analysis failed ===")
            
            return error_results
