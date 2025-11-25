import pandas as pd
import os

from bbbregressions.src.create_input.cleaner import clean_nan, clean_reps, handle_nan
from bbbregressions.src.create_input.addon import add_totals

def formatter(data: pd.DataFrame,
            metric: str,
            config: dict) -> None:
    """
    """

    # pivot and reindex with selected elements and samples
    data_p = data.pivot(values = metric,
                        index = "element",
                        columns = "sample")
    data_p = data_p.reindex(index = config["elements"],
                            columns = config["samples"])

    # data cleaning
    data_c = clean_nan(data_p)
    data_c = clean_reps(data_c)

    # add total for element or sample if applicable
    data_te = add_totals(data_c, "element", config["elements_total_by"]) 
    data_ts = add_totals(data_te, "sample", config["samples_total_by"]) 

    # handle NA
    data_ok = handle_nan(data_ts, config)

    # save 
    file = os.path.join(output_dir, "", f"{metric_var4file.lower()}.tsv")
    data_ok.to_csv(file, sep = "\t")
    
    return None