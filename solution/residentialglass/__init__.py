# High-Performance Glass (Residential) solution model.
# Originally exported from: Glass_RRS_Model_Residential-Aug21.xlsm

from pathlib import Path
import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls as ac
from model import ch4calcs
from model import co2calcs
from model import conversions
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

DATADIR = Path(__file__).parents[2]/'data'
THISDIR = Path(__file__).parent
VMAs = vma.VMA.load_vma_directory(THISDIR/'vma_data/vma_sources.json')

units = {
    "implementation unit": "million sq-meters",
    "functional unit": "million sq-meters",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'High-Performance Glass (Residential)'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR/'ac', vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-72p2050-2.75% Retrofit Rate - Integrated"
PDS2 = "PDS2-87p2050-5% Retrofit Rate - Integrated"
PDS3 = "PDS3-95p2050-8% Retrofit Rate - Integrated"

class Scenario(scenario.RRSScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category
    module_name = THISDIR.stem
    base_year = 2018

    def __init__(self, scen=None):
        # AC
        self.initialize_ac(scen, scenarios, PDS2)

        # TAM

        # Instructions: Set TAM override parameters appropriately if any of these vary from the standard (then delete these comments):
        # trend (3rd Poly): 3rd Poly 3rd Poly 3rd Poly 3rd Poly 3rd Poly 3rd Poly 3rd Poly 3rd Poly 3rd Poly 3rd Poly
        # growth (medium): Medium Medium Medium Medium Medium Medium Medium Medium Medium Medium
        # low_sd_mult (1.0): 1 1 1 1 1 1 1 1 1 1
        # high_sd_mult (1.0): 1 1 1 1 1 1 1 1 1 1

        self._ref_tam_sources = scenario.load_sources(THISDIR/'tam/tam_ref_sources.json','*')
        self._pds_tam_sources = self._ref_tam_sources
        self.set_tam()
        ref_tam_per_region=self.tm.ref_tam_per_region()
        pds_tam_per_region=self.tm.pds_tam_per_region()

        # ADOPTION
        self._pds_ca_sources = scenario.load_sources(THISDIR/'ca_pds_data/ca_pds_sources.json', 'filename')
        (ref_adoption_data_per_region,
         pds_adoption_data_per_region,
         pds_adoption_trend_per_region,
         pds_adoption_is_single_source) = self.initialize_adoption_bases()

        final_year=2050  # Currently fixed for all models; may be variable in the future.
        ht_ref_adoption_initial = pd.Series(self.ac.ref_base_adoption)
        ht_ref_adoption_final = (ref_tam_per_region.loc[final_year] * 
            (ht_ref_adoption_initial / ref_tam_per_region.loc[self.base_year]))
        ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_ref_datapoints.loc[self.base_year] = ht_ref_adoption_initial
        ht_ref_datapoints.loc[final_year] = ht_ref_adoption_final
        pds_initial_year = 2018  # sometimes, but rarely, different than self.base_year
                                # Excel 'Helper Tables'!B85
        ht_pds_adoption_initial = ht_ref_adoption_initial
        ht_pds_adoption_final_percentage = pd.Series(self.ac.pds_adoption_final_percentage)
        ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[final_year]
        ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_pds_datapoints.loc[pds_initial_year] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[final_year] = ht_pds_adoption_final
        self.ht = helpertables.HelperTables(ac=self.ac,
            ref_datapoints=ht_ref_datapoints,
            pds_datapoints=ht_pds_datapoints,
            ref_adoption_data_per_region=ref_adoption_data_per_region,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=ref_tam_per_region,
            pds_adoption_limits=pds_tam_per_region,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            # Quirks Parameters.  The extractor should get these right in most cases.
            # If it fails, check the documentation for HelperTables.__init__() to see how these are used.
            copy_pds_to_ref=False,
            copy_ref_datapoint=False,
            copy_pds_datapoint="Ref Table",
            copy_pds_world_too=True,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        # DERIVED VALUES

        # Emissions: if this is an older model, you may need to set a data version to make tests pass.
        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=ref_tam_per_region,
            pds_total_adoption_units=pds_tam_per_region,
            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
            repeated_cost_for_iunits=False,
            # Quirks parameters
            replacement_period_offset=0,
            bug_cfunits_double_count=False)
        soln_pds_tot_iunits_reqd = self.ua.soln_pds_tot_iunits_reqd()
        soln_ref_tot_iunits_reqd = self.ua.soln_ref_tot_iunits_reqd()
        conv_ref_tot_iunits = self.ua.conv_ref_tot_iunits()
        soln_net_annual_funits_adopted=self.ua.soln_net_annual_funits_adopted()

        self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=2,
            ref_learning_increase_mult=2,
            conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
            soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
            conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
            fc_convert_iunit_factor=1)

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
            conversion_factor=1)

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

