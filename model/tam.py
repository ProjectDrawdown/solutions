"""Total Addressible Market module calculations."""

import os.path

import pandas as pd

class TAM:
  """Implementation for the Total Addressible Market module. """
  csv_files_dir = os.path.dirname(__file__)

  def ref_tam_per_region(self):
    filename = os.path.join(self.csv_files_dir, 'tam_ref_tam_per_region.csv')
    return pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True)

  def pds_tam_per_region(self):
    filename = os.path.join(self.csv_files_dir, 'tam_pds_tam_per_region.csv')
    return pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True)
