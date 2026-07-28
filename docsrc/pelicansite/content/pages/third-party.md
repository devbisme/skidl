Title: Third-Party Tools

# Third-Party Tools

Tools and projects built by the SKiDL community.

---

## SKiDL IntelliSense VS Code Extension

**Repository:** [ashergarland/skidl-vscode](https://github.com/ashergarland/skidl-vscode)  
**VS Code Marketplace:** [skidl-lsp](https://marketplace.visualstudio.com/items?itemName=ashergarland.skidl-lsp)  
**Discussion:** [#292](https://github.com/devbisme/skidl/discussions/292)

A Visual Studio Code extension that provides intelligent development tools for SKiDL. Features include live fuzzy search across 21,000+ KiCad symbols and 15,000+ footprints, automatic bill-of-materials generation, design validation with pre-flight checks, and an MCP server that lets AI assistants (GitHub Copilot, Claude) browse KiCad libraries and validate SKiDL code.

---

## SKiDL Skills

**Repository:** [nickkraakman/skidl-skills](https://github.com/nickkraakman/skidl-skills)  
**Discussion:** [#291](https://github.com/devbisme/skidl/discussions/291)

A Claude Code plugin that converts plain-English circuit board descriptions into KiCad netlists using SKiDL. Nine specialized AI agents collaborate to handle orchestration, circuit architecture, requirements gathering, and datasheet research. Automatically sources real, in-stock components from KiCad libraries.

---

## Circuitron

**Repository:** [Shaurya-Sethi/circuitron](https://github.com/Shaurya-Sethi/circuitron)  
**Discussion:** [#263](https://github.com/devbisme/skidl/discussions/263)

An open-source, agent-driven PCB design accelerator that transforms natural language requirements into working PCB designs using SKiDL. Powered by OpenAI's Agents SDK with RAG via Model Context Protocol, it produces schematic files, netlists, SVG previews, and KiCad PCB files. Agents iteratively validate and correct designs until ERC checks pass.

---

## Galvano.ai

**Website:** [galvano.ai](https://galvano.ai/)  
**Discussion:** [#267](https://github.com/devbisme/skidl/discussions/267)

An AI-powered schematic review service that analyzes electronic circuit schematics and netlists before PCB manufacturing. Upload KiCad schematics or SPICE netlists along with relevant datasheets, and Galvano checks each node for common design errors, assigns risk scores, and provides an interactive chat interface for design recommendations.

---

## pcbflow

**Repository:** [michaelgale/pcbflow](https://github.com/michaelgale/pcbflow)

A Python package for PCB layout and design that lets you script circuits with SKiDL definitions and render them onto physical boards. It integrates CuFlow functionality to go from a scripted description to a manufacturable layout.

---

## WireStudio

**Repository:** [moellere/WireStudio](https://github.com/moellere/WireStudio)

An agent-driven design studio for ESPHome and LoRaWAN devices. It generates YAML configuration, KiCad schematics and PCBs, and enclosures, using SKiDL to describe the underlying circuitry.

---

## Solder

**Repository:** [solderable/solder](https://github.com/solderable/solder)

A command-line application with an AI agent that helps create, modify, and compile electronic projects described as SKiDL files.

---

## Skimibowi

**Repository:** [jvestman/skimibowi](https://github.com/jvestman/skimibowi)

A wizard that uses SKiDL to define components and generate KiCad netlists for microcontroller boards, guiding you through part selection and wiring.

---

## kle2netlist

**Repository:** [adamws/kle2netlist](https://github.com/adamws/kle2netlist)

Converts mechanical keyboard layout JSON (KLE) into KiCad netlists, using SKiDL to describe the resulting circuit for PCB design.

---

## skidl-codegen, skidl-layout, and skidl-eda

**Repositories:** [freudenthal/skidl-codegen](https://github.com/freudenthal/skidl-codegen) · [freudenthal/skidl-layout](https://github.com/freudenthal/skidl-layout) · [freudenthal/skidl-eda](https://github.com/freudenthal/skidl-eda)

A set of peer packages that extend SKiDL across the design flow:

- **skidl-codegen** regenerates runnable SKiDL source from KiCad schematics, with cleanup and round-trip verification.
- **skidl-layout** is a standalone PCB placement and layout engine that classifies parts, plans board placement from congestion metrics, and generates `.kicad_pcb` files.
- **skidl-eda** is an AI circuit-design loop harness that turns a SKiDL description into KiCad projects with verification gates, simulation entry points, and human-in-the-loop regeneration.

---

## skidl-tools

**Repository:** [sylefeb/skidl-tools](https://github.com/sylefeb/skidl-tools)

A set of tools for interacting with SKiDL code and KiCad to support iterative electronic system design and PCB generation.
