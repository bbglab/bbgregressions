from bbgregressions.globals import GENERAL_CONFIG_OPTIONS

# mutdensity
MUTDENSITY_METRICS = ["mutdensity", "mutreadsdensity"]
MUTDENSITY_REGIONS = ["all", "protein_affecting", "non_protein_affecting", "synonymous"]
MUTDENSITY_MUTTYPES = {"all": "all_types",
                    "snv": "SNV", 
                    "indel": "DELETION-INSERTION",
                    "snv_indel": "DELETION-INSERTION-SNV"}
MUTDENSITY_ADJUSTMENT = ["yes", "no"]

CONFIG_TEMPLATE_MUTDENSITY = CONFIG_TEMPLATE_MUTREADSDENSITY = {
    "metric_name": "mutdensity",
    "file": "/path/to/all_mutdensities.tsv",
    "region": [
        f"select between {", ".join(MUTDENSITY_REGIONS)}",
        ""
    ],
    f"muttype": [
        f"select between {", ".join(MUTDENSITY_MUTTYPES)}",
        ""
    ],
    "adjust" : f"select between {", ".join(MUTDENSITY_ADJUSTMENT)}",
    "elements_total_by": f"select between {", ".join(GENERAL_CONFIG_OPTIONS['elements_total_by'])}",
    "samples_total_by": f"select between {", ".join(GENERAL_CONFIG_OPTIONS['samples_total_by'])}"          
}

CONFIG_TEMPLATE_MUTREADSDENSITY["metric_name"] = "mutreadsdensity"
