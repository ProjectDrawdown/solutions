"""Afforestation solution model.
   Excel filename: Drawdown_RRS-BIOSEQ_Model_v1.1_MASTER_Afforestation-Mar2020.xlsm
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
        filename=None, use_weight=False),
    'CONVENTIONAL First Cost per Implementation Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_First_Cost_per_Implementation_Unit.csv"),
        use_weight=False),
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
        filename=None, use_weight=False),
    'Yield Gain (% Increase from CONVENTIONAL to SOLUTION)': vma.VMA(
        filename=None, use_weight=False),
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
        filename=THISDIR.joinpath("vma_data", "t_CO2_eq_Aggregate_emissions_Reduced_per_Land_Unit.csv"),
        use_weight=False),
    't CO2 Reduced per Land Unit': vma.VMA(
        filename=None, use_weight=False),
    't N2O-CO2-eq Reduced per Land Unit': vma.VMA(
        filename=None, use_weight=False),
    't CH4-CO2-eq Reduced per Land Unit': vma.VMA(
        filename=None, use_weight=False),
    'Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit -- CHOOSE ONLY ONE': vma.VMA(
        filename=None, use_weight=False),
    'Indirect CO2 Emissions per SOLUTION Implementation Unit': vma.VMA(
        filename=None, use_weight=False),
    'Sequestration Rates': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Sequestration_Rates.csv"),
        use_weight=False),
    'Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Sequestered_Carbon_NOT_Emitted_after_Cyclical_Harvesting_Clearing.csv"),
        use_weight=False),
    'Disturbance Rate': vma.VMA(
        filename=None, use_weight=False),
    'Rotational length (years)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Rotational_length_years.csv"),
        use_weight=False),
    'Carbon content in biomass (%)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Carbon_content_in_biomass.csv"),
        use_weight=False),
    'Aboveground Biomass (AGB)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Aboveground_Biomass_AGB.csv"),
        use_weight=False),
    'Belowground Biomass (BGB)': vma.VMA(
        filename=None, use_weight=False),
    'Soil Organic Carbon (SOC)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Soil_Organic_Carbon_SOC.csv"),
        use_weight=False),
    'Weight for financial variable on degraded area': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Weight_for_financial_variable_on_degraded_area.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Afforestation'
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
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0],
            dtype=np.object).set_index('param')
        ad_data_sources = {
            'Raw Data for ALL LAND TYPES': {
                'FAO 2015': THISDIR.joinpath('ad', 'ad_FAO_2015.csv'),
            },
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            main_includes_regional=True,
            adconfig=adconfig)

        # Custom PDS Data
        ca_pds_columns = ['Year'] + dd.REGIONS
        adoption_2014 = self.ac.ref_base_adoption['World']
        tla_2050 = self.tla_per_region.loc[2050, 'World']
        tla_afforestation = 717.972721643776
        tla_bamboo = 363.757256176669
        tla_perennial_bioenergy = 264.89533875
        tla_all_biomass = tla_afforestation + tla_bamboo + tla_perennial_bioenergy
        ds6_percent_afforestation = tla_afforestation / tla_all_biomass
        ds6_percent_adoption_2050 = (1614 * ds6_percent_afforestation) / tla_all_biomass
        ds6_adoption_2050 = ds6_percent_adoption_2050 * tla_2050
        ds7_percent_adoption_2050 = 1614 / tla_all_biomass
        ds7_adoption_2050 = ds7_percent_adoption_2050 * tla_2050

        ca_pds_data_sources = [
                {'name': 'Regional linear trend', 'include': True, 'datapoints_degree': 1,
              # Future forest plantation area is projected based on country level data available
              # for the year 1990, 2000, 2005, and 2010 from the FAO's Forest Resource Assessment
              # report from 2015. 
              #
              # Country level data about planted forest area from 1990 - 2014 was aggregated at
              # the regional level (for details see hidden ""HistoricAndProjectedData"" sheet).
              # This data was then used to project future adoption using a linear trend.
             'datapoints': pd.DataFrame([
                [1990, np.nan, 96.8914, 44.1631, 106.1562, 16.5338, 14.9281, 0.0, 0.0, 0.0, 0.0],
                [2000, np.nan, 97.2555, 44.2605, 107.5489, 16.7251, 15.2771, 0.0, 0.0, 0.0, 0.0],
                [2005, np.nan, 97.6355, 44.3794, 109.8028, 16.9607, 15.6649, 0.0, 0.0, 0.0, 0.0],
                [2010, np.nan, 97.8700, 44.4540, 111.5210, 17.1760, 16.0730, 0.0, 0.0, 0.0, 0.0],
                [2014, np.nan, 98.1783330003811, 44.5558196042818, 113.7890763825080,
                    17.4259450169749, 16.5131623025461, 0.0, 0.0, 0.0, 0.0],
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Regional max linear trend', 'include': True,
              # "Future forest plantation area is projected based on country level data available
              # for the year 1990, 2000, 2005, and 2010 from the FAO's Forest Resource Assessment
              # report from 2015. Country level data about planted forest area from 1990 - 2014
              # was aggregated at the regional level, and used to determine regional annual growth
              # rates. For details about the calculations of regional rates see hidden
              # ""HistoricAndProjectedData"" sheet).
              #
              # In this scenario, regional future adoption of forest plantations is projected
              # based on the maximum historical regional growth rate reported in the respective
              # region (between 1990 - 2014). For each region, future adoption projected based
              # on the maximum linear regional trend between any two given time periods.
             'datapoints': pd.DataFrame([
                [2010, np.nan, 97.8700, 44.4540, 111.5210, 17.1760, 16.0730, 0.0, 0.0, 0.0, 0.0],
                [2014, np.nan, 98.1783330003811, 44.5558196042818, 113.7890763825080,
                    17.4259450169749, 16.5131623025461, 0.0, 0.0, 0.0, 0.0],
                 ], columns=ca_pds_columns).set_index('Year')},
            {'name': '50% of the max historical annual afforestation rate across the regions', 'include': True,
              # Future forest plantation area is projected based on country level data available
              # for the year 1990, 2000, 2005, and 2010 from the FAO's Forest Resource Assessment
              # report from 2015. Country level data about planted forest area from 1990 - 2014
              # was aggregated at the regional level, and used to determine regional annual growth
              # rates. For details about the calculations of regional rates see hidden
              # "HistoricAndProjectedData" sheet).
              #
              # In this scenario, regional future adoption of forest plantations is projected
              # based on the maximum historical regional growth rate across all regions (between
              # 1990 - 2014), which occurred in Asia (0.57 Mha annual increase between 2010 -2014). 
              # For the ASIA region this same rate (0.57 Mha annual increase) is used for
              # projecting the future adoption of forest plantation. For all other regions half
              # of this growth rate is applied (0.29 Mha annual increase).
             'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_50_of_the_max_historical_annual_afforestation_rate_across_the_regions.csv')},
            {'name': '100% of the max historical annual afforestation rate across the regions', 'include': True,
             # Future forest plantation area is projected based on country level data available
             # for the year 1990, 2000, 2005, and 2010 from the FAO's Forest Resource Assessment
             # report from 2015. Country level data about planted forest area from 1990 - 2014
             # was aggregated at the regional level, and used to determine regional annual growth
             # rates. For details about the calculations of regional rates see hidden
             # "HistoricAndProjectedData" sheet).
             #
             # In this scenario, regional future adoption of forest plantations is projected
             # based on the maximum historical regional growth rate across all regions (between
             # 1990 - 2014), which occurred in Asia (0.57 Mha increase between 2010 -2014). 
             # To project future adoption of forest plantations, this rate was applied to all
             # regions, including Asia (0.57 Mha annual increase).
             'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_100_of_the_max_historical_annual_afforestation_rate_across_the_regions.csv')},
            {'name': '200% increase for Asia and 100% for the other regions', 'include': True,
              # Future forest plantation area is projected based on country level data available
              # for the year 1990, 2000, 2005, and 2010 from the FAO's Forest Resource Assessment
              # report from 2015. Country level data about planted forest area from 1990 - 2014
              # was aggregated at the regional level, and used to determine regional annual growth
              # rates. For details about the calculations of regional rates see hidden
              # "HistoricAndProjectedData" sheet).
              #
              # In this scenario, regional future adoption of forest plantations is projected
              # based on the maximum historical regional growth rate across all regions (between
              # 1990 - 2014), which occurred in Asia (0.57 Mha increase between 2010 -2014). 
              # To project future adoption of forest plantations, this rate was applied to all
              # regions (0.57 Mha annual increase) except for Asia region where the rate was
              # doubled (1.14 Mha annual increase).
             'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_200_increase_for_Asia_and_100_for_the_other_regions.csv')},
            {'name': 'Conservative growth projection based on Kreidenweis et al. (2016)', 'include': True,
              # This projection of future adoption of afforestation is based on Kreidenweis
              # et al. (2016)'s ""global afforestation"" scenario, which assumes 1614 Mha total
              # afforested area by 2050. 
              # We calculated the proportion of this projection based on the percent of
              # afforestation to the total TLA set for the biomass crops as per 2019 land
              # allocation model. This proportion was applied to TLA set for this solution
              # allocated on forest AEZs.
             'datapoints': pd.DataFrame([
                 [2014, adoption_2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [2050, ds6_adoption_2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 ], columns=ca_pds_columns).set_index('Year'),
             'maximum': tla_bamboo},
            {'name': 'High growth projection based on Kreidenweis et al. (2016)', 'include': True,
              # "This projection of future adoption of afforestation is based on Kreidenweis
              # et al. (2016)'s ""global afforestation"" scenario, which assumes 1614 Mha total
              # afforested area by 2050. 
              # We calculated the proportion of this projection based on the percent of
              # afforestation to the total TLA set for the biomass crops as per 2019 land
              # allocation model.  This proportion was applied to TLA set for this solution
              # allocated on forest AEZs.
             'datapoints': pd.DataFrame([
                 [2014, adoption_2014, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [2050, ds7_adoption_2050, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Linear projections based on  Evans (2009) publication', 'include': True,
              # Projections of future adoption of forest plantations are based on the total
              # predicted area of planted forest in 2030 (344.5 Mha), as reported by Evans (2009),
              # see Table 5.5. The predictions are made according to two scenarios (Scenario 2:
              # "Business as Usual" and Scenario 3: "Higher Productivity") described in
              # Table 5.2 of the publication.
             'datapoints': pd.DataFrame([
                 [2014, 294.140179643776, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 [2030, 344.500000000000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                 ], columns=ca_pds_columns).set_index('Year')},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=0.5, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

        # Manual adjustment made in spreadsheet for Drawdown 2020.
        for s in self.pds_ca.scenarios.values():
            df = s['df']
            df.loc[2014] = [290.462336306692, 98.1783330003811, 44.5558196042818, 113.789076382508,
                    17.4259450169749, 16.5131623025461, 0.0, 0.0, 0.0, 0.0]
            df.loc[2015] = [291.336550416405, 98.2542011640878, 44.5812227272287, 114.378174359749,
                    17.4918608321974, 16.6310913331414, 0.0, 0.0, 0.0, 0.0]
            df.loc[2016] = [292.240912741787, 98.3317866108997, 44.6073285492058, 114.988603296961,
                    17.5600505509306, 16.7531437337891, 0.0, 0.0, 0.0, 0.0]
            df.loc[2017] = [293.175447683892, 98.4110924492030, 44.6341380907823, 115.620380827999,
                    17.6305154458053, 16.8793208701027, 0.0, 0.0, 0.0, 0.0]
            df.loc[2018] = [294.140179643776, 98.4921217873836, 44.6616523725276, 116.273524586716,
                    17.7032567894526, 17.0096241076960, 0.0, 0.0, 0.0, 0.0]

        # Custom REF Data
        ca_ref_data_sources = [
            {'name': '[Type Scenario 1 Name Here (REF CASE)...]', 'include': True,
                'filename': THISDIR.joinpath('ca_ref_data', 'custom_ref_ad_Type_Scenario_1_Name_Here_REF_CASE_.csv')},
        ]
        self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
            soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)

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
        ht_ref_adoption_final = self.tla_per_region.loc[2050] * (ht_ref_adoption_initial / self.tla_per_region.loc[2014])
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
            use_first_pds_datapoint_main=False,
            adoption_base_year=2018,
            copy_pds_to_ref=False,
            copy_ref_datapoint=False,
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
            annual_land_area_harvested=self.ua.soln_pds_annual_land_area_harvested(),
            regime_distribution=self.ae.get_land_distribution(),
            regimes=dd.THERMAL_MOISTURE_REGIMES8)

