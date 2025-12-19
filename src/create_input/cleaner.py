import pandas as pd
import daiquiri

from src import __logger_name__

logger = daiquiri.getLogger(__logger_name__)


def clean_nan(data: pd.DataFrame) -> pd.DataFrame:
    """
    """
    logger.info("QC: missing values")
    elements2remove = data.loc[data.isna().all(axis = 1)].index.tolist()
    if elements2remove:
        logger.info(f"All NA for the following elements: {elements2remove}")
        logger.info("Elements removed from the analysis")
        data = data.dropna(how = "all", axis = 0)
    else:
        logger.info("All the elements have at least one no NA value. Kept all.")

    return data

def clean_reps(data: pd.DataFrame) -> pd.DataFrame:
    """
    """
    logger.info("QC: identical values")
    elements2remove = data.loc[data.nunique(axis = 1) == 1].index.tolist()
    if elements2remove:
        logger.info(f"Identical values across samples for the following elements: {elements2remove}")
        logger.info("Elements removed from the analysis")
        data = data.loc[data.nunique(axis = 1) > 1]
    else:
        logger.info("No element has identical values across samples. Kept all.")

    return data

def handle_nan(data: pd.DataFrame,
            config: dict) -> pd.DataFrame:
    """
    """
    logger.info("QC: handle remaining missing values")
    if config["handle_na"] == "ignore":
        logger.info("Option: ignore. Keeping NAs")
    elif config["handle_na"] == "mean":
        logger.info("Option: mean. NAs filled with mean per element")
        data = data.apply(lambda row: row.fillna(row.mean()), axis = 1)
    elif config["handle_na"] == "cohort":
        logger.info("Option: cohort. NAs filled with the totals value per elements")
        if "all_samples" in data.columns:
            total_col = "all_samples"
        else:
            total_col = "total_sample"
        data = data.apply(lambda col: col.fillna(data[total_col]))
    
    return data

