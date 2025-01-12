"""Module for circuit analysis using LLMs through OpenRouter."""

from typing import Dict, Optional
from datetime import datetime
import time
import os
import requests

class SkidlCircuitAnalyzer:
    """Circuit analyzer using Large Language Models through OpenRouter."""
    
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
            model: Name of the OpenRouter model to use
            api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
            custom_prompt: Additional custom prompt template to append
            analysis_flags: Dict of analysis sections to enable/disable
            **kwargs: Additional configuration options
        """
        # Check for OPENROUTER_API_KEY environment variable
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Either:\n"
                "1. Set OPENROUTER_API_KEY environment variable\n"
                "2. Pass api_key parameter to analyze_with_llm"
            )
        
        self.model = model
        
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
            print(f"\n=== Starting Circuit Analysis with {self.model} ===")
        
        try:
            # Generate the analysis prompt
            prompt = self._generate_analysis_prompt(circuit_description)
            
            if verbose:
                print("\nGenerating analysis...")
            
            # Get analysis from OpenRouter
            request_start = time.time()
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/devbisme/skidl",
                "X-Title": "SKiDL Circuit Analyzer"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 20000,
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            analysis_text = response.json()["choices"][0]["message"]["content"]
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
