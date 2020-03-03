"""Metaclass instance cache.
Python metaclass which checks arguments passed to constructor and maintains a cache.
Passing in the same arguments will return the same object, shared by all callers.

This is especially useful for objects with expensive methods which are decorated
@lru_cache, like TAM.py. Sharing a single object means when any of them have warmed
the cache, all solutions benefit.
"""

import pandas as pd
import json

# pylint is confused by the __call__ syntax
# pylint: disable=no-value-for-parameter

class MetaclassCache(type):

    cache = {}

    def hash_item(self, item):
        if isinstance(item, pd.DataFrame) or isinstance(item, pd.Series):
            item = tuple(pd.util.hash_pandas_object(item))
        try:
            return hash(item)
        except TypeError:
            pass

        try:
            return hash(json.dumps(item, separators=(',', ':')))
        except TypeError:
            pass

        try:
            return(hash(str(item)))
        except TypeError:
            pass

        try:
            return hash(tuple(item))
        except TypeError as e:
            raise e


    def __call__(self, *args, **kwargs):
        key = self.hash_item(self)
        for arg in args:
            key = (key << 64) ^ self.hash_item(arg)
        for arg in sorted(kwargs.keys()):
            key = (key << 64) ^ self.hash_item(arg)
            key = (key << 64) ^ self.hash_item(kwargs[arg])
        try:
            return self.cache[key]
        except KeyError:
            instance = type.__call__(self, *args, **kwargs)
            self.cache[key] = instance
            return instance
