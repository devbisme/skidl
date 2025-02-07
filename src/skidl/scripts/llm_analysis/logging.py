"""Logging configuration for circuit analysis."""

import sys
import logging
from typing import Optional

logger = logging.getLogger("kicad_skidl_llm")

def configure_logging(debug_level: Optional[int] = None) -> None:
    """Configure logging for the circuit analysis pipeline.
    
    Sets up a StreamHandler with appropriate formatting and level.
    Debug levels work inversely - higher number means more verbose output.
    
    Args:
        debug_level: Debug level (None for no debug, or 0+ for increasing verbosity)
    """
    if debug_level is not None:
        # Calculate log level - higher debug_level means lower logging level
        log_level = logging.DEBUG + 1 - debug_level
        
        # Create and configure handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        handler.setLevel(log_level)
        
        # Configure logger
        logger.addHandler(handler)
        logger.setLevel(log_level)
    else:
        # If no debug level specified, only show INFO and above
        logger.setLevel(logging.INFO)

def log_analysis_results(results: dict) -> None:
    """Log analysis results summary.
    
    Args:
        results: Dictionary containing analysis results and metrics
    """
    if results["success"]:
        logger.info("\nAnalysis Results:")
        logger.info(f"  ✓ Completed Circuits: {len(results['completed_circuits'])}")
        logger.info(f"  ✓ Total Analysis Time: {results['total_analysis_time']:.2f} seconds")
        logger.info(f"  ✓ Total Pipeline Time: {results['total_time_seconds']:.2f} seconds")
        if results.get("total_tokens"):
            logger.info(f"  ✓ Total Tokens Used: {results['total_tokens']}")

        if results["failed_circuits"]:
            logger.warning("\nFailed Circuits:")
            for circuit, error in results["failed_circuits"].items():
                logger.warning(f"  ✗ {circuit}: {error}")

def log_backend_help(backend: str) -> None:
    """Log backend-specific troubleshooting tips.
    
    Args:
        backend: Name of the LLM backend
    """
    if backend == "openrouter":
        logger.error("\nTroubleshooting tips:")
        logger.error("1. Check your API key")
        logger.error("2. Verify you have sufficient API credits")
        logger.error("3. Check for rate limiting")
    else:  # ollama
        logger.error("\nTroubleshooting tips:")
        logger.error("1. Verify Ollama is running locally")
        logger.error("2. Check if the requested model is installed")