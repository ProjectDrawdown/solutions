""" Helper script for solution generation """

import os
import pathlib
from tools import solution_xls_extract, vma_xls_extract


def make_dirs(dir_name):
    outputdir = str(pathlib.Path(__file__).parents[0].joinpath(dir_name))
    os.mkdir(outputdir)
    os.mkdir(os.path.join(outputdir, 'testdata'))

def make_soln_files(dir_name, class_name):
    outputdir = str(pathlib.Path(__file__).parents[0].joinpath(dir_name))
    xls_name = \
    [f for f in os.listdir(os.path.join(outputdir, 'testdata')) if not f.startswith('~') and f.endswith('xlsm')][0]
    solution_xls_extract.output_solution_python_file(outputdir, os.path.join(outputdir, 'testdata', xls_name),
                                                     class_name)


    # to copy + paste into test_solutions
    print("""
def test_{0}():
  scenario = list({0}.scenarios.keys())[0]
  obj = {0}.{1}(scenario=scenario)
  assert obj.scenario == scenario
  assert obj.name""".format(dir_name, class_name))

    print('\n')

    # to copy + paste into test_excel_integration
    print("""
@pytest.mark.integration
@pytest.mark.parametrize('start_excel',
    [str(solutiondir.joinpath('{0}', 'testdata', '{2}'))],
    indirect=True)
def test_{1}_LAND(start_excel, tmpdir):
  \"\"\"Test for Excel model file {2}.\"\"\"
  workbook = start_excel
  for scenario in {0}.scenarios.keys():
    obj = {0}.{1}(scenario=scenario)
    verify = LAND_solution_verify_list(obj)
    check_excel_against_object(obj=obj, workbook=workbook, scenario=scenario, verify=verify)""".format(
        dir_name, class_name, xls_name))

if __name__ == '__main__':
    dir_name = 'tropicaltreestaples'
    class_name = 'TropicalTreeStaples'

    # make_dirs(dir_name)
    #
    # print('Copy xls into testdata and make edits.\n '
    #       'See: https://docs.google.com/document/d/1OiKg3_OOGjYOUdnHTQuZggsko5n31qv_YV4h77E3LHk/edit')
    # input('Press enter to continue after this is done...')

    make_soln_files(dir_name, class_name)

