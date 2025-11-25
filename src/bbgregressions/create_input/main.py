import os

from bbgregressions.utils.io import read_yaml
from bbgregressions.create_input.readers.clonalstructure import *
from bbgregressions.create_input.schemas.globals import METRIC2READER

def main(config_file: str) -> None:
    """
    """

    config = read_yaml(config_file)
    metrics_config = config["metrics"]

    output_dir = config["general"]["output_dir"]
    os.makedirs(output_dir, exist_ok = True) 

    for metric in metrics_config:

        reader = METRIC2READER[metric]
        reader(config)

    return None