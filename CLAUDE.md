# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Residential Smart Grid Prototype (RSGP) - a Python-based simulation system for smart grid research and analysis. The project simulates residential energy systems, including household power consumption, solar power generation, and power management strategies.

## Architecture

The RSGP follows a modular, distributed architecture with three main simulation components:

### Core Modules
- **`rsgp/houses_sim/`** - Houses simulation: Models household energy consumption with various devices and appliances using ADSR envelope patterns
- **`rsgp/solar_system_sim/`** - Solar system simulation: Models solar panels, batteries, and inverters with real-world data from NSRDB
- **`rsgp/power_mng/`** - Power management: Handles load balancing, virtual battery management, and grid interactions between houses and solar systems
- **`rsgp/utils/`** - Shared utilities: Time simulation, remote object interface, logging, and data handling

### Supporting Components
- **`dashboard/`** - Browser dashboard using Starlette, standards-based HTML, CSS, and JavaScript
- **`rasp_controller/`** - Raspberry Pi GPIO controller for hardware integration
- **`notebooks/`** - Jupyter notebooks for data visualization and analysis
- **`docs/`** - Sphinx documentation with multi-language support (English/Arabic)

### Key Design Patterns
- **Remote Object Architecture**: Uses Pyro5 for distributed simulation across components
- **Time Simulation**: Centralized time management with configurable simulation speed factors
- **CSV Data Logging**: Each simulation component logs data to timestamped CSV files in `rsgp/_logs/`
- **Configuration Management**: Centralized settings in `rsgp/config/settings.py`

## Running the System

### Main RSGP Simulation
```bash
# Run the main simulation system
python -m rsgp

# Or run from project root
cd /path/to/residential-smart-grid
python -m rsgp
```

### Dashboard
```bash
# Run the GUI dashboard
python -m dashboard
```

### Raspberry Pi Controller
```bash
# Run hardware controller (requires GPIO setup)
python -m rasp_controller
```

### Individual Components
```bash
# Run notebooks for data analysis
python notebooks/rsgp_logs_visualization.py
python notebooks/nsrdb_visualization.py
python notebooks/graphs_editor.py
```

## Documentation

### Building Documentation
```bash
# Build Sphinx documentation (language-specific)
cd docs/

# English documentation
make html-en    # HTML format
make latex-en   # LaTeX/PDF format

# Arabic documentation  
make html-ar    # HTML format
make latex-ar   # LaTeX/PDF format

# Clean build
make clean
```

The documentation supports bilingual generation (English/Arabic) and includes:
- API reference with auto-generated module documentation
- Technical chapters covering each simulation component
- Mathematical formulations and algorithms
- System architecture diagrams

### Documentation Writing Guidelines

When writing documentation for this project, follow the established style guide in the existing CLAUDE.md:

- Use academic, technical tone with verbose descriptions
- Include mathematical formulas in LaTeX/MathJax syntax
- Create mermaid diagrams for system workflows
- Maintain completeness criteria covering edge cases
- Include justification for component existence
- Support bilingual documentation (English/Arabic)

## Dependencies and Environment

The project uses these key dependencies:
- **Simulation**: `numpy`, `pandas`, `scipy`, `pvlib` (solar calculations)
- **Remote Objects**: `Pyro5` for distributed simulation
- **Web UI**: `Starlette` and `Uvicorn` with dependency-free HTML, CSS, and JavaScript
- **Data**: `h5py`, `xlrd` for data file handling  
- **Hardware**: GPIO libraries for Raspberry Pi integration
- **Documentation**: `sphinx`, `sphinx-rtd-theme` for docs generation
- **Notebooks**: `marimo` for interactive analysis

Install dependencies:
```bash
pip install -r requirements.txt
```

## Data Sources and Simulation

### NSRDB Data
Solar simulation uses National Solar Radiation Database (NSRDB) data stored in:
- `rsgp/_static/nsrdb.csv` - Main solar irradiance data
- `notebooks/_static/nsrdb/` - Historical datasets

### Simulation Logging
Each simulation run creates timestamped directories in `rsgp/_logs/` containing:
- `houses_simulation.csv` - House energy consumption data
- `solar_system_simulation.csv` - Solar generation and battery data  
- `power_management.csv` - Power flow and grid interaction data

### Configuration
Key settings in `rsgp/config/settings.py`:
- `TIME_FACTOR` - Simulation speed multiplier
- Remote object server settings (host/port)
- Logging configurations
- Simulation parameters

## Development Guidelines

### Code Organization
- Follow the existing modular structure
- Use type hints and docstrings consistently
- Implement `@expose` decorator for Pyro5 remote methods
- Log important events using the centralized logger

### Simulation Components
- Each simulator inherits common patterns for threading and data logging
- Use the shared time simulation (`time_sim`) for synchronized timestamps  
- Follow CSV logging format established in existing modules
- Implement proper start/stop methods for clean shutdown

### Documentation Writing Style

When writing or updating documentation, adhere to these specific guidelines from the project's documentation style:

- Don't use abbreviations; spell out terms
- Use academic, technical tone with verbose descriptions
- Write with bland, uncolorful language using simpler words
- Use active voice: "The time simulation provides synchronization" not "Synchronization is provided by the time simulation"
- Compose top-down: conclusions first, then reasoning
- Keep documentation modular with inter-connected sub-topics
- Include justification for each component's existence
- Use examples to illuminate complex concepts
- Prefer shorter sentences (under 25 words), break down complex sentences
- Include mathematical formulas in LaTeX/MathJax syntax where algorithms are implemented
- Create mermaid diagrams for complex processes and workflows

### Arabic Translation Instructions

For bilingual documentation:
- Translate technical concepts accurately while preserving meaning
- Keep original English terms in parentheses after Arabic translation
- Never translate code snippets, variable names, function names, or file paths
- Keep API names, library names, and framework names in English
- For established terms: "قاعدة البيانات (Database)"
- For newer terms: "إطار العمل (Framework)" 
- Maintain formal, technical register
- Keep all reStructuredText markup unchanged

## Important Notes

- No formal test suite is currently implemented - the project relies on simulation validation
- The system is designed for research and educational purposes
- Hardware integration requires proper Raspberry Pi GPIO setup
- Remote object communication requires network configuration for distributed deployment
- CSV logging can generate large amounts of data during extended simulations
