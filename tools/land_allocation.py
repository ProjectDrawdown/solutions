import os
import pathlib
import pandas as pd

from model.aez import AEZ
from model.dd import THERMAL_MOISTURE_REGIMES, MAIN_REGIONS, AEZ_LAND_COVER_MAP
from tools.util import to_filename, get_full_soln_name

pd.set_option('display.expand_frame_repr', False)
datadir = pathlib.Path(__file__).parents[1].joinpath('data')


def get_full_soln_name(soln_name):
    """ Returns full name of solution when given the module name.
        e.g. 'tropicalforests'  -->  'Tropical Forests' """
    solns_csv = pathlib.Path(__file__).parents[1].joinpath('data', 'overview', 'solutions.csv')
    # remove leading spaces
    solns_df = pd.read_csv(solns_csv).apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
    # there are some exceptions
    exceptions = {'riceintensification': 'SRI', 'indigenouspeoplesland': 'IP Forest Management',
                  'peatlands': 'Peatland Protection', 'improvedrice': 'Improved Rice',
                  'tropicalforests': 'Tropical Forest Restoration', 'perennialbioenergy': 'Perennial Bioenergy Crops',
                  'tropicaltreestaples': 'Tropical Tree Staples'}
    if soln_name in exceptions.keys():
        return exceptions[soln_name]
    else:
        return solns_df[solns_df[' DirName'] == soln_name]['Solution'].values[0]


def get_tla_regime_and_region():
    """ Returns total land area df (rows = regions, columns = regimes) """
    total_land_dict = {}
    for tmr in THERMAL_MOISTURE_REGIMES:
        df = pd.read_csv(datadir.joinpath('land', 'world', to_filename(tmr) + '.csv'), index_col=0).iloc[
            :5, 0] / 10000
        total_land_dict[tmr] = df
    return pd.DataFrame(total_land_dict)


def get_tla_regime_and_aez(region=None):
    """ Returns total land area df (rows = regimes, columns = AEZs) """
    total_land_dict = {}
    for tmr in THERMAL_MOISTURE_REGIMES:
        df = pd.read_csv(datadir.joinpath('land', 'world', to_filename(tmr) + '.csv'), index_col=0).iloc[:5, 1:]
        if region is not None:
            df = df.loc[region, :] / 10000
        else:
            df = df.sum(axis=0) / 10000
        total_land_dict[tmr] = df
    return pd.DataFrame(total_land_dict).T


def total_land_array(compress_aezs=False):
    """
    Note: currently not used
    Build 3-D DataArray from World land data. Dimensions are:
    - region (the 5 main world regions)
    - aez (29 AEZ types)
    - tmr (6 Thermal Moisture Regimes)
    """
    import xarray as xr
    tmr_list = []
    for tmr in THERMAL_MOISTURE_REGIMES:
        df = pd.read_csv(datadir.joinpath('land', 'world', to_filename(tmr) + '.csv'), index_col=0).loc[
            MAIN_REGIONS, :].iloc[:, 1:] / 10000
        if compress_aezs:
            for land_cover, aez_codes in AEZ_LAND_COVER_MAP.items():
                df[land_cover] = df.loc[:, aez_codes].sum(axis=1)
                df.drop(columns=aez_codes, inplace=True)
            df.drop(columns=['AEZ29: All Barren Land'], inplace=True)
            print(df)
        tmr_list.append(xr.DataArray(df, dims=['region', 'aez']))
    array = xr.concat(tmr_list, dim=pd.Index(THERMAL_MOISTURE_REGIMES, name='tmr'))
    return array


def get_max_adoption_per_region(soln, match_regions_to_world=False):
    """
    Finds max adoption value for each region from every dataset included in CustomAdoption
    Args:
        soln: Solution class
        match_regions_to_world: Adjust regional values so main regions sum to World while maintaining
                                their relative ratios.

    Returns: Series of max values with regions as index
    """
    max_vals = None
    for scen in soln.pds_ca.scenarios.values():
        if scen['include']:
            if max_vals is None:
                max_vals = scen['df'].max(axis=0)
            else:
                max_vals = max_vals.combine(scen['df'].max(axis=0), max)
    if match_regions_to_world:
        max_vals[MAIN_REGIONS] = max_vals[MAIN_REGIONS] * max_vals['World'] / max_vals[MAIN_REGIONS].sum()
    return max_vals.fillna(0)


def allocate_region(tla, allocation_target, land_type_guide):
    """
    Allocates land to a region, attempting to meet a target adoption value.
    The user must supply a table of land types assigned to the solution. The algorithm will then try to
    allocate the solution evenly (or optionally to a user-specified ratio) amongst the land types.
    Args:
        tla: A DataFrame specifying the TLA for the region (rows: regimes, cols: AEZs)
        allocation_target: The target adoption area to allocate
        land_type_guide: A DataFrame of the same format as TLA, which specifies which combinations
            of regime and AEZ have been assigned to the solution. Land types that have not been assigned
            should have a value of 0, while those that have been assigned can specify a guide ratio for
            the algorithm to aim for.

            For example, consider a simplified land type guide table consisting of 4 AEZs and no regimes.

            To attempt to allocate land to AEZs 2-4 evenly, the guide values would be 0 for AEZ 1
            and 1 elsewhere:
            +-------+-------+-------+-------+
            | AEZ 1 | AEZ 2 | AEZ 3 | AEZ 4 |
            +-------+-------+-------+-------+
            |   0   |   1   |   1   |   1   |

            To attempt to allocate as much land to AEZ 4 as AEZ 2 and 3 combined, the guide values
            would look like this:
            +-------+-------+-------+-------+
            | AEZ 1 | AEZ 2 | AEZ 3 | AEZ 4 |
            +-------+-------+-------+-------+
            |   0   |  0.5  |  0.5  |   1   |

            Note these values are normalised so only the ratio between them matters - not the absolute values.

            With unlimited TLA the ratios will match the final allocation exactly, but when land types fill
            up out the algorithm will continue filling the remaining ones. This can potentially result in a
            final allocation spread that looks very different to the initial allocation guide.

    Returns:
        success_flag: True if the allocation target is met else False
        tla: The remaining TLA after allocation
        land_allocated: DataFrame of land allocated by land type (rows: regimes, cols: AEZs)
    """
    success_flag = False
    land_allocated = pd.DataFrame().reindex_like(land_type_guide).fillna(0)
    total_remaining_land = allocation_target
    for _ in range(10):
        # remove assigned land types where tla is already 0
        assigned_land_types_with_land_left = land_type_guide[tla > 0].fillna(0)
        if assigned_land_types_with_land_left.sum().sum() == 0:
            break

        # normalise assigned land type ratios so combined they add up to 1
        # if ratios are all 1, this will divide the allocated land evenly between them
        target_alloc_spread = assigned_land_types_with_land_left / assigned_land_types_with_land_left.sum().sum()
        land_to_allocate = target_alloc_spread * total_remaining_land

        tla -= land_to_allocate
        # this subtraction may result in negative tla values, indicating land we have failed to allocate
        # we sum these negative values to calculate how much land we have left to allocate
        total_remaining_land = -tla[tla < 0].sum().sum()

        # the land allocated in this iteration is thus land_to_allocate + the negative tla values
        land_allocated += land_to_allocate + tla[tla < 0].fillna(0)

        # we can now set the negative tla values to 0, denoting land types that have been totally filled
        tla[tla < 0] = 0
        if total_remaining_land == 0:
            success_flag = True
            break
    else:
        raise Exception('Cannot allocate land after 10 iterations. Potential issue in allocation algorithm')
    return success_flag, tla, land_allocated


def ranked_land_allocation(csv_dirname=None):
    """
    Allocates land solutions one by one, using a ranked order specified by the user.
    Solutions are assumed to require the maximum adoption area specified for each region across all included
    Custom Adoption scenarios, subject to scaling (sum of main regions is matched to World value).
    Allocation failures will not raise Exceptions, but will show up in the printout.
    This function is intended to be edited as needed. It may be useful to print or plot certain values
    during allocation.

    Args:
        csv_dirname: directory to save solution allocations and TLA remaining (stored in data/land/allocation/ranked).
                     Will create if it doesn't exist.
    """
    from tools.health.landsurvey import land_solutions_scenarios

    # We first allocate any solutions with fixed allocation values for AEZ, regime and region. These
    # values would probably not be created from scratch, but adapted from a previous iteration of
    # ranked allocation.
    solns_with_fixed_allocation = []

    # Remaining solutions are divided into those with regional data and those without.
    # Ones with specified regional data are allocated first.
    # Lists of solutions are ranked by priority of allocation (first gets highest priority).
    solns_with_reg_data = ['conservationagriculture', 'improvedrice', 'afforestation', 'bamboo', 'silvopasture',
                           'managedgrazing']
    solns_without_reg_data = ['indigenouspeoplesland', 'peatlands', 'tropicalforests', 'forestprotection',
                              'temperateforests', 'multistrataagroforestry', 'treeintercropping',
                              'riceintensification', 'farmlandrestoration', 'tropicaltreestaples',
                              'perennialbioenergy']

    # Add on solutions can share allocation with other solutions. They are included here for completeness.
    add_on_solns = ['irrigationefficiency', 'regenerativeagriculture', 'nutrientmanagement']

    num_dashes = 127  # number of dashes for divider lines in the printout
    print('Allocating solutions with fixed allocation...')
    regional_tlas = {}
    for reg in MAIN_REGIONS:
        # Start with the TLA of each region
        tla = get_tla_regime_and_aez(region=reg)
        for name in solns_with_fixed_allocation:
            # Here we would subtract the fixed allocation df for each region from its TLA.
            # As there are currently no fixed allocations stored for any solutions, this
            # code is empty for now.
            pass
        regional_tlas[reg] = tla
    print('Success - no solutions with fixed allocation\n')

    solution_allocation_results = {s: {} for s in solns_with_reg_data + solns_without_reg_data}
    print('Allocating solutions with regional data...')
    for reg in MAIN_REGIONS:
        print('-' * num_dashes + f'\n{reg}\n' + '-' * num_dashes)
        for name in solns_with_reg_data:
            print(f'Processing: {name}...', end=' ' * (30 - len(name)))
            constructor, _ = land_solutions_scenarios[name]
            soln = constructor()
            # Set target area to allocate based on max adoption value for this region
            # In the case where the sum of the max main region values is less than the max World value,
            # the regional values will be boosted so their sum is equal to the World value.
            target_regional_adoption = \
            get_max_adoption_per_region(soln, match_regions_to_world=True)[reg]

            if target_regional_adoption == 0:
                print('Success - no adoption forecasted for this region')
                continue
            success_flag, regional_tlas[reg], allocated =\
                allocate_region(tla=regional_tlas[reg],
                                allocation_target=target_regional_adoption,
                                land_type_guide=soln.ae.soln_land_alloc_df)
            if success_flag:
                print('Success')
            else:
                remainder = target_regional_adoption - allocated.sum().sum()
                print(f'Failed to meet allocation target. Land remaining: {remainder:.1f} Mha')

            if reg not in solution_allocation_results[name]:
                solution_allocation_results[name][reg] = allocated.copy(deep=True)
            else:
                solution_allocation_results[name][reg] += allocated

    print('-' * num_dashes + '\n\nAllocating solutions without regional data...')

    for name in solns_without_reg_data:
        print('\n' + '-' * num_dashes + f'\n{name}\n' + '-' * num_dashes)
        constructor, _ = land_solutions_scenarios[name]
        soln = constructor()

        # Set target area to allocate based on max adoption value for World region
        target_world_adoption = get_max_adoption_per_region(soln)['World']

        for i in range(1, 11):
            # Calculate the sum of land remaining per region for land types assigned to the solution
            total_assigned_land_remaining = pd.Series(index=MAIN_REGIONS)
            for reg in MAIN_REGIONS:
                total_assigned_land_remaining[reg] = regional_tlas[reg][soln.ae.soln_land_alloc_df > 0].fillna(
                    0).sum().sum()

            if total_assigned_land_remaining.sum() == 0:
                print(f'Failure - no assigned land left to allocate')
                break

            # Order the regions from least to most assigned land remaining for solution
            regions_ranked_by_remaining_land = total_assigned_land_remaining.sort_values(ascending=True).index.values

            # Allocate land to each region, starting with the region with the least remaining assigned land available
            for reg in regions_ranked_by_remaining_land:
                # Divide regional allocation in proportion to available assigned land
                # This ensures a good spread of regional adoption for each solution by preventing regions from
                # 'filling up' too early. If we wanted to use other criteria to guide regional allocation
                # for solutions without specified regional data, this is the part of the code to edit.
                regional_ratios = total_assigned_land_remaining / total_assigned_land_remaining.sum()

                # Calculate target adoption area for this region based on regional ratios
                target_regional_adoption = regional_ratios[reg] * target_world_adoption
                if target_regional_adoption < 0.1:
                    continue  # skip region if no assigned land left

                success_flag, regional_tlas[reg], allocated = \
                    allocate_region(tla=regional_tlas[reg],
                                    allocation_target=target_regional_adoption,
                                    land_type_guide=soln.ae.soln_land_alloc_df)

                land_remaining = target_regional_adoption - allocated.sum().sum()
                if not success_flag:
                    print(f'Allocation for {reg} failed to meet target of {target_regional_adoption:.1f} Mha. '
                          f'{land_remaining:.1f} Mha will be carried over to the remaining regions.')
                else:
                    assert land_remaining < 0.1, \
                        f'Error: success_flag is True but land remaining is nonzero ({land_remaining:.1f} Mha)'
                # Drop region from remaining land table now that it has been allocated
                total_assigned_land_remaining.drop(reg, inplace=True)

                # Generate new target adoption value
                target_world_adoption -= allocated.sum().sum()

                if reg not in solution_allocation_results[name]:
                    solution_allocation_results[name][reg] = allocated.copy(deep=True)
                else:
                    solution_allocation_results[name][reg] += allocated

            if target_world_adoption < 0.1:
                print('Success')
                break
            else:
                # Note: with regional allocation divided proportionally based on TLA remaining, there is
                # no benefit to iterating (if it fails first time it means no applicable land is left).
                # However, if the criteria for allocating to each region changes, we may want to try
                # multiple iterations.
                print(f'Failed to allocate all land on iteration {i}. Remaining: {target_world_adoption:.1f} Mha')
        else:
            raise Exception('Cannot allocate land after 10 iterations. Potential issue in allocation algorithm')

    print('\n' + '-' * num_dashes)
    tla_left = None
    for reg, tl in regional_tlas.items():
        if tla_left is None:
            tla_left = tl.copy(deep=True)
        else:
            tla_left += tl

    print('Total land area remaining')
    print(tla_left)
    print('-' * 200)

    if csv_dirname is not None:
        ranked_allocation_csv_path = datadir.joinpath('land', 'allocation', 'ranked', csv_dirname)
        if not os.path.exists(ranked_allocation_csv_path):
            os.mkdir(ranked_allocation_csv_path)
        for name in solution_allocation_results:
            solution_allocation_csv_path = ranked_allocation_csv_path.joinpath(name)
            if not os.path.exists(solution_allocation_csv_path):
                os.mkdir(solution_allocation_csv_path)
            for reg, tl in solution_allocation_results[name].items():
                tl.to_csv(solution_allocation_csv_path.joinpath(f'{to_filename(reg)}_allocation.csv'))

        tla_remaining_csv_path = ranked_allocation_csv_path.joinpath('tla_remaining')
        if not os.path.exists(tla_remaining_csv_path):
            os.mkdir(tla_remaining_csv_path)
        for reg, tl in regional_tlas.items():
            tl.to_csv(tla_remaining_csv_path.joinpath(f'{to_filename(reg)}_tla_remaining.csv'))
        tla_left.to_csv(tla_remaining_csv_path.joinpath('World_tla_remaining.csv'))

        ranked_order = pd.Series(solns_with_fixed_allocation + solns_with_reg_data + solns_without_reg_data)
        ranked_order.name = 'solutions in ranked order'
        ranked_order.to_csv(ranked_allocation_csv_path.joinpath('solution_order.csv'))


def plot_tla_remaining(alloc_name, reg=None):
    """
    Plots TLA remaining after land allocation, comparing results of the ranked allocation with
    the original DD allocation. Defaults to 'World' values, but can also plot individual regions.
    Args:
        alloc_name: dirname of ranked allocation run (e.g. initial_abatement_cost_run)
        reg: optional region name (e.g. 'OECD90')
    """
    import matplotlib.pyplot as plt
    csv_path = datadir.joinpath('land', 'allocation', 'ranked', alloc_name, 'tla_remaining')
    reg_tla_remaining = {r: pd.read_csv(
        csv_path.joinpath(f'{to_filename(r)}_tla_remaining.csv'), index_col=0) for r in ['World'] + MAIN_REGIONS}

    if reg is None:
        reg = 'World'
        tot_tla = get_tla_regime_and_aez()
    else:
        tot_tla = get_tla_regime_and_aez(reg)
    reg_df = reg_tla_remaining[reg]

    xlims = (0, tot_tla.iloc[:, :-1].sum(axis=0).max() * 1.1)
    fig, axes = plt.subplots(2, 2, figsize=(20, 10))

    plot_alloc(tot_tla, ax=axes[0, 0], title='TLA before allocation', xlims=xlims)

    path = datadir.joinpath('land', 'allocation', 'perc_land_remaining_after_allocation.csv')
    perc_tla_left_orig = pd.read_csv(path, index_col=0)
    tla_left_orig = tot_tla * perc_tla_left_orig / 100
    plot_alloc(tla_left_orig, ax=axes[0, 1], title='TLA remaining after original allocation', xlims=xlims)

    plot_alloc(reg_df, ax=axes[1, 0], title='TLA remaining after ranked allocation', xlims=xlims)

    diff = reg_df - tla_left_orig
    neg_xlim = diff.iloc[:, :-1][diff.iloc[:, :-1] < 0].sum(axis=0).min() * 1.1
    plot_alloc(diff, ax=axes[1, 1], title='TLA remaining (ranked - original)', xlims=(neg_xlim, xlims[1]))
    plt.axvline(0, color='black', linewidth=0.5, alpha=0.5)

    fig.suptitle(f'Allocation results for {reg}', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


def plot_solution_allocation(soln_name, alloc_name):
    """
    Plots land allocation charts for a given solution, comparing results of the ranked allocation
    with the original DD allocation.
    Args:
        soln_name: Solution dirname (e.g. 'tropicalforests')
        alloc_name: dirname of ranked allocation run (e.g. initial_abatement_cost_run)
    """
    import matplotlib.pyplot as plt
    fullname = get_full_soln_name(soln_name)
    orig_assigned_land = AEZ(fullname).soln_land_alloc_df

    csv_path = datadir.joinpath('land', 'allocation', 'ranked', alloc_name, soln_name)
    regional_allocations = {}
    orig_regional_allocations = {}
    soln_regional_df = pd.DataFrame()
    orig_soln_regional_df = pd.DataFrame()
    for reg in MAIN_REGIONS:
        try:
            regional_allocations[reg] = pd.read_csv(csv_path.joinpath(f'{to_filename(reg)}_allocation.csv'),
                                                    index_col=0)
        except FileNotFoundError:
            print(f'No allocation data for {reg}')
            continue
        orig_regional_allocations[reg] = get_tla_regime_and_aez(reg) * orig_assigned_land
        if 'World' not in regional_allocations:
            regional_allocations['World'] = regional_allocations[reg].copy(deep=True)
            orig_regional_allocations['World'] = get_tla_regime_and_aez() * orig_assigned_land
        else:
            regional_allocations['World'] += regional_allocations[reg]
        soln_regional_df[reg] = regional_allocations[reg].sum(axis=1)
        orig_soln_regional_df[reg] = orig_regional_allocations[reg].sum(axis=1)

    fig, axes = plt.subplots(2, 2, figsize=(15, 11))

    max_lim = max(regional_allocations['World'].sum(axis=0).max(),
                  orig_regional_allocations['World'].sum(axis=0).max()) * 1.1
    plot_alloc(regional_allocations['World'], ax=axes[1, 0], title='Allocation by AEZ (ranked)', xlims=(0, max_lim))
    plot_alloc(orig_regional_allocations['World'], ax=axes[0, 0], title='Allocation by AEZ (original)',
               xlims=(0, max_lim))

    max_lim = max(soln_regional_df.sum(axis=0).max(), orig_soln_regional_df.sum(axis=0).max()) * 1.1
    plot_alloc(soln_regional_df, ax=axes[1, 1], title='Allocation by region (ranked)', xlims=(0, max_lim))
    plot_alloc(orig_soln_regional_df, ax=axes[0, 1], title='Allocation by region (original)', xlims=(0, max_lim))

    pd.options.display.float_format = '{:.1f}'.format

    fig.suptitle(f'Land allocation breakdown for {fullname}', fontsize=20)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


def plot_alloc(df, ax=None, title=None, regimes_subset=None, y_subset=None, xlims=None):
    """
    Plot a land allocation DataFrame as a horizontal stacked bar chart.
    Args:
        df: DataFrame (rows=regimes, cols=AEZs or regions)
        ax: matplotlib Axis (for subplotting)
        title: title of plot
        regimes_subset: subset of regimes to include in plot (list of regime strings)
        y_subset: subset of AEZs or regions (depends on input df) to include in plot (list of strings)
        xlims: limits of x-axis (tuple)
    """
    import matplotlib.pyplot as plt
    if ax is None:
        fig, (ax) = plt.subplots(1, 1, figsize=(18, 9))
    if regimes_subset is None:
        regimes_subset = slice(None)
    if y_subset is None:
        y_subset = slice(None)

    if 'AEZ29: All Barren Land' in df.columns:
        df = df.drop(columns=['AEZ29: All Barren Land'])

    df_to_plot = df.loc[regimes_subset, y_subset].iloc[:, ::-1].T
    if xlims is not None:
        ax.set_xlim(*xlims)
    ax = df_to_plot.plot(kind='barh', stacked=True, title=title, ax=ax, width=0.8)
    ax.set_xlabel('Land area (Mha)')


if __name__ == '__main__':
    # ranked_land_allocation(csv_dirname='matching_tla')

    # for s in ['riceintensification', 'forestprotection', 'indigenouspeoplesland', 'peatlands']:
    s = 'peatlands'
    # s = 'improvedrice'
    # plot_solution_allocation(s, 'matching_tla')
    # plot_tla_remaining('matching_tla')
