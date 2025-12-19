import pandas as pd

import daiquiri

from src import __logger_name__

logger = daiquiri.getLogger(__logger_name__)

def add_totals(data: pd.DataFrame,
            ttype: str,
            method: str) -> pd.DataFrame:
    """
    """
    logger.info(f"ADD: total for each {ttype}")
    if ttype == "element":
        axis = 1
        opposite_ttype = "sample"
    elif ttype == "sample":
        axis = 0
        opposite_ttype = "element"

    if method == "included":
        logger.info(f"Method: included. The totals for each {ttype} are already in the data")
    elif method == "none":
        logger.info(f"Method: none. The totals for each {ttype} won't be included")
    else:
        if method == "sum":
            total = data.sum(axis = axis, skipna = True).to_frame(f"total_{opposite_ttype}")
        elif method == "mean":
            total = data.mean(axis = axis, skipna = True).to_frame(f"total_{opposite_ttype}")
        elif method == "median":
            total = data.median(axis = axis, skipna = True).to_frame(f"total_{opposite_ttype}")

        if opposite_ttype == "sample":
            data = data.merge(total, right_index = True, left_index = True, how = "left")
        elif opposite_ttype == "element":
            data = pd.concat([data, total.T])

        logger.info(f"Method: {method}. The totals for each {ttype} are calculated as the {method} of all {opposite_ttype}s")
        logger.warning("Double check the totals were not already in the table")
    
    return data

        