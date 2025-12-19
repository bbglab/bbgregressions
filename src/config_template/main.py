import copy

import daiquiri
import yaml

from src import __logger_name__
from src.create_input.schemas.clonalstructure import *
from src.globals import CONFIG_TEMPLATE_GENERAL, CONFIG_TEMPLATE_PLOT

logger = daiquiri.getLogger(__logger_name__)

def main(metrics: list) -> None:
    """
    """

    config = {}
    config["metrics"] = {}
    config["general"] = CONFIG_TEMPLATE_GENERAL
    config["plot"] = CONFIG_TEMPLATE_PLOT

    templates = [var for var in globals() if var.startswith("CONFIG_TEMPLATE_")]
    
    for i, metric in enumerate(metrics):
        if f"CONFIG_TEMPLATE_{metric.upper()}" in templates:
            logger.info(f"Template available for {metric}")
            template_content = copy.deepcopy(globals()[f"CONFIG_TEMPLATE_{metric.upper()}"])
            config["metrics"][f"metric_{i+1}"] = template_content
        
        else:
            logger.warning(f"Template not available for {metric}. Skipping.")

    with open("config.yml", "w") as file:
        yaml.dump(config, file, sort_keys = False,
                default_flow_style = False)
    
    logger.info("Template config create in the current directory as config.yaml")
