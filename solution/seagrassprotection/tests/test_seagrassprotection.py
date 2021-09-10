from os import path
import json

from _pytest import mark
from solution.seagrassprotection.seagrassprotection_solution import SeagrassProtectionSolution
solution = SeagrassProtectionSolution()
scenarios_to_test = solution.get_scenario_names()

results_file = path.join('solution','seagrassprotection', 'tests', 'scenario_results.json')
stream = open(results_file,'r')
results = json.load(stream)

from tools.test_ocean_solution  import TestOceanSolution

def pytest_generate_tests(metafunc):
    argkeys = ['solution', 'scenario_name', 'scenario_results']
    argvals = []
    
    scenario_names = scenarios_to_test
    for scenario_name in scenario_names:
        argvals.append([solution,scenario_name,results[scenario_name]])

    metafunc.parametrize(argkeys, argvals, scope="class")
