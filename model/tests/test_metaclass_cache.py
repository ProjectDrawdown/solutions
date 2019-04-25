"""Tests for metaclass_cache.py"""

import pandas as pd
from model import metaclass_cache



# test_tam.py also exercises metaclass_cache.

class MemoizedClass(object, metaclass=metaclass_cache.MetaclassCache):
    def __init__(self, df, number):
        pass



def test_subclass():
    """Verify that nothing blows up."""
    df = pd.DataFrame(0, index=[1, 2, 3], columns=['A', 'B', 'C'])
    _ = MemoizedClass(df=df, number=3)
