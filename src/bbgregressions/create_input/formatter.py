import pandas as pd
import os
import re
import daiquiri

from bbgregressions.create_input.cleaner import clean_nan, clean_reps, handle_nan
from bbgregressions.create_input.addon import add_totals

from bbgregressions import __logger_name__

logger = daiquiri.getLogger(__logger_name__)

def formatter(data: pd.DataFrame,
            metric: str,
            filters: str,
            config: dict,
            elements: list,
            samples: list,
            output_dir: str) -> None:
    """
    """
    
    # check if elements and/or samples were provided as regex
    if isinstance(elements, str):
        regex = f'r"{elements}"'
        allelements = data["element"].unique()
        elements = [elem for elem in allelements if re.search(regex, elem)]
    if isinstance(samples, str):
        regex = samples
        allsamples = data["sample"].unique()
        samples = [sampl for sampl in allsamples if re.search(regex, sampl)]

    # pivot and reindex with selected elements and samples
    data_p = data.pivot(values = metric,
                        index = "element",
                        columns = "sample")
    data_p = data_p.reindex(index = elements,
                            columns = samples)

    # data cleaning
    data_c = clean_nan(data_p)
    data_c = clean_reps(data_c)

    # add total for element or sample if applicable
    data_te = add_totals(data_c, "element", config["elements_total_by"]) 
    data_ts = add_totals(data_te, "sample", config["samples_total_by"]) 

    # handle NA
    data_ok = handle_nan(data_ts, config)

    # transpose df: samples rows, elements columns
    data_ok = data_ok.T

    # save 
    file = os.path.join(output_dir, f"{metric.lower()}.{filters}.tsv")
    logger.info(f"Input generated for {metric}")
    data_ok.to_csv(file, sep = "\t")
    logger.info(f"Saved as {file}")
    
    return None