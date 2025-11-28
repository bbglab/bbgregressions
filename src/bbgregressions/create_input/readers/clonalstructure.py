import pandas as pd
import daiquiri

from bbgregressions.create_input.schemas.clonalstructure import *
from bbgregressions.create_input.formatter import formatter

from bbgregressions import __logger_name__

logger = daiquiri.getLogger(__logger_name__)

def mutdensity(config: dict,
            output_dir: str) -> pd.DataFrame:
    """
    Reads and filters mutdensity and mutreadsdensity
    data from deepCSA. Calls formatter to produce
    a regressions input table for each filtering combination
    
    Parameters
    ----------
    config: dict
        filtering info and file name

    """
    
    # load data
    data = pd.read_csv(config["file"], sep = "\t")
    data = data.rename({"GENE": "element", "SAMPLE_ID": "sample"}, axis = 1)

    # read filters
    metric = f'{config["metric_name"].upper()}_MB'
    metric = f'{config["metric_name"].upper()}_ADJUSTED' if config["adjust"] == "yes" else metric
    regions = MUTDENSITY_REGIONS if not config["region"] else config["region"]
    muttypes = MUTDENSITY_MUTTYPES.values() if not config["muttype"] else [
    MUTDENSITY_MUTTYPES[muttype] for muttype in config["muttype"] ]
    elements = data["element"].unique() if not config["elements"] else config["elements"]
    samples = data["sample"].unique() if not config["samples"] else config["samples"]

    # filter data and prepare for formatter
    for region in regions:
        for muttype in muttypes:
            
            data_f = data.loc[(data["REGIONS"] == region) &
                            (data["MUTTYPES"] == muttype)]
            
            logger.info("Generating table with these filter combination:")
            logger.info(f"\tRegion: {region}")
            logger.info(f"\tMutation type: {muttype.lower()}")
            filters = f"{region}.{muttype.lower()}"
            formatter(data = data_f,
                    metric = metric,
                    filters = filters,
                    config = config,
                    elements = elements,
                    samples = samples,
                    output_dir = output_dir)

    return None

def process_oncodrivefml(oncodrivefml_dir, total_cols_by,
                         rows_names, cols_names, 
                         save_files_dir):
    """
    Generates and saves pivoted dataframes of OncodriveFML metrics
    (z-score and difference between observed and expected mean 
    deleteriousness scores), with columns as samples and rows as genes.
    Does the same with a two column table for the total of
    the genes and the total of the samples.
    Creates as many versions as those specified in 
    metrics and muts4profile, and for each type created a version with all
    values and another with significant values only
    
    Parameters
    ----------
    oncodrivefml_dir: str
        Path to the directory where the output files of OncodriveFML
        are stored
    total_cols_by: str
        How to calculate the total for the columns of the dataframe.
        Can be "sum", "mean" or "median"
    rows_names: list
        List of values to be used as the row names of the 
        pivoted dataframe. Used both to subset the df if needed
        and to add rows with NA we want to keep for downstream 
        analysis
    cols_names: list
        List of values to be used as the column names of the 
        pivoted dataframe. Used both to subset the df if needed
        and to add columns with NA we want to keep for downstream 
        analysis
    save_files_dir: str
        Path where to store the generated files

    Returns
    -------
    None
    """

    # load OncodriveFML results in a df
    oncodrivefml_df = pd.DataFrame()
    for file in os.listdir(oncodrivefml_dir):
        sample_df = pd.read_csv(f"{oncodrivefml_dir}/{file}/{file.split('.')[0]}-oncodrivefml.tsv.gz", 
                                sep = "\t", header = 0)
        sample_df["sample"] = file
        oncodrivefml_df = pd.concat((oncodrivefml_df, sample_df)).reset_index(drop = True)

    # compute new metric: difference between expected and observed mean deleteriousness scores
    oncodrivefml_df["DIFF-OBSvsEXP"] = oncodrivefml_df["AVG_SCORE_OBS"] - oncodrivefml_df["POPULATION_MEAN"]

    # create tables
    metrics = ["Z-SCORE", "DIFF-OBSvsEXP"]
    # muts4profile = [".all", ".non_prot_aff"] # muts used to create the bg profile
    muts4profile = [".all"] # muts used to create the bg profile # Ferriol deactivated nonprotaff profile in the latest run

    for metric_var in metrics:
        for profile in muts4profile:
            
            oncodrivefml_df_f = oncodrivefml_df.loc[oncodrivefml_df["sample"].str.contains(profile)]
            oncodrivefml_df_f["sample"] = oncodrivefml_df_f.apply(
                lambda row: row["sample"].split(".")[0], axis = 1)    # after use, remove profile info to every sample id
            oncodrivefml_df_f = oncodrivefml_df_f.rename({"GENE_ID": "gene"}, axis = 1)

            ## all oncodrivefml values, regardless of significance
            print(metric_var, profile)
            create_metric_table(metric_df = oncodrivefml_df_f,
                            metric_var = metric_var,
                            rows_var = "gene", cols_var = "sample",
                            rows_names = rows_names, cols_names = cols_names, 
                            total_cols_by = total_cols_by,
                            total_rows_by = "all_samples",
                            metric_var4file = f'oncodrivefml.{"".join(metric_var.split("-"))}_{"".join(profile[1:].split("_"))}prof_nosignificant', 
                            save_files_dir = save_files_dir, 
                            keep_rows_ordered = True, keep_cols_ordered = True)

            ## only significant oncodrivefml values (qvalue is not calculated for one sample only)
            ### aproach 1: filter out non-significant values, generates NA
            # oncodrivefml_df_f = oncodrivefml_df_f.loc[(oncodrivefml_df_f["Q_VALUE"] < 0.05)  
            #                                           | ((oncodrivefml_df_f["Q_VALUE"].isna()) & (oncodrivefml_df_f["P_VALUE"] < 0.05))]
            ### aproach 2: fill non-significant values with zero (for regressions)
            oncodrivefml_df_f.loc[(oncodrivefml_df_f["Q_VALUE"] > 0.05)  
                                | ((oncodrivefml_df_f["Q_VALUE"].isna()) & (oncodrivefml_df_f["P_VALUE"] > 0.05)), metric_var] = 0
            print(metric_var, profile, "significant")
            create_metric_table(metric_df = oncodrivefml_df_f,
                            metric_var = metric_var,
                            rows_var = "gene", cols_var = "sample",
                            rows_names = rows_names, cols_names = cols_names, 
                            total_cols_by = total_cols_by,
                            total_rows_by = "all_samples",
                            metric_var4file = f'oncodrivefml.{"".join(metric_var.split("-"))}_{"".join(profile[1:].split("_"))}prof_significant', 
                            save_files_dir = save_files_dir, 
                            keep_rows_ordered = True, keep_cols_ordered = True)
            
    return None

def omega(config: dict,
        output_dir: str) -> pd.DataFrame:
    """
    Reads and filters omega data from deepCSA.
    Calls formatter to produce a regressions input
    table for each filtering combination
    
    Parameters
    ----------
    config: dict
        filtering info and file name

    """

    # load data
    data = pd.read_csv(config["file"], sep = "\t")
    data = data.rename({"gene": "element", "sample": "sample", "dnds": "omega"},
                    axis = 1)

    # read filters
    impacts = OMEGA_IMPACTS if not config["impact"] else config["impact"]
    elements = data["element"].unique() if not config["elements"] else config["elements"]
    elements = [f"{elem}_{impact}" for impact in impacts for elem in elements]
    samples = data["sample"].unique() if not config["samples"] else config["samples"]
    sign_thres = 1.01 if config["significance_threshold"] == 1 else config["significance_threshold"]

    # filter data and prepare for formatter
    data_f = data.loc[data["impact"].isin(impacts)]
    data_f = data_f.loc[data_f["pvalue"] < sign_thres] 
    ## element: element + impact to avoid repetition
    data_f["element"] = data_f.apply(lambda row: f"{row['element']}_{row['impact']}", axis = 1)
    logger.info("Generating table with these filter combination:")
    logger.info(f"\tImpacts: {impacts}")
    logger.info(f"\tGlobal loc mode: {config["global_loc"]}")
    logger.info(f"\tMulti mode: {config["multi"]}")

    globalloc_label = "globalloc" if config["global_loc"] == "yes" else "no-globalloc"
    multi_label = "multi" if config["multi"] == "yes" else "no-multi"
    sign_thres_label = "no-significance-thres" if config["significance_threshold"] == 1 else f"significance-thres-{sign_thres}"
    filters = f"{globalloc_label}.{multi_label}.{sign_thres_label}"
    formatter(data = data_f,
            metric = config["metric_name"],
            filters = filters,
            config = config,
            elements = elements,
            samples = samples,
            output_dir = output_dir)
                
    return None