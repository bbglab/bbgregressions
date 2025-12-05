import daiquiri
import pandas as pd
import os
import numpy as np
from statsmodels.stats.multitest import fdrcorrection

from bbgregressions import __logger_name__

logger = daiquiri.getLogger(__logger_name__)


def init_storage(elements: list,
                predictors: list) -> dict:
    """
    """

    res_elements = ["coeff", "low_ci", "high_ci", 
                    "pval", "intercept"]
    results = {}
    
    for res_elem in res_elements:
        results[res_elem] = pd.DataFrame(index = elements,
                                        columns = predictors)
    
    return results

def fill_storage(results: dict,
                model_res,
                element: str,
                predictors: str,
                intercept: str) -> dict:
    """
    """

    predictors = predictors.split("+")
    for predictor in predictors:

        results["coeff"].loc[element, predictor] = model_res.params[predictor]
        results["low_ci"].loc[element, predictor] = model_res.conf_int().loc[predictor][0]
        results["high_ci"].loc[element, predictor] = model_res.conf_int().loc[predictor][1]
        results["pval"].loc[element, predictor] = model_res.pvalues[predictor]
        if intercept == " - 1":
            results["intercept"].loc[element, predictor] = 0
        elif intercept == " + 1":
            results["intercept"].loc[element, predictor] = model_res.params["Intercept"]
        
    return results

def add_intercept(predictor_term: str, 
            config: dict) -> str:
    """
    """

    predictors_intercept_0 = config["predictors_intercept_0"]
    if not isinstance(predictors_intercept_0, list):
        predictors_intercept_0 = list(predictors_intercept_0)
    for pred_int_0 in predictors_intercept_0:
        if pred_int_0 in predictor_term:
            intercept = " - 1"
        else:
            intercept = " + 1"

    return intercept

def correct_pvals(results: dict) -> dict:
    """
    """
    _, corr_pvals = fdrcorrection(results["pval"].values.flatten(),
                                alpha = 0.05, method = 'indep', 
                                is_sorted = False)
    results["qval"] = pd.DataFrame(corr_pvals.reshape(results["pval"].shape),
                                index = results["pval"].index, 
                                columns = results["pval"].columns)

    return results

def update_predictors(predictors: set,
                    force_rules: list) -> tuple:
    """
    """
    applied_rules = set()
    for rule in force_rules:
        if set(predictors).intersection(set(rule)):
            applied_rules.update(rule)

    predictors_upd = list(predictors.union(applied_rules))
    forced_predictors = list(applied_rules - predictors)
    
    return (predictors_upd, forced_predictors)

def multi_rules(output_dir_uni: str,
                config: dict) -> tuple:
    """
    """
    if any("qval" in file for file in os.listdir(output_dir_uni)):
        uni_file = os.path.join(output_dir_uni, "qval.tsv")
    else:
        uni_file = os.path.join(output_dir_uni, "pval.tsv")

    data = pd.read_csv(uni_file, sep = "\t", index_col = 0)
    
    # elements analyzed
    elements = data.index.tolist()

    # univariate significant predictors to be included in the multi analysis
    mask = (data < config["significance_threshold"]).to_numpy()
    predictors = data.columns.to_numpy()
    sign_predictors = [set(predictors[row]) for row in mask]

    # predictors forced to be included 
    force_rules = []
    for rule in config["predictors_multi_force"]:
        rule = {pred.strip() for pred in rule.split(",")}
        force_rules.append(rule)

    forced_predictors = []
    sign_predictors_upd = []
    for sign_preds in sign_predictors:
        sign_preds_upd, force_preds = update_predictors(sign_preds, force_rules)
        sign_predictors_upd.append(sign_preds_upd)
        forced_predictors.append(force_preds)
        
    # remove elements for which there is no need to do the multi analysis
    elements_upd = []
    sign_predictors_upd2 = []
    forced_predictors_upd = []
    for elem, sign_pred, force_pred in zip(elements, sign_predictors_upd, forced_predictors):
        if len(sign_pred) > 1:
            elements_upd.append(elem)
            sign_predictors_upd2.append(sign_pred)
            forced_predictors_upd.append(force_pred)
    
    # format predictors for formula syntax
    sign_predictors_upd = ["+".join(pred) for pred in sign_predictors_upd2]

    return (elements, sign_predictors_upd, forced_predictors)

def clean_multi(results: dict,
                forced_predictors: list) -> dict:
    """
    """
    for res_elem in results:
        for elem, force_preds in zip(results[res_elem].index, forced_predictors):
            if force_preds:
                results[res_elem].loc[elem, force_preds] = np.nan
    
    return results
