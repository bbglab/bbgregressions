import os

from bbgregressions.utils.io import read_yaml
from bbgregressions.create_input.readers.clonalstructure import *
from bbgregressions.create_input.schemas.globals import METRIC2READER
from bbgregressions.globals import GENERAL_CONFIG_OPTIONS

def update_config(metric_config: dict,
                general_config: dict) -> dict:
    """
    """
    for elem in GENERAL_CONFIG_OPTIONS:
        if elem not in metric_config.keys():
            metric_config[elem] = general_config[elem]

    return metric_config

def main(config_file: str) -> None:
    """
    """

    config = read_yaml(config_file)
    metrics_config = config["metrics"]
    general_config = config["general"]

    output_dir = config["general"]["output_dir"]
    os.makedirs(output_dir, exist_ok = True) 

    for metric in metrics_config:

        metric_config = metrics_config[metric]
        metric_config = update_config(metric_config, general_config)
        reader = METRIC2READER[metric_config["metric_name"]]
        reader(metric_config, output_dir)

    return None