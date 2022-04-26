"""Tree Intercropping solution model.
   Excel filename: Drawdown_RRS-BIOSEQAgri_Model_v1.1b_TreeIntercropping_Mar2020.xlsm
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

name = 'Tree Intercropping'
solution_category = ac.SOLUTION_CATEGORY.LAND

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS-84p2050-Plausible-customPDS-avg-30Jan2020"
PDS2 = "PDS-99p2050-Drawdown-customPDS-high-30Jan2020"
PDS3 = "PDS-100p2050-Optimum-customPDS-39%EUadoption-Jan2020"

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

        # ADOPTION
        self._ref_ca_sources = scenario.load_sources(THISDIR/'ca_ref_data'/'ca_ref_sources.json', 'filename')

        ca_pds_columns = ['Year'] + dd.REGIONS
        tla_world_2050 = self.tla_per_region.loc[2050, 'World']
        ad_2018 = self.ac.ref_base_adoption['World']

        # Data Source 4-5
        # Zomer et al. 2014; Zomer, R. J., Trabucco, A., Coe, R., Place, F.,
        # Van Noordwijk, M., & Xu, J. C. (2014). Trees on farms: an update and
        # reanalysis of agroforestry’s global extent and socio-ecological characteristics.
        # World Agroforestry Center Working Paper, 179.
        ds5_adoption = ad_2018
        for y in range(2015, 2049):
            ds5_adoption = ds5_adoption * (1 + 0.0128)
        # In Excel, the 2018 adoption is used as 2014 and the 2048 adoption is used as 2050.
        ds5_ad_2050 = ds5_adoption

        # Data Source 6-9
        # Thomson et al. 2018; Thomson, A., Misselbrook, T., Moxley, J., Buys, G.,
        # Evans, C., Malcolm, H., ... & Reinsch, S. (2018). Quantifying the impact
        # of future land use scenarios to 2050 and beyond. Final report.
        ds6_cropland_percent = 0.05
        global_cropland = 1411.0
        remaining_cropland = global_cropland - ad_2018
        ds6_ad_2018 = 248.0  # No idea why ds6 uses a different adoption in 2018
        ds6_ad_2050 = (remaining_cropland * ds6_cropland_percent) + ds6_ad_2018
        ds7_cropland_percent = 0.1
        ds7_ad_2050 = (remaining_cropland * ds7_cropland_percent) + ad_2018
        ds8_cropland_percent = 0.2
        ds8_ad_2050 = (remaining_cropland * ds8_cropland_percent) + ad_2018
        ds9_cropland_percent = 0.39
        ds9_ad_2050 = (remaining_cropland * ds9_cropland_percent) + ad_2018

        ca_pds_data_sources = [
            {'name': 'Medium, linear growth', 'include': False,
                'description': (
                    'Due to the unavailability of any historical data or future prognostication, '
                    'we have assumed a 75% adoption of the solution under this scenario. '
                    ),
                'maximum': tla_world_2050,
                'datapoints': pd.DataFrame([
                    [2018, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, 0.75 * tla_world_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'High, linear growth', 'include': False,
                'description': (
                    'Due to the unavailability of any historical data or future prognostication, '
                    'we have assumed a 90% adoption of the solution under this scenario. '
                    ),
                'maximum': tla_world_2050,
                'datapoints': pd.DataFrame([
                    [2018, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, 0.9 * tla_world_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Max, linear growth', 'include': True,
                'description': (
                    'Due to the unavailability of any historical data or future prognostication, '
                    'we have assumed a 100% adoption of the solution under this scenario. '
                    ),
                'maximum': tla_world_2050,
                'datapoints': pd.DataFrame([
                    [2018, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, 1.0 * tla_world_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': '0.64% annual adoption increase based on Zomer 2014 global increase rates of <20% tree cover on cropland', 'include': True,
                'description': (
                    'Linear projection based on current global increase rates of tree cover '
                    'greater than 10% on cropland, as calculated based on Zomer et al. (2014) '
                    'data. Percent of agricultural land under >10% and >20% tree cover in 2000 '
                    "and 2010 was calculated (see 'Zomer2014-CurrentAdoption' sheet). We "
                    'compared this to total global cropland (1473 Mha according to GAEZ zones) '
                    'and calculated a global increase in 10-20% tree cover on cropland of 6.4% '
                    'from 2000 - 2010, which was converted to an annual increase rate of 0.64 % '
                    'for this scenario. '
                    ),
                'maximum': tla_world_2050,
                'growth_initial': pd.DataFrame([[2018, ad_2018, 0., 0., 0., 0.,
                    0., 0., 0., 0., 0.]], columns=ca_pds_columns).set_index('Year'),
                'growth_rate': 0.0064},
            {'name': '1.28% annual adoption increase based on Zomer 2014 global increase rates of <10% tree cover on cropland', 'include': True,
                'description': (
                    'Linear projection based on current global increase rates of tree cover '
                    'greater than 10% on cropland, as calculated based on Zomer et al. (2014) '
                    'data. Percent of agricultural land under >10% and >20% tree cover in 2000 '
                    "and 2010 was calculated (see 'Zomer2014-CurrentAdoption' sheet). We "
                    'compared this to total global cropland (1473 Mha according to GAEZ zones) '
                    'and calculated a global increase in 10-20% tree cover on cropland of 6.4% '
                    'from 2000 - 2010, which was doubled and converted to an annual increase '
                    'rate of 1.28 % for this scenario. '
                    ),
                'maximum': tla_world_2050,
                'datapoints': pd.DataFrame([
                    [2018, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds5_ad_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Low conversion of remaining cropland by 2050 (5% - UK medium ambition scenario)', 'include': True,
                'description': (
                    'Linear projection based on the projected rate of 5% conversion of remaining '
                    'cropland by 2050 as reported by Thomson et al. (2018) for UK projections of '
                    'future land-use change. Total remaining global cropland in 2014 is '
                    'estimated at 1225 Mha, which was calculated based on the difference between '
                    'total current cropland of 1473 Mha and the total global area already under '
                    'tree intercropping. '
                    ),
                'maximum': tla_world_2050,
                'datapoints': pd.DataFrame([
                    [2018, ds6_ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds6_ad_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Medium conversion of remaining cropland by 2050 (10% - UK medium ambition scenario)', 'include': True,
                'description': (
                    'Linear projection based on the projected rate of 10% conversion of '
                    'remaining cropland by 2050 as reported by Thomson et al. (2018) for UK '
                    'projections of future land-use change. Total remaining global cropland in '
                    '2014 is estimated at 1225 Mha, which was calculated based on the difference '
                    'between total current cropland of 1473 Mha and the total global area '
                    'already under tree intercropping. '
                    ),
                'maximum': tla_world_2050,
                'datapoints': pd.DataFrame([
                    [2018, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds7_ad_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'High conversion of remaining cropland by 2050 (20%)', 'include': True,
                'description': (
                    'Linear projection estimating a medium current adoption rate of 20% of tree '
                    'intercropping on remaining global cropland. Total remaining global cropland '
                    'in 2014 is estimated at 1225 Mha, which was calculated based on the '
                    'difference between total current cropland of 1473 Mha and the total global '
                    'area already under tree intercropping. '
                    ),
                'maximum': tla_world_2050,
                'datapoints': pd.DataFrame([
                    [2018, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds8_ad_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Very high conversion of remaining cropland by 2050 (39% - current adoption in EU)', 'include': True,
                'description': (
                    'Linear projection based on current adoption rate of tree intercropping on '
                    'cropland in the EU, which is 39% as reported in den Herder et al. (2017). '
                    'This rate was applied to all current remaining global cropland by 2050. '
                    'Total remaining global cropland in 2014 is estimated at 1225 Mha, which was '
                    'calculated based on the difference between total current cropland of 1473 '
                    'Mha and the total global area already under tree intercropping. '
                    ),
                'maximum': tla_world_2050,
                'datapoints': pd.DataFrame([
                    [2018, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds9_ad_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        for s in self.pds_ca.scenarios.values():
            df = s['df']
            df.loc[2012, 'World'] = 254.91717271225
            df.loc[2013, 'World'] = 256.900453733641
            df.loc[2014, 'World'] = 259.672330723017
            df.loc[2015, 'World'] = 261.743911973822
            df.loc[2016, 'World'] = 263.820565911005
            df.loc[2017, 'World'] = 265.901052727049
            df.loc[2018, 'World'] = 267.984718062521

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
        ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
        copy_pds_world_too = False
        if (self.ac.name == 'PDS-100p2050-Optimum' or
                self.ac.name == 'PDS-100p2050-Optimum-Jan2019' or
                self.ac.name == 'PDS-97p2050-Drawdown-Jan2019'):
            copy_pds_world_too = True
        self.ht = helpertables.HelperTables(ac=self.ac,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=self.tla_per_region, pds_adoption_limits=self.tla_per_region,
            ref_adoption_data_per_region=ref_adoption_data_per_region,
            copy_pds_world_too=copy_pds_world_too,
            copy_through_year=2018,
            copy_pds_to_ref=False, copy_ref_datapoint=False,
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