"""Forest Protection solution model.
   Excel filename: Drawdown_RRS-BIOSEQProtect_Model_v1.1b_Forest_Protection_Mar2020.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls as ac
from model import aez
from model import ch4calcs
from model import co2calcs
from model import customadoption
from model import dd
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import operatingcost
from model import s_curve
from model import unitadoption
from model import vma
from model import tla
from solution import land

DATADIR = pathlib.Path(__file__).parents[2].joinpath('data')
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = {
    'Current Adoption': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Current_Adoption.csv"),
        use_weight=False),
    'CONVENTIONAL First Cost per Implementation Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION First Cost per Implementation Unit': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=None, use_weight=False),
    'Yield from CONVENTIONAL Practice': vma.VMA(
        filename=None, use_weight=False),
    'Yield Gain (% Increase from CONVENTIONAL to SOLUTION)': vma.VMA(
        filename=None, use_weight=False),
    'Average Electricty Used DEGRADED LAND': vma.VMA(
        filename=None, use_weight=False),
    'Energy Efficiency Factor UNDEGRADED LAND': vma.VMA(
        filename=None, use_weight=False),
    'ALTERNATIVE APPROACH Annual Energy Used UNDEGRADED LAND': vma.VMA(
        filename=None, use_weight=False),
    'Fuel Consumed on DEGRADED Land': vma.VMA(
        filename=None, use_weight=False),
    'Fuel Reduction Factor for UNDEGRADED Land': vma.VMA(
        filename=None, use_weight=False),
    't CO2-eq (Aggregate emissions) Reduced per Land Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "t_CO2_eq_Aggregate_emissions_Reduced_per_Land_Unit.csv"),
        use_weight=False),
    't CO2 Reduced per Land Unit': vma.VMA(
        filename=None, use_weight=False),
    't N2O-CO2-eq Reduced per Land Unit': vma.VMA(
        filename=None, use_weight=False),
    't CH4-CO2-eq Reduced per Land Unit': vma.VMA(
        filename=None, use_weight=False),
    'Indirect CO2-eq Emissions DEGRADED LAND': vma.VMA(
        filename=None, use_weight=False),
    'Indirect CO2-eq Emissions UNDEGRADED LAND': vma.VMA(
        filename=None, use_weight=False),
    'Sequestration Rates': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Sequestration_Rates.csv"),
        use_weight=False),
    'Growth Rate of Land Degradation': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Growth_Rate_of_Land_Degradation.csv"),
        use_weight=False),
    'Disturbance Rate': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Disturbance_Rate.csv"),
        use_weight=False),
    't C storage in Protected Landtype': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "t_C_storage_in_Protected_Landtype.csv"),
        use_weight=False),
    'Global Multipler for Regrowth': vma.VMA(
        filename=None, use_weight=False),
    'Tropical Multipler for Regrowth': vma.VMA(
        filename=None, use_weight=False),
    'Temperate Multiplier for Regrowth': vma.VMA(
        filename=None, use_weight=False),
    'Cost of avoided emission': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Cost_of_avoided_emission.csv"),
        use_weight=False),
    'Forest area with Forest Management Plan': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Forest_area_with_Forest_Management_Plan.csv"),
        use_weight=False),
    'Forest area with Forest Management Plan for Production': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Forest_area_with_Forest_Management_Plan_for_Production.csv"),
        use_weight=False),
    'Forest area with Forest Management Plan for Conservation': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Forest_area_with_Forest_Management_Plan_for_Conservation.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Forest Protection'
solution_category = ac.SOLUTION_CATEGORY.LAND

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)


class Scenario:
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category

    def __init__(self, scenario=None):
        if scenario is None:
            scenario = list(scenarios.keys())[0]
        self.scenario = scenario
        self.ac = scenarios[scenario]

        # TLA
        self.ae = aez.AEZ(solution_name=self.name, cohort=2020,
                regimes=dd.THERMAL_MOISTURE_REGIMES8)
        if self.ac.use_custom_tla and self.ac.custom_tla_fixed_value is not None:
            self.c_tla = tla.CustomTLA(fixed_value=self.ac.custom_tla_fixed_value)
            custom_world_vals = self.c_tla.get_world_values()
        elif self.ac.use_custom_tla:
            self.c_tla = tla.CustomTLA(filename=THISDIR.joinpath('custom_tla_data.csv'))
            custom_world_vals = self.c_tla.get_world_values()
        else:
            custom_world_vals = None
        self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution(),
            custom_world_values=custom_world_vals)

        adconfig_list = [
            ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
             'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
            ['trend', self.ac.soln_pds_adoption_prognostication_trend, 'Medium',
             'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
             'Medium', 'Medium', 'Medium'],
            ['growth', self.ac.soln_pds_adoption_prognostication_growth, 'NOTE',
             'NOTE', 'NOTE', 'NOTE', 'NOTE', 'NOTE',
             'NOTE', 'NOTE', 'NOTE'],
            ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0],
            dtype=np.object).set_index('param')
        ad_data_sources = {
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            main_includes_regional=True,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_columns = ['Year'] + dd.REGIONS
        ad_world_2018 = self.ac.ref_base_adoption['World']
        ad_2018 = pd.Series(self.ac.ref_base_adoption)
        tla_world_2050 = self.tla_per_region.loc[2050, 'World']

        degrade_rate_conservative = pd.Series(self.ac.degradation_rate, index=range(2014, 2061))

        degrade_rate_low = pd.Series(0, index=range(2014, 2061))
        degrade_rate_low.loc[2014] = self.ac.degradation_rate
        degrade_rate_low.loc[2020] = degrade_rate_low.loc[2014] / 2.0
        step = (degrade_rate_low.loc[2014] - degrade_rate_low.loc[2020]) / 6.0
        for year in range(2015, 2020):
            degrade_rate_low.loc[year] = degrade_rate_low.loc[2014] - ((year - 2014) * step)
        step = (degrade_rate_low.loc[2020] - degrade_rate_low.loc[2030]) / 10.0
        for year in range(2021, 2030):
            degrade_rate_low.loc[year] = degrade_rate_low.loc[2020] - ((year - 2020) * step)
        degrade_rate_low.loc[2030:] = 0.0

        # In Excel, the Custom PDS Scenarios tab columns AC:AF compute a limit on adoption
        # based on the amount of degraded land remaining. We compute the same limit here.
        def constrained_tla(rate):
            degrade_df = pd.DataFrame(0, index=range(2014, 2061), columns=[
                'Total undegraded land at the start of the year',
                'Degraded land at the end of the year',
                'Total undegraded land at the end of the year', 'Constrained TLA'])
            for year in range(2014, 2061):
                if year == 2014:
                    # Not a typo, Excel uses the 2018 base adoption number starting in 2014.
                    # We are bug-for-bug compatible here.
                    undeg_start = tla_world_2050 - ad_world_2018
                else:
                    last = degrade_df.loc[year-1, 'Constrained TLA']
                    undeg_start = last - ad_world_2018
                degrade_df.loc[year, 'Total undegraded land at the start of the year'] = undeg_start
                degraded_end = max(0, undeg_start * rate[year])
                degrade_df.loc[year, 'Degraded land at the end of the year'] = degraded_end
                degrade_df.loc[year, 'Total undegraded land at the end of the year'] = (
                        undeg_start - degraded_end)
                degrade_df.loc[year, 'Constrained TLA'] = (tla_world_2050 -
                        degrade_df['Degraded land at the end of the year'].sum())
            return degrade_df

        # Data Source 1
        ds1_growth_rate = 0.0197583057035311
        ds1_datapoints = pd.DataFrame(0.0, index=range(2012, 2061), columns=dd.REGIONS)
        ds1_datapoints.loc[2012:2018, 'World'] = ad_world_2018
        ds1_maximum = 1035.0
        for year in range(2019, 2061):
            rate = 1 + ds1_growth_rate
            newval = ds1_datapoints.loc[year-1, 'World'] * rate
            ds1_datapoints.loc[year, 'World'] = min(ds1_maximum, newval)

        # Data Source 2
        ds2_growth_rate = 0.0102232658124979
        ds2_datapoints = pd.DataFrame(0.0, index=range(2012, 2061), columns=dd.REGIONS)
        ds2_datapoints.loc[2012:2018, 'World'] = ad_world_2018
        ds2_maximum = 1016.0
        for year in range(2019, 2061):
            rate = 1 + ds2_growth_rate
            newval = ds2_datapoints.loc[year-1, 'World'] * rate
            ds2_datapoints.loc[year, 'World'] = min(ds2_maximum, newval)

        # Data Source 3
        ds3_growth_rate = 0.00550564152557609
        ds3_datapoints = pd.DataFrame(0.0, index=range(2012, 2061), columns=dd.REGIONS)
        ds3_datapoints.loc[2012:2018, 'World'] = ad_world_2018
        ds3_maximum = 998.0
        for year in range(2019, 2061):
            rate = 1 + ds3_growth_rate
            newval = ds3_datapoints.loc[year-1, 'World'] * rate
            ds3_datapoints.loc[year, 'World'] = min(ds3_maximum, newval)

        # Data Source 4
        ds4_growth_rate = 0.0197583057035311
        ds4_datapoints = pd.DataFrame(0.0, index=range(2012, 2061), columns=dd.REGIONS)
        ds4_datapoints.loc[2012:2018, 'World'] = ad_world_2018
        ds4_maximum = 1047.9
        for year in range(2019, 2061):
            rate = 1 + ds4_growth_rate
            newval = ds4_datapoints.loc[year-1, 'World'] * rate
            ds4_datapoints.loc[year, 'World'] = min(ds4_maximum, newval)

        # Data Source 5
        ds5_growth_rate = 0.0102232658124979
        ds5_datapoints = pd.DataFrame(0.0, index=range(2012, 2061), columns=dd.REGIONS)
        ds5_datapoints.loc[2012:2018, 'World'] = ad_world_2018
        ds5_maximum = 1046.8
        for year in range(2019, 2061):
            rate = 1 + ds5_growth_rate
            newval = ds5_datapoints.loc[year-1, 'World'] * rate
            ds5_datapoints.loc[year, 'World'] = min(ds5_maximum, newval)

        # Data Source 6
        ds6_growth_rate = 0.00550564152557609
        ds6_datapoints = pd.DataFrame(0.0, index=range(2012, 2061), columns=dd.REGIONS)
        ds6_datapoints.loc[2012:2018, 'World'] = ad_world_2018
        ds6_minimum = 1046.0
        for year in range(2019, 2061):
            rate = 1 + ds6_growth_rate
            newval = ds6_datapoints.loc[year-1, 'World'] * rate
            ds6_datapoints.loc[year, 'World'] = min(ds6_minimum, newval)

        # Data Source 7
        ds7_constrained = constrained_tla(rate=degrade_rate_conservative)
        ds7_constrained_2050 = ds7_constrained.loc[2050, 'Constrained TLA']
        ds7_datapoints = pd.DataFrame(columns=ca_pds_columns).set_index('Year')
        ds7_datapoints.loc[2014] = ad_2018
        ds7_datapoints.loc[2030] = (1.0 * ds7_constrained_2050)
        ds7_datapoints.loc[2050] = ds7_constrained_2050

        # Data Source 8
        ds8_datapoints = pd.DataFrame(columns=ca_pds_columns).set_index('Year')
        ds8_datapoints.loc[2014] = ad_2018
        ds8_datapoints.loc[2030] = (0.9 * ds7_constrained_2050)
        ds8_datapoints.loc[2050] = ds7_constrained_2050

        # Data Source 9
        ds9_constrained = constrained_tla(rate=degrade_rate_low)
        ds9_constrained_2050 = ds9_constrained.loc[2050, 'Constrained TLA']
        ds9_datapoints = pd.DataFrame(columns=ca_pds_columns).set_index('Year')
        ds9_datapoints.loc[2014] = ad_2018
        ds9_datapoints.loc[2030] = (1.0 * ds9_constrained_2050)
        ds9_datapoints.loc[2050] = ds9_constrained_2050

        # Data Source 10
        ds10_datapoints = pd.DataFrame(columns=ca_pds_columns).set_index('Year')
        ds10_datapoints.loc[2014] = ad_2018
        ds10_datapoints.loc[2030] = (0.9 * ds9_constrained_2050)
        ds10_datapoints.loc[2050] = ds9_constrained_2050

        ca_pds_data_sources = [
            {'name': 'High adoption and conservative degradation rate', 'include': True,
                'description': (
                    'The historical protected area evolution (1990-2015) in Morales-Hidalgo was '
                    'used to estimate three protected areas\' yearly increase rates: 1,98%; 1,02% '
                    'and 0,55% for the forest PA corresponding to 1990-2015, 2005- 2015 and '
                    '2010- 2015 respectively. This, coupled with the TLA\'s current degradation '
                    'rate of 0.31% result in scenarios 1, 2 and 3. The New York declaration on '
                    'Forests is used  to estimate an alternative degradation rate which starts '
                    'from 0.31% and linearly decreases to half its value in 2020 and then to '
                    'zero in 2030. The yearly increase rates from Morales- Hidalgo plus this '
                    'degradation rate result in scenarios 4, 5 and 6. '
                    ),
                'maximum': 1035.0, 'datapoints': ds1_datapoints},
            {'name': 'Medium adoption and conservative degradation rate', 'include': True,
                'description': (
                    'The historical protected area evolution (1990-2015) in Morales-Hidalgo was '
                    'used to estimate three protected areas yearly increase rates: 1,98%; 1,02% '
                    'and 0,55% for the forest PA corresponding to 1990-2015, 2005- 2015 and '
                    '2010- 2015 respectively. This, coupled with the TLA\'s current degradation '
                    'rate of 0.31% result in scenarios 1, 2 and 3. The New York declaration on '
                    'Forests is used  to estimate an alternative degradation rate which starts '
                    'from 0.31% and linearly decreases to half its value in 2020 and then to '
                    'zero in 2030. The yearly increase rates from Morales- Hidalgo plus this '
                    'degradation rate result in scenarios 4, 5 and 6. '
                    ),
                'maximum': 1016.0, 'datapoints': ds2_datapoints},
            {'name': 'Low adoption and conservative degradation rate', 'include': True,
                'description': (
                    'The historical protected area evolution (1990-2015) in Morales-Hidalgo was '
                    'used to estimate three protected areas yearly increase rates: 1,98%; 1,02% '
                    'and 0,55% for the forest PA corresponding to 1990-2015, 2005- 2015 and '
                    '2010- 2015 respectively. This, coupled with the TLA\'s current degradation '
                    'rate of 0.31% result in scenarios 1, 2 and 3. The New York declaration on '
                    'Forests is used  to estimate an alternative degradation rate which starts '
                    'from 0.31% and linearly decreases to half its value in 2020 and then to '
                    'zero in 2030. The yearly increase rates from Morales- Hidalgo plus this '
                    'degradation rate result in scenarios 4, 5 and 6. '
                    ),
                'maximum': 998.0, 'datapoints': ds3_datapoints},
            {'name': 'High adoption and low degradation rate', 'include': True,
                'description': (
                    'The historical protected area evolution (1990-2015) in Morales-Hidalgo was '
                    'used to estimate three protected areas yearly increase rates: 1,98%; 1,02% '
                    'and 0,55% for the forest PA corresponding to 1990-2015, 2005- 2015 and '
                    '2010- 2015 respectively. This, coupled with the TLA\'s current degradation '
                    'rate of 0.31% result in scenarios 1, 2 and 3. The New York declaration on '
                    'Forests is used  to estimate an alternative degradation rate which starts '
                    'from 0.31% and linearly decreases to half its value in 2020 and then to '
                    'zero in 2030. The yearly increase rates from Morales- Hidalgo plus this '
                    'degradation rate result in scenarios 4, 5 and 6. '
                    ),
                'maximum': 1047.9, 'datapoints': ds4_datapoints},
            {'name': 'Medium adoption and low degradation rate', 'include': True,
                'description': (
                    'The historical protected area evolution (1990-2015) in Morales-Hidalgo was '
                    'used to estimate three protected areas\' yearly increase rates: 1,98%; 1,02% '
                    'and 0,55% for the forest PA corresponding to 1990-2015, 2005- 2015 and '
                    '2010- 2015 respectively. This, coupled with the TLA\'s current degradation '
                    'rate of 0.31% result in scenarios 1, 2 and 3. The New York declaration on '
                    'Forests is used  to estimate an alternative degradation rate which starts '
                    'from 0.31% and linearly decreases to half its value in 2020 and then to '
                    'zero in 2030. The yearly increase rates from Morales- Hidalgo plus this '
                    'degradation rate result in scenarios 4, 5 and 6. '
                    ),
                'maximum': 1046.8, 'datapoints': ds5_datapoints},
            {'name': 'Low adoption and low degradation rate', 'include': True,
                'description': (
                    'The historical protected area evolution (1990-2015) in Morales-Hidalgo was '
                    'used to estimate three protected areas\' yearly increase rates: 1,98%; 1,02% '
                    'and 0,55% for the forest PA corresponding to 1990-2015, 2005- 2015 and '
                    '2010- 2015 respectively. This, coupled with the TLA\'s current degradation '
                    'rate of 0.31% result in scenarios 1, 2 and 3. The New York declaration on '
                    'Forests is used  to estimate an alternative degradation rate which starts '
                    'from 0.31% and linearly decreases to half its value in 2020 and then to '
                    'zero in 2030. The yearly increase rates from Morales- Hidalgo plus this '
                    'degradation rate result in scenarios 4, 5 and 6. '
                    ),
                'maximum': 1046, 'datapoints': ds6_datapoints},
            {'name': '100% conservative degradation TLA in 2030', 'include': True,
                'description': (
                    'Linear increase up to 100% of TLA value in 2030 (calculated with the '
                    'conservative degradation rate) and TLA value from then onwards '
                    ),
                'maximum': ds7_constrained_2050, 'datapoints': ds7_datapoints},
            {'name': '90% conservative degradation TLA in 2030', 'include': True,
                'description': (
                    'Linear increase up to 90% of TLA value in 2030 (calculated with the '
                    'conservative degradation rate) and then linear increase to 100% TLA value '
                    'in 2050 from then onwards '
                    ),
                'maximum': ds7_constrained_2050, 'datapoints': ds8_datapoints},
            {'name': '100% low degradation TLA by 2030', 'include': True,
                'description': (
                    'Linear increase up to 100% of TLA value in 2030 (calculated with the low '
                    'degradation rate) and TLA value from then onwards '
                    ),
                'maximum': ds9_constrained_2050, 'datapoints': ds9_datapoints},
            {'name': '90% low degradation TLA by 2030', 'include': True,
                'description': (
                    'Linear increase up to 90% of TLA value in 2030 (calculated with the low '
                    'degradation rate) and TLA value from then onwards '
                    ),
                'maximum': ds9_constrained_2050, 'datapoints': ds10_datapoints},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=self.ac.soln_pds_adoption_custom_high_sd_mult,
            low_sd_mult=self.ac.soln_pds_adoption_custom_low_sd_mult,
            total_adoption_limit=self.tla_per_region)

        for s in self.pds_ca.scenarios.values():
            df = s['df']
            df.loc[2014:2018, 'World'] = 651.0

        ref_adoption_data_per_region = None

        if False:
            # One may wonder why this is here. This file was code generated.
            # This 'if False' allows subsequent conditions to all be elif.
            pass
        elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
            pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
            pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
            pds_adoption_is_single_source = None
        elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
            pds_adoption_data_per_region = self.ad.adoption_data_per_region()
            pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()
            pds_adoption_is_single_source = self.ad.adoption_is_single_source()

        ht_ref_adoption_initial = pd.Series(
            list(self.ac.ref_base_adoption.values()), index=dd.REGIONS)
        ht_ref_adoption_final = self.tla_per_region.loc[2050] * (ht_ref_adoption_initial /
            self.tla_per_region.loc[2014])
        ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_ref_datapoints.loc[2018] = ht_ref_adoption_initial
        ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
        ht_pds_adoption_initial = ht_ref_adoption_initial
        ht_pds_adoption_final_percentage = pd.Series(
            list(self.ac.pds_adoption_final_percentage.values()),
            index=list(self.ac.pds_adoption_final_percentage.keys()))
        ht_pds_adoption_final = ht_pds_adoption_final_percentage * self.tla_per_region.loc[2050]
        ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_pds_datapoints.loc[2018] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
        self.ht = helpertables.HelperTables(ac=self.ac,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=self.tla_per_region, pds_adoption_limits=self.tla_per_region,
            use_first_pds_datapoint_main=True,
            adoption_base_year=2018,
            copy_pds_to_ref=True,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=self.tla_per_region,
            pds_total_adoption_units=self.tla_per_region,
            electricity_unit_factor=1000000.0,
            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
            bug_cfunits_double_count=False)
        soln_pds_tot_iunits_reqd = self.ua.soln_pds_tot_iunits_reqd()
        soln_ref_tot_iunits_reqd = self.ua.soln_ref_tot_iunits_reqd()
        conv_ref_tot_iunits = self.ua.conv_ref_tot_iunits()
        soln_net_annual_funits_adopted=self.ua.soln_net_annual_funits_adopted()

        self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=2,
            ref_learning_increase_mult=2, conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
            soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
            conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
            conv_ref_first_cost_uses_tot_units=True,
            fc_convert_iunit_factor=land.MHA_TO_HA)

        self.oc = operatingcost.OperatingCost(ac=self.ac,
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_annual_tot_iunits=self.ua.conv_ref_annual_tot_iunits(),
            soln_pds_annual_world_first_cost=self.fc.soln_pds_annual_world_first_cost(),
            soln_ref_annual_world_first_cost=self.fc.soln_ref_annual_world_first_cost(),
            conv_ref_annual_world_first_cost=self.fc.conv_ref_annual_world_first_cost(),
            single_iunit_purchase_year=2017,
            soln_pds_install_cost_per_iunit=self.fc.soln_pds_install_cost_per_iunit(),
            conv_ref_install_cost_per_iunit=self.fc.conv_ref_install_cost_per_iunit(),
            conversion_factor=land.MHA_TO_HA)

        self.c4 = ch4calcs.CH4Calcs(ac=self.ac,
            soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

        self.c2 = co2calcs.CO2Calcs(ac=self.ac,
            ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
            soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),
            soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),
            soln_pds_direct_co2eq_emissions_saved=self.ua.direct_co2eq_emissions_saved_land(),
            soln_pds_direct_co2_emissions_saved=self.ua.direct_co2_emissions_saved_land(),
            soln_pds_direct_n2o_co2_emissions_saved=self.ua.direct_n2o_co2_emissions_saved_land(),
            soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),
            soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
            soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
            conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
            conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
            conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            tot_red_in_deg_land=self.ua.cumulative_reduction_in_total_degraded_land(),
            pds_protected_deg_land=self.ua.pds_cumulative_degraded_land_protected(),
            ref_protected_deg_land=self.ua.ref_cumulative_degraded_land_protected(),
            regime_distribution=self.ae.get_land_distribution(),
            regimes=dd.THERMAL_MOISTURE_REGIMES8)

