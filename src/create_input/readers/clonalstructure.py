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
    metric = f'{config["metric_name"].upper()}_ADJUSTED' if config["adjust"] else metric
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
    if not config["elements"]:
        # elements = [elem for elem in data["element"].unique() if "--" not in elem] # removes sub-genic regions
        elements = [f"{elem}_{impact}" for impact in impacts for elem in elements]
    else:
        elements = config["elements"]
    samples = data["sample"].unique() if not config["samples"] else config["samples"]
    sign_thres = 1.01 if config["significance_threshold"] == 1 else config["significance_threshold"]

    # filter data and prepare for formatter
    data_f = data.loc[data["impact"].isin(impacts)]
    data_f = data_f.loc[data_f["pvalue"] < sign_thres] 
    data_f["element"] = data_f.apply(lambda row: f"{row['element']}_{row['impact']}", axis = 1)
    logger.info("Generating table with these filter combination:")
    logger.info(f"\tImpacts: {impacts}")
    logger.info(f"\tGlobal loc mode: {config["global_loc"]}")
    logger.info(f"\tMulti mode: {config["multi"]}")

    globalloc_label = "globalloc" if config["global_loc"] else "no-globalloc"
    multi_label = "multi" if config["multi"] else "no-multi"
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