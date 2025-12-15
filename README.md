# bbgregressions
bbgregressions is a software package designed to manage and execute **customized statistical regression analyses**.  It provides a modular, end-to-end pipeline that handles the entire workflow, from configuration setup and data preparation to model execution and results visualization.

## Installation

### Using uv (recommended for development)
Install uv following the installation instructions in the [official uv site](https://docs.astral.sh/uv/getting-started/installation/).

Clone the repository locally:
`git clone https://github.com/bbglab/bbgregressions.git`

uv will manage project dependencies when you run the commands using `uv run`. Example:
`uv run bbgregressions --help`

### Using Docker
*WIP*

## Usage

bbgregressions provides a command line interface (CLI) to perform various tasks. It uses a single YAML to control the several steps of the process.

### Commands

- `config_template`: generates a YAML template with instruction on how to complete it. It will create one metric entry per value in metrics. Valid metrics (currently implemented): mutdensity, omega
`bbgregressions config template --metrics <metric1,metric2,...>`
- `create_input`: reads metric data, applies filters, and formats and writes per-metric input TSVs to `<output_dir>/input/`.
`bbgregressions create_input -config <file.yml>`
- `regressions`: loads formatted data in `<output_dir>/input/*` and runs the selected model; writes TSVs per metric and mode (univariate and/or multivariate).
`bbgregressions regressions -config <file.yml>`
- `plot coefplot`: builds per-model, per-metric, per-mode PDFs with coefficient visualization grids.
`bbgregressions plot coefplot -config <file.yml>`
- `minipipeline`: runs `create_input`, `regressions`, and `plot coefplot` sequentially.
`bbgregressions minipipeline -config <file.yml>`

Add `-v` to any command for debug-level logs.

Parameters:
- `-config, --config_file`: path to the YAML file containing the configuration settings of the analysis (required).
- `--metrics`: metrics you want to analyze (format: comma-separated without spaces). Note: if you want to create the template for the same metric to be filled with different values, input it as many times as needed.
- `-v, --verbose`: enable verbose output (sets logging level to DEBUG).

### Configuration YAML



Notes:
- Predictor metadata tab-delimited
- Critical for config: what needs to be specified as list and what not