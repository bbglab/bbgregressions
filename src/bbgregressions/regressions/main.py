import os
import daiquiri
import pandas as pd

from bbgregressions import __logger_name__

from bbgregressions.utils.io import read_yaml
from bbgregressions.regressions.utils import init_storage, multi_rules
from bbgregressions.regressions.models import main as run_model

logger = daiquiri.getLogger(__logger_name__)

def main(config_file: str) -> None:
    """
    """

    config = read_yaml(config_file)
    config = config["general"]

    output_dir = os.path.join(config["output_dir"], "regressions")
    os.makedirs(output_dir, exist_ok = True) 
    logger.info(f"Regression results will be stored in {output_dir}")

    # use existing inputs (check)
    inputs_dir = os.path.join(config["output_dir"], "inputs")
    if os.path.isdir(inputs_dir):
        if os.listdir(inputs_dir):
            inputs = os.listdir(inputs_dir)
        else:
            logger.critical("Input directory does not have files. Aborting run")
            logger.critical("Run/re-run bbgregressions create_input")
            raise IOError("No files in input directory")
    else:
        logger.critical("Input directory does not exist. Aborting run")
        logger.critical("Run/re-run bbgregressions create_input")
        raise IOError("No input directory")
    
    # calculate regressions per input
    output_dir = os.path.join(config["output_dir"], "regressions")
    os.makedirs(output_dir, exist_ok = True) 
    logger.info(f"Model results will be stored in {output_dir}")

    for file in inputs:

        metric = ".".join(file.split(".")[:-1])
        data = pd.read_csv(file, sep = "\t")
        logger.info(f"Running model for: {metric}")

        # init storage dataframes
        elements = data.columns
        predictors = config["predictors"]
        results = init_storage(elements, predictors)

        # run univariate model
        logger.info("Starting with univariate analysis")
        output_dir_uni = os.path.join(output_dir, metric, "univariate")
        os.makedirs(output_dir_uni, exist_ok = True) 

        results = run_model(data, results, elements, predictors, config,
                            mode = "uni")
        for res_elem in results:
            file = os.path.join(output_dir_uni, f"{res_elem}.tsv")
            results[res_elem].to_csv(file, sep = "\t")
        
        # run multivariate model (if applicable)
        if config["multi"] == "yes":
            logger.info("Multivariate analysis selected. Continue.")
            output_dir_multi = os.path.join(output_dir, metric, "multivariate")
            os.makedirs(output_dir_multi, exist_ok = True) 

            elements, predictors = multi_rules(output_dir_uni, config)
            results = run_model(data, results, elements, predictors, config,
                                mode = "multi")
            for res_elem in results:
                file = os.path.join(output_dir_multi, f"{res_elem}.tsv")
                results[res_elem].to_csv(file, sep = "\t")
    
    return None