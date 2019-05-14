""" Helper script for solution generation """

import glob
import os
import pathlib
from tools import solution_xls_extract, vma_xls_extract


def make_soln_files(dir_name, class_name):
    outputdir = str(pathlib.Path(__file__).parents[1].joinpath('solution', dir_name))
    xls_name = glob.glob(os.path.join(outputdir, 'testdata', '[!~]*.xlsm'))[0]
    solution_xls_extract.output_solution_python_file(outputdir=outputdir,
            xl_filename=xls_name, classname=class_name)

    # to copy + paste into factory
    print("""
everything['{0}'] = ({0}.{1}, list({0}.scenarios.keys()))""".format(dir_name, class_name))
    print('\n')

    # to copy + paste into test_excel_integration
    stype = 'LAND' if 'BioS' in xls_name else 'RRS'
    print(f"""
@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('{dir_name}', 'testdata',
        '{xls_name}'))],
    indirect=True)
def test_{class_name}_{stype}(start_excel, tmpdir):
  workbook = start_excel
  for scenario in {dir_name}.scenarios.keys():
    obj = {dir_name}.{class_name}(scenario=scenario)
    verify = {stype}_solution_verify_list(obj, workbook)
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)""")


if __name__ == '__main__':
    dir_name = 'indigenouspeoplesland'
    class_name = 'IndigenousPeoplesLand'
    make_soln_files(dir_name, class_name)
