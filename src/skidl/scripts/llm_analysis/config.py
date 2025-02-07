"""Configuration settings and constants for KiCad/SKiDL LLM analysis."""

from enum import Enum

# Default timeout for LLM response (seconds)
DEFAULT_TIMEOUT: int = 300

# Default LLM model
DEFAULT_MODEL: str = "google/gemini-2.0-flash-001"

class Backend(Enum):
    """Supported LLM backends."""
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"

    @classmethod
    def from_str(cls, backend: str) -> 'Backend':
        """Convert string to Backend enum, with validation."""
        try:
            return cls(backend.lower())
        except ValueError:
            valid_backends = ", ".join(b.value for b in cls)
            raise ValueError(
                f"Invalid backend: {backend}. Valid options: {valid_backends}"
            )