#!/usr/bin/env python

import click
import daiquiri

from bbgregressions import __logger_name__, __version__

from bbgregressions.create_input.main   import main as create_input_main
# from bbgregressions.regressions.main    import main as regressions_main
# from bbgregressions.plot.main           import main as plot_main

from bbgregressions.globals             import DATE, setup_logging_decorator, startup_message

logger = daiquiri.getLogger(__logger_name__)


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__)
def bbgregressions():
    """bbgregressions: software for customized regression models"""
    pass


@bbgregressions.command(name='create_input',
                        context_settings=dict(help_option_names=['-h', '--help']),
                        help="Build input tables")
@click.option('-config', '--config_file', type=click.Path(exists=True), help='')
@setup_logging_decorator
def create_input(config_file):
    """Build formatted input tables to run regressions"""
    startup_message(__version__, "Initializing input formatting...")

    test_message = "idk"
    logger.info("example message")
    logger.info(f"example message: {test_message}")

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