from bbgregressions.regressions.models import linear, linear_me

MULTI_OPTIONS = ["yes", "no"]
MODELS = {"linear": linear,
        "linear-mixed-effects": linear_me}
