"""Total Addressible Market module calculations."""

import pandas as pd

class TAM:
  """Implementation for the Total Addressible Market module."""

  def __init__(self, ref_tam_per_region_filename, pds_tam_per_region_filename):
    super()
    self.ref_tam_per_region_filename = ref_tam_per_region_filename
    self.pds_tam_per_region_filename = pds_tam_per_region_filename

  def ref_tam_per_region(self):
    return pd.read_csv(self.ref_tam_per_region_filename, header=0, index_col=0,
        skipinitialspace=True)

  def pds_tam_per_region(self):
    return pd.read_csv(self.pds_tam_per_region_filename, header=0, index_col=0,
        skipinitialspace=True)
