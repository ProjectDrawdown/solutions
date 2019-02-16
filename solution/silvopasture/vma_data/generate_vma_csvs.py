import pathlib
from tools.vma_xls_extract import VMAReader

soln_dir = pathlib.Path(__file__).parents[1]

vma_r = VMAReader(soln_dir.joinpath('testdata', 'Silvopasture_L-Use_v1.1a_3Aug18.xlsm'))
vma_r.read_xls(csv_path=soln_dir.joinpath('vma_data'))
