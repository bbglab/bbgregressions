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

### Concepts

Regression analyses aim to uncover potential associations between variables, in which one or more independent variables explain/predict an independent one. In bbgregressions, we refer to independent and dependent variables as follows:
- Independent variables are called predictors.
- Dependent variables are called elements. To be more precise, each dependent variable is the metric per element. For example, an element can be CDKN1A gene. The corresponding dependent variable for this gene could be CDKN1A dN/dS, CDKN1A mutdensity, etc.  

### Commands

- `config_template`: generates a YAML template with instruction on how to complete it. It will create one metric entry per value in metrics. Valid metrics (currently implemented): mutdensity, omega
`bbgregressions config template --metrics <metric1,metric2,...>`
- `create_input`: reads metric data, applies filters, and formats and writes per-metric input TSVs to `<output_dir>/input/`.
`bbgregressions create_input -config <file.yml>`
- `regressions`: loads formatted data in `<output_dir>/input/*` and runs the selected model; writes TSVs per metric and mode (univariate and/or multivariate).
`bbgregressions regressions -config <file.yml>`
- `plot coefplot`: builds per-model, per-metric, per-mode PDFs with coefficient visualization grids.
`bbgregressions plot coefplot -config <file.yml>`
- `minipipeline`: runs `create_input`, `regressions`, and `plot coefplot` sequentially (recommended).
`bbgregressions minipipeline -config <file.yml>`

Parameters:
- `-config, --config_file`: path to the YAML file containing the configuration settings of the analysis (required).
- `--metrics`: metrics you want to analyze (format: comma-separated without spaces). Note: if you want to create the template for the same metric to be filled with different values, input it as many times as needed.
- `-v, --verbose`: enable verbose output (sets logging level to DEBUG).

### Configuration YAML

bbgregressions uses a single YAML to configure the analysis. This config file also works as a tracker of the specificities of each of the analysis run.

`config_template` provides a detailed template for analysis configuration. It is very important you follow the instructions detailed in the template. Following YAML conventions, the YAML reader will attempt to auto-detect data types, so do not quote any string/integer/float/etc unless otherwise specified. Keep the field empty if you don't want to set up a specific option. If you see an indication of providing your input as list, you need to fill in this field as a sequence collection. Example:
```yaml
impact:
  - missense
  - truncating
```
Remember to delete the instructions from the YAML and only keep the selected values.

Note: one metric section will be created for each time a metric is specified in `config_template`. They will be numbered from 1 to *n*.

<details>
  <summary>YAML fields: detailed explanation</summary>
  
  The config YAML is divided in 3 sections containing several fields. Description (optional fields indicated below):
  - `metrics`: specific instructions to process each input file (metric).
    * `metric_name`: metric name chosen from the available ones. Currently valid: mutdensity, omega.
    * `file`: path to the raw input file for the specific metric.
    * `elements_total_by/samples_total_by`: how to compute an overall cohort value per element or an overall sample value for all elements. Options:
      - `included`: the total is already part of the input.
      - `none`: do not compute a total value.
      - `sum`: the total is the sum of all elements/samples.
      - `mean`: the total is the mean of all elements/samples.
      - `median`: the total is the median of all elements/samples.
    * mutdensity specific:
      - `region`: genome region where mutdensity was computed. Provided as list.
      - `muttype`: mutation type(s) for which mutdensity was computed. Provided as list.
      - `adjust`: whether to use the adjusted mutdensity (yes/no).
    * omega specific:
      - `impact`: impact type (s) for which omega was computed. Provided as list.
      - `global_loc`: whether omega was calculated in the global loc mode (yes/no)
      - `multi`: whether omega was calculated in the multi mode (yes/no)
      - `significance_threshold`: p-value threshold to filter out dN/dS estimates (1 means all estimates are included)
  - `general`: general instructions to process input files and to run the models.
    * `output_dir`: directory where all outputs are stored (formatted input files, model results and PDFs with plots).
    * `handle_na`: strategy for NA handling. If this field is moved under the specific metric config, the general settings is override. Options:
      - `mean`: uses the mean per element to fill NAs.
      - `cohort`: uses the cohort's total value per element to fill NAs.
      - `ignore`: keeps NAs  
    * `elements` (optional): specific elements (*e.g* genes) to use in the analysis. Provided as a list or as a regular expression (the latter between single quotes). If this field is moved under the specific metric config, the general settings is override.
    * `samples` (optional): specific samples to use in the analysis. Provided as a list or as a regular expression (the latter between single quotes). If this field is moved under the specific metric config, the general settings is override.
    * `model`: available model options are displayed in the config template.
    * `multi`: whether to additionally run the multivariate version of the selected model (yes/no).
    * `predictors_file`: path to the tab-separated file containing your predictors (one value per sample in the input metric). For categorical variables, only admits binary variable codified as 0 (baseline effect) and 1.
    * `sample_column`: samples' column name in `predictors_file`.
    * `predictors`: predictors' column names in `predictors_file`. Provided as a list.
    * `predictors_intercept_0` (optional): predictors' column names in `predictors_file` which require the model forcing the intercept through zero.
    * `predictor_random_effect` (optional): when selecting mixed-effects models, predictor's column name of the random effects variable. 
    * `predictors_multi_force` (optional): pairs of predictors that should be included together in any multivariate analysis. Provided as list of pairs separated by comma (*e.g*: age_decades, history_smoking).
    * `correct_pvals`: whether to perform multiple testing correction (yes/no).
    * `significance_threshold`: threshold to deem an association significant.  
  - `plot`: general instructions for plot aesthetics.
    * `predictors_names` (optional): aesthetic names for predictors. Provided as list ordered as `predictors` in the general section.
    * `predictors_colors` (optional): color codes for predictors. Provided as list ordered as `predictors` in the general section.
  
</details>

### Output description

- `config_template`: generates `config.yaml` with all the possible fields that the user should populate to run the analysis. Field name can be changed.
- `create_input`: generates one tab-separated input file per metric-modality combination specified in the configuration YAML. The number of files generated depends on the metric set-up. All files are stored in `<output_dir>/input/`. Format: 
  * Elements as column names.
  * Samples as row names.
  * Metric per sample-element combination in each cell.
- `regressions`: calculates one model per file in `<output_dir>/input/` and generates 5 or 6 output files:
  * `coeff.tsv`: coefficients for each predictor-element combination.
  * `high_ci.tsv`: upper bound of the confidence interval for each predictor-element combination coefficient.
  * `low_ci.tsv`: lower bound of the confidence interval for each predictor-element combination coefficient.
  * `intercept.tsv`: intercept for each predictor-element combination.
  * `pval.tsv`: p-values for each predictor-element combination.
  * `qval.tsv`: q-values for each predictor-element combination (generated when multiple testing correction is on).  
  
  The format of these files is:
  * Predictors as column names.
  * Elements as row names.
  * Coefficient/p-value/CI/etc per sample-element combination in each cell.  
  Results are separated in different directories according to model and mode (univariate or multivariate), all within the `<output_dir>/regressions/` directory.
  
- `plot coefplot`: generates one PDF per model-metric-mode regressions results with coefficient plots. Results are first displayed as element-centric and then as predictor-centric. 

## Maintainers

- [Raquel Blanco](https://github.com/rblancomi)
