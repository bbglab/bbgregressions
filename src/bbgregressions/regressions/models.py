import daiquiri
from itertools import product
import pandas as pd
import statsmodels.formula.api as smf

from bbgregressions.regressions.utils import add_intercept, fill_storage, correct_pvals
from bbgregressions.regressions.schema import MODELS

from bbgregressions import __logger_name__

logger = daiquiri.getLogger(__logger_name__)

def linear(data: pd.DataFrame, 
        formula: str,
        config: dict):
    """
    """
    mod = smf.ols(formula = formula, data = data, missing = "drop")
    res = mod.fit()

    return res

def linear_me(data: pd.DataFrame, 
        formula: str,
        config: dict):
    """
    """
    rand_effect = config["predictor_random_effect"]
    mod = smf.mixedlm(formula = formula, data = data, groups = data[rand_effect],
                    missing = "drop")
    res = mod.fit()

    return res



def main(data: pd.DataFrame, results: dict, elements: list,
        predictors: list, config: dict,
        mode = str) -> dict:
    """
    """

    if mode == "uni":
        terms = product(elements, predictors)
    elif mode == "multi":
        terms = zip(elements, predictors)

    for element, predictors in zip(terms):

        intercept = add_intercept(predictors, config)
        
        formula = f"{element} ~ {predictors}{intercept}"
        logger.debug(f"Running: {formula}")
        model = MODELS[config["model"]]
        model_res = model(data, formula, config)
        results = fill_storage(results, model_res,
                            element, predictors)
    
    if config["correct_pvals"] == "yes":
        results = correct_pvals(results)
    
    return results