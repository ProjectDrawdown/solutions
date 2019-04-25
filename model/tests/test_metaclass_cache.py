"""Tests for metaclass_cache.py"""  # by Denton Gentry
# by Denton Gentry
import pandas as pd  # by Denton Gentry
from model import metaclass_cache  # by Denton Gentry


# by Denton Gentry
# test_tam.py also exercises metaclass_cache.  # by Denton Gentry
# by Denton Gentry
class MemoizedClass(object, metaclass=metaclass_cache.MetaclassCache):  # by Denton Gentry
    def __init__(self, df, number):  # by Denton Gentry
        pass  # by Denton Gentry
    # by Denton Gentry


def test_subclass():  # by Denton Gentry
    """Verify that nothing blows up."""  # by Denton Gentry
    df = pd.DataFrame(0, index=[1, 2, 3], columns=['A', 'B', 'C'])  # by Denton Gentry
    _ = MemoizedClass(df=df, number=3)  # by Denton Gentry
