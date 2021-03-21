import importlib

# Load an instance of the solarvputil solution
# This solution contains the code to compute all the results for all scenarios for this solution
solution_name = "solarpvutil"
solution = importlib.import_module('solution.'+solution_name)

# To see those results, compute them for a specific scenario.
# The scenarios supported for each solution are named in the 'ac' subdirectory of the solution, e.g.
# look in solutions/solarpvutil/ac
solution_data = solution.Scenario(scenario='PDS-25p2050-Optimum2020')

# There are lots of different datasets inside the solution object.
# You can see them in the __init__.py file for the solution you are working with.
print(solution_data.c2.co2_mmt_reduced())
