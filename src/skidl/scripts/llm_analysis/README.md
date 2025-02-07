# KiCad/SKiDL LLM Analysis Package

This package provides functionality for analyzing electronic circuit designs using Large Language Models (LLMs). It supports analyzing KiCad schematics, netlists, and SKiDL Python files with powerful AI-driven insights.

## Overview

The package is organized into several modules, each with a specific responsibility:

```
llm_analysis/
├── __init__.py          # Package initialization and public interface
├── cli.py              # Command-line interface and argument handling
├── config.py           # Configuration settings and constants
├── generator.py        # Netlist and SKiDL project generation
├── kicad.py           # KiCad integration utilities
├── logging.py         # Logging configuration
├── state.py           # Analysis state management
├── analyzer.py        # Core circuit analysis functionality
└── prompts/           # LLM prompt templates
    ├── __init__.py
    ├── base.py       # Base analysis prompt structure
    └── sections.py   # Individual analysis section templates
```

## Module Details

### cli.py
- Main entry point and command-line interface
- Handles argument parsing and validation
- Orchestrates the analysis pipeline
- Key Functions:
  * `parse_args()`: Command-line argument parsing
  * `validate_args()`: Input validation
  * `main()`: Pipeline orchestration

### config.py
- Configuration constants and enums
- Defines LLM backends and defaults
- Constants:
  * `DEFAULT_TIMEOUT`: LLM request timeout
  * `DEFAULT_MODEL`: Default LLM model
  * `Backend`: Enum of supported LLM backends

### generator.py
- Handles file generation and conversion
- Key Functions:
  * `generate_netlist()`: KiCad schematic to netlist conversion
  * `generate_skidl_project()`: Netlist to SKiDL project conversion
  * `get_skidl_source()`: Source resolution logic

### kicad.py
- KiCad integration utilities
- Handles platform-specific paths
- Library management
- Key Functions:
  * `validate_kicad_cli()`: CLI executable validation
  * `get_default_kicad_cli()`: Platform-specific defaults
  * `handle_kicad_libraries()`: Library path management

### logging.py
- Logging configuration and utilities
- Custom formatters and handlers
- Key Functions:
  * `configure_logging()`: Logger setup
  * `log_analysis_results()`: Results formatting
  * `log_backend_help()`: Backend-specific troubleshooting

### state.py
- Thread-safe analysis state management
- Persistence support
- Key Class: `AnalysisState`
  * Tracks completed/failed analyses
  * Manages results
  * Supports save/load for resumable analysis

### analyzer.py
- Core analysis functionality
- Parallel processing support
- Key Functions:
  * `analyze_single_circuit()`: Individual circuit analysis
  * `analyze_circuits()`: Parallel analysis orchestration

### prompts/
- LLM prompt templates and structure
- Modular analysis sections
- Files:
  * `base.py`: Base prompt structure
  * `sections.py`: Analysis section templates

## Dependencies

- **skidl**: Core circuit processing functionality
- **KiCad**: Required for schematic/netlist operations
- **OpenRouter/Ollama**: LLM backends for analysis

## Usage

1. **Direct Command Line Usage**:
```bash
kicad_skidl_llm --schematic circuit.kicad_sch --generate-netlist --generate-skidl --analyze
```

2. **API Usage**:
```python
from skidl.scripts.llm_analysis import analyze_circuits, Backend

results = analyze_circuits(
    source=source_path,
    api_key="your-api-key",
    backend=Backend.OPENROUTER
)
```

## Data Flow

1. Input Processing:
   - Schematic → Netlist → SKiDL Project (optional)
   - Direct SKiDL file/project input

2. Analysis Pipeline:
   ```
   Input → Circuit Loading → Parallel Analysis → Results Collection → Report Generation
   ```

3. State Management:
   - Thread-safe tracking
   - Persistent state (optional)
   - Progress monitoring

## Threading Model

- Parallel circuit analysis using ThreadPoolExecutor
- Thread-safe state management via locks
- Configurable concurrency limits

## Error Handling

- Platform-specific guidance
- Backend-specific troubleshooting
- Detailed error reporting
- State persistence for recovery

## Configuration

- Environment Variables:
  * `KICAD_SYMBOL_DIR`: KiCad library path
  * `OPENROUTER_API_KEY`: API key for OpenRouter

- Command Line Options:
  * Backend selection
  * Model selection
  * Debug levels
  * Concurrent analysis limits

## Development

### Adding Support for New LLM Backends

1. Add backend to `Backend` enum in `config.py`
2. Implement backend-specific error handling
3. Update `analyzer.py` with backend-specific logic

### Adding New Analysis Sections

1. Add section template to `prompts/sections.py`
2. Update `ANALYSIS_SECTIONS` dictionary
3. Update base prompt if needed

## Common Issues

1. **KiCad CLI Not Found**:
   - Check PATH
   - Verify KiCad installation
   - Use `--kicad-cli` to specify path

2. **Library Path Issues**:
   - Set KICAD_SYMBOL_DIR
   - Use `--kicad-lib-paths`
   - Check library file existence

3. **LLM Backend Issues**:
   - Verify API key
   - Check credits/rate limits
   - Confirm backend availability

## Future Improvements

1. Additional LLM backends
2. More analysis section templates
3. Enhanced parallel processing
4. Interactive analysis modes
5. Result visualization