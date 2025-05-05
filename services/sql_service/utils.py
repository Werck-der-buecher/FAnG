import logging
from collections import OrderedDict
from functools import wraps
from inspect import signature
from typing import Callable, Union, List

import numpy as np


def check(logging_level, func, *args):
    if not func(*args):
        logging.log(logging_level, func.__self__.lastError().text())
        raise ValueError(func.__self__.lastError())


def dig_round(arr, bins):
    bin_centers = (bins[:-1] + bins[1:]) / 2
    idx = np.digitize(arr, bin_centers)
    result = bins[idx]
    return result


def bind_preproc_functions(func):
    sig = signature(func)

    @wraps(func)
    def inner(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        bound.arguments = OrderedDict(
            (param, sig.parameters[param].annotation(value))
            if isinstance(sig.parameters[param].annotation, Callable)
            else (param, value)
            for param, value in bound.arguments.items()
        )
        return func(*bound.args, **bound.kwargs)

    return inner


def prune_label_name(labels: Union[str, List[str]]) -> str:
    def repl(lbl):
        return '\'\'' if lbl == '\'' else lbl

    if isinstance(labels, list):
        out = list(map(repl, labels))
    else:
        out = repl(labels)

    return out
