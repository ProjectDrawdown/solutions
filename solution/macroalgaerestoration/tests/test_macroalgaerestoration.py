from os import path
import json

from solution.macroalgaerestoration.macroalgaerestoration_solution import MacroalgaeRestorationSolution
solution = MacroalgaeRestorationSolution()
scenarios_to_test = solution.get_scenario_names()

print('Here are the scenarios to test:', scenarios_to_test)

results_file = path.join('solution','macroalgaerestoration', 'tests', 'expected_results.json')
stream = open(results_file,'r')
results = json.load(stream)

from tools.tests.test_ocean_solution  import TestOceanSolution

def pytest_generate_tests(metafunc):
    argkeys = ['solution', 'scenario_name', 'expected_results']
    argvals = []
    
    scenario_names = scenarios_to_test
    for scenario_name in scenario_names:
        argvals.append([solution,scenario_name,results[scenario_name]])

    metafunc.parametrize(argkeys, argvals, scope="class")
