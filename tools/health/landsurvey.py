"""Survey all land solutions, outputting info about model health to CSV."""

import importlib
import pathlib
import tempfile
import numpy as np
import pandas as pd
import scipy.stats
from pprint import pprint

import solution.factory
from model.dd import THERMAL_MOISTURE_REGIMES
from tools.util import to_filename

datadir = pathlib.Path(__file__).parents[2].joinpath('data')

soln_df = pd.read_csv(datadir.joinpath('overview', 'solutions.csv'), index_col=0)
land_soln_names = soln_df[soln_df[' Sector'].isin([' Food', ' Land Use'])].dropna()[' DirName'].values
land_soln_names = [x.strip() for x in land_soln_names if x.strip() not in ['biochar', 'improvedcookstoves', 'composting']]
land_solutions_scenarios = {k: x for k, x in solution.factory.all_solutions_scenarios().items() if k in land_soln_names}


def adoption_basis():
    """ Which solutions use which adoption basis """
    pds_adoption_basis_counts = {
        'Linear': set(),
        'Existing Adoption Prognostications': set(),
        'Bass Diffusion S-Curve': set(),
        'Logistic S-Curve': set(),
        'Fully Customized PDS': set(),
        'Customized S-Curve Adoption': set()}

    for name in land_solutions_scenarios.keys():
        m = importlib.import_module('solution.'+name)
        for scenario in m.scenarios.values():
            pds_adoption_basis_counts[scenario.soln_pds_adoption_basis].add(name)
            assert scenario.seq_rate_global is not None, '{}'.format(name)

    return pds_adoption_basis_counts


def get_tla_per_regime():
    """ Total land area per regime """
    total_land_dict = {}
    for tmr in THERMAL_MOISTURE_REGIMES:
        df = pd.read_csv(datadir.joinpath('land', 'world', to_filename(tmr) + '.csv'), index_col=0).iloc[
            :5, 0] / 10000
        total_land_dict[tmr] = df

    return total_land_dict


def get_scenario_variables():
    """ See which variables change between scenarios"""
    vars_per_soln = {}
    total_var_dict = {}
    for name in land_solutions_scenarios.keys():
        m = importlib.import_module('solution.'+name)
        scenarios = list(m.scenarios.values())
        var_dict = {}
        for scenario in scenarios:
            for k, v in vars(scenario).items():
                if k in [None, 'vmas'] or type(v) not in [float, int, str]:
                    continue
                if k not in var_dict:
                    var_dict[k] = {v}
                else:
                    var_dict[k].add(v)
        vars_per_soln[name] = [var for var, vals in var_dict.items() if len(vals) > 1]
    for soln, var_list in vars_per_soln.items():
        for v in var_list:
            if v not in total_var_dict:
                total_var_dict[v] = [soln]
            else:
                total_var_dict[v].append(soln)
    return vars_per_soln, total_var_dict


def full_survey():
    """
    Runs all land solutions and extracts data to csv.
    Looks at 'High' (most aggressive) adoption scenario.
    Data recorded:
        - % of tla adopted
        - avg abatement cost
    """
    results = pd.DataFrame(columns=['% tla', 'avg abatement cost'])
    results.index.name = 'Solution'
    for name, (constructor, scenarios) in land_solutions_scenarios.items():
        print('processing: {}'.format(name))
        max_land = abatement_cost = 0
        high_scenario = [scen for scen in scenarios if 'high' in scen.lower()]
        if not high_scenario:
            high_scenario = scenarios  # do all scenarios if 'high' is not in any of their names
        for scenario in high_scenario:
            s = constructor(scenario)
            land_adopted = s.ht.soln_pds_funits_adopted().loc[:, 'World'].max()
            if land_adopted > max_land:
                max_land = land_adopted
                abatement_cost = avg_abatement_cost(s)
        perc_tla = 100 * max_land / s.tla_per_region.at[2050, 'World']
        results.at[name, '% tla'] = perc_tla
        results.at[name, 'avg abatement cost'] = abatement_cost
    results.to_csv(datadir.joinpath('health', 'landsurvey.csv'))
    return results


def avg_abatement_cost(soln):
    """
    A measure of the relative cost of reducing emissions using this solution over its lifetime,
    which equals the ratio of the Lifetime Cashflow NPV to the Total Emissions Reduction.
    Args:
        soln: a Land solution class

    Returns:
        Average abatement cost ($/tCO2)
    """
    npv = soln.oc.soln_net_present_value().loc[2020:2050].sum()
    seq = soln.c2.co2_sequestered_global().loc[2020:2050, 'All'].sum()
    red = soln.c2.co2eq_mmt_reduced().loc[2020:2050, 'World'].sum()
    abatement = (seq + red) / 1000
    abatement_cost = -npv / (abatement * 1e9)
    return abatement_cost


if __name__ == '__main__':
    # res = adoption_basis()
    # res = get_scenario_variables()
    res = full_survey()
    # pprint(res[1])

    # print(res.sort_values(by=['% tla'], ascending=False))

