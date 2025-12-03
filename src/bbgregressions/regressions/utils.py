import daiquiri
import pandas as pd
import os
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
                predictors: str) -> dict:
    """
    """

    predictors = predictors.split("+")
    for predictor in predictors:

        results["coeff"].loc[element, predictor] = model_res.params[predictor]
        results["low_ci"].loc[element, predictor] = model_res.conf_int().loc[predictor][0]
        results["high_ci"].loc[element, predictor] = model_res.conf_int().loc[predictor][1]
        results["pval"].loc[element, predictor] = model_res.pvalues[predictor]
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

def multi_rules(output_dir_uni: str,
                config: dict) -> tuple:
    """
    """
    if any("qval" in file for file in os.listdir(output_dir_uni)):
        uni_file = os.path.join(output_dir_uni, "qval.tsv")
    else:
        uni_file = os.path.join(output_dir_uni, "pval.tsv")
    
    data = pd.read_csv(uni_file, sep = "\t")
    mask = (data < config["significance_threshold"]).to_numpy()
    predictors = data.columns.to_numpy()
    sign_predictors = ["+".join(predictors[row]) for row in mask]

    # incorporate multi rules

    elements = data.index.tolist()

    return (elements, sign_predictors)


