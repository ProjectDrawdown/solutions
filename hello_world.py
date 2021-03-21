import solution.factory
solutions = solution.factory.all_solutions_scenarios()
obj = solutions["solarpvutil"][0](scenario='PDS-25p2050-Optimum2020')
print( obj.c2.co2_mmt_reduced())
