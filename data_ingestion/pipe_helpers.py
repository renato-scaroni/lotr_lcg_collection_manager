from typing import Iterator, Callable
from pipe import Pipe, select, where
from pipe import select, where

@Pipe
def as_type(it: Iterator, t: type):
    """Convert a generator to a list"""
    return t(it)


@Pipe
def as_list(it: Iterator):
    """Convert a generator to a list"""
    return list(it)

@Pipe
def as_dict(it: Iterator):
    """Convert a generator to a dict"""
    return dict(it)

@Pipe
def where_tuple(it: Iterator, fun: Callable):
    """Filter a list of tuples by the given function"""
    return it | where(lambda x: fun(*x))

@Pipe
def select_tuple(it: Iterator, fun: Callable):
    """Select a list of tuples by the given function"""
    return it | select(lambda x: fun(*x))