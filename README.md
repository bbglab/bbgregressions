# bbgregressions
Code to run linear models for association analysis 

This branch contains the ready-to-use mini pipeline for custom  linear regressions (bit messy but does the job).

Follow these steps to run it:

## 1. Generate the input tables
The notebook `create_input.ipynb` contains the functions to parse mutdensity, omega and oncodrivefml from deepCSA. Some data type names may be obsolete or not included - feel free to change the functions but open an issue so that this is applied in the main branch. 

The notebook contains several examples based on the bladder analysis to take as reference, but change paths, IDs, etc. accordingly. 

## 2. Prepare the config file
The minipipeline uses a config file to customize the analysis. This is also useful to track how you did the analysis everytime. The recommendation is to name the config file as `YYYYMMDD_config_somedescription.ini`, and that this name is also used when selecting a name for the output pdf and folder (see below).

You have an example config in `example_config.ini` filled with information used in the bladder analysis. **Maintain the structure of this file, do not remove any line, just change the values next to each field**. Here is brief description of how you should fill the config:
- `metrics.dirpaths`: provide the path to the directory where the input files for that specific metric were stored. If a path is not provided, the metric won't be run.
- `metrics.config`: this field specifies how the analysis per metric will be done. Add the keywords of the analysis separated by a comma. Sometimes, for a keyword type you will use more than one value (e.g.: omega run both for truncating and missense mutations). In this case, the values must be separated by `|`. If for this metric you are not running regressions, leave the specific metric field empty. 
- `variables`: this field contains information about several variables used in the analysis. 
    + `responses_subset` and `samples_subset`: you may want to run the analysis sometimes with a subset of genes and samples. Provide this information here, separating the values to be included by commas. Otherwise, leave the field empty.
    + `predictors_file`: path to the file containing the per sample values of the predictors you want to include in the analysis (usually your metadata table).
    + `predictors`: has the format of a python dictionary: the key should be the corresponding name in the predictors_file and the values are a list containing (in this order) the color code and the title to be used in the plots.
    + `random_effects` and `covariables_multi` must be left empty if the regressions won't include random effects and/or additional covariables. For random effects, if it does include it, this field must contain the corresponding column name in predictors_file 
- `advance`: this field contains some more information for the regressions
    + `multipletesting_join`: python dictionary with rules to be followed when making the multiple testing correction. Right now this only applies to omega mutation types, so leave it as in the example just changing the impacts you would like to test. If you don't want to apply this, leave an empty dictionary in the field.
    + `multivariate_rules`: python dictionary with pairs of variables you want to always test in the multivariate analysis, regardless of their significance in the univariate analysis. The recommendation is to select these rules based on previous exploration of the correlation between your predictors. 
    + `predictors2plot`: leave this empty

## 3. Run the regressions
The regressions are run by executing `regression_analysis.py`. Here you have an example of command execution:

```
python3 regression_analysis.py -config YYYYMMDD_config_describeyouranalysis.ini \
-pdf YYYYMMDD_describeyouranalysis.pdf \
-save YYYYMMDD_describeyouranalysis \
--no-response_subplots --no-total_plot --response_and_total_subplots \
--make2 \
--correct_pvals --sign_threshold 0.2
```
- `--no-response_subplots`, `--no-total_plot`, `--response_and_total_subplots`: these parameters select the plotting modality (basically whether to add or not the totals comparison). Recommended to keep it like this, but can be changed by adding/removing `--no` at the beginning. 
- `make2`: similar as the previous parameters but this one is for plotting the regressions by predictor instead of gene. Recommended to keep it like this, but can be changed by adding/removing `--no` at the beginning. 
- `correct_pvals` can be deactivated using `--no-correct_pvals` (not recommended). `sign_threshold` has 0.05 as default value (recommended to fine tune it as 0.05 can be very strict)

## 4. Look at the results
The minipipeline creates a pdf with the results of all metrics, providing as title of each page the details of the specific metric used. In the folder used to save the results, you will find stored the output files for the coefficients, confidence intervals, p-values (or q-values), and intercepts of the models. You will have one file generated per each of these elements and metric analyzed. 

As the refactoring of the code is in the making, any feedback is more than welcome! Just open an issue to let me know. If something does not work, let @rblancomi know :)
