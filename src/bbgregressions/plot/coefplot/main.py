import daiquiri
import os
from bbgregressions import __logger_name__

from bbgregressions.utils.io import read_yaml

logger = daiquiri.getLogger(__logger_name__)

def main(config_file: str) -> None:
    """
    """

    config = read_yaml(config_file)
    config_general = config["general"]
    config = config["plot"]
    config["output_dir"] = config_general["output_dir"]

    # use existing inputs (check)
    regres_dir = os.path.join(config["output_dir"], "regressions")
    if os.path.isdir(regres_dir):
        if os.listdir(regres_dir):
            regressions = os.listdir(regres_dir)
        else:
            logger.critical("Regressions directory does not have files. Aborting run")
            logger.critical("Run/re-run bbgregressions regressions")
            raise IOError("No files in regressions directory")
    else:
        logger.critical("Regressions directory does not exist. Aborting run")
        logger.critical("Run/re-run bbgregressions regressions")
        raise IOError("No regressions directory")

    return None