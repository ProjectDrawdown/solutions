"""Regenerative Agriculture solution model.
   Excel filename: Drawdown_RRS-BIOSEQAgri_Model_v1.1_Regenerative_Agriculture_Mar 2020.xlsm
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
from model import scenario
from model import unitadoption
from model import vma
from model import tla
from model import conversions

DATADIR = pathlib.Path(__file__).parents[2].joinpath('data')
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = vma.VMA.load_vma_directory(THISDIR/'vma_data/vma_sources.json')

units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Regenerative Agriculture'
solution_category = ac.SOLUTION_CATEGORY.LAND

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS-32p2050-Plausible-customPDS-29Jan2020"
PDS2 = "PDS-47p2050-Drawdown-customPDS-high-29Jan2020"
PDS3 = "PDS-62p2050-Optimum-PDSCustom-max-Nov2019"

class Scenario(scenario.LandScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category
    module_name = THISDIR.stem

    def __init__(self, scen=None):
        # AC
        self.initialize_ac(scen, scenarios, PDS2)

        # TLA
        self.ae = aez.AEZ(solution_name=self.name, cohort=2020,
                regimes=dd.THERMAL_MOISTURE_REGIMES8)
        self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())

        # ADOPTION
        self._ref_ca_sources = scenario.load_sources(THISDIR/'ca_ref_data'/'ca_ref_sources.json', 'filename')
        self._pds_ad_sources = scenario.load_sources(THISDIR/'ad'/'ad_sources.json', '*')

        # Do the initialization ourself b/c we use it in the custom PDS initialization below
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=self._pds_ad_sources,
            main_includes_regional=True,
            adconfig=adoptiondata.make_adoption_config(overrides=[
                ('trend','World',self.ac.soln_pds_adoption_prognostication_trend),
                ('growth','World',self.ac.soln_pds_adoption_prognostication_growth)]))

        # Custom PDS Data
        ca_pds_columns = ['Year'] + dd.REGIONS
        tla_2050 = self.tla_per_region.loc[2050]
        world_2014 = self.tla_per_region.loc[2014, 'World']
        ad_2018 = list(self.ac.ref_base_adoption.values())

        # % smallholder area, based on updates to smallholder area VMA sheet
        # (34.1% was estimated in Book Ed1)
        smallholder_pct = 0.315909724971454

        # Maximum technical potential adoption area available for conservation agriculture,
        # based on % large farmers  (Note: not a typo, we're accounting for leftover
        # Conservation Agriculture land here)
        max_adoption = smallholder_pct * world_2014

        def _get_datapoints(percent, extra=0.0):
            w = self.tla_per_region.loc[2014, 'World']
            dp = [0.0,  # World is the sum of the regions.
                  ((percent['OECD90'] + extra) * self.tla_per_region.loc[2050, 'OECD90']),
                  ((percent['Eastern Europe'] + extra) *
                      self.tla_per_region.loc[2050, 'Eastern Europe']),
                  ((percent['Asia (Sans Japan)'] + extra) *
                      self.tla_per_region.loc[2050, 'Asia (Sans Japan)']),
                  ((percent['Middle East and Africa'] + extra) *
                      self.tla_per_region.loc[2050, 'Middle East and Africa']),
                  ((percent['Latin America'] + extra) *
                      self.tla_per_region.loc[2050, 'Latin America']),
                  0.0, 0.0, 0.0, 0.0]  # China, India, USA, EU
            dp[0] = sum(dp)
            return dp

        # Data Source 1
        lin = 'Willer 2018 SEI calc RA lin'
        ds1_percent = {
                'OECD90': self.ad.adoption_sources(region='OECD90').loc[2050, lin] / world_2014,
                'Eastern Europe': self.ad.adoption_sources(
                    region='Eastern Europe').loc[2050, lin] / world_2014,
                'Asia (Sans Japan)': self.ad.adoption_sources(
                    region='Asia (Sans Japan)').loc[2050, lin] / world_2014,
                'Middle East and Africa': self.ad.adoption_sources(
                    region='Middle East and Africa').loc[2050, lin] / world_2014,
                'Latin America': self.ad.adoption_sources(
                    region='Latin America').loc[2050, lin] / world_2014,
                'China': 0.0, 'India': 0.0, 'EU': 0.0, 'USA': 0.0}
        ds1_regen = 0.2  # RA adoption in addition to organic agriculture adoption
        ds1_2050 = _get_datapoints(percent=ds1_percent, extra=ds1_regen)
        ds1_2030 = [x * 0.6 for x in ds1_2050]

        # Data Source 2
        ply = 'Willer 2018 SEI calc RA 3rd poly'
        exp = 'Willer 2018 SEI calc RA exp'
        ds2_percent = {
                'OECD90': self.ad.adoption_sources(region='OECD90').loc[2050, ply] / world_2014,
                'Eastern Europe': self.ad.adoption_sources(
                    region='Eastern Europe').loc[2050, exp] / world_2014,
                'Asia (Sans Japan)': self.ad.adoption_sources(
                    region='Asia (Sans Japan)').loc[2050, ply] / world_2014,
                'Middle East and Africa': self.ad.adoption_sources(
                    region='Middle East and Africa').loc[2050, exp] / world_2014,
                'Latin America': self.ad.adoption_sources(
                    region='Latin America').loc[2050, ply] / world_2014,
                'China': 0.0, 'India': 0.0, 'EU': 0.0, 'USA': 0.0}
        ds2_regen = 0.2  # RA adoption in addition to organic agriculture adoption
        ds2_2050 = _get_datapoints(percent=ds2_percent, extra=ds2_regen)
        ds2_2030 = [x * 0.6 for x in ds2_2050]

        # Data Source 3
        ds3_percent = {'OECD90': 0.6, 'Eastern Europe': 0.6, 'Asia (Sans Japan)': 0.6,
                   'Middle East and Africa': 0.6, 'Latin America': 0.6,
                   'China': 0.0, 'India': 0.0, 'EU': 0.0, 'USA': 0.0}
        ds3_2050 = _get_datapoints(percent=ds3_percent)
        ds3_2030 = [x * 0.8 for x in ds3_2050]

        # Data Source 4
        ds4_regen = 0.3  # RA adoption in addition to organic agriculture adoption
        ds4_2050 = _get_datapoints(percent=ds2_percent, extra=ds4_regen)
        ds4_2030 = [x * 0.8 for x in ds4_2050]

        # Data Source 5, SOURCE: Project Drawdown 2016, constrained TLA for RA
        ds5_regen = 0.3  # RA adoption in addition to organic agriculture adoption
        ds5_2050 = _get_datapoints(percent=ds1_percent, extra=ds5_regen)
        ds5_2030 = [x * 0.8 for x in ds5_2050]

        # Data Source 6
        ds6_2050 = ds3_2050
        ds6_2040 = [x * 0.75 for x in ds6_2050]

        # Data Source 7
        ds7_2050 = ds3_2050
        ds7_2040 = [x * 0.8 for x in ds7_2050]

        # Data Source 8
        ds8_percent = {}
        for region in ds1_percent.keys():
            ds8_percent[region] = (ds1_percent[region] + ds2_percent[region]) / 2.0
        ds8_2050 = _get_datapoints(percent=ds8_percent)

        # Shrinkage in land area used for the Conservation Agriculture solution are added to
        # the land area available for Regenerative Agriculture.
        cons_ag_dataframes = {}
        for idx in range(1, 9):
            if 'BookVersion1' in self.ac.name:
                fname = f'ds{idx}_incr_change_in_cons_ag_book.csv'
            else:
                fname = f'ds{idx}_incr_change_in_cons_ag_current.csv'
            cons_ag_file = THISDIR.joinpath('ca_pds_data', fname)
            key = f'ds{idx}_cons_ag'
            if cons_ag_file.is_file():
                cons_ag_adopt = pd.read_csv(str(cons_ag_file), header=0, index_col=0, comment='#',
                        skipinitialspace=True, skip_blank_lines=True, dtype=np.float64)
                cons_ag_adopt['China'] = 0.0
                cons_ag_adopt['India'] = 0.0
                cons_ag_adopt['EU'] = 0.0
                cons_ag_adopt['USA'] = 0.0
                # growth in Conservation Agriculture is not a factor, only reduction in area
                cons_ag_adopt[cons_ag_adopt >= 0.0] = 0.0
                cons_ag_dataframes[key] = cons_ag_adopt.abs()
            else:
                cons_ag_dataframes[key] = None

        ca_pds_data_sources = [
            {'name': 'Low, Linear Trend', 'include': False,
                'description': (
                    'This scenario projected the future growth of regenerative agriculture based '
                    'on the low historical growth rate of the organic agriculture in different '
                    'regions (Willer et al 2016). In addition, it was assumed that the adoption '
                    'of RA will be higher (20%) than that of the organic agriculture and 60% of '
                    'the estimated adoption by 2050 will be achieved by 2030. Along with this, '
                    'this scenario also includes the leftover area from conservation '
                    'agriculture, as discussed above. Current adoption values for the year '
                    '2012-2017 are taken from the sheet "org adoption by country". This change '
                    'was made in response to the new year set for the currrent adoption, i.e., '
                    '2018. '
                    ),
             'dataframe': cons_ag_dataframes['ds1_cons_ag'],
             'datapoints': pd.DataFrame([
                [2018] + ad_2018,
                [2030] + ds1_2030,
                [2050] + ds1_2050,
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'High, Linear Trend', 'include': False,
                'description': (
                    'This scenario projected the future growth of regenerative agriculture based '
                    'on the high historical growth rate of the organic agriculture in different '
                    'regions (Willer et al 2018, after calculation for arable land). In '
                    'addition, it was assumed that the adoption of RA will be higher (20%) than '
                    'that of the organic agriculture and 60% of the estimated adoption by 2050 '
                    'will be achieved by 2030. Along with this, this scenario also includes the '
                    'leftover area from conservation agriculture, as discussed above. Current '
                    'adoption values for the year 2012-2017 are taken from the sheet "org '
                    'adoption by country". This change was made in response to the new year set '
                    'for the currrent adoption, i.e., 2018. '
                    ),
             'dataframe': cons_ag_dataframes['ds2_cons_ag'],
             'datapoints': pd.DataFrame([
                [2018] + ad_2018,
                [2030] + ds2_2030,
                [2050] + ds2_2050,
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Max, Linear Trend', 'include': False,
                'description': (
                    'This scenario projected a 60% adoption of the solution by 2050 and assumed '
                    '80% of the that will be achieved by 2030. Along with this, this scenario '
                    'also includes the leftover area from conservation agriculture, as discussed '
                    'above. Current adoption values for the year 2012-2017 are taken from the '
                    'sheet "org adoption by country". This change was made in response to the '
                    'new year set for the currrent adoption, i.e., 2018. '
                    ),
             'dataframe': cons_ag_dataframes['ds3_cons_ag'],
             'datapoints': pd.DataFrame([
                [2018] + ad_2018,
                [2030] + ds3_2030,
                [2050] + ds3_2050,
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Aggressive-high, early growth, linear trend', 'include': False,
                'description': (
                    'This scenario projected the future growth of regenerative agriculture based '
                    'on the high historical growth rate of the organic agriculture in different '
                    'regions (Willer et al 2018, after calculaion for arable land). In addition, '
                    'it was assumed that the adoption of RA will be higher (30%) than that of '
                    'the organic agriculture and 80% of the estimated adoption by 2050 will be '
                    'achieved by 2030. Along with this, this scenario also includes the leftover '
                    'area from conservation agriculture, as discussed above. Current adoption '
                    'values for the year 2012-2017 are taken from the sheet "org adoption by '
                    'country". This change was made in response to the new year set for the '
                    'currrent adoption, i.e., 2018. '
                    ),
             'dataframe': cons_ag_dataframes['ds4_cons_ag'],
             'datapoints': pd.DataFrame([
                [2018] + ad_2018,
                [2030] + ds4_2030,
                [2050] + ds4_2050,
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Aggressive-low, early growth, linear trend', 'include': False,
                'description': (
                    'This scenario projected the future growth of regenerative agriculture based '
                    'on the low historical growth rate of the organic agriculture in different '
                    'regions (Willer et al 2016). In addition, it was assumed that the adoption '
                    'of RA will be higher (30%) than that of the organic agriculture and 80% of '
                    'the estimated adoption by 2050 will be achieved by 2030. Along with this, '
                    'this scenario also includes the leftover area from conservation '
                    'agriculture, as discussed above. Current adoption values for the year '
                    '2012-2017 are taken from the sheet "org adoption by country". This change '
                    'was made in response to the new year set for the currrent adoption, i.e., '
                    '2018. '
                    ),
             'dataframe': cons_ag_dataframes['ds5_cons_ag'],
             'datapoints': pd.DataFrame([
                [2018] + ad_2018,
                [2030] + ds5_2030,
                [2050] + ds5_2050,
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Conservative, low growth 1, only RA', 'include': False,
                'description': (
                    'Assuming a lower current adoption of the solution, this scenario has taken '
                    'a conservative approach and projected a 60% adoption of the solution by '
                    '2050 and assumed 75% of the that will be achieved by 2040. This scenario is '
                    'built independent of conservation agriculture, so no leftover area of '
                    'conservation agriculture was added to this solution. Current adoption '
                    'values for the year 2012-2017 are taken from the sheet "org adoption by '
                    'country". This change was made in response to the new year set for the '
                    'currrent adoption, i.e., 2018. '
                    ),
             'dataframe': cons_ag_dataframes['ds6_cons_ag'],
             'datapoints': pd.DataFrame([
                [2018] + ad_2018,
                [2040] + ds6_2040,
                [2050] + ds6_2050,
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Conservative, low growth 2, only RA', 'include': False,
                'description': (
                    'Assuming a lower current adoption of the solution, this scenario has taken '
                    'a conservative approach and projected a 60% adoption of the solution by '
                    '2050 and assumed 80% of the that will be achieved by 2040. This scenario is '
                    'built independent of conservation agriculture, so no leftover area of '
                    'conservation agriculture was added to this solution. Current adoption '
                    'values for the year 2012-2017 are taken from the sheet "org adoption by '
                    'country". This change was made in response to the new year set for the '
                    'currrent adoption, i.e., 2018. '
                    ),
             'dataframe': cons_ag_dataframes['ds7_cons_ag'],
             'datapoints': pd.DataFrame([
                [2018] + ad_2018,
                [2040] + ds7_2040,
                [2050] + ds7_2050,
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Baseline scenario', 'include': True,
                'description': (
                    'Baseline adoption '
                    ),
             'dataframe': cons_ag_dataframes['ds8_cons_ag'],
             'datapoints': pd.DataFrame([
                [2018] + ad_2018,
                [2050] + ds8_2050,
                ], columns=ca_pds_columns).set_index('Year')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        # Current adoption values for the year 2012-2017 are taken from the sheet
        # "org adoption by country" in the Excel file for this solution.
        for s in self.pds_ca.scenarios.values():
            df = s['df']
            df.loc[2014] = [10.0425, 6.230983199564, 1.024820758485, 1.495740017536,
                    0.280348210165, 0.342272547086, 0.0, 0.0, 0.0, 0.0]
            df.loc[2015] = [10.4821, 6.392187207238, 1.186149025025, 1.609802907785,
                    0.313522708425, 0.349200927281, 0.0, 0.0, 0.0, 0.0]
            df.loc[2016] = [10.9217, 6.560831715351, 1.372873741988, 1.732564062959,
                    0.350622850918, 0.356484379405, 0.0, 0.0, 0.0, 0.0]
            df.loc[2017] = [11.3613, 6.743428946088, 1.588992842952, 1.864686799696,
                    0.392113171655, 0.364411206077, 0.0, 0.0, 0.0, 0.0]
            df.loc[2018] = [11.8009, 6.946491121632, 1.839133620034, 2.006885018162,
                    0.438513174434, 0.373269709916, 0.0, 0.0, 0.0, 0.0]

        self.initialize_adoption_bases()
        if self.ac.soln_ref_adoption_basis == 'Custom':
            ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()
        else:
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
            ref_adoption_data_per_region=ref_adoption_data_per_region,
            copy_pds_world_too=False,
            copy_through_year=2018,
            copy_pds_to_ref=False,
            copy_ref_datapoint=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=1)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=self.tla_per_region,
            pds_total_adoption_units=self.tla_per_region,
            electricity_unit_factor=1000000.0,
            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
            bug_cfunits_double_count=True)
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
            fc_convert_iunit_factor=conversions.mha_to_ha)

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
            conversion_factor=conversions.mha_to_ha)

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
            annual_land_area_harvested=self.ua.soln_pds_annual_land_area_harvested(),
            regime_distribution=self.ae.get_land_distribution(),
            regimes=dd.THERMAL_MOISTURE_REGIMES8)