import pandas as pd

def clean_nan(data: pd.DataFrame) -> pd.DataFrame:
    """
    """
    print("QC: missing values")
    elements2remove = data.loc[data.isna().all(axis = 1)].index.tolist()
    if elements2remove:
        print("All NA for the following elements. Removed from the analysis:")
        print(elements2remove)
        data = data.dropna(how = "all", axis = 0)
    else:
        print("All the elements have at least one no NA value. Kept.")

    return data

def clean_reps(data: pd.DataFrame) -> pd.DataFrame:
    """
    """
    print("QC: identical values")
    elements2remove = data.loc[data.nunique(axis = 1) == 1].index.tolist()
    if elements2remove:
        print("Identical values across samples for the following elements. Removed from the analysis:")
        print(elements2remove)
        data = data.loc[data.nunique(axis = 1) > 1].index
    else:
        print("No element has identical values. Kept.")

    return data

def handle_nan(data: pd.DataFrame,
            config: dict) -> pd.DataFrame:
    """
    """
    print("QC: handle remaining missing values")
    if config["handle_na"] == "ignore":
        print("Option: ignore. Keeping NAs")
    elif config["handle_na"] == "mean":
        print("Option: mean. NAs filled with mean per element")
        data = data.apply(lambda row: row.fillna(row.mean()), axis = 1)
    elif config["handle_na"] == "cohort":
        print("Option: all_samples. NAs filled with the all_samples value per elements")
        data = data.apply(lambda col: col.fillna(data["all_samples"]))
    
    return data

