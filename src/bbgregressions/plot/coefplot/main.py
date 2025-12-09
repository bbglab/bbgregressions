import daiquiri
import os
from matplotlib.backends.backend_pdf import PdfPages

from bbgregressions import __logger_name__

from bbgregressions.utils.io import read_yaml
from bbgregressions.plot.utils import regressions_reader, grid_dims, add_customs, transposer
from bbgregressions.plot.plots import coefplot
from bbgregressions.globals import DEFAULT_CONFIG_PLOT 


logger = daiquiri.getLogger(__logger_name__)

def main(config_file: str) -> None:
    """
    """

    config = read_yaml(config_file)
    config_general = config["general"]
    config = config["plot"]

    # update plot config with general config and defaults
    for k in DEFAULT_CONFIG_PLOT.keys():
        config[k] = DEFAULT_CONFIG_PLOT[k]
    config["output_dir"] = config_general["output_dir"]
    config["sign_thres"] = config_general["significance_threshold"]
    config["predictors"] = config_general["predictors"]
    config = add_customs(config)

    # check if regressions directory exists
    regres_dir = os.path.join(config["output_dir"], "regressions")
    if not os.path.isdir(regres_dir):
        logger.critical("Regressions directory does not exist. Aborting run")
        logger.critical("Run/re-run bbgregressions regressions")
        raise IOError("No regressions directory")
    
    output_dir = os.path.join(config["output_dir"], "plot")
    os.makedirs(output_dir, exist_ok = True) 
    logger.info(f"Plots will be stored in {output_dir}")

    # make plots per model, per metric, per mode
    models = os.listdir(regres_dir)
    for model in models:
        logger.info(f"Plots for {model}")
        model_dir = os.path.join(regres_dir, model)
        metrics = os.listdir(model_dir)
        for metric in metrics:
            logger.info(f"Making plots for {metric}...")
            metric_dir = os.path.join(model_dir, metric)
            modes = os.listdir(metric_dir)
            for mode in modes:
                logger.info(f"{mode} regressions exist. Creating pdf with plots.")
                pdf_file = os.path.join(output_dir, model, metric, mode, f"{metric}.{mode}.pdf")
                os.makedirs(os.path.dirname(pdf_file), exist_ok = True)
                logger.info(f"pdf will be stored as {pdf_file}")
                with PdfPages(pdf_file) as pdf:

                    # load regression results
                    mode_dir = os.path.join(metric_dir, mode)
                    regressions_res = regressions_reader(mode_dir)
                    elements = regressions_res["coeff"].index.tolist()
                    predictors = regressions_res["coeff"].columns.tolist()

                    # configure plot
                    config["main_title"] = "\n".join([model, metric, mode])

                    # plot with elements as main, then with predictors as main
                    for display in ["elem_main", "pred_main"]:
                        if display == "elem_main":
                            main_vars = elements
                            coeff_vars = predictors
                            config["colors"] = config["predictors_colors"]
                            config["names"] = config["predictors_names"]
                            config["titles"] = {elem: elem for elem in elements}
                        elif display == "pred_main":
                            regressions_res = transposer(regressions_res)
                            main_vars = predictors
                            coeff_vars = elements
                            config["colors"] = {elem: "#C4BCB7" for elem in elements}
                            config["names"] = {elem: elem for elem in elements}
                            config["titles"] = config["predictors_names"]

                        # configure plot grid
                        config = grid_dims(config, main_vars, coeff_vars)
                        
                        # make plots
                        n0 = 0
                        n1 = config["subplots_per_page"]
                        for page in range(config["pdf_pages"]):
                            coefplot(regressions_res, config, 
                                    main_vars[n0:n1], coeff_vars,
                                    pdf)
                            n0 = n1
                            n1 += config["subplots_per_page"]

    return None