import yaml
import daiquiri
import copy

from bbgregressions import __logger_name__
from bbgregressions.globals import CONFIG_TEMPLATE_GENERAL
from bbgregressions.create_input.schemas.clonalstructure import *

logger = daiquiri.getLogger(__logger_name__)

def main(metrics: list) -> None:
    """
    """

    config = {}
    config["metrics"] = {}
    config["general"] = CONFIG_TEMPLATE_GENERAL

    templates = [var for var in globals() if var.startswith("CONFIG_TEMPLATE_")]
    
    for i, metric in enumerate(metrics):
        if f"CONFIG_TEMPLATE_{metric.upper()}" in templates:
            logger.info(f"Template available for {metric}")
            template_content = copy.deepcopy(globals()[f"CONFIG_TEMPLATE_{metric.upper()}"])
            config["metrics"][f"metric_{i+1}"] = template_content
        
        else:
            logger.warning(f"Template not available for {metric}. Skipping.")

    with open("config.yaml", "w") as file:
        yaml.dump(config, file, sort_keys = False,
                default_flow_style = False)
    
    logger.info("Template config create in the current directory as config.yaml")