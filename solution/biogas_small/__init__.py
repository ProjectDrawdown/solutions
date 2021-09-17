"""Small Biogas Digesters solution model.
     Excel filename: Drawdown-Small Biogas Digesters_RRS_v1.1_28Nov2018_PUBLIC.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls as ac
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
            use_weight=True),
    'SOLUTION First Cost per Implementation Unit': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
            use_weight=False),
    'CONVENTIONAL Lifetime Capacity': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Lifetime_Capacity.csv"),
            use_weight=True),
    'SOLUTION Lifetime Capacity': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "SOLUTION_Lifetime_Capacity.csv"),
            use_weight=False),
    'CONVENTIONAL Average Annual Use': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Average_Annual_Use.csv"),
            use_weight=True),
    'SOLUTION Average Annual Use': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "SOLUTION_Average_Annual_Use.csv"),
            use_weight=False),
    'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Variable_Operating_Cost_VOM_per_Functional_Unit.csv"),
            use_weight=True),
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
            use_weight=True),
    'SOLUTION Fuel Efficiency Factor': vma.VMA(
            filename=None, use_weight=False),
    'CONVENTIONAL Direct Emissions per Functional Unit': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Direct_Emissions_per_Functional_Unit.csv"),
            use_weight=True),
    'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "SOLUTION_Direct_Emissions_per_Functional_Unit.csv"),
            use_weight=False),
    'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
            filename=None, use_weight=False),
    'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
            filename=None, use_weight=False),
    'CH4-CO2eq Tons Reduced': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "CH4_CO2eq_Tons_Reduced.csv"),
            use_weight=False),
    'N2O-CO2eq Tons Reduced': vma.VMA(
            filename=None, use_weight=False),
    'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
            filename=None, use_weight=False),
    'SOLUTION Revenue per Functional Unit': vma.VMA(
            filename=None, use_weight=False),
    'tCO2/yr per digester': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "tCO2_yr_per_digester.csv"),
            use_weight=False),
    'Black carbon GWP': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "Black_carbon_GWP.csv"),
            use_weight=False),
    't CO2 eq per Metric ton of fuel': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "t_CO2_eq_per_Metric_ton_of_fuel.csv"),
            use_weight=True),
    'Average Household Biodigester Production per year': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "Average_Household_Biodigester_Production_per_year.csv"),
            use_weight=False),
    'Kerosene (Heating Oil) Spot Price': vma.VMA(
            filename=DATADIR.joinpath(*('energy', 'vma_Kerosene_Heating_Oil_Spot_Price.csv')),
            use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "Biogas plant",
    "functional unit": "TWh (therms)",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Small Biogas Digesters'
solution_category = ac.SOLUTION_CATEGORY.NOT_APPLICABLE

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-2p2050_Asian Adoption (Book Ed.1)"
PDS2 = "PDS2-3p2050_Chinese Adoption (Book Ed.1)"
PDS3 = "PDS3-3p2050_Max Adoption (Book Ed.1)"

class Scenario(scenario.RRSScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category
    module_name = THISDIR.stem

    _ref_tam_sources = scenario.load_sources(THISDIR/'tam'/'tam_ref_sources.json','*')
    _pds_tam_sources=_ref_tam_sources
    _ref_ca_sources = scenario.load_sources(THISDIR/'ca_ref_data'/'ca_ref_sources.json', 'filename')
    _pds_ad_sources = scenario.load_sources(THISDIR/'ad'/'ad_sources.json', '*')

    def __init__(self, scen=None):
        # AC
        self.initialize_ac(scen, scenarios, PDS2)

        # TAM
        tam_config_values = [('growth','Asia (Sans Japan)', 'Low')]
        self.set_tam(config_values=tam_config_values)
        ref_tam_per_region=self.tm.ref_tam_per_region()
        pds_tam_per_region=self.tm.pds_tam_per_region()

        # ADOPTION
        self.initialize_adoption_bases()
        ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()

        if False:
            # One may wonder why this is here. This file was code generated.
            # This 'if False' allows subsequent conditions to all be elif.
            pass
        elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
            pds_adoption_data_per_region = self.ad.adoption_data_per_region()
            pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()
            pds_adoption_is_single_source = self.ad.adoption_is_single_source()

        ht_ref_adoption_initial = pd.Series(
            [86.0, 0.0, 0.0, 25.04194984517459, 5.337266131329677,
             36.925127117549664, 0.0, 0.0, 0.0, 0.0],
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
                ref_adoption_data_per_region=ref_adoption_data_per_region,
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
                conversion_factor=1000000000.0)

        self.c4 = ch4calcs.CH4Calcs(ac=self.ac,
                soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

        self.n2o = n2ocalcs.N2OCalcs(ac=self.ac,
                soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

        self.c2 = co2calcs.CO2Calcs(ac=self.ac,
                ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
                ch4_megatons_avoided_or_reduced=self.c4.ch4_megatons_avoided_or_reduced(),
                n2o_megatons_avoided_or_reduced=self.n2o.n2o_megatons_avoided_or_reduced(),
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
