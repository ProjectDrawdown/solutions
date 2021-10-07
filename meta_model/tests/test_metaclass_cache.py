"""Tests for metaclass_cache.py"""

import pandas as pd
from meta_model.metaclass_cache import MetaclassCache

# test_tam.py also exercises metaclass_cache.

class MemoizedClass(object, metaclass=MetaclassCache):
    def __init__(self, df, number, number2):
        pass


def test_subclass():
    """Verify that nothing blows up."""
    df = pd.DataFrame(0, index=[1, 2, 3], columns=['A', 'B', 'C'])
    a = MemoizedClass(df=df, number=3, number2=6)
    b = MemoizedClass(df=df, number=3, number2=6)
    c = MemoizedClass(df=df, number=3, number2=7)
    d = MemoizedClass(df, 3, 7)
    assert a is b
    assert a is not c
    assert c is not d


def test_unhashable():
    # Test that it does not raise TypeError
    _ = MemoizedClass(df=[dict()], number=0, number2=0)


def test_cache():
    df = pd.DataFrame(0, index=[1, 2, 3], columns=['A', 'B', 'C'])
    a = MemoizedClass(df=df, number=6, number2=6)
    b = MemoizedClass(df=df, number=7, number2=7)
    assert a is not b
