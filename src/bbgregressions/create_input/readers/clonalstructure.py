import pandas as pd

from bbgregressions.create_input.schemas.clonalstructure import *
from bbgregressions.create_input.formatter import formatter


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

            formatter(data = data_f,
                    metric = metric,
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

def process_omega_mle(omega_dir,
                      total_cols_by,
                      rows_names, cols_names, 
                      save_files_dir,
                      omega_modality = "mle"):
    """
    Generates and saves pivoted dataframes of omega (MLE or bayes),
    with columns as samples and rows as genes.
    Does the same with a two column table for the total of
    the genes and the total of the samples.
    Creates as many versions as those specified in 
    metrics and muts4profile, and for each type created a version with all
    values and another with significant values only

    Parameters
    ----------
    omega_dir: str
        Path to the directory where the output files of omega
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
    omega_modality: str (default: "mle")
        Omega modality used to compute omegas. Can be "mle" or "bayes".

    Returns
    -------
    None
    """

    # load omega results in a df
    omega_df = pd.DataFrame()
    files = [file for file in os.listdir(omega_dir) if omega_modality in file]  
    for file in files:
        sample_df = pd.read_csv(f"{omega_dir}/{file}", sep = "\t", header = 0)
        sample_df["sample"] = file
        omega_df = pd.concat((omega_df, sample_df)).reset_index(drop = True)

    # create tables
    metric_var = "dnds"
    impacts4muts = omega_df["impact"].unique() # mutation impact filter used to compute the omega values
    print(impacts4muts)
    # muts4profile = ["NoValue", "non_prot_aff"] # muts used to create the bg profile
    muts4profile = ["NoValue"] # muts used to create the bg profile # Ferriol deactivated nonprotaff profile in the latest run
    # uniqueormulti_muts = ["NoValue", "multi"] # whether each mutation is considered once or as many ALT reads is has
    uniqueormulti_muts = ["NoValue"]

    ## equivalence for file names needed for the regression module
    names4files_profile = {
        "NoValue": "allprof",
        "non_prot_aff": "nonprotaffprof"
    }
    names4files_uniqmultimuts = {
        "NoValue": "uniquemuts",
        "multi": "multimuts"
    }

    samples = list(set([".".join(file.split(".")[:2]) for file in omega_df["sample"]]))
    # print(samples)
    for profile in muts4profile:
        for uniqormulti in uniqueormulti_muts:
            # analysis_info = [f'{sampl}.{profile}.{uniqormulti}.tsv'.replace('.NoValue', '') for sampl in samples] # this way we do the subset properly (checked)
            analysis_info = [f'{sampl}.{profile}.{uniqormulti}.global_loc.tsv'.replace('.NoValue', '') for sampl in samples] # this way we do the subset properly (checked)
            # print(analysis_info)
            for impact in impacts4muts:
                # print(impact)
                print(impact, profile, uniqormulti)
                if impact in ['essential_splice_plus', 'truncating_plus']:
                    continue
                omega_df_f = omega_df.loc[(omega_df["sample"].isin(analysis_info)) &
                                            (omega_df["impact"] == impact)]
                # display(omega_df_f)
                omega_df_f["sample"] = omega_df_f.apply(lambda row: row["sample"].split(".")[1], axis = 1)   # after use, remove analysis info to every sample id
                omega_df_f = omega_df_f.rename({"GENE_ID": "gene"}, axis = 1)

                ## all omega values, regardless of significance
                
                metric_var4file = f"omega.{metric_var}_{omega_modality}_{impact.replace('_', '')}_{names4files_profile[profile]}_{names4files_uniqmultimuts[uniqormulti]}_nosignificant"
                create_metric_table(metric_df = omega_df_f,
                                    metric_var = metric_var,
                                    rows_var = "gene", cols_var = "sample",
                                    rows_names = rows_names, cols_names = cols_names, 
                                    total_cols_by = total_cols_by,
                                    total_rows_by = "all_samples",
                                    metric_var4file = metric_var4file, 
                                    save_files_dir = save_files_dir, 
                                    keep_rows_ordered = True, keep_cols_ordered = True)
                
                ## only significant omega values
                print(impact, profile, uniqormulti, "significant")
                metric_var4file = f"omega.{metric_var}_{omega_modality}_{impact.replace('_', '')}_{names4files_profile[profile]}_{names4files_uniqmultimuts[uniqormulti]}_significant"
                ### aproach 1: filter out non-significant values, generates NA
                omega_df_f = omega_df_f.loc[(omega_df_f["pvalue"] < 0.05)]
                ### aproach 2: fill non-significant values with zero (for regressions)
                # omega_df_f.loc[(omega_df_f["pvalue"] > 0.05), metric_var] = 0
                create_metric_table(metric_df = omega_df_f,
                                    metric_var = metric_var,
                                    rows_var = "gene", cols_var = "sample",
                                    rows_names = rows_names, cols_names = cols_names, 
                                    total_cols_by = total_cols_by,
                                    total_rows_by = "all_samples",
                                    metric_var4file = metric_var4file, 
                                    save_files_dir = save_files_dir, 
                                    keep_rows_ordered = True, keep_cols_ordered = True)
                

    return None