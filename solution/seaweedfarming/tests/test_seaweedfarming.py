from os import path
import json

from solution.seaweedfarming.seaweedfarming_solution import SeaweedFarmingSolution
solution = SeaweedFarmingSolution()
scenarios_to_test = solution.get_scenario_names()

results_file = path.join('solution','seaweedfarming', 'tests', 'expected_results.json')
stream = open(results_file,'r')
results = json.load(stream)

from tools.test_ocean_solution  import TestOceanSolution, TestOceanSolutionFinancialResults

def pytest_generate_tests(metafunc):
    argkeys = ['solution', 'scenario_name', 'expected_results']
    argvals = []
    
    scenario_names = scenarios_to_test
    for scenario_name in scenario_names:
        if scenario_name in results.keys():
            argvals.append([solution,scenario_name,results[scenario_name]])
        else:
            msg = f'scenario {scenario_name} not found in {results_file}'
            raise ValueError(msg)

    metafunc.parametrize(argkeys, argvals, scope="class")
