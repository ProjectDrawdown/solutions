"""Managed Grazing solution model.
   Excel filename: Drawdown_RRS-BIOSEQ_Model_v1.1b_MASTER_Managed_Grazing_Mar2020.xlsm
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
VMAs = {
    'Current Adoption': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Current_Adoption.csv"),
        use_weight=False),
    'CONVENTIONAL First Cost per Implementation Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION First Cost per Implementation Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
        use_weight=False),
    'CONVENTIONAL Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Operating_Cost_per_Functional_Unit_per_Annum.csv"),
        use_weight=False),
    'SOLUTION Operating Cost per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Operating_Cost_per_Functional_Unit_per_Annum.csv"),
        use_weight=False),
    'CONVENTIONAL Net Profit Margin per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Net_Profit_Margin_per_Functional_Unit_per_Annum.csv"),
        use_weight=False),
    'SOLUTION Net Profit Margin per Functional Unit per Annum': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Net_Profit_Margin_per_Functional_Unit_per_Annum.csv"),
        use_weight=False),
    'Yield from CONVENTIONAL Practice': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Yield_from_CONVENTIONAL_Practice.csv"),
        use_weight=True),
    'Yield Gain (% Increase from CONVENTIONAL to SOLUTION)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Yield_Gain_Increase_from_CONVENTIONAL_to_SOLUTION.csv"),
        use_weight=False),
    'Electricty Consumed per CONVENTIONAL Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Energy Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
    'Total Energy Used per SOLUTION functional unit': vma.VMA(
        filename=None, use_weight=False),
    'Fuel Consumed per CONVENTIONAL Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'Fuel Reduction Factor SOLUTION': vma.VMA(
        filename=None, use_weight=False),
    't CO2-eq (Aggregate emissions) Reduced per Land Unit': vma.VMA(
        filename=None, use_weight=False),
    't CO2 Reduced per Land Unit': vma.VMA(
        filename=None, use_weight=False),
    't N2O-CO2-eq Reduced per Land Unit': vma.VMA(
        filename=None, use_weight=False),
    't CH4-CO2-eq Reduced per Land Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "t_CH4_CO2_eq_Reduced_per_Land_Unit.csv"),
        use_weight=False),
    'Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit -- CHOOSE ONLY ONE': vma.VMA(
        filename=None, use_weight=False),
    'Indirect CO2 Emissions per SOLUTION Implementation Unit': vma.VMA(
        filename=None, use_weight=False),
    'Sequestration Rates': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Sequestration_Rates.csv"),
        use_weight=False),
    'Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing': vma.VMA(
        filename=None, use_weight=False),
    'Disturbance Rate': vma.VMA(
        filename=None, use_weight=False),
    'Current Adoption of Holistic Grazing': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Current_Adoption_of_Holistic_Grazing.csv"),
        use_weight=False),
    'All other current adoption estimates': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "All_other_current_adoption_estimates.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Managed Grazing'
solution_category = ac.SOLUTION_CATEGORY.LAND

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS-43p2050-Plausible-customPDS-avg-Jan2020"
PDS2 = "PDS-65p2050-Drawdown-customPDS-high-Jan2020"
PDS3 = "PDS-100p2050-Optimum-PDSCustom-futuremax-Nov2019"

class Scenario(scenario.LandScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category

    def __init__(self, scen=None):
        if isinstance(scen, ac.AdvancedControls):
            self.scenario = scen.name
            self.ac = scen
        else:
            self.scenario = scen or PDS2
            self.ac = scenarios[self.scenario]

        # TLA
        self.ae = aez.AEZ(solution_name=self.name, cohort=2020,
                regimes=dd.THERMAL_MOISTURE_REGIMES8)
        if self.ac.use_custom_tla:
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
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
        ad_data_sources = {
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            main_includes_regional=True,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_columns = ['Year'] + dd.REGIONS
        tla_2050 = self.tla_per_region.loc[2050]
        total_grazing_area = 2700.0

        ds1_percentages = pd.Series([0.0, 0.413624302911244, 0.0, 0.070550343761321,
            0.138183856774756, 0.845901090636972, 0.0, 0.0, 0.0, 0.0], index=dd.REGIONS)
        ds1_2050 = tla_2050 * ds1_percentages
        ds1_2050['World'] = ds1_2050.sum()

        ds2_percentages = pd.Series([0.0, 0.596920577658838, 0.0, 0.0836983623713848,
            0.178254518319696, 0.933216308519849, 0.0, 0.0, 0.0, 0.0], index=dd.REGIONS)
        ds2_2050 = tla_2050 * ds2_percentages
        ds2_2050['World'] = ds2_2050.sum()

        ds3_percentages = pd.Series([0.494785212286615, 0.494785212286615, 0.0, 0.0743985443301198,
            0.153620863162148, 0.853238399576085, 0.0, 0.0, 0.0, 0.0], index=dd.REGIONS)
        ds3_2050 = tla_2050 * ds3_percentages

        # Data source 4 is described as scenario 1 with 70% adoption by 2030, but in actual
        # implementation it does not make the World be a sum of the regions. Instead, it
        # makes the World use the percentage of the OECD90 region.
        ds4_percentages = pd.Series([0.413624302911244, 0.413624302911244, 0.0, 0.070550343761321,
            0.138183856774756, 0.845901090636972, 0.0, 0.0, 0.0, 0.0], index=dd.REGIONS)
        ds4_2050 = tla_2050 * ds4_percentages

        # Data source 5 is described as scenario 2 with 70% adoption by 2030, but in actual
        # implementation it does not make the World be a sum of the regions. Instead, it
        # makes the World use the percentage of the OECD90 region.
        ds5_percentages = pd.Series([0.596920577658838, 0.596920577658838, 0.0, 0.0836983623713848,
            0.178254518319696, 0.933216308519849, 0.0, 0.0, 0.0, 0.0], index=dd.REGIONS)
        ds5_2050 = tla_2050 * ds5_percentages

        # SOURCE: Organic World 2009 Table 47, Organic World 2019 and FAOStat.
        # Region, Organic grazing area 2009 Mha, Organic grazing area 2009 %,
        #     Organic grazing area 2019 Mha, Organic grazing area 2019 %
        # Africa,        0.03,  0%,    0.08, 0%
        # Asia,          0.6,   0%,    1,    0%
        # EU,            2.1,   3%,    5.7,  8%
        # Latin America, 0.006, 0%,    4.9,  3%
        # N. America,    1.1,   0%,    1.4,  0%
        # Oceania,       11.7,  8%,    34.9, 24%
        # Global Total,  15.5,  0.50%, 48,   2%
        ds7_mha_2009 = 15.5
        ds7_mha_2019 = 48
        ds7_growth_rate = (ds7_mha_2019 - ds7_mha_2009) / (2019 - 2009)
        # Note that Excel says the ref_base_adoption is for 2018, when computing a growth
        # projection it uses it as 2014. We do the same here, bug-for-bug compatibility.
        ds7_2050 = self.ac.ref_base_adoption['World'] + (ds7_growth_rate * (2050 - 2014))

        # Costa Rica proposes a 20-40% increase in 20 years; increase managed grazing
        # area by 1-2% per year (Navarro 2015).
        ds8_2050 = 0.4 * total_grazing_area

        # Brazil INDC proposes to restore 15 Mha of degraded grassland, (20% of national
        # grazing area), (Federative Republic of Brazil 2015)
        ds9_2050 = 0.2 * total_grazing_area

        # Sá (2016) projects an increase in restoration of degraded pasture in Latin America
        # from 10Mha in 2015 to 20Mha in 2020. That’s 11% of 177.4 Mha grazing land for
        # South America (FAOstat 2019)
        ds10_2050 = 0.11 * total_grazing_area

        ca_pds_data_sources = [
            {'name': 'Low Growth, Linear Trend', 'include': True,
                # The adoption of managed grazing is projected based on weighted "average, medium,
                # and high" growth rates, calculated based on the available country specifc area
                # under managed grazing and the region specific total grazing area (Using Henderson
                # et al 2015 estimates). This scenario builds the future projection based on the
                # low growth rate.													
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2050] + ds1_2050.tolist(),
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'High Growth, Linear Trend', 'include': True,
                # The adoption of managed grazing is projected based on weighted "average, medium,
                # and high" growth rates, calculated based on the available country specifc area
                # under managed grazing and the region specific total grazing area (Using Henderson
                # et al 2015 estimates). This scenario builds the future projection based on the
                # high growth rate.													
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2050] + ds2_2050.tolist(),
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Medium Growth, Linear Trend', 'include': True,
                # The adoption of managed grazing is projected based on weighted "average, medium,
                # and high" growth rates, calculated based on the available country specifc area
                # under managed grazing and the region specific total grazing area (Using Henderson
                # et al 2015 estimates). This scenario builds the future projection based on the
                # medium growth rate.
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2050] + ds3_2050.tolist(),
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Low High Early Growth, Linear Trend', 'include': True,
                # This is scenario 1 with 70% adoption by 2030.
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2030] + (0.7 * ds4_2050).tolist(),
                    [2050] + ds4_2050.tolist(),
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'High High Early Growth, Linear Trend', 'include': True,
                # This is scenario 2 with 70% adoption by 2030.
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2030] + (0.7 * ds5_2050).tolist(),
                    [2050] + ds5_2050.tolist(),
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Medium High Early Growth, Linear Trend', 'include': True,
                # This is scenario 3 with 70% adoption by 2030.
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2030] + (0.7 * ds3_2050).tolist(),
                    [2050] + ds3_2050.tolist(),
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Linear growth, based on Organic Grazing Historic Growth', 'include': True,
                # The future adoption of managed grazing is projected based on the organic
                # grazing historic growth rate using the linear trend.
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2050] + [ds7_2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Future commitments, max growth', 'include': True,
                # Future adoption of managed grazing is projected based on the country/regional
                # commitments as given in the table below. It is assumed that the country/regional
                # level trends will be adopted at the global level. This scenario is based on the
                # high end commitments given for the Costa Rica.
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2050, ds8_2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Future Commitments, moderate growth', 'include': True,
                # Future adoption of managed grazing is projected based on the country/regional
                # commitments as given in the table below. It is assumed that the country/regional
                # level trends will be adopted at the global level. This scenario is based on the
                # high end commitments given for the Brazil.
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2050, ds9_2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Future Commitments, low growth', 'include': True,
                # Future adoption of managed grazing is projected based on the country/regional
                # commitments as given in the table below. It is assumed that the country/regional
                # level trends will be adopted at the global level. This scenario is based on the
                # high end commitments given for the Latin America.
                'datapoints': pd.DataFrame([
                    [2018] + list(self.ac.ref_base_adoption.values()),
                    [2050, ds10_2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                    ], columns=ca_pds_columns).set_index('Year')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        for s in self.pds_ca.scenarios.values():
            df = s['df']
            for y in range(2012, 2019):
                df.loc[y] = [71.6320447618946, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

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
        self.ht = helpertables.HelperTables(ac=self.ac,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=self.tla_per_region, pds_adoption_limits=self.tla_per_region,
            use_first_pds_datapoint_main=True,
            adoption_base_year=2018,
            copy_pds_to_ref=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

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
            ch4_megatons_avoided_or_reduced=self.c4.ch4_megatons_avoided_or_reduced(),
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

