""" Generates Custom Adoption CSV files from solution xls in testdata dir """

import pathlib
from tools.custom_adoption_xls_extract import CustomAdoptionReader

thisdir = pathlib.Path(__file__).parents[0]
xlsdir = pathlib.Path(__file__).parents[1].joinpath('testdata')

if __name__ == '__main__':
    ca_r = CustomAdoptionReader(xlsdir.joinpath('Silvopasture_L-Use_v1.1a_3Aug18.xlsm'), 'pds')
    ca_r.read_xls(csv_path=thisdir)
