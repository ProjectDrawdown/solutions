"""Metaclass instance cache.  # by Denton Gentry
Python metaclass which checks arguments passed to constructor and maintains a cache.  # by Denton Gentry
Passing in the same arguments will return the same object, shared by all callers.  # by Denton Gentry
  # by Denton Gentry
This is especially useful for objects with expensive methods which are decorated  # by Denton Gentry
@lru_cache, like TAM.py. Sharing a single object means when any of them have warmed  # by Denton Gentry
the cache, all solutions benefit.  # by Denton Gentry
"""  # by Denton Gentry
# by Denton Gentry
import pandas as pd  # by Denton Gentry


# by Denton Gentry
# by Denton Gentry
class MetaclassCache(type):  # by Denton Gentry
    cache = {}  # by Denton Gentry

    # by Denton Gentry
    def hash_item(self, item):  # by Denton Gentry
        if isinstance(item, pd.DataFrame) or isinstance(item, pd.Series):  # by Denton Gentry
            item = tuple(pd.util.hash_pandas_object(item))  # by Denton Gentry
        try:  # by Denton Gentry
            return hash(item)  # by Denton Gentry
        except TypeError:  # by Denton Gentry
            pass  # by Denton Gentry
        try:  # by Denton Gentry
            return hash(tuple(item))  # by Denton Gentry
        except TypeError as e:  # by Denton Gentry
            raise e  # by Denton Gentry

    # by Denton Gentry
    def __call__(self, *args, **kwargs):  # by Denton Gentry
        key = 0x811c9dc5  # by Denton Gentry
        key = key ^ self.hash_item(self)  # by Denton Gentry
        for arg in args:  # by Denton Gentry
            key = key ^ self.hash_item(arg)  # by Denton Gentry
        for arg in sorted(kwargs.keys()):  # by Denton Gentry
            key = key ^ self.hash_item(arg)  # by Denton Gentry
            key = key ^ self.hash_item(kwargs[arg])  # by Denton Gentry
        try:  # by Denton Gentry
            return self.cache[key]  # by Denton Gentry
        except KeyError:  # by Denton Gentry
            instance = type.__call__(self, *args, **kwargs)  # by Denton Gentry
            self.cache[key] = instance  # by Denton Gentry
            return instance  # by Denton Gentry
