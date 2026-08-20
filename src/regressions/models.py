from itertools import product

import daiquiri
import pandas as pd
import statsmodels.formula.api as smf

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


def main(data: pd.DataFrame, results: dict, elements: list, predictors: list, config: dict, mode=str, depths_info: bool=False) -> dict:
    """ """

    if mode == "uni":
        terms = product(elements, predictors)
        if depths_info:
            new_terms = [(e, f"{e.split('_')[0]}_mean_depth") for e in elements if f"{e.split('_')[0]}_mean_depth" in data.columns]
            terms = list(terms) + new_terms
            if len(new_terms) < len(elements):
                logger.warning(f"Depth metric was not available for: {', '.join([e for e in elements if f'{e.split('_')[0]}_mean_depth' not in data.columns])}. Will be used only for those with available data.")
    elif mode == "multi":
        terms = zip(elements, predictors)
        if depths_info:
            new_terms = [(e, f"{e.split('_')[0]}_mean_depth") for e in elements if f"{e.split('_')[0]}_mean_depth" in data.columns]
            terms = list(terms) + new_terms
            if len(new_terms) < len(elements):
                logger.warning(f"Depth metric was not available for: {', '.join([e for e in elements if f'{e.split('_')[0]}_mean_depth' not in data.columns])}. Will be used only for those with available data.")


    for element, predictors in terms:
        intercept = add_intercept(predictors, config)

        formula = f"{element} ~ {predictors}{intercept}"
        if '+mean_depth' or ' mean_depth' in formula:
            logger.info(f"Running model for: {element} with depth as predictor")
            formula = formula.replace("+mean_depth", f"+{element.split('_')[0]}_mean_depth").replace(" mean_depth", f" {element.split('_')[0]}_mean_depth")
        logger.debug(f"Running: {formula}")
        model = MODELS[config["model"]]
        model_res = model(data, formula, config)
        results = fill_storage(results, model_res, element, predictors, intercept)

    if config["correct_pvals"]:
        results = correct_pvals(results)

    return results
