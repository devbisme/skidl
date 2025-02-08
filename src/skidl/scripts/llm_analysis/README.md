# KiCad/SKiDL LLM Analysis Package

This package provides functionality for analyzing electronic circuit designs using Large Language Models (LLMs). It supports analyzing KiCad schematics, netlists, and SKiDL Python files with powerful AI-driven insights.

## Command-Line Usage

### Basic Usage

```bash
kicad_skidl_llm [input source] [operations] [options]
```

### Input Sources (Required, Choose One)

* `--schematic`, `-s` PATH
  - Path to KiCad schematic (.kicad_sch) file
  - Example: `--schematic project.kicad_sch`

* `--netlist`, `-n` PATH
  - Path to netlist (.net) file
  - Example: `--netlist project.net`

* `--skidl` PATH
  - Path to SKiDL Python file to analyze
  - Example: `--skidl circuit.py`

* `--skidl-dir` PATH
  - Path to SKiDL project directory
  - Example: `--skidl-dir ./project_skidl`

### Operations

* `--generate-netlist`
  - Generate netlist from schematic
  - Requires `--schematic`

* `--generate-skidl`
  - Generate SKiDL project from netlist
  - Requires either `--netlist` or `--generate-netlist`

* `--analyze`
  - Run LLM analysis on circuits
  - Can be used with any input source

### Analysis Options

* `--backend` {openrouter, ollama}
  - LLM backend to use (default: openrouter)
  - Example: `--backend ollama`

* `--api-key` KEY
  - OpenRouter API key (required for OpenRouter backend)
  - Example: `--api-key your-api-key`

* `--model` MODEL
  - Specific LLM model to use
  - Default: google/gemini-2.0-flash-001
  - Example: `--model gpt-4`

* `--analysis-prompt` PROMPT
  - Custom prompt for circuit analysis
  - Example: `--analysis-prompt "Focus on power distribution"`

* `--skip-circuits` LIST
  - Comma-separated list of circuits to skip
  - Example: `--skip-circuits "power_reg,usb_interface"`

* `--max-concurrent` N
  - Maximum number of concurrent LLM analyses
  - Default: 4
  - Example: `--max-concurrent 8`

### Output Options

* `--output-dir`, `-o` DIR
  - Output directory for generated files
  - Default: current directory
  - Example: `--output-dir ./output`

* `--analysis-output` FILE
  - Output file for analysis results
  - Default: circuit_analysis.txt
  - Example: `--analysis-output results.txt`

### KiCad Configuration

* `--kicad-cli` PATH
  - Path to kicad-cli executable
  - Default: Platform-specific default path
  - Example: `--kicad-cli /usr/local/bin/kicad-cli`

* `--kicad-lib-paths` [PATHS...]
  - List of custom KiCad library paths
  - Example: `--kicad-lib-paths ~/kicad/libs /opt/kicad/libs`

### Debug Options

* `--debug`, `-d` [LEVEL]
  - Print debugging info
  - Higher LEVEL means more info
  - Example: `--debug 2`

### Example Commands

1. Basic Analysis of KiCad Schematic:
```bash
kicad_skidl_llm \
  --schematic project.kicad_sch \
  --analyze \
  --api-key $OPENROUTER_API_KEY
```

2. Complete Pipeline with Custom Options:
```bash
kicad_skidl_llm \
  --schematic project.kicad_sch \
  --generate-netlist \
  --generate-skidl \
  --analyze \
  --backend openrouter \
  --api-key $OPENROUTER_API_KEY \
  --model gpt-4 \
  --max-concurrent 8 \
  --output-dir ./analysis \
  --analysis-output results.txt \
  --kicad-lib-paths ~/kicad/libs
```

3. Analyze Existing SKiDL Project:
```bash
kicad_skidl_llm \
  --skidl-dir ./project_skidl \
  --analyze \
  --api-key $OPENROUTER_API_KEY \
  --analysis-prompt "Focus on signal integrity"
```

4. Local Analysis with Ollama:
```bash
kicad_skidl_llm \
  --skidl circuit.py \
  --analyze \
  --backend ollama \
  --model llama2
```

## Environment Setup

### Required Environment Variables

1. For OpenRouter Backend:
```bash
export OPENROUTER_API_KEY="your-api-key"
```

2. For KiCad Integration:
```bash
export KICAD_SYMBOL_DIR="/path/to/kicad/symbols"
```

### Backend Requirements

1. OpenRouter Backend:
- Valid API key
- Internet connection
- Sufficient API credits

2. Ollama Backend:
- Local Ollama installation
- Required models installed
- Run `ollama pull model-name` to install models

## Package Overview

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