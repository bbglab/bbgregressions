from src.globals import GENERAL_CONFIG_OPTIONS

# mutdensity and mutreadsdensity
MUTDENSITY_METRICS = ["mutdensity", "mutreadsdensity"]
MUTDENSITY_REGIONS = ["all", "protein_affecting", "non_protein_affecting", "synonymous"]
MUTDENSITY_MUTTYPES = {
    "all": "all_types",
    "snv": "SNV",
    "indel": "DELETION-INSERTION",
    "snv_indel": "DELETION-INSERTION-SNV",
}
MUTDENSITY_ADJUSTMENT = ["yes", "no"]

CONFIG_TEMPLATE_MUTDENSITY = {
    "metric_name": "mutdensity",
    "file": "/path/to/all_mutdensities.tsv",
    "region": [f"select between {', '.join(MUTDENSITY_REGIONS)}", ""],
    "muttype": [f"select between {', '.join(MUTDENSITY_MUTTYPES)}", ""],
    "adjust": f"select between {', '.join(MUTDENSITY_ADJUSTMENT)}",
    "elements_total_by": f"select between {', '.join(GENERAL_CONFIG_OPTIONS['elements_total_by'])}",
    "samples_total_by": f"select between {', '.join(GENERAL_CONFIG_OPTIONS['samples_total_by'])}",
}

CONFIG_TEMPLATE_MUTREADSDENSITY = CONFIG_TEMPLATE_MUTDENSITY.copy()
CONFIG_TEMPLATE_MUTREADSDENSITY["metric_name"] = "mutreadsdensity"

# omega
OMEGA_IMPACTS = [
    "essential_splice",
    # "essential_splice_plus",
    "missense",
    "nonsense",
    "nonsynonymous_splice",
    "splice_region_variant",
    "truncating",
    # "truncating_plus"
]

OMEGA_GLOBALLOC = OMEGA_MULTI = ["yes", "no"]

CONFIG_TEMPLATE_OMEGA = {
    "metric_name": "omega",
    "file": "/path/to/file",
    "global_loc": f"select between {', '.join(OMEGA_GLOBALLOC)}",
    "multi": f"select between {', '.join(OMEGA_MULTI)}",
    "impact": [f"select between {', '.join(OMEGA_IMPACTS)}", ""],
    "significance_threshold": "recommended 0.05 (if no filtering by significance, choose 1)",
    "elements_total_by": f"select between {', '.join(GENERAL_CONFIG_OPTIONS['elements_total_by'])}",
    "samples_total_by": f"select between {', '.join(GENERAL_CONFIG_OPTIONS['samples_total_by'])}",
}
