"""Green Roofs solution model.
     Excel filename: Drawdown-Green Roofs_RRS_v1.1_18Nov2018_PUBLIC.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls as ac
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
from model import tam
from solution import rrs

DATADIR = pathlib.Path(__file__).parents[2].joinpath('data')
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = {
    'Current Adoption': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "Current_Adoption.csv"),
            use_weight=False),
    'CONVENTIONAL First Cost per Implementation Unit': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_First_Cost_per_Implementation_Unit.csv"),
            use_weight=False),
    'SOLUTION First Cost per Implementation Unit': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
            use_weight=False),
    'CONVENTIONAL Lifetime Capacity': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Lifetime_Capacity.csv"),
            use_weight=False),
    'SOLUTION Lifetime Capacity': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "SOLUTION_Lifetime_Capacity.csv"),
            use_weight=False),
    'CONVENTIONAL Average Annual Use': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Average_Annual_Use.csv"),
            use_weight=False),
    'SOLUTION Average Annual Use': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "SOLUTION_Average_Annual_Use.csv"),
            use_weight=False),
    'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
            use_weight=False),
    'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "SOLUTION_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
            use_weight=False),
    'CONVENTIONAL Fixed Operating Cost (FOM)': vma.VMA(
            filename=None, use_weight=False),
    'SOLUTION Fixed Operating Cost (FOM)': vma.VMA(
            filename=None, use_weight=False),
    'CONVENTIONAL Total Energy Used per Functional Unit': vma.VMA(
            filename=None, use_weight=False),
    'SOLUTION Energy Efficiency Factor': vma.VMA(
            filename=None, use_weight=False),
    'SOLUTION Total Energy Used per Functional Unit': vma.VMA(
            filename=None, use_weight=False),
    'CONVENTIONAL Fuel Consumed per Functional Unit': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Fuel_Consumed_per_Functional_Unit.csv"),
            use_weight=False),
    'SOLUTION Fuel Efficiency Factor': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "SOLUTION_Fuel_Efficiency_Factor.csv"),
            use_weight=False),
    'CONVENTIONAL Direct Emissions per Functional Unit': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Direct_Emissions_per_Functional_Unit.csv"),
            use_weight=False),
    'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
            filename=None, use_weight=False),
    'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
            filename=None, use_weight=False),
    'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
            filename=None, use_weight=False),
    'CH4-CO2eq Tons Reduced': vma.VMA(
            filename=None, use_weight=False),
    'N2O-CO2eq Tons Reduced': vma.VMA(
            filename=None, use_weight=False),
    'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
            filename=None, use_weight=False),
    'SOLUTION Revenue per Functional Unit': vma.VMA(
            filename=None, use_weight=False),
    'Global Average Number of Floors Commercial Buildings': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "Global_Average_Number_of_Floors_Commercial_Buildings.csv"),
            use_weight=False),
    'Global Average Number of Floors Residential Buildings': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "Global_Average_Number_of_Floors_Residential_Buildings.csv"),
            use_weight=False),
    'Operating and Maintenance Costs per m2 CONVENTIONAL': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "Operating_and_Maintenance_Costs_per_m2_CONVENTIONAL.csv"),
            use_weight=False),
    'Operating and Maintenance Costs per m2 SOLUTION': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "Operating_and_Maintenance_Costs_per_m2_SOLUTION.csv"),
            use_weight=False),
    'STORMWATER Related Costs CONVENTIONAL': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "STORMWATER_Related_Costs_CONVENTIONAL.csv"),
            use_weight=False),
    'STORMWATER Related Costs SOLUTION': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "STORMWATER_Related_Costs_SOLUTION.csv"),
            use_weight=False),
    'ENERGY RELATED Operating Cost Benefits SOLUTION (per m2)': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "ENERGY_RELATED_Operating_Cost_Benefits_SOLUTION_per_m2.csv"),
            use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "m²",
    "functional unit": "m²",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Green Roofs'
solution_category = ac.SOLUTION_CATEGORY.NOT_APPLICABLE

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-30p2050-Integrated-FE-12.75% (Book)"
PDS2 = "PDS2-50p2050-Integrated-FE-12.6% (Book)"
PDS3 = "PDS3-75p2050-Integrated-FE-12.54% (Book)"

class Scenario(scenario.RRSScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category
    module_name = THISDIR.stem

    _ref_tam_sources = scenario.load_sources(THISDIR/'tam'/'tam_ref_sources.json','*')
    _pds_tam_sources=_ref_tam_sources

    def __init__(self, scen=None):
        # AC
        self.initialize_ac(scen, scenarios, PDS2)

        # TAM
        self.set_tam()
        ref_tam_per_region=self.tm.ref_tam_per_region()
        pds_tam_per_region=self.tm.pds_tam_per_region()

        # ADOPTION
        sconfig_list = [['region', 'base_year', 'last_year'],
            ['World', 2014, 2050],
            ['OECD90', 2014, 2050],
            ['Eastern Europe', 2014, 2050],
            ['Asia (Sans Japan)', 2014, 2050],
            ['Middle East and Africa', 2014, 2050],
            ['Latin America', 2014, 2050],
            ['China', 2014, 2050],
            ['India', 2014, 2050],
            ['EU', 2014, 2050],
            ['USA', 2014, 2050]]
        sconfig = pd.DataFrame(sconfig_list[1:], columns=sconfig_list[0]).set_index('region')
        sconfig['pds_tam_2050'] = pds_tam_per_region.loc[[2050]].T
        sc_regions, sc_percentages = zip(*self.ac.pds_base_adoption)
        sconfig['base_adoption'] = pd.Series(list(sc_percentages), index=list(sc_regions))
        sconfig['base_percent'] = sconfig['base_adoption'] / pds_tam_per_region.loc[2014]
        sc_regions, sc_percentages = zip(*self.ac.pds_adoption_final_percentage)
        sconfig['last_percent'] = pd.Series(list(sc_percentages), index=list(sc_regions))
        if self.ac.pds_adoption_s_curve_innovation is not None:
            sc_regions, sc_percentages = zip(*self.ac.pds_adoption_s_curve_innovation)
            sconfig['innovation'] = pd.Series(list(sc_percentages), index=list(sc_regions))
        if self.ac.pds_adoption_s_curve_imitation is not None:
            sc_regions, sc_percentages = zip(*self.ac.pds_adoption_s_curve_imitation)
            sconfig['imitation'] = pd.Series(list(sc_percentages), index=list(sc_regions))
        self.sc = s_curve.SCurve(transition_period=16, sconfig=sconfig)

        self.initialize_adoption_bases()
        ref_adoption_data_per_region = None

        if False:
            # One may wonder why this is here. This file was code generated.
            # This 'if False' allows subsequent conditions to all be elif.
            pass
        elif self.ac.soln_pds_adoption_basis == 'Logistic S-Curve':
            pds_adoption_data_per_region = None
            pds_adoption_trend_per_region = self.sc.logistic_adoption()
            pds_adoption_is_single_source = None
        elif self.ac.soln_pds_adoption_basis == 'Bass Diffusion S-Curve':
            pds_adoption_data_per_region = None
            pds_adoption_trend_per_region = self.sc.bass_diffusion_adoption()
            pds_adoption_is_single_source = None
        elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
            pds_adoption_data_per_region = self.ad.adoption_data_per_region()
            pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()
            pds_adoption_is_single_source = self.ad.adoption_is_single_source()

        ht_ref_adoption_initial = pd.Series(
            [165284837.0, 153214036.0, 2001574.0, 10001070.0, 1759.0,
             66398.0, 10000000.0, 1070.0, 129000000.0, 21532448.0],
             index=dd.REGIONS)
        ht_ref_adoption_final = ref_tam_per_region.loc[2050] * (ht_ref_adoption_initial / ref_tam_per_region.loc[2014])
        ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
        ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
        ht_pds_adoption_initial = ht_ref_adoption_initial
        ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)
        ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))
        ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[2050]
        ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
        self.ht = helpertables.HelperTables(ac=self.ac,
                ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
                pds_adoption_data_per_region=pds_adoption_data_per_region,
                ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
                pds_adoption_trend_per_region=pds_adoption_trend_per_region,
                pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
                ref_total_adoption_units=ref_tam_per_region, pds_total_adoption_units=pds_tam_per_region,
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
                fc_convert_iunit_factor=1.0)

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
                conversion_factor=1.0)

        self.c4 = ch4calcs.CH4Calcs(ac=self.ac,
                soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

        self.c2 = co2calcs.CO2Calcs(ac=self.ac,
                ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
                soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),
                soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),
                soln_pds_direct_co2_emissions_saved=self.ua.soln_pds_direct_co2_emissions_saved(),
                soln_pds_direct_ch4_co2_emissions_saved=self.ua.soln_pds_direct_ch4_co2_emissions_saved(),
                soln_pds_direct_n2o_co2_emissions_saved=self.ua.soln_pds_direct_n2o_co2_emissions_saved(),
                soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
                soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
                conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
                conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
                conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
                soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
                fuel_in_liters=False)

        self.r2s = rrs.RRS(total_energy_demand=ref_tam_per_region.loc[2014, 'World'],
                soln_avg_annual_use=self.ac.soln_avg_annual_use,
                conv_avg_annual_use=self.ac.conv_avg_annual_use)
