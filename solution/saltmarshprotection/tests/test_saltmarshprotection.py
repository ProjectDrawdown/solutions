

from os import path
import json

from solution.saltmarshprotection.saltmarshprotection_solution import SaltmarshProtectionSolution
solution = SaltmarshProtectionSolution()
scenarios_to_test = solution.get_scenario_names()

print('Here are the scenarios to test:', scenarios_to_test)

results_file = path.join('solution','saltmarshprotection', 'tests', 'scenario_results.json')
stream = open(results_file,'r')
results = json.load(stream)

from tools.test_ocean_solution  import TestOceanSolution, TestOceanSolutionProtectionResults

def pytest_generate_tests(metafunc):
    argkeys = ['solution', 'scenario_name', 'scenario_results']
    argvals = []
    
    scenario_names = scenarios_to_test
    for scenario_name in scenario_names:
        argvals.append([solution,scenario_name,results[scenario_name]])

    metafunc.parametrize(argkeys, argvals, scope="class")

