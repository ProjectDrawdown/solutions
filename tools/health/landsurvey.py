"""Survey all land solutions, outputting info about model health to CSV."""

import importlib
import pathlib
import pandas as pd
import xarray as xr

import solution.factory
from model.aez import AEZ

pd.set_option('display.expand_frame_repr', False)
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


def land_alloc_sum(solns=None, save_csv=False):
    """
    Sums land allocations for each TMR/AEZ type. Prints df of remaining %s.
    Args:
        solns: optional subset of solutions in the form of the
            land_solutions_scenarios dict: {name: (constructor, scenarios)}
    """
    add_on_solns = ['regenerativeagriculture', 'nutrientmanagement', 'irrigationefficiency']
    if solns is None:
        solns = land_solutions_scenarios
    df = None
    for name, (constructor, _) in solns.items():
        if name in add_on_solns:
            continue
        print('processing: {}'.format(name))
        s = constructor()
        if df is None:
            df = s.ae.soln_land_alloc_df
        else:
            df += s.ae.soln_land_alloc_df
    df *= 100
    df = 100 - df
    df[df < 0] = 0
    pd.options.display.float_format = '{:.1f}'.format
    print(df)
    if save_csv:
        df.to_csv(datadir.joinpath('land', 'allocation', 'perc_land_remaining_after_allocation.csv'))
    return df


def full_survey():
    """
    Runs all land solutions and extracts data to csv.
    Looks at 'High' (most aggressive) adoption scenario.
    Data recorded:
        - % of tla adopted
        - avg abatement cost
    """
    results = pd.DataFrame(
        columns=['% tla', '% world alloc', 'avg abatement cost', 'model type', 'has regional data',
                 'ca exceeds alloc', 'ca exceeds max tla', 'ca scen exceeds alloc count',
                 'ca scen exceeds max tla count', 'ca scen regions exceed world count',
                 'ca scen world exceeds regions count'])

    results.index.name = 'Solution'
    for name, (constructor, scenarios) in land_solutions_scenarios.items():
        print('processing: {}'.format(name))
        max_land = 0
        high_scenario = [scen for scen in scenarios if 'high' in scen.lower()]
        if not high_scenario:
            high_scenario = scenarios  # do all scenarios if 'high' is not in any of their names
        abatement_cost, alloc_check, max_tla_check = [], [], []
        for scenario in high_scenario:
            print(scenario)
            s = constructor(scenario)
            land_adopted = s.ht.soln_pds_funits_adopted().loc[:, 'World'].max()
            alloc_tla = s.tla_per_region
            max_tla = tla_with_no_regional_allocation(s)
            if land_adopted > max_land:
                max_land = land_adopted
                abatement_cost.append(avg_abatement_cost(s))

                ca = s.pds_ca.adoption_data_per_region()
                diff = (alloc_tla - ca).fillna(0)
                alloc_check.append(diff[diff < 0].any().any())
                diff = (max_tla - ca).fillna(0)
                max_tla_check.append(diff[diff < 0].any().any())

        alloc_report, _ = s.pds_ca.report(adoption_limits=alloc_tla)
        max_tla_report, _ = s.pds_ca.report(adoption_limits=max_tla)

        perc_tla = 100 * max_land / s.tla_per_region.at[2050, 'World']
        perc_world_alloc = 100 * s.tla_per_region.at[2050, 'World'] / get_total_world_area()

        if s.ua.pds_cumulative_degraded_land_protected()['World'].loc[2050] > 0:
            model_type = 'protect'
        elif s.ac.yield_coeff > 0:
            model_type = 'yield'
        else:
            model_type = 'core'
        results.at[name, '% tla'] = perc_tla
        results.at[name, '% world alloc'] = perc_world_alloc
        results.at[name, 'avg abatement cost'] = max(abatement_cost)
        results.at[name, 'model type'] = model_type
        results.at[name, 'has regional data'] = alloc_report.loc[:, 'Has regional data'].any()
        results.at[name, 'ca exceeds alloc'] = max(alloc_check)
        results.at[name, 'ca exceeds max tla'] = max(max_tla_check)
        results.at[name, 'ca scen exceeds alloc count'] = alloc_report.loc[:, 'Exceeds limits'].sum()
        results.at[name, 'ca scen exceeds max tla count'] = max_tla_report.loc[:, 'Exceeds limits'].sum()
        results.at[name, 'ca scen regions exceed world count'] = alloc_report.loc[
                                                                 :, 'Regions exceed world'].fillna(False).sum()
        results.at[name, 'ca scen world exceeds regions count'] = alloc_report.loc[
                                                                  :, 'World exceeds regions'].fillna(False).sum()

    results.to_csv(datadir.joinpath('health', 'landsurvey.csv'))
    return results


def aez_survey():
    """ Check whether applicability matrix is redundant when land is allocated to DD allocations """
    for name, (constructor, scenarios) in land_solutions_scenarios.items():
        print('processing: {}'.format(name))
        fullname = constructor().name
        ae = AEZ(solution_name=fullname, ignore_allocation=False)
        with_applicable_zones = ae.soln_land_dist_df
        ae.applicable_zones = ae.soln_land_alloc_df.columns.values  # all zones
        ae._populate_solution_land_distribution()
        without_applicable_zones = ae.soln_land_dist_df
        pd.testing.assert_frame_equal(with_applicable_zones, without_applicable_zones)


def tla_with_no_regional_allocation(soln):
    """
    The original DD model arbitrarily imposes the global land allocation %
    at the regional level. Currently the python model's tla_per_region is
    consistent with this.
    This function calculates a different tla_per_region, where the regions
    are only limited by their max applicable land area or the area allocated
    globally for the solution.
    Args:
        soln: solution class

    Returns: DataFrame with the same format as soln.tla_per_region

    """
    world_alloc = soln.ae.get_land_distribution().at['Global', 'All']
    max_tla = AEZ(soln.name, ignore_allocation=True).get_land_distribution()
    return max_tla.clip(upper=world_alloc)


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
    # res = full_survey()
    # aez_survey()
    res = land_alloc_sum(save_csv=True)
    # res = survey_regional_limits()

