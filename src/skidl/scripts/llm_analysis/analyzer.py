"""Core circuit analysis functionality using LLMs."""

import sys
import time
import logging
import importlib
from pathlib import Path
from typing import Optional, Set, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from skidl import *  # Required for accessing default_circuit and other globals

from .config import Backend, DEFAULT_MODEL
from .state import AnalysisState

logger = logging.getLogger("kicad_skidl_llm")

def analyze_single_circuit(
    circuit: str,
    api_key: Optional[str],
    backend: Backend,
    model: Optional[str],
    prompt: Optional[str],
    state: AnalysisState
) -> None:
    """Analyze a single circuit and update the shared state.
    
    Args:
        circuit: Circuit hierarchy path to analyze
        api_key: API key for cloud LLM services
        backend: LLM backend to use
        model: Specific model to use for analysis
        prompt: Custom analysis prompt
        state: Shared analysis state tracker
    """
    try:
        start_time = time.time()
        
        circuit_desc = default_circuit.get_circuit_info(hierarchy=circuit, depth=1)
        
        result = default_circuit.analyze_with_llm(
            api_key=api_key,
            output_file=None,
            backend=backend.value,
            model=model or DEFAULT_MODEL,
            custom_prompt=prompt,
            analyze_subcircuits=False
        )
        
        result["request_time_seconds"] = time.time() - start_time
        
        state.add_result(circuit, result)
        logger.info(f"✓ Completed analysis of {circuit}")
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        state.add_failure(circuit, error_msg)
        logger.error(f"✗ Failed analysis of {circuit}: {str(e)}")

def analyze_circuits(
    source: Path,
    output_file: Path,
    api_key: Optional[str] = None,
    backend: Backend = Backend.OPENROUTER,
    model: Optional[str] = None,
    prompt: Optional[str] = None,
    skip_circuits: Optional[Set[str]] = None,
    max_concurrent: int = 4,
    state_file: Optional[Path] = None
) -> Dict[str, any]:
    """Analyze SKiDL circuits using parallel LLM analysis.
    
    Args:
        source: Path to SKiDL source (file or directory)
        output_file: Path to save analysis results
        api_key: API key for cloud LLM services
        backend: LLM backend to use
        model: Specific model to use for analysis
        prompt: Custom analysis prompt
        skip_circuits: Set of circuit names to skip
        max_concurrent: Maximum number of concurrent analyses
        state_file: Path to save/load analysis state
        
    Returns:
        Dictionary containing analysis results and metrics
        
    Raises:
        RuntimeError: If analysis pipeline fails
    """
    pipeline_start_time = time.time()
    skip_circuits = skip_circuits or set()
    
    # Initialize or load state
    state = (AnalysisState.load_state(state_file) 
             if state_file and state_file.exists() 
             else AnalysisState())
    
    if skip_circuits:
        logger.info(f"Skipping circuits: {', '.join(sorted(skip_circuits))}")
    
    # Add source directory to Python path for imports
    sys.path.insert(0, str(source.parent if source.is_file() else source))
    try:
        # Import and execute circuit definition
        module_name = source.stem if source.is_file() else 'main'
        logger.info(f"Importing {module_name} module...")
        module = importlib.import_module(module_name)
        importlib.reload(module)
        
        if hasattr(module, 'main'):
            logger.info("Executing circuit main()...")
            module.main()
        
        # Collect circuits to analyze
        hierarchies = set()
        for part in default_circuit.parts:
            if part.hierarchy != default_circuit.hierarchy:
                if (part.hierarchy not in skip_circuits and 
                    part.hierarchy not in state.completed):
                    hierarchies.add(part.hierarchy)
        
        if hierarchies:
            logger.info(f"Starting parallel analysis of {len(hierarchies)} circuits...")
            with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                futures = []
                for circuit in sorted(hierarchies):
                    future = executor.submit(
                        analyze_single_circuit,
                        circuit=circuit,
                        api_key=api_key,
                        backend=backend,
                        model=model,
                        prompt=prompt,
                        state=state
                    )
                    futures.append(future)
                    
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Thread failed: {str(e)}")
                    
                    if state_file:
                        state.save_state(state_file)
        
        # Generate consolidated report
        consolidated_text = ["=== Circuit Analysis Report ===\n"]
        
        if state.completed:
            consolidated_text.append("\n=== Successful Analyses ===")
            for circuit in sorted(state.completed):
                result = state.results[circuit]
                consolidated_text.append(f"\n{'='*20} {circuit} {'='*20}\n")
                consolidated_text.append(result.get("analysis", "No analysis available"))
                token_info = (
                    f"\nTokens used: {result.get('total_tokens', 0)} "
                    f"(Prompt: {result.get('prompt_tokens', 0)}, "
                    f"Completion: {result.get('completion_tokens', 0)})"
                )
                consolidated_text.append(token_info)
        
        if state.failed:
            consolidated_text.append("\n=== Failed Analyses ===")
            for circuit, error in sorted(state.failed.items()):
                consolidated_text.append(f"\n{circuit}: {error}")
        
        # Save consolidated results
        if output_file:
            with open(output_file, "w") as f:
                f.write("\n".join(consolidated_text))
        
        # Calculate total metrics
        total_tokens = sum(
            result.get("total_tokens", 0) 
            for result in state.results.values()
        )
        
        return {
            "success": len(state.completed) > 0 and not state.failed,
            "completed_circuits": sorted(state.completed),
            "failed_circuits": state.failed,
            "results": state.results,
            "total_time_seconds": time.time() - pipeline_start_time,
            "total_analysis_time": state.total_analysis_time,
            "total_tokens": total_tokens
        }
        
    finally:
        sys.path.pop(0)