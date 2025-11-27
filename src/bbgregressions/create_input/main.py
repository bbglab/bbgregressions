import os
import daiquiri

from bbgregressions import __logger_name__

from bbgregressions.utils.io import read_yaml
from bbgregressions.create_input.readers.clonalstructure import *
from bbgregressions.create_input.schemas.globals import METRIC2READER
from bbgregressions.globals import GENERAL_CONFIG_OPTIONS

logger = daiquiri.getLogger(__logger_name__)


def update_config(metric_config: dict,
                general_config: dict) -> dict:
    """
    """
    for elem in GENERAL_CONFIG_OPTIONS:
        if elem not in metric_config.keys():
            metric_config[elem] = general_config[elem]
            logger.info(f"[updated from general config] {elem}: {metric_config[elem]}")

    return metric_config

def main(config_file: str) -> None:
    """
    """

    config = read_yaml(config_file)
    metrics_config = config["metrics"]
    general_config = config["general"]

    output_dir = os.path.join(config["general"]["output_dir"], "input")
    os.makedirs(output_dir, exist_ok = True) 
    logger.info(f"Input tables will be stored in {output_dir}")

    for metric in metrics_config:

        metric_config = metrics_config[metric]
        logger.info(f'Processing {metric.upper()}: {metric_config["metric_name"]}')
        logger.info("###############################################")
        logger.info("Received configuration:")
        for elem in metric_config:
            if elem != "metric_name":
                logger.info(f"{elem}: {metric_config[elem]}")
        
        metric_config = update_config(metric_config, general_config)
        reader = METRIC2READER[metric_config["metric_name"]]
        logger.debug(f"Selected reader: {reader}")
        reader(metric_config, output_dir)

    return None