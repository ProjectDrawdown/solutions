"""Peatland Protection solution model.
   Excel filename: Drawdown_RRS-BIOSEQProtect_Model_v1.1b_Peatland_Mar2020.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls as ac
from model import aez
from model import ch4calcs
from model import co2calcs
from model import n2ocalcs
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

name = 'Peatland Protection'
solution_category = ac.SOLUTION_CATEGORY.LAND

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS-58p2050-Plausible-customPDS-avg-Jan2020"
PDS2 = "PDS-97p2050-Drawdown-customPDS-high-Jan2020"
PDS3 = "PDS-95p2050-Optimum-PDSCustom-80%lowdeg-Nov2019"

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

        # Custom PDS Data
        ca_pds_columns = ['Year'] + dd.REGIONS
        tla_world_2050 = self.tla_per_region.loc[2050, 'World']
        ad_2018 = self.ac.ref_base_adoption['World']
        growth_initial = pd.DataFrame([[2018] + list(self.ac.ref_base_adoption.values())],
                columns=ca_pds_columns).set_index('Year')

        degrade_rate_high = pd.Series(0.00506640879193976, index=range(2014, 2061))

        degrade_rate_low = pd.Series(0, index=range(2014, 2061))
        degrade_rate_low.loc[2014:2019] = 0.00506640879193976
        degrade_rate_low.loc[2020:2029] = 0.00253320439596988
        degrade_rate_low.loc[2030:] = 0.0

        degrade_rate_alt = pd.Series(0, index=range(2014, 2061))
        degrade_rate_alt.loc[2014] = 0.00506640879193976
        degrade_rate_alt.loc[2015] = 0.00464420805927811
        degrade_rate_alt.loc[2016] = 0.00422200732661647
        degrade_rate_alt.loc[2017] = 0.00379980659395482
        degrade_rate_alt.loc[2018] = 0.00337760586129317
        degrade_rate_alt.loc[2019] = 0.00295540512863153
        degrade_rate_alt.loc[2020] = 0.00253320439596988
        degrade_rate_alt.loc[2021] = 0.00227988395637289
        degrade_rate_alt.loc[2022] = 0.00202656351677590
        degrade_rate_alt.loc[2023] = 0.00177324307717892
        degrade_rate_alt.loc[2024] = 0.00151992263758193
        degrade_rate_alt.loc[2025] = 0.00126660219798494
        degrade_rate_alt.loc[2026] = 0.00101328175838795
        degrade_rate_alt.loc[2027] = 0.00075996131879096
        degrade_rate_alt.loc[2028] = 0.00050664087919398
        degrade_rate_alt.loc[2029] = 0.00025332043959699
        degrade_rate_alt.loc[2030:] = 0.0

        # In Excel, the Custom PDS Scenarios tab columns AC:AF compute a limit on adoption
        # based on the amount of degraded land remaining. We compute the same limit here.
        # This version takes the adoption into account.
        def constrained_tla_adoption(rate, datapoints):
            degrade_df = pd.DataFrame(0, index=range(2014, 2061), columns=[
                'Total undegraded land at the start of the year',
                'Degraded land at the end of the year',
                'Total undegraded land at the end of the year', 'Constrained TLA'])
            for year in range(2014, 2061):
                if year == 2014:
                    # Not a typo, Excel uses the 2018 base adoption number starting in 2014.
                    # We are bug-for-bug compatible here.
                    undeg_start = tla_world_2050 - ad_2018
                else:
                    last = degrade_df.loc[year-1, 'Total undegraded land at the end of the year']
                    new = datapoints.loc[year, 'World'] - datapoints.loc[year-1, 'World']
                    undeg_start = last - new
                degrade_df.loc[year, 'Total undegraded land at the start of the year'] = undeg_start
                degraded_end = max(0, undeg_start * rate[year])
                degrade_df.loc[year, 'Degraded land at the end of the year'] = degraded_end
                degrade_df.loc[year, 'Total undegraded land at the end of the year'] = (
                        undeg_start - degraded_end)
                degrade_df.loc[year, 'Constrained TLA'] = (tla_world_2050 -
                        degrade_df['Degraded land at the end of the year'].sum())
            return degrade_df

        def constrained_tla(rate):
            degrade_df = pd.DataFrame(0, index=range(2014, 2061), columns=[
                'Total undegraded land at the start of the year',
                'Degraded land at the end of the year',
                'Total undegraded land at the end of the year', 'Constrained TLA'])
            for year in range(2014, 2061):
                if year == 2014:
                    # Not a typo, Excel uses the 2018 base adoption number starting in 2014.
                    # We are bug-for-bug compatible here.
                    undeg_start = tla_world_2050 - ad_2018
                else:
                    last = degrade_df.loc[year-1, 'Constrained TLA']
                    undeg_start = last - ad_2018
                degrade_df.loc[year, 'Total undegraded land at the start of the year'] = undeg_start
                degraded_end = max(0, undeg_start * rate[year])
                degrade_df.loc[year, 'Degraded land at the end of the year'] = degraded_end
                degrade_df.loc[year, 'Total undegraded land at the end of the year'] = (
                        undeg_start - degraded_end)
                degrade_df.loc[year, 'Constrained TLA'] = (tla_world_2050 -
                        degrade_df['Degraded land at the end of the year'].sum())
            return degrade_df


        # DATA SOURCE 1
        # https://rsis.ramsar.org/ris-search/peatland?pagetab=2&f%5B0%5D=wetlandTypes_en_ss%3AInland%20wetlands&f%5B1%5D=wetlandTypes_en_ss%3AU%3A%20Permanent%20Non-forested%20peatlands&f%5B2%5D=wetlandTypes_en_ss%3AXp%3A%20Permanent%20Forested%20peatlands&f%5B3%5D=managementPlanAvailable_i%3A-1
        ds1_growth_rate = 0.0622897686767343
        # silvopasture and farmlandrestoration use a growth_rate feature of customadoption
        # to do something like this. However those two solutions calculate a linear growth
        # and then use it to call TREND() to fit a line through it. peatlands uses the raw
        # linear growth data as its Custom Adoption. not quite compatible with what
        # silvopasture and farmlandrestoration do, so we calculate it here.
        ds1_datapoints = pd.DataFrame(0.0, index=range(2012, 2061), columns=dd.REGIONS)
        ds1_datapoints.loc[2012:2018, 'World'] = ad_2018
        for year in range(2019, 2061):
            rate = 1 + ds1_growth_rate
            ds1_datapoints.loc[year, 'World'] = ds1_datapoints.loc[year-1, 'World'] * rate

        # DATA SOURCE 2
        df = constrained_tla_adoption(rate=degrade_rate_high, datapoints=ds1_datapoints)
        ds2_adoption_2050 = df.loc[2050, 'Constrained TLA']
        ds2_adoption_2030 = 0.7 * ds2_adoption_2050

        # DATA SOURCE 4
        df = constrained_tla_adoption(rate=degrade_rate_alt, datapoints=ds1_datapoints)
        ds4_adoption_2050 = df.loc[2050, 'Constrained TLA']
        ds4_adoption_2030 = 0.7 * ds4_adoption_2050

        # DATA SOURCE 5
        df = constrained_tla(rate=degrade_rate_high)
        ds5_constrained_tla = df.loc[2050, 'Constrained TLA']

        # DATA SOURCE 7
        ds7_constrained_tla = constrained_tla(degrade_rate_low).loc[2050, 'Constrained TLA']

        # DATA SOURCE 9
        ds9_growth_rate = 0.0394112383173051
        # silvopasture and farmlandrestoration use a growth_rate feature of customadoption
        # to do something like this. However those two solutions calculate a linear growth
        # and then use it to call TREND() to fit a line through it. peatlands uses the raw
        # linear growth data as its Custom Adoption. So calculate it here.
        ds9_datapoints = pd.DataFrame(0.0, index=range(2012, 2061), columns=dd.REGIONS)
        ds9_datapoints.loc[2012:2018, 'World'] = ad_2018
        for year in range(2019, 2061):
            rate = 1 + ds9_growth_rate
            ds9_datapoints.loc[year, 'World'] = ds9_datapoints.loc[year-1, 'World'] * rate
        df = constrained_tla_adoption(degrade_rate_high, ds9_datapoints)
        ds9_constrained_tla = df.loc[:, 'Constrained TLA'].min()

        # DATA SOURCE 10
        df = constrained_tla_adoption(degrade_rate_low, ds9_datapoints)
        ds10_constrained_tla = df.loc[:, 'Constrained TLA'].min()

        ca_pds_data_sources = [
            {'name': 'High adoption and conservative degradation rate', 'include': True,
                'description': (
                    'The Peatlands Ramsar sites with management plans evolution (1985-2015) was '
                    'used to estimate the yearly increase rate of 6,23% corresponding to 1985- '
                    "2015 coupled with the TLA's current degradation rate of 0.51%. "
                    ),
                'datapoints': ds1_datapoints, 'maximum': 331},
            {'name': 'Scenario 1 + 70% conservative degradation TLA in 2030', 'include': True,
                'description': (
                    'Scenario 1 with linear increase up to 70% of TLA 2050 value in 2030 and '
                    'then linear increase to 100% TLA value in 2050 from then onwards '
                    ),
                'maximum': ds2_adoption_2050,
                'datapoints': pd.DataFrame([
                    [2014, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2030, ds2_adoption_2030, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds2_adoption_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'High adoption and low degradation rate', 'include': True,
                'description': (
                    'The Peatlands Ramsar sites with management plans  evolution (1985-2015) was '
                    'used to estimate the yearly increase rate of 6,23% corresponding to 1985- '
                    '2015 coupled with the he New York declaration on Forests is used  to '
                    'estimate an alternative degradation rate which starts from 0.51% and '
                    'linearly decreases to half its value in 2020 and then to zero in 2030. '
                    ),
                'datapoints': ds1_datapoints, 'maximum': 396},
            {'name': 'Scenario 3 + 70% low degradation TLA in 2030', 'include': True,
                'description': (
                    'Scenario 3 with linear increase up to 70% of TLA 2050 value in 2030 and '
                    'then linear increase to 100% TLA value in 2050 from then onwards '
                    ),
                'maximum': ds4_adoption_2050,
                'datapoints': pd.DataFrame([
                    [2014, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2030, ds4_adoption_2030, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds4_adoption_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': '100% conservative degradation TLA in 2050', 'include': True,
                'description': (
                    '100% adoption ofconservative degradation rate TLA  by 2050 '
                    ),
                'maximum': ds5_constrained_tla,
                'datapoints': pd.DataFrame([
                    [2014, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds5_constrained_tla, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': '80% conservative degradation TLA in 2030', 'include': True,
                'description': (
                    'Linear increase up to 80% of TLA 2050 value in 2030 (calculated with the '
                    'conservative degradation rate) and then linear increase to 100% TLA value '
                    'in 2050 from then onwards '
                    ),
                'maximum': ds5_constrained_tla,
                'datapoints': pd.DataFrame([
                    [2014, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2030, 0.8 * ds5_constrained_tla, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds5_constrained_tla, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': '100% low degradation TLA in 2050', 'include': True,
                'description': (
                    '100% adoption of low degradation rate TLA  by 2050 '
                    ),
                'maximum': ds7_constrained_tla,
                'datapoints': pd.DataFrame([
                    [2014, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds7_constrained_tla, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': '80% low degradation TLA in 2030', 'include': True,
                'description': (
                    '80% low degradation TLA in 2030 '
                    ),
                'maximum': ds7_constrained_tla,
                'datapoints': pd.DataFrame([
                    [2014, ad_2018, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2030, 0.8 * ds7_constrained_tla, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    [2050, ds7_constrained_tla, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Medium adoption and conservative degradation rate', 'include': True,
                'description': (
                    'The Peatlands Ramsar sites with management plans evolution (1985-2015) was '
                    'used to estimate the yearly increase rate of 3,94% corresponding to 1990- '
                    "2015 coupled with the TLA's current degradation rate of 0.51%. "
                    ),
                'datapoints': ds9_datapoints, 'maximum': ds9_constrained_tla},
            {'name': 'Medium adoption and low degradation rate', 'include': True,
                'description': (
                    'The Peatlands Ramsar sites with management plans evolution (1985-2015) was '
                    'used to estimate the yearly increase rate of 3,94% corresponding to 1990- '
                    "2015 coupled with the TLA's low degradation rate of 0.51%. "
                    ),
                'datapoints': ds9_datapoints, 'maximum': ds10_constrained_tla},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        for s in self.pds_ca.scenarios.values():
            df = s['df']
            df.loc[2014:2018, 'World'] = ad_2018

        self.initialize_adoption_bases()
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
            copy_pds_world_too=True,
            copy_through_year=2018,
            copy_pds_to_ref=True,
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

        self.n2o = n2ocalcs.N2OCalcs(ac=self.ac,
            soln_pds_direct_n2o_co2_emissions_saved=self.ua.direct_n2o_co2_emissions_saved_land(),
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

        self.c2 = co2calcs.CO2Calcs(ac=self.ac,
            ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
            ch4_megatons_avoided_or_reduced=self.c4.ch4_megatons_avoided_or_reduced(),
            n2o_megatons_avoided_or_reduced=self.n2o.n2o_megatons_avoided_or_reduced(),
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