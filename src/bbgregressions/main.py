#!/usr/bin/env python

import click
import daiquiri

from bbgregressions import __logger_name__, __version__

from bbgregressions.config_template.main            import main as create_config_main
from bbgregressions.create_input.main               import main as create_input_main
from bbgregressions.create_input.schemas.globals    import METRIC2READER as VALID_METRICS
# from bbgregressions.regressions.main    import main as regressions_main
# from bbgregressions.plot.main           import main as plot_main

from bbgregressions.globals                         import setup_logging_decorator, startup_message

logger = daiquiri.getLogger(__logger_name__)


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__)
def bbgregressions():
    """bbgregressions: software for customized regression models"""
    pass

@bbgregressions.command(name='config_template',
                        context_settings=dict(help_option_names=['-h', '--help']),
                        help="Build configuration template")
@click.option('--metrics', type=click.STRING,
            callback=lambda ctx, param, value: [x.strip() for x in value.split(",")],
            help="""Metrics you want to analyze (format: comma-separated without spaces).
            Note: if you want to create the template for the same metric to be filled with
            different values, input it as many times as needed""")
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


@bbgregressions.command(name='create_input',
                        context_settings=dict(help_option_names=['-h', '--help']),
                        help="Build input tables")
@click.option('-config', '--config_file', type=click.Path(exists=True),
            help='YAML file with config settings')
@setup_logging_decorator
def create_input(config_file):
    """Build formatted input tables to run regressions"""
    startup_message(__version__, "Module 1: input generation from metrics\n")
    logger.info(f"Reading user defined settings from {config_file}")

    create_input_main(config_file)


# @bbgregressions.command(context_settings=dict(help_option_names=['-h', '--help']),
#                         help="Run regressions")
# @click.option('--option1-example', type=click.Choice(['', '', '']), default = 'hg38', help='')
# @click.option('--option2-example', type=click.Path(exists=True), help='')
# @click.option('--option2-example', type=click.STRING, default = None, help='')
# @setup_logging_decorator
# def regressions(args):
#     """message"""
#     startup_message(__version__, "Running regressions...")

#     logger.info("example message")
#     logger.info(f"example message: {laa}")
#     regressions_main(args)


# @bbgregressions.command(context_settings=dict(help_option_names=['-h', '--help']),
#                         help="Plot results")
# @click.option('--option1-example', type=click.Choice(['', '', '']), default = 'hg38', help='')
# @click.option('--option2-example', type=click.Path(exists=True), help='')
# @click.option('--option2-example', type=click.STRING, default = None, help='')
# @setup_logging_decorator
# def plot(args):
#     startup_message(__version__, "Plotting...")

#     logger.info("example message")
#     logger.info(f"example message: {laa}")
#     plot_main(args)


if __name__ == "__main__":
    bbgregressions() 