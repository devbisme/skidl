"""Module for circuit analysis using LLMs through OpenRouter or local Ollama instance."""

from typing import Dict, Optional, Literal
from datetime import datetime
import time
import os
import hashlib
import requests
from openai import OpenAI
from .logger import active_logger  # Import the active_logger

# API configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OLLAMA_API_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "google/gemini-2.0-flash-001"
DEFAULT_OLLAMA_MODEL = "llama3.2:latest"
DEFAULT_TIMEOUT = 30
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 20000
MAX_RETRIES = 3
FILE_OPERATION_RETRIES = 3  # Retries for file operations
FILE_RETRY_DELAY = 1  # Delay between retries in seconds

# Approximate cost per 1K tokens for typical OpenRouter usage
# (These are user-defined or approximate values and might not match real billing exactly.)
DEFAULT_COST_PER_1K_TOKENS = 0.002  

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
        cost_per_1k_tokens: float = DEFAULT_COST_PER_1K_TOKENS,
        **kwargs
    ):
        """
        Initialize the circuit analyzer with configuration parameters.
        
        Args:
            model: Model identifier for the LLM
            api_key: API key for OpenRouter (required if using OpenRouter backend)
            custom_prompt: Additional custom prompts to include in analysis
            analysis_flags: Dict of analysis sections to enable/disable
            timeout: Request timeout in seconds
            temperature: Model temperature parameter
            max_tokens: Maximum tokens for completion
            backend: Either "openrouter" or "ollama"
            cost_per_1k_tokens: Approximate cost to be multiplied per 1K tokens (for OpenRouter)
        """
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
        else:
            self.api_key = None
            # For Ollama, use provided model or default Ollama model
            self.model = model if model else DEFAULT_OLLAMA_MODEL
        
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.custom_prompt = custom_prompt
        
        from .prompts import ANALYSIS_SECTIONS
        self.analysis_flags = analysis_flags or {
            section: True for section in ANALYSIS_SECTIONS.keys()
        }
        invalid_sections = set(self.analysis_flags.keys()) - set(ANALYSIS_SECTIONS.keys())
        if invalid_sections:
            raise ValueError(f"Invalid analysis sections: {invalid_sections}")
        
        # Keep track of total cost (approximate)
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.total_approx_cost = 0.0
        
        self.config = kwargs

    def _generate_unique_identifier(self, subcircuit_name: str, module_path: str) -> str:
        """
        Generate a unique identifier for a subcircuit to avoid name collisions.
        
        Args:
            subcircuit_name: Name of the subcircuit function
            module_path: Path to the module containing the subcircuit
            
        Returns:
            A unique identifier string
        """
        # Create a unique string combining module path and subcircuit name
        unique_string = f"{module_path}:{subcircuit_name}"
        # Generate a hash and take first 8 characters for brevity
        hash_id = hashlib.md5(unique_string.encode()).hexdigest()[:8]
        return f"{subcircuit_name}_{hash_id}"

    def _save_analysis_with_retry(self, output_file: str, analysis_text: str, verbose: bool = True) -> None:
        """
        Save analysis results to a file with retry mechanism for handling file locks.
        
        Args:
            output_file: Path to save the analysis
            analysis_text: Analysis content to save
            verbose: Whether to print progress messages
        """
        if verbose:
            active_logger.info(f"\nSaving analysis to {output_file}...")
            
        for attempt in range(FILE_OPERATION_RETRIES):
            try:
                with open(output_file, "w") as f:
                    f.write(analysis_text)
                if verbose:
                    active_logger.info("Analysis saved successfully")
                return
            except PermissionError as e:
                if attempt < FILE_OPERATION_RETRIES - 1:
                    if verbose:
                        active_logger.warning(f"Retry {attempt + 1}: File locked, waiting...")
                    time.sleep(FILE_RETRY_DELAY)
                else:
                    raise IOError(f"Failed to save analysis after {FILE_OPERATION_RETRIES} attempts: {str(e)}")

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
            save_query_only: If True, only save the query without executing
            
        Returns:
            Dictionary containing analysis results and metadata
        """
        start_time = time.time()
        
        # Show appropriate default model based on backend
        display_model = self.model if self.model else (DEFAULT_OLLAMA_MODEL if self.backend == "ollama" else DEFAULT_MODEL)
        if verbose:
            active_logger.info(f"\n=== {'Saving Query' if save_query_only else 'Starting Circuit Analysis'} with {display_model} ===")
        
        try:
            # Generate the analysis prompt
            prompt = self._generate_analysis_prompt(circuit_description)
            
            # If save_query_only is True, just save the prompt and return
            if save_query_only:
                if output_file:
                    self._save_analysis_with_retry(output_file, prompt, verbose)
                    if verbose:
                        active_logger.info("\n=== Query saved successfully ===")
                return {
                    "success": True,
                    "query": prompt,
                    "timestamp": int(datetime.now().timestamp()),
                    "total_time_seconds": time.time() - start_time
                }
            
            if verbose:
                active_logger.info("\nGenerating analysis...")
            
            # Get analysis from selected backend with retries
            request_start = time.time()
            
            if self.backend == "openrouter":
                analysis_results = self._handle_openrouter_request(prompt, request_start, verbose)
            else:
                analysis_results = self._handle_ollama_request(prompt, request_start)
            
            # Add common result fields
            results = {
                "success": True,
                "timestamp": int(datetime.now().timestamp()),
                "total_time_seconds": time.time() - start_time,
                "enabled_analyses": [
                    k for k, v in self.analysis_flags.items() if v
                ],
                **analysis_results
            }
            
            # Save analysis to file if required
            if output_file and results.get("analysis"):
                self._save_analysis_with_retry(output_file, results["analysis"], verbose)
            
            if verbose:
                active_logger.info(f"\n=== Analysis completed in {results['total_time_seconds']:.2f} seconds ===")
            
            return results
            
        except Exception as e:
            error_message = f"Analysis failed: {str(e)}"
            active_logger.error(f"\nERROR: {error_message}")
            
            error_results = {
                "success": False,
                "error": error_message,
                "timestamp": int(datetime.now().timestamp()),
                "total_time_seconds": time.time() - start_time
            }
            
            if output_file:
                try:
                    self._save_analysis_with_retry(output_file, error_message, verbose)
                except Exception as save_error:
                    active_logger.error(f"Failed to save error message: {str(save_error)}")
            
            return error_results

    def _handle_openrouter_request(self, prompt: str, request_start: float, verbose: bool) -> Dict:
        """
        Handle requests to OpenRouter API with retries, and track approximate cost.
        
        Args:
            prompt: The analysis prompt to send
            request_start: Start time of the request
            verbose: Whether to print progress messages
            
        Returns:
            Dictionary containing API response data
        """
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        
        extra_headers = {
            "HTTP-Referer": "https://github.com/devbisme/skidl",
            "X-Title": "SKiDL Circuit Analyzer"
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                completion = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    extra_headers=extra_headers
                )
                
                # Extract text and usage
                analysis_text = completion.choices[0].message.content
                prompt_tokens = completion.usage.prompt_tokens
                completion_tokens = completion.usage.completion_tokens
                total_tokens = completion.usage.total_tokens
                request_time = time.time() - request_start
                
                # Approximate cost (user-defined or guess)
                cost = (prompt_tokens + completion_tokens) / 1000.0 * self.cost_per_1k_tokens
                self.total_approx_cost += cost
                
                if verbose:
                    active_logger.info(f"Approximate cost for this query: ${cost:.4f}")
                
                return {
                    "analysis": analysis_text,
                    "request_time_seconds": request_time,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "approx_query_cost": cost,
                    "total_approx_cost_so_far": self.total_approx_cost
                }
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise ValueError(f"OpenRouter API request failed after {MAX_RETRIES} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff

    def _handle_ollama_request(self, prompt: str, request_start: float) -> Dict:
        """
        Handle requests to Ollama API with retries (no token cost tracking).
        
        Args:
            prompt: The analysis prompt to send
            request_start: Start time of the request
            
        Returns:
            Dictionary containing API response data
        """
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": self.temperature,
            }
        }
        
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
                
                # Ollama doesn't provide token usage or cost
                return {
                    "analysis": analysis_text,
                    "request_time_seconds": request_time,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            except requests.exceptions.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    raise ValueError(f"Ollama API request failed after {MAX_RETRIES} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
