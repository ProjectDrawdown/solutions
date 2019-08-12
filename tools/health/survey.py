"""Survey all solutions+scenarios, outputting info about model health to CSV.
"""
import os.path
import tempfile
import numpy as np
import pandas as pd
import scipy.stats
import solution.factory

def scenario_survey(outfile):
    results = pd.DataFrame(columns=['RegionalFractionTAM', 'RegionalFractionAdoption', 'Rvalue'])
    results.index.name = 'Solution'
    all_solutions_scenarios = solution.factory.all_solutions_scenarios()
    for soln in all_solutions_scenarios.keys():
        constructor, scenarios = all_solutions_scenarios[soln]
        for scenario in scenarios:
            s = constructor(scenario)
            name = f'{soln}:{scenario}'

            if hasattr(s, 'tm'):
                pds = s.tm.pds_tam_per_region()
                world = pds.loc[2050, 'World']
                regional_sum = pds.loc[2050, ['OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                                              'Middle East and Africa', 'Latin America']].sum()
                fraction = regional_sum / world if world else np.nan
                results.loc[name, 'RegionalFractionTAM'] = fraction
            else:
                results.loc[name, 'RegionalFractionTAM'] = np.nan

            pds = s.ht.soln_pds_funits_adopted()
            world = pds.loc[2050, 'World']
            regional_sum = pds.loc[2050, ['OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                                          'Middle East and Africa', 'Latin America']].sum()
            fraction = regional_sum / world if world else np.nan
            results.loc[name, 'RegionalFractionAdoption'] = fraction

            x = s.ht.soln_pds_funits_adopted().index
            y = s.ht.soln_pds_funits_adopted().loc[:, 'World'].values
            slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
            results.loc[name, 'Rvalue'] = r_value
    outdata = results.to_csv(path_or_buf=outfile)

if __name__ == '__main__':
    (_, outfile) = tempfile.mkstemp(prefix='survey_', suffix='.csv',
                                    dir=os.path.join('data', 'health'))
    scenario_survey(outfile)
    # print the file name on exit, allows the calling script to decide whether to check it in.
    print(outfile)
