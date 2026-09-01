from src.create_input.readers.clonalstructure import *

METRIC2READER = {
    "mutdensity": mutdensity,
    "mutreadsdensity": mutdensity,
    # "oncodrivefml": oncodrivefml,
    "omega": omega,
    "dominance": dynamics,
    "PMB": dynamics,
    "major": dynamics,
    "depth": depths,
    "mutdensity_adjusted": mutdensity_adj,
}
