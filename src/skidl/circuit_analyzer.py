"""Module for circuit analysis using LLMs through OpenRouter or local Ollama instance."""

from typing import Dict, Optional, Literal
from datetime import datetime
import time
import os
import requests

# API configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OLLAMA_API_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "google/gemini-flash-1.5"
DEFAULT_OLLAMA_MODEL = "mistral"
DEFAULT_TIMEOUT = 30
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 20000
MAX_RETRIES = 3

class SkidlCircuitAnalyzer:
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        analysis_flags: Optional[Dict[str, bool]] = None,
        timeout: int = DEFAULT_TIMEOUT,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        backend: Literal["openrouter", "ollama"] = "openrouter",
        **kwargs
    ):
        """Initialize with fixed model selection logic"""
        self.backend = backend
        
        # Check for API key if using OpenRouter
        if backend == "openrouter":
            self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "OpenRouter API key required. Either:\n"
                    "1. Set OPENROUTER_API_KEY environment variable\n"
                    "2. Pass api_key parameter to analyze_with_llm"
                )
            # Fixed model selection logic
            self.model = model if model else DEFAULT_MODEL
            
        else:  # ollama
            self.api_key = None
            # For Ollama, use provided model or default Ollama model
            self.model = model if model else DEFAULT_OLLAMA_MODEL
        
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.custom_prompt = custom_prompt
        
        # Validate analysis flags against available sections
        from .prompts import ANALYSIS_SECTIONS
        self.analysis_flags = analysis_flags or {
            section: True for section in ANALYSIS_SECTIONS.keys()
        }
        invalid_sections = set(self.analysis_flags.keys()) - set(ANALYSIS_SECTIONS.keys())
        if invalid_sections:
            raise ValueError(f"Invalid analysis sections: {invalid_sections}")
            
        self.config = kwargs

    def _save_analysis(self, output_file: str, analysis_text: str, verbose: bool = True) -> None:
        """
        Save analysis results to a file.
        
        Args:
            output_file: Path to save the analysis
            analysis_text: Analysis content to save
            verbose: Whether to print progress messages
        """
        if verbose:
            print(f"\nSaving analysis to {output_file}...")
        with open(output_file, "w") as f:
            f.write(analysis_text)
        if verbose:
            print("Analysis saved successfully")

    def _generate_analysis_prompt(self, circuit_description: str) -> str:
        """
        Generate the complete analysis prompt.
        
        Args:
            circuit_description: Description of the circuit to analyze
            
        Returns:
            Complete prompt string for the LLM
        """
        from .prompts import get_base_prompt, ANALYSIS_SECTIONS
        
        # Build enabled analysis sections
        enabled_sections = []
        for section, content in ANALYSIS_SECTIONS.items():
            if self.analysis_flags.get(section, True):
                enabled_sections.append(content)
                
        analysis_sections = "\n".join(enabled_sections)
        
        # Generate complete prompt using base template
        prompt = get_base_prompt(
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
        verbose: bool = True,
        save_query_only: bool = False
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
        
        # Show appropriate default model based on backend
        display_model = self.model if self.model else (DEFAULT_OLLAMA_MODEL if self.backend == "ollama" else DEFAULT_MODEL)
        if verbose:
            print(f"\n=== {'Saving Query' if save_query_only else 'Starting Circuit Analysis'} with {display_model} ===")
        
        try:
            # Generate the analysis prompt
            prompt = self._generate_analysis_prompt(circuit_description)
            
            # If save_query_only is True, just save the prompt and return
            if save_query_only:
                if output_file:
                    self._save_analysis(output_file, prompt, verbose)
                    if verbose:
                        print("\n=== Query saved successfully ===")
                return {
                    "success": True,
                    "query": prompt,
                    "timestamp": int(datetime.now().timestamp()),
                    "total_time_seconds": time.time() - start_time
                }
            
            if verbose:
                print("\nGenerating analysis...")
            
            # Get analysis from selected backend with retries
            request_start = time.time()
            
            if self.backend == "openrouter":
                # Use the OpenAI client to query OpenRouter
                from openai import OpenAI  # Requires the OpenAI package configured for OpenRouter
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                )
                
                # Set extra headers as required
                extra_headers = {
                    "HTTP-Referer": "https://github.com/devbisme/skidl",
                    "X-Title": "SKiDL Circuit Analyzer"
                }
                
                # if verbose:
                #     print("Sending payload to OpenRouter:")
                #     print({
                #         "model": self.model,
                #         "messages": [{"role": "user", "content": prompt}],
                #         "temperature": self.temperature,
                #         "max_tokens": self.max_tokens,
                #         "extra_headers": extra_headers,
                #     })
                
                for attempt in range(MAX_RETRIES):
                    try:
                        completion = client.chat.completions.create(
                            model=self.model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=self.temperature,
                            max_tokens=self.max_tokens,
                            extra_headers=extra_headers
                        )

                        analysis_text = completion.choices[0].message.content
                        request_time = time.time() - request_start
                        
                        # Retrieve token usage if available
                        prompt_tokens = completion.usage.prompt_tokens
                        completion_tokens = completion.usage.completion_tokens
                        total_tokens = completion.usage.total_tokens
                        break
                    except Exception as e:
                        if attempt == MAX_RETRIES - 1:
                            raise ValueError(f"API request failed after {MAX_RETRIES} attempts: {str(e)}")
                        time.sleep(2 ** attempt)  # Exponential backoff
            else:  # ollama backend remains unchanged
                data = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                    }
                }
                
                # Implement retries with exponential backoff
                for attempt in range(MAX_RETRIES):
                    try:
                        response = requests.post(
                            OLLAMA_API_URL,
                            json=data,
                            timeout=self.timeout
                        )
                        response.raise_for_status()
                        response_json = response.json()
                        analysis_text = response_json["message"]["content"]
                        request_time = time.time() - request_start
                        
                        # Ollama doesn't provide token usage
                        prompt_tokens = 0
                        completion_tokens = 0
                        total_tokens = 0
                        break
                    except requests.exceptions.RequestException as e:
                        if attempt == MAX_RETRIES - 1:
                            raise ValueError(f"API request failed after {MAX_RETRIES} attempts: {str(e)}")
                        time.sleep(2 ** attempt)  # Exponential backoff
            
            # Prepare results with token usage
            results = {
                "success": True,
                "analysis": analysis_text,
                "timestamp": int(datetime.now().timestamp()),
                "request_time_seconds": request_time,
                "total_time_seconds": time.time() - start_time,
                "enabled_analyses": [
                    k for k, v in self.analysis_flags.items() if v
                ],
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
            
            # Save analysis to file if required
            if output_file:
                self._save_analysis(output_file, analysis_text, verbose)
            
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
