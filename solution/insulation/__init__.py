"""Insulation solution model.
         Excel filename: Drawdown-Insulation_RRS_v1,1_18Dec2018_PUBLIC.xlsm
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
                        filename=None, use_weight=False),
        'SOLUTION Lifetime Capacity': vma.VMA(
                        filename=None, use_weight=False),
        'CONVENTIONAL Average Annual Use': vma.VMA(
                        filename=None, use_weight=False),
        'SOLUTION Average Annual Use': vma.VMA(
                        filename=None, use_weight=False),
        'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
                        filename=None, use_weight=False),
        'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
                        filename=None, use_weight=False),
        'CONVENTIONAL Fixed Operating Cost (FOM)': vma.VMA(
                        filename=None, use_weight=False),
        'SOLUTION Fixed Operating Cost (FOM)': vma.VMA(
                        filename=None, use_weight=False),
        'CONVENTIONAL Total Energy Used per Functional Unit': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Total_Energy_Used_per_Functional_Unit.csv"),
                        use_weight=False),
        'SOLUTION Energy Efficiency Factor': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "SOLUTION_Energy_Efficiency_Factor.csv"),
                        use_weight=False),
        'SOLUTION Total Energy Used per Functional Unit': vma.VMA(
                        filename=None, use_weight=False),
        'CONVENTIONAL Fuel Consumed per Functional Unit': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Fuel_Consumed_per_Functional_Unit.csv"),
                        use_weight=False),
        'SOLUTION Fuel Efficiency Factor': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "SOLUTION_Fuel_Efficiency_Factor.csv"),
                        use_weight=False),
        'CONVENTIONAL Direct Emissions per Functional Unit': vma.VMA(
                        filename=None, use_weight=False),
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
        'Threshold  Avg. Annual Temperature Gradient of Cooling': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "Threshold_Avg_Annual_Temperature_Gradient_of_Cooling.csv"),
                        use_weight=False),
        'Average Commercial Building Wall Height': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "Average_Commercial_Building_Wall_Height.csv"),
                        use_weight=False),
        'Average Residential Building Wall Height': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "Average_Residential_Building_Wall_Height.csv"),
                        use_weight=False),
        'Average Commercial Building Floor Count': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "Average_Commercial_Building_Floor_Count.csv"),
                        use_weight=False),
        'Average Residential Building Floor Count': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "Average_Residential_Building_Floor_Count.csv"),
                        use_weight=False),
        'Individual Commercial:Residential Building Floor Area Ratio': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "Individual_Commercial_Residential_Building_Floor_Area_Ratio.csv"),
                        use_weight=False),
        'Conventional Insulation R-value for Cold Latitudes': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "Conventional_Insulation_R_value_for_Cold_Latitudes.csv"),
                        use_weight=False),
        'Solution Insulation R-value for Cold Latitudes': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "Solution_Insulation_R_value_for_Cold_Latitudes.csv"),
                        use_weight=False),
        'Surface Area per Floor Area Ratio': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "Surface_Area_per_Floor_Area_Ratio.csv"),
                        use_weight=False),
        'Discount Rate - Households': vma.VMA(
                        filename=THISDIR.joinpath("vma_data", "Discount_Rate_Households.csv"),
                        use_weight=False),
        # Denise 9/2021: Added VMAs from new model to enable integration calcs
        'Envelope Surface Area per Floor Area Ratio': vma.VMA(
            filename=THISDIR.joinpath("vma_data", "Envelope_Surface_Area_per_Floor_Area_Ratio.csv"),
            use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
        "implementation unit": "Mm²",
        "functional unit": "Mm²",
        "first cost": "US$B",
        "operating cost": "US$B",
}

name = 'Insulation'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-69p2050-Slow Growth, Medium (Book Ed.1)"
PDS2 = "PDS2-100p2050-Medium Growth, Medium (Book Ed.1)"
PDS3 = "PDS3-100p2050-High Growth, Lower (Book Ed.1)"

class Scenario(scenario.RRSScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category
    module_name = THISDIR.stem

    _ref_tam_sources = scenario.load_sources(THISDIR/'tam'/'tam_ref_sources.json','*')
    _pds_tam_sources = _ref_tam_sources
    _ref_ca_sources = scenario.load_sources(THISDIR/'ca_ref_data'/'ca_ref_sources.json', 'filename')
    _pds_ca_sources = scenario.load_sources(THISDIR/'ca_pds_data'/'ca_pds_sources.json', 'filename')

    def __init__(self, scen=None):
        # AC
        self.initialize_ac(scen, scenarios, PDS2)

        # TAM
        self.set_tam()
        ref_tam_per_region=self.tm.ref_tam_per_region()
        pds_tam_per_region=self.tm.pds_tam_per_region()

        # ADOPTION
        self.initialize_adoption_bases()
        ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()

        if False:
            # One may wonder why this is here. This file was code generated.
            # This 'if False' allows subsequent conditions to all be elif.
            pass
        elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
            pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
            pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
            pds_adoption_is_single_source = None

        ht_ref_adoption_initial = pd.Series(
            [35739.10972659552, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0],
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

    def adoption_as_material_mass(self):
            """Calculate the mass of insulation material required each year by adoption in this scenario.
            Units: million tonnes insulating material.  Assumes cellulose density."""
            # Excel Biomass tab, column G
            
            (factor1,_,_) = self.vmas['Envelope Surface Area per Floor Area Ratio'].avg_high_low()
            
            # This is a calculated value in the workbook.  I am short circuiting to a simple value for now:
            # Biomass!B12 "Average % of Solution Low-EC"
            factor2 = 0.17955112
            
            # This is a calculated value in the workbook.  I am short circuiting to a simple value for now:
            # Biomass!B13 "Thickness of material (m) based on Conductivity"
            factor3 = 0.0256596

            # This is a simple value from the workbook.  VMA!M756 "Density of Final Material (kg/m3)"
            factor4 = 50

            #This is a simple value from the workbook.  Biomass!B15 
            # "Assumed Ratio of Raw Material to Final Material by Mass (production efficiency)"
            factor5 = 1/0.85

            # The calculations for biomass columns D, E, F
            netfactor = factor1*factor2*factor3*factor4*factor5 / 10**3

            # NOTE: the "diff" leaves the first row empty, which matches the Excel, but seems wrong.
            return (self.ht.soln_pds_funits_adopted()['World'] * netfactor).diff()


