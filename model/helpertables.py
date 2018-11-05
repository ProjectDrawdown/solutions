"""Helper Tables module.
"""

import numpy as np
import pandas as pd

class HelperTables:
  """Implementation for the Helper Tables module.

  Arguments:
  ac = advanced_controls.py object, storing settings to control
    model operation.
  """
  def __init__(self, ac):
    self.ac = ac

  def soln_ref_funits_adopted(self, datapoints, ref_tam_per_region):
    """Cumulative Adoption in funits, interpolated between two datapoints.

       datapoints: a DataFrame with columns per region and two rows for two years of data.
       ref_tam_per_region: Total Addressable Market dataframe, ex: from tam.py

       'Helper Tables'!B26:L73
    """
    first_year = datapoints.first_valid_index()
    last_year = 2060
    adoption = pd.DataFrame(0, index=np.arange(first_year, last_year + 1),
        columns=datapoints.columns.copy(), dtype='float')
    for col in adoption.columns:
      year1 = datapoints.index.values[0]
      year2 = datapoints.index.values[1]
      adopt1 = datapoints.loc[year1, col]
      adopt2 = datapoints.loc[year2, col]
      for year in range(first_year, last_year + 1):
        adoption.loc[year, col] = self._forecast(year1, adopt1, year2, adopt2, year)
    adoption.name = "soln_ref_funits_adopted"
    if self.ac.ref_adoption_regional_data:
      adoption.loc[:, "World"] = 0
      adoption.loc[:, "World"] = adoption.sum(axis=1)
    for col in adoption.columns:
      adoption[col] = adoption[col].combine(ref_tam_per_region[col], min)
    return adoption

  def _forecast(self, year1, adopt1, year2, adopt2, year):
    """Interoplates a line between (year1, adopt1) and (year2, adopt2)."""
    fract_year = (float(year) -float(year1)) / (float(year2) - float(year1))
    fract_adopt = fract_year * (float(adopt2) - float(adopt1))
    return adopt1 + fract_adopt
