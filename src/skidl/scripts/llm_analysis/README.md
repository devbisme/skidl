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

## Module Details

[Rest of the original README content follows...]