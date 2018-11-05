"""Total Addressible Market module calculations."""

import os.path

import pandas as pd

class TAM:
  """Implementation for the Total Addressible Market module."""
  model_dir = os.path.dirname(__file__)
  solution_dir = os.path.join(os.path.dirname(model_dir), 'solution')

  def ref_tam_per_region(self):
    filename = os.path.join(self.solution_dir, 'solarpvutil_ref_tam_per_region.csv')
    return pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True)

  def pds_tam_per_region(self):
    filename = os.path.join(self.solution_dir, 'solarpvutil_pds_tam_per_region.csv')
    return pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True)
