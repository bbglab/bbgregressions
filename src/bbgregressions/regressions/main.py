import os
import daiquiri
import pandas as pd

from bbgregressions import __logger_name__

from bbgregressions.utils.io import read_yaml
from bbgregressions.regressions.utils import init_storage, multi_rules, clean_multi, clean_input
from bbgregressions.regressions.models import main as run_model

logger = daiquiri.getLogger(__logger_name__)

def main(config_file: str) -> None:
    """
    """

    config = read_yaml(config_file)
    config = config["general"]

    # use existing inputs (check)
    inputs_dir = os.path.join(config["output_dir"], "input")
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
    
    logger.info(f"Model that will be run: {config['model']}")

    # load predictors
    predictors_data = pd.read_csv(config["predictors_file"], sep = "\t",
                                index_col = config["sample_column"])
    logger.info(f"Predictors obtained from {config['predictors_file']}")
    logger.info(f"Predictors: {config['predictors']}")

    # calculate regressions per input
    output_dir = os.path.join(config["output_dir"], "regressions", config["model"])
    os.makedirs(output_dir, exist_ok = True) 
    logger.info(f"Model results will be stored in {output_dir}")

    for file in inputs:

        metric = ".".join(file.split(".")[:-1])
        file = os.path.join(inputs_dir, file)
        data = pd.read_csv(file, sep = "\t", index_col = 0)
        data = clean_input(data)
        logger.info(f"Running model for: {metric}")

        # init storage dataframes
        elements = data.columns
        predictors = config["predictors"]
        results = init_storage(elements, predictors)

        # merge with predictors
        data = data.merge(predictors_data, right_index = True, 
                        left_index = True, how = "left")

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
        if config["multi"]:
            logger.info("Multivariate analysis selected. Continue.")
            output_dir_multi = os.path.join(output_dir, metric, "multivariate")
            os.makedirs(output_dir_multi, exist_ok = True) 

            # restart storage
            results = init_storage(elements, predictors)

            elements, predictors, forced_predictors = multi_rules(output_dir_uni,
                                                                config)
            results = run_model(data, results, elements, predictors, config,
                                mode = "multi")
            results = clean_multi(results, forced_predictors)
            for res_elem in results:
                file = os.path.join(output_dir_multi, f"{res_elem}.tsv")
                results[res_elem].to_csv(file, sep = "\t")
    
    return None