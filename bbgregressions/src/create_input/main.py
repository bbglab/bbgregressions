from bbgregressions.utils.io import *
from bbgregressions.create_inputs.readers.clonalstructure import *
from bbgregressions.create_inputs.globals import *

def main(config_file: str) -> None:
    """
    """

    config = read_yaml(config_file)
    config = config["metrics"]

    for metric in metrics:

        reader = METRIC2READER[metric]
        reader(config)
