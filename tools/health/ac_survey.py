"""Survey scenarios from all solutions, outputting info to CSV.
"""
import dataclasses
import os.path
import tempfile

import pandas as pd

from model import advanced_controls as ac
import solution.factory

a = ac.AdvancedControls()
columns = []
for field in dataclasses.fields(a):
    columns.append(field.name)

results = pd.DataFrame(columns=columns, dtype='int')
results.index.name = 'Solution'
all_solutions_scenarios = solution.factory.all_solutions_scenarios()
for soln in all_solutions_scenarios.keys():
    constructor, scenarios = all_solutions_scenarios[soln]
    values = {}
    for scenario in scenarios:
        s = constructor(scenario)
        for field in columns:
            field_values = values.get(field, [])
            field_values.append(str(getattr(s.ac, field)))
            values[field] = field_values
    for field in columns:
        results.loc[soln, field] = len(set(values[field]))


(_, outfile) = tempfile.mkstemp(prefix='scenario_uniq_values_', suffix='.csv',
                                dir=os.path.join('data', 'health'))
outdata = results.to_csv(path_or_buf=outfile)

# print the file name on exit, allows the calling script to decide whether to check it in.
print(outfile)
