import os
import pandas as pd
import seaborn as sns

def regressions_reader(directory: str) -> dict:
    """
    """
    results = {}
    files = os.listdir(directory)
    # do not load pvals if qvals were calculated
    if "qval.tsv" in files:
        files.remove("pval.tsv")

    for file in files:
        name = file.split(".")[0]:
        if name in ["qval", "pval"]:
            name = "sign"
        
        results[name] = pd.read_csv(os.path.join(directory, file),
                                    sep = "\t", index_col = 0)

    return results

def grid_dims(config: dict,
            main_vars: list,
            coeff_vars: list) -> dict:
    """
    """
    height = config["fig_height"]
    ratio = config["unit_height2height"]
    # height unit to maintain the pre-defined ratio
    unit = ratio * height    
    # subplot height given the y-axis variables
    subplot_height = unit * coeff_vars
    # max number of rows per grid
    config["nrows"] = height // subplot_height

    n_subplots = config["ncols"] * config["nrows"]
    n_pages = main_vars // n_subplots
    if main_vars % n_subplots:
        n_pages += 1
    config["pdf_pages"] = n_pages
    config["subplots_per_page"] = n_subplots

    return config

def add_customs(config: dict) -> dict:
    """
    """

    # custom names for predictors
    if config["predictors_names"]:
        config["predictors_names"] = dict(zip(config["predictors"],
                                            config["predictors_names"]))
    else:
        config["predictors_names"] = dict(zip(config["predictors"], 
                                            config["predictors"]))
    
    # custom color for predictors
    if config["predictors_colors"]:
        config["predictors_colors"] = dict(zip(config["predictors"],
                                            config["predictors_colors"]))
    else:
        n_predictors = len(config["predictors"])
        colors = sns.color_palette("tab20").as_hex()[:n_predictors]
        config["predictors_colors"] = dict(zip(config["predictors"], colors))

    # default names for elements
    config["elements_name"]

    # default color for elements

    return config
                        
    