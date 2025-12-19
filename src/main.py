#!/usr/bin/env python

import click
import daiquiri

from src import __logger_name__, __version__
from src.config_template.main import main as create_config_main
from src.create_input.main import main as create_input_main
from src.create_input.schemas.globals import METRIC2READER as VALID_METRICS
from src.globals import setup_logging_decorator, startup_message
from src.plot.coefplot.main import main as coefplot_main
from src.regressions.main import main as regressions_main

logger = daiquiri.getLogger(__logger_name__)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__)
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Enable verbose output (sets logging level to DEBUG)."
)
def bbgregressions(verbose):
    """bbgregressions: software for customized regression models"""
    pass


@bbgregressions.command(
    name="config_template",
    context_settings=dict(help_option_names=["-h", "--help"]),
    help="Build configuration template",
)
@click.option(
    "--metrics",
    type=click.STRING,
    callback=lambda ctx, param, value: [x.strip() for x in value.split(",")],
    help="""Metrics you want to analyze (format: comma-separated without spaces).
            Note: if you want to create the template for the same metric to be filled with
            different values, input it as many times as needed""",
)
@setup_logging_decorator
def create_config_template(metrics):
    """Config template to run regressions"""
    startup_message(__version__, "Pre-analysis: create template for config\n")
    for metric in metrics:
        if metric not in VALID_METRICS.keys():
            logger.critical(f"No reader exist for this metric. Valid metrics: {VALID_METRICS.keys()}")
            logger.info("Aborting run")
            raise IOError("No reader exist for this metric")

    create_config_main(metrics)


@bbgregressions.command(
    name="create_input", context_settings=dict(help_option_names=["-h", "--help"]), help="Build input tables"
)
@click.option("-config", "--config_file", type=click.Path(exists=True), help="YAML file with config settings")
@setup_logging_decorator
def create_input(config_file):
    """Build formatted input tables to run regressions"""
    startup_message(__version__, "Module 1: input generation from metrics\n")
    logger.info(f"Reading user defined settings from {config_file}")

    create_input_main(config_file)


@bbgregressions.command(
    name="regressions", context_settings=dict(help_option_names=["-h", "--help"]), help="Run regression models"
)
@click.option("-config", "--config_file", type=click.Path(exists=True), help="YAML file with config settings")
@setup_logging_decorator
def regressions(config_file):
    """Run regression models"""
    startup_message(__version__, "Module 2: run regression models\n")

    logger.info(f"Reading user defined settings from {config_file}")
    regressions_main(config_file)


@bbgregressions.group(
    name="plot", context_settings=dict(help_option_names=["-h", "--help"]), help="Plot regressions results"
)
@setup_logging_decorator
def plot():
    """Plot regression results"""
    pass


@plot.command(name="coefplot", context_settings=dict(help_option_names=["-h", "--help"]), help="Coefficients plot")
@click.option("-config", "--config_file", type=click.Path(exists=True), help="YAML file with config settings")
@setup_logging_decorator
def coefplot(config_file):
    startup_message(__version__, "Module 3: plot regression results - coefficients\n")
    logger.info(f"Reading user defined settings from {config_file}")
    coefplot_main(config_file)


@bbgregressions.command(
    name="minipipeline",
    context_settings=dict(help_option_names=["-h", "--help"]),
    help="Run create_input, regressions, and coefplot sequentially",
)
@click.option(
    "-config",
    "--config_file",
    type=click.Path(exists=True),
    help="YAML file with config settings for the entire pipeline",
)
@setup_logging_decorator
def minipipeline(config_file):
    """
    Executes the full pipeline:
    1. Builds input tables (create_input)
    2. Runs regression models (regressions)
    3. Plots the coefficients (coefplot)
    """
    startup_message(__version__, "Full Pipeline: input, regressions, and plot\n")
    logger.info(f"Starting full pipeline using settings from {config_file}")

    # 1. Run create_input
    logger.info("--- Starting create_input (Module 1) ---")
    create_input_main(config_file)
    logger.info("--- create_input finished successfully ---")

    # 2. Run regressions
    logger.info("--- Starting regressions (Module 2) ---")
    regressions_main(config_file)
    logger.info("--- regressions finished successfully ---")

    # 3. Run coefplot
    logger.info("--- Starting coefplot (Module 3) ---")
    coefplot_main(config_file)
    logger.info("--- Full pipeline finished successfully ---")


if __name__ == "__main__":
    bbgregressions()
