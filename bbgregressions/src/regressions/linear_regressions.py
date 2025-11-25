"""
This module provides linear regressions implementations
"""
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import fdrcorrection

def univar_linear_regression(
    data: pd.DataFrame,
    predictor_vars: list,
    response_vars: list, 
    correct_pvals: bool = True
    )-> tuple[pd.DataFrame, pd.DataFrame, 
            pd.DataFrame, pd.DataFrame,
            pd.DataFrame]:
    """
    Calculates the coefficients, confidence intervals and p values of a 
    univariate linear regression for a list of response and predictor variables  
    
    Parameters:
    data (pd.DataFrame): input DataFrame with values per sample (row) for 
    the predictor and response variables (columns)
    predictor_vars (list): list of predictor variables (must match column name
    in data)
    response_vars (list): list of response variables (must match column name in
    data)
    correct_pvals (bool): whether to apply multiple testing correction

    Returns:
    coeffs (pd.DataFrame): coefficients for each predictor-response pair
    lower_ci (pd.DataFrame): lower bounds of the confidence intervals for each
    predictor-response pair
    upper_ci (pd.DataFrame): upper bounds of the confidence intervals for each
    predictor-response pair
    pvals_df (pd.DataFrame): p-values for each predictor-response pair
    """
    
    # initialize param model dfs to store results
    coeffs_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    lowi_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    highi_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    pvals_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    intercepts_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    
    # list of variables that need intercept passing through zero
    vars_zero_intercep = ["age_decades"]

    # compute linear regressions for each response variable
    for response_var in name_response_vars:

        # access each covariate
        for pred_var in name_predictor_vars:

            if pred_var in vars_zero_intercep:
                interc = "- 1"
            else:
                interc = "+ 1"
            
            print(f"MODEL formula (univariable): {response_var} ~ {pred_var} {interc}")
            mod = smf.ols(formula = f'{response_var} ~ {pred_var} {interc}', data = response_vars_df, missing = "drop")
            res = mod.fit()

            # extract predictor variable coefficient, intervals, and p-value
            coeffs_df.loc[response_var, pred_var] = res.params[pred_var]
            lowi_df.loc[response_var, pred_var] = res.conf_int().loc[pred_var][0]
            highi_df.loc[response_var, pred_var] = res.conf_int().loc[pred_var][1]
            pvals_df.loc[response_var, pred_var] = res.pvalues[pred_var]
            # new! extract also the intercept
            if pred_var in vars_zero_intercep:
                intercept = 0
            else:
                intercept = res.params["Intercept"]
            intercepts_df.loc[response_var, pred_var] = intercept

    # correct p values for false discovery rate
    if correct_pvals:
        _, corr_pvals = fdrcorrection(pvals_df.values.flatten(), alpha = 0.05, method = 'indep', is_sorted = False)
        corr_pvals_df = pd.DataFrame(corr_pvals.reshape(pvals_df.shape), index = pvals_df.index, columns = pvals_df.columns)
    else:
        corr_pvals_df = pvals_df

    return coeffs_df, lowi_df, highi_df, corr_pvals_df, intercepts_df

def univar_mixedeffects_linear_regression(response_vars_df, name_response_vars,
name_predictor_vars, name_random_effects, correct_pvals = True):
    """
    Calculates a  univariate mixed-effects linear regression for several response and predictor variables
    and returns the coefficients, confidence intervals and p values in a dataframe.
    
    Parameters
    ----------
    response_vars_df: pandas DataFrame
        Dataframe containing the data points of the response variables and
        predictor variable per sample. Both predictor and response variables must be
        in the dataframe columns, and samples in the rows. 
    name_response_vars: list
        Response variables
    name_predictor_vars: list
        Predictor variables
    name_random_effects: str
        Random effects we want take into account in the model
    correct_pvals: boolean (default: True)
        Whether to correct the p-values for multiple testing
        
    Returns
    -------
    coeffs_df: pandas DataFrame
        Dataframe containing each predictor-response coefficient
    lowi_df: pandas DataFrame
        Dataframe containing each predictor-response low confidence interval 
        of the coefficient
    highi_df: pandas DataFrame
        Dataframe containing each predictor-response high confidence interval 
        of the coefficient
    corr_pvals_df: pandas DataFrame
        Dataframe containing each predictor-response corrected p value of the coefficient
        (Benjamini/Hochberg method)
    intercepts_df: pandas DataFrame
        Dataframe containing each predictor-response model intercept
    """
    
    # initialize param model dfs to store results
    coeffs_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    lowi_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    highi_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    pvals_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    intercepts_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)

    # list of variables that need intercept passing through zero
    vars_zero_intercep = ["age_decades", "AGE"]

    # compute linear regressions for each response variable
    for response_var in name_response_vars:

            # access each covariate
            for pred_var in name_predictor_vars:

                if pred_var in vars_zero_intercep:
                    interc = "- 1"
                else:
                    interc = "+ 1"
                
                print(f"MODEL formula (univariable): {response_var} ~ {pred_var} {interc}")
                mod = smf.mixedlm(formula = f'{response_var} ~ {pred_var} {interc}', data = response_vars_df,
                                groups = response_vars_df[name_random_effects], missing = "drop") #raises error if NA otherwise
                res = mod.fit()

                # extract predictor variable coefficient, intervals, and p-value
                coeffs_df.loc[response_var, pred_var] = res.params[pred_var]
                lowi_df.loc[response_var, pred_var] = res.conf_int().loc[pred_var][0]
                highi_df.loc[response_var, pred_var] = res.conf_int().loc[pred_var][1]
                pvals_df.loc[response_var, pred_var] = res.pvalues[pred_var]
                # new! extract also the intercept
                if pred_var in vars_zero_intercep:
                    intercept = 0
                else:
                    intercept = res.params["Intercept"]
                intercepts_df.loc[response_var, pred_var] = intercept


    # correct p values for false discovery rate
    if correct_pvals:
        _, corr_pvals = fdrcorrection(pvals_df.values.flatten(), alpha = 0.05, method = 'indep', is_sorted = False)
        corr_pvals_df = pd.DataFrame(corr_pvals.reshape(pvals_df.shape), index = pvals_df.index, columns = pvals_df.columns)
    else:
        corr_pvals_df = pvals_df

    return coeffs_df, lowi_df, highi_df, corr_pvals_df, intercepts_df

def multivar_linear_regression(response_vars_df, name_response_vars,
                            name_predictor_vars,
                            correct_pvals = True, rules = None):
    """
    Calculates a multivariate linear regression for several response variables
    and returns the coefficients, confidence intervals and corrected p values in a dataframe.
    
    Parameters
    ----------
    response_vars_df: pandas DataFrame
        Dataframe containing the data points of the response variables and
        predictor variable per sample. Both predictor and response variables must be
        in the dataframe columns, and samples in the rows. 
    name_response_vars: list
        Response variables
    name_predictor_vars: list
        Predictor variables
    correct_pvals: boolean (default: True)
        Whether to correct the p-values for multiple testing
        
    Returns
    -------
    coeffs_df: pandas DataFrame
        Dataframe containing each predictor-response coefficient
    lowi_df: pandas DataFrame
        Dataframe containing each predictor-response low confidence interval 
        of the coefficient
    highi_df: pandas DataFrame
        Dataframe containing each predictor-response high confidence interval 
        of the coefficient
    corr_pvals_df: pandas DataFrame
        Dataframe containing each predictor-response corrected p value of the coefficient
        (Benjamini/Hochberg method)
    """
    
    # initialize param model dfs to store results
    coeffs_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    lowi_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    highi_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    pvals_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    intercepts_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    
    # list of variables that need intercept passing through zero
    vars_zero_intercep = ["age_decades"]

    # compute a multivariate linear regressions for each response variable
    for response_var in name_response_vars:

        # generate formula
        formula = f'{response_var} ~ '
        if rules == None:
            for pred_var in name_predictor_vars:
                formula = f'{formula} + {pred_var}'
                
        else:
            name_predictor_vars = rules[response_var]
            for pred_var in name_predictor_vars:
                formula = f'{formula} + {pred_var}'

        formula = formula.replace("+", "", 1)

        if any(pred_var in vars_zero_intercep for pred_var in name_predictor_vars):
            formula = f"{formula} -1"

        # compute model
        print(f"MODEL formula (multivariable): {formula}")
        mod = smf.ols(formula = formula, data = response_vars_df, missing = "drop")
        res = mod.fit()

        ## extract covar coefficient, intervals, and p-value for each predictor
        for pred_var in name_predictor_vars:
            coeffs_df.loc[response_var, pred_var] = res.params[pred_var]
            lowi_df.loc[response_var, pred_var] = res.conf_int().loc[pred_var][0]
            highi_df.loc[response_var, pred_var] = res.conf_int().loc[pred_var][1]
            pvals_df.loc[response_var, pred_var] = res.pvalues[pred_var]
            # new! extract also the intercept
            if any(pred_var in vars_zero_intercep for pred_var in name_predictor_vars):
                    intercept = 0
            else:
                intercept = res.params["Intercept"]
            intercepts_df.loc[response_var, pred_var] = intercept

    # correct p values for false discovery rate
    if correct_pvals:
        _, corr_pvals = fdrcorrection(pvals_df.values.flatten(), alpha = 0.05, method = 'indep', is_sorted = False)
        corr_pvals_df = pd.DataFrame(corr_pvals.reshape(pvals_df.shape), index = pvals_df.index, columns = pvals_df.columns)
    else:
        corr_pvals_df = pvals_df

    return coeffs_df, lowi_df, highi_df, corr_pvals_df, intercepts_df

def multivar_mixedeffects_linear_regression(response_vars_df, name_response_vars,
                                            name_predictor_vars, name_random_effects, 
                                            correct_pvals = True, rules = None):
    """
    Calculates a mixed-effects linear regression for several response variables
    and returns the coefficients, confidence intervals and corrected p values in a dataframe.
    
    Parameters
    ----------
    response_vars_df: pandas DataFrame
        Dataframe containing the data points of the response variables and
        predictor variable per sample. Both predictor and response variables must be
        in the dataframe columns, and samples in the rows. 
    name_response_vars: list
        Response variables
    name_predictor_vars: list
        Predictor variables
    name_random_effects: str
        Random effects we want take into account in the model
    correct_pvals: boolean (default: True)
        Whether to correct the p-values for multiple testing
    rules: dictionary (default: None)
        Dictionary with the format {response:[predictors]} to 
        specify the set of predictors to be included in the 
        model for each response
        
        
    Returns
    -------
    coeffs_df: pandas DataFrame
        Dataframe containing each predictor-response coefficient
    lowi_df: pandas DataFrame
        Dataframe containing each predictor-response low confidence interval 
        of the coefficient
    highi_df: pandas DataFrame
        Dataframe containing each predictor-response high confidence interval 
        of the coefficient
    corr_pvals_df: pandas DataFrame
        Dataframe containing each predictor-response corrected p value of the coefficient
        (Benjamini/Hochberg method)
    intercepts_df: pandas DataFrame
        Dataframe containing each predictor-response model intercept
    """
    
    # initialize param model dfs to store results
    coeffs_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    lowi_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    highi_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    pvals_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)
    intercepts_df = pd.DataFrame(index = name_response_vars, columns = name_predictor_vars)

    # list of variables that need intercept passing through zero
    vars_zero_intercep = ["age_decades"]

    # compute a multivariate linear regressions for each response variable
    for response_var in name_response_vars:

        # generate formula
        formula = f'{response_var} ~ '
        if rules == None:
            for pred_var in name_predictor_vars:
                formula = f'{formula} + {pred_var}'

        else:
            name_predictor_vars = rules[response_var]
            for pred_var in name_predictor_vars:
                formula = f'{formula} + {pred_var}'

        formula = formula.replace("+", "", 1)

        if any(pred_var in vars_zero_intercep for pred_var in name_predictor_vars):
            formula = f"{formula} -1"

        # compute model
        print(f"MODEL formula (multivariable): {formula}")
        mod = smf.mixedlm(formula = formula, data = response_vars_df, groups = response_vars_df[name_random_effects], missing = "drop")
        res = mod.fit()

        ## extract covar coefficient, intervals, and p-value for each predictor
        for pred_var in name_predictor_vars:
            if "depth" in pred_var:
                pred_var_colname = "depth"
            else:
                pred_var_colname = pred_var
            coeffs_df.loc[response_var, pred_var_colname] = res.params[pred_var]
            lowi_df.loc[response_var, pred_var_colname] = res.conf_int().loc[pred_var][0]
            highi_df.loc[response_var, pred_var_colname] = res.conf_int().loc[pred_var][1]
            pvals_df.loc[response_var, pred_var_colname] = res.pvalues[pred_var]
            # new! extract also the intercept
            if any(pred_var in vars_zero_intercep for pred_var in name_predictor_vars):
                    intercept = 0
            else:
                intercept = res.params["Intercept"]
            intercepts_df.loc[response_var, pred_var_colname] = intercept

    # correct p values for false discovery rate
    if correct_pvals:
        _, corr_pvals = fdrcorrection(pvals_df.values.flatten(), alpha = 0.05, method = 'indep', is_sorted = False)
        corr_pvals_df = pd.DataFrame(corr_pvals.reshape(pvals_df.shape), index = pvals_df.index, columns = pvals_df.columns)
    else:
        corr_pvals_df = pvals_df

    return coeffs_df, lowi_df, highi_df, corr_pvals_df, intercepts_df