import os
import logging

from itertools import groupby


def realrelpath(origin, dest):
    """ Get the relative path between two paths, accounting for filepaths
    :param origin:
    :param dest:
    :return:
    """
    # get the absolute paths so that strings can be compared
    origin = os.path.abspath(origin)
    dest = os.path.abspath(dest)

    # find out if the origin and destination are filepaths
    origin_isfile = os.path.isfile(origin)
    dest_isfile = os.path.isfile(dest)

    # if dealing with filepaths,
    if origin_isfile or dest_isfile:
        # get the base filename
        filename = os.path.basename(origin) if origin_isfile else os.path.basename(dest)
        # in cases where we're dealing with a file, use only the directory name
        origin = os.path.dirname(origin) if origin_isfile else origin
        dest = os.path.dirname(dest) if dest_isfile else dest
        # get the relative path between directories, then re-add the filename
        return os.path.join(os.path.relpath(dest, origin), filename)
    else:
        # if not dealing with any filepaths, just run relpath as usual
        return os.path.relpath(dest, origin)





# See see rapid-photo-downloaded-0.9.34
# Source of class AdjacentKey, first_and_last and runs:
# http://stupidpythonideas.blogspot.com/2014/01/grouping-into-runs-of-adjacent-values.html
class AdjacentKey:
    __slots__ = ["obj"]

    def __init__(self, obj) -> None:
        self.obj = obj

    def __eq__(self, other) -> bool:
        ret = self.obj - 1 <= other.obj <= self.obj + 1
        if ret:
            self.obj = other.obj
        return ret


def first_and_last(iterable):
    start = end = next(iterable)
    for end in iterable:
        pass
    return start, end

def runs(iterable):
    for k, g in groupby(iterable, AdjacentKey):
        yield first_and_last(g)