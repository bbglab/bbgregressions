from itertools import product

import daiquiri
import pandas as pd
import statsmodels.formula.api as smf
import numpy as np

from src import __logger_name__
from src.regressions.utils import add_intercept, correct_pvals, fill_storage

logger = daiquiri.getLogger(__logger_name__)


def linear(data: pd.DataFrame, formula: str, config: dict):
    """ """
    mod = smf.ols(formula=formula, data=data, missing="drop")
    res = mod.fit()

    return res


def linear_me(data: pd.DataFrame, formula: str, config: dict):
    """ """
    rand_effect = config["predictor_random_effect"]
    mod = smf.mixedlm(formula=formula, data=data, groups=data[rand_effect], missing="drop")
    res = mod.fit()

    return res


MODELS = {"linear": linear, "linear-mixed-effects": linear_me}


def main(data: pd.DataFrame, results: dict, elements: list, predictors: list, config: dict, mode=str) -> dict:
    """ 
    """

    if mode == "uni":
        terms = product(elements, predictors)
    elif mode == "multi":
        terms = zip(elements, predictors)

    for element, predictors in terms:
        intercept = add_intercept(predictors, config)

        formula = f"{element} ~ {predictors}{intercept}"
        logger.debug(f"Running: {formula}")
        
        try:
            model = MODELS[config["model"]]
            model_res = model(data, formula, config)
            results = fill_storage(results, model_res, element, predictors, intercept)
        except np.linalg.LinAlgError as e:
            if "Singular matrix" in str(e):
                logger.warning(f"Singular matrix encountered for formula: {formula}. Skipping this model.")
            else:
                raise
        except Exception as e:
            logger.error(f"Unexpected error for formula {formula}: {str(e)}")

    if config["correct_pvals"]:
        results = correct_pvals(results)

    return results
