import os
import logging
import daiquiri
import click
from datetime import datetime

from functools import wraps

from bbgregressions import __logger_name__
from bbgregressions.regressions.schema import *
from bbgregressions.regressions.models import MODELS

logger = daiquiri.getLogger(__logger_name__)

DATE = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
FORMAT = "%(asctime)s - %(color)s%(levelname)-7s%(color_stop)s | %(name)s - %(color)s%(message)s%(color_stop)s"

# =========
#  Logging
# =========

def setup_logging_decorator(func):
    @wraps(func)
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        log_dir = os.path.join('.','log')
        command_name = ctx.command.name

        fname = f"{command_name}_{DATE}.log"

        os.makedirs(log_dir, exist_ok=True)
        
        verbose_flag = ctx.parent.params.get('verbose', False)
        level = logging.DEBUG if verbose_flag else logging.INFO

        formatter = daiquiri.formatter.ColorFormatter(fmt=FORMAT)
        
        daiquiri.setup(level=level, outputs=(
            daiquiri.output.Stream(formatter=formatter), 
            daiquiri.output.File(filename=os.path.join(log_dir, fname), formatter=formatter)
        ))
        
        return func(*args, **kwargs)

    return wrapper


def startup_message(version, initializing_text):
    
    author = "Biomedical Genomics Lab - IRB Barcelona"
    support_email = "raquel.blanco@irbbarcelona.org"
    banner_width = 70

    logger.info("#" * banner_width)
    logger.info(f"{'#' + ' ' * (banner_width - 2) + '#'}")
    logger.info(f"{'#' + 'Welcome to bbgregressions!'.center(banner_width - 2) + '#'}")
    logger.info(f"{'#' + ' ' * (banner_width - 2) + '#'}")
    logger.info(f"{'#' + initializing_text.center(banner_width - 2) + '#'}")
    logger.info(f"{'#' + f'Version: {version}'.center(banner_width - 2) + '#'}")
    logger.info(f"{'#' + f'Author: {author}'.center(banner_width - 2) + '#'}")
    logger.info(f"{'#' + f'Support: {support_email}'.center(banner_width - 2) + '#'}")
    logger.info(f"{'#' + ' ' * (banner_width - 2) + '#'}")
    logger.info("#" * banner_width)
    logger.info("")

# ==============
#  Configuration
# ==============

GENERAL_CONFIG_OPTIONS = {
    "handle_na" : ["ignore", "mean", "all_samples"],
    "elements_total_by" : ["none", "included", "sum", "mean", "median"],
    "samples_total_by" : ["none", "included", "sum", "mean", "median"],
    "elements": "",
    "samples": "",
}

CONFIG_TEMPLATE_GENERAL = {
    "output_dir": "/path/to/dir",
    "handle_na": f"""select between {", ".join(GENERAL_CONFIG_OPTIONS['handle_na'])} 
    (move this field to the specific metric section if you want a metric-specific NA handling)""",
    "elements": "add list of elements or regex. Move this field to the specific metric section if the subset by elements is not general",
    "samples": "add list of samples or regex. Move this field to the specific metric section if the subset by samples is not general",

    "model": f"select between {", ".join(MODELS)}",
    "multi": f"select between {", ".join(MULTI_OPTIONS)}",

    "predictors_file": "path/to/file",
    "sample_column": "add sample column name",
    "predictors": "column names in predictors file (if empty, all colnames in predictor file will be used)",
    "predictors_intercept_0": "leave empty if NA",
    "predictor_random_effect": "leave empty if NA",
    "predictors_multi_force": "leave empty if NA",
    
    "correct_pvals": "select between yes or no",
    "significance_threshold": "leave empty if no multiple testing correction"
}

CONFIG_TEMPLATE_PLOT = {
    "predictors_names": "(optional) add names for your predictors (same order as above)",
    "predictors_colors": "(optional) add color codes for your predictors (same order as above)",
}

DEFAULT_CONFIG_PLOT = {
    "ncols": 4,
    "unit_height2height": 0.04, # don't change, visually defined
    "fig_width": 16,
    "fig_height": 14,
    "coeffdot_size": 150,
    "coeffdot_linewidth": 2
}