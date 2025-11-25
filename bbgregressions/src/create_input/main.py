from bbgregressions.src.utils.io import read_yaml
from bbgregressions.src.create_input.readers.clonalstructure import *
from bbgregressions.src.create_input.schemas.globals import METRIC2READER

def main(config_file: str) -> None:
    """
    """

    config = read_yaml(config_file)
    metrics_config = config["metrics"]

    for metric in metrics_config:

        reader = METRIC2READER[metric]
        reader(config)
