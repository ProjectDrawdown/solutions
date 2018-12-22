"""CH4 Calcs module.

Computes reductions in CO2-equivalent emissions.
"""

import math
import numpy as np
import pandas as pd

class CH4Calcs:
  """CH4 Calcs module.
       Arguments:
         ac: advanced_cost.py object, storing settings to control
           model operation.
         soln_net_annual_funits_adopted:
    """
  def __init__(self, ac, soln_net_annual_funits_adopted):
    self.ac = ac
    self.soln_net_annual_funits_adopted = soln_net_annual_funits_adopted

  def ch4_tons_reduced(self):
    """CH4 reduced, in tons.
       replace gas_ch4_step = `gas_tons_ch4' * `e'^(-(time_from_present - `n')/12)
       'CH4 Calcs'!A10:K56
    """
    if self.ac.ch4_is_co2eq:
      result = self.soln_net_annual_funits_adopted * 0
    else:
      result = self.soln_net_annual_funits_adopted * self.ac.ch4_co2_per_twh
    result.loc[:self.ac.report_start_year - 1] = 0.0
    result.loc[self.ac.report_end_year + 1:] = 0.0
    result.name = "ch4_tons_reduced"
    return result

  def ch4_ppb_calculator(self):
    """Parts Per Billion reduction calculator for CH4.

       Each yearly reduction in CH4 (in metric tons) is modeled as a discrete avoided pulse.
       A Simplified atmospheric lifetime function for CH4 is taken from Myhrvald and Caldeira
       (2012). Atmospheric tons of CH4 are converted to parts per billion CH4 based on the
       molar mass of CH4 and the moles of atmosphere. 

       'CH4 Calcs'!A64:AW110
    """
    ch4_tons_reduced = self.ch4_tons_reduced()
    columns = ["PPB", "Total"] + list(range(2015, 2061))
    ppb_calculator = pd.DataFrame(0, columns=columns,
        index=ch4_tons_reduced.index.copy(), dtype=np.float64)
    ppb_calculator.index = ppb_calculator.index.astype(int)
    first_year = ppb_calculator.first_valid_index()
    last_year = ppb_calculator.last_valid_index()
    for year in ppb_calculator.index:
      b = ch4_tons_reduced.loc[year, "World"]
      for delta in range(1, last_year - first_year + 1):
        if (year + delta - 1) > last_year:
          break
        ppb_calculator.loc[year + delta - 1, year] = b * math.exp(-delta/12)
    ppb_calculator.loc[:, "Total"] = ppb_calculator.sum(axis=1)
    for year in ppb_calculator.index:
      ppb_calculator.loc[year, "PPB"] = ppb_calculator.loc[year, "Total"] / (16.04 * 1.8 * 10**5)
    ppb_calculator.name = "ch4_ppb_calculator"
    return ppb_calculator

  def to_dict(self):
    """Return all fields as a dict, to be serialized to JSON."""
    rs = dict()
    rs['ch4_tons_reduced'] = self.ch4_tons_reduced()
    rs['ch4_ppb_calculator'] = self.ch4_ppb_calculator()
    return rs
