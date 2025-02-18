"""State management for circuit analysis tracking across threads."""

import json
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set, Dict, Optional

@dataclass
class AnalysisState:
    """Tracks the state of circuit analysis across threads.
    
    This class provides thread-safe tracking of completed circuits,
    failed analyses, and results. It also supports saving and loading
    state from disk for resumable analysis sessions.
    
    Attributes:
        completed: Set of completed circuit names
        failed: Dictionary mapping failed circuit names to error messages
        results: Dictionary mapping circuit names to analysis results
        lock: Thread lock for synchronization
        total_analysis_time: Total time spent in analysis
    """
    completed: Set[str] = field(default_factory=set)
    failed: Dict[str, str] = field(default_factory=dict)
    results: Dict[str, dict] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)
    total_analysis_time: float = 0.0
    
    def save_state(self, path: Path) -> None:
        """Save current analysis state to disk.
        
        Args:
            path: Path to save state file
        """
        with self.lock:
            state_dict = {
                "completed": list(self.completed),
                "failed": self.failed,
                "results": self.results,
                "total_analysis_time": self.total_analysis_time
            }
            with open(path, 'w') as f:
                json.dump(state_dict, f, indent=2)
    
    @classmethod
    def load_state(cls, path: Path) -> 'AnalysisState':
        """Load analysis state from disk.
        
        Args:
            path: Path to state file
            
        Returns:
            Loaded AnalysisState instance
        """
        with open(path) as f:
            state_dict = json.load(f)
        state = cls()
        state.completed = set(state_dict["completed"])
        state.failed = state_dict["failed"]
        state.results = state_dict["results"]
        state.total_analysis_time = state_dict.get("total_analysis_time", 0.0)
        return state

    def add_result(self, circuit: str, result: dict) -> None:
        """Thread-safe addition of analysis result.
        
        Args:
            circuit: Name of the analyzed circuit
            result: Analysis result dictionary
        """
        with self.lock:
            self.results[circuit] = result
            self.completed.add(circuit)
            if "request_time_seconds" in result:
                self.total_analysis_time += result["request_time_seconds"]
    
    def add_failure(self, circuit: str, error: str) -> None:
        """Thread-safe recording of analysis failure.
        
        Args:
            circuit: Name of the failed circuit
            error: Error message describing the failure
        """
        with self.lock:
            self.failed[circuit] = error

    def get_circuit_status(self, circuit: str) -> Optional[str]:
        """Get the status of a specific circuit.
        
        Args:
            circuit: Name of the circuit to check
            
        Returns:
            'completed', 'failed', or None if not processed
        """
        with self.lock:
            if circuit in self.completed:
                return 'completed'
            if circuit in self.failed:
                return 'failed'
            return None

    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics of analysis state.
        
        Returns:
            Dictionary with counts of completed, failed, and total circuits
        """
        with self.lock:
            return {
                "completed": len(self.completed),
                "failed": len(self.failed),
                "total": len(self.completed) + len(self.failed)
            }