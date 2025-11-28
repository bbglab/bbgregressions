import os
import daiquiri

from bbgregressions import __logger_name__

from bbgregressions.utils.io import read_yaml

logger = daiquiri.getLogger(__logger_name__)

def main(config_file: str) -> None:
    """
    """

    config = read_yaml(config_file)
    general_config = config["general"]

    output_dir = os.path.join(config["general"]["output_dir"], "regressions")
    os.makedirs(output_dir, exist_ok = True) 
    logger.info(f"Regression results will be stored in {output_dir}")

    inputs_dir = os.path.join(config["general"]["output_dir"], "inputs")
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
    
    return None