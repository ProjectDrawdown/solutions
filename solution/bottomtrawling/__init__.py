""" Test solution file for Oceans model based on Limiting Bottom Trawling solution """

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls
from model import dez
from model import ch4calcs
from model import co2calcs
from model import customadoption
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import operatingcost
from model import s_curve
from model import unitadoption
from model import vma
from model.advanced_controls import SOLUTION_CATEGORY
from model.dd import OCEAN_REGIONS

from model import toa
from solution import land

DATADIR = str(pathlib.Path(__file__).parents[2].joinpath('data'))
THISDIR = pathlib.Path(__file__).parents[0]

scenarios = {
    'default': advanced_controls.AdvancedControls(

        # general
        solution_category=SOLUTION_CATEGORY.OCEAN,
        # vmas=VMAs,
        report_start_year=2020, report_end_year=2050,

        # adoption
        # soln_ref_adoption_regional_data=False, soln_pds_adoption_regional_data=False,
        soln_pds_adoption_basis='Linear',
        # soln_pds_adoption_custom_name='Average of All Custom Scenarios',
        pds_adoption_final_percentage=[
            ('World', 1.0), ('OECD90', 1.0), ('Eastern Europe', 1.0), ('Asia (Sans Japan)', 1.0),
            ('Middle East and Africa', 1.0), ('Latin America', 1.0), ('ABNJ', 1.0),
            ('China', 1.0), ('India', 1.0), ('EU', 1.0), ('USA', 1.0)],

        # financial
        pds_2014_cost=0.0, ref_2014_cost=0.0,
        conv_2014_cost=0.0,
        soln_first_cost_efficiency_rate=0.0,
        conv_first_cost_efficiency_rate=0.0,
        npv_discount_rate=0.1,
        soln_expected_lifetime=30.0,
        conv_expected_lifetime=30.0,
        yield_from_conv_practice=0.0,
        yield_gain_from_conv_to_soln=0.0,

        soln_fixed_oper_cost_per_iunit=0.0,
        conv_fixed_oper_cost_per_iunit=0.0,

        # emissions
        soln_indirect_co2_per_iunit=0.0,
        conv_indirect_co2_per_unit=0.0,
        soln_annual_energy_used=0.0, conv_annual_energy_used=0.0,

        tco2eq_reduced_per_land_unit=5.0,
        tco2eq_rplu_rate='One-time',

        emissions_grid_source='Meta-Analysis', emissions_grid_range='Mean',
        emissions_use_co2eq=True,
        emissions_use_agg_co2eq=True,

        # sequestration
        seq_rate_global=0.,
        disturbance_rate=0.02,
    )
}


class Scenario:
    name = 'Limiting bottom trawling'
    units = {
        "implementation unit": None,
        "functional unit": "Mha",
        "first cost": "US$B",
        "operating cost": "US$B",
    }

    def __init__(self, scenario=None):
        if scenario is None:
            scenario = 'default'
        self.scenario = scenario
        self.ac = scenarios[scenario]

        # TOA
        self.de = dez.DEZ(solution_name=self.name)
        self.toa_per_region = toa.toa_per_region(self.de.get_ocean_distribution())

        if self.ac.soln_pds_adoption_basis == 'Linear':
            pds_adoption_data_per_region = None
            pds_adoption_trend_per_region = None
            pds_adoption_is_single_source = False

        ht_ref_adoption_initial = pd.Series([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                                            index=OCEAN_REGIONS)
        ht_ref_adoption_final = self.toa_per_region.loc[2050] * (
            ht_ref_adoption_initial / self.toa_per_region.loc[2014])
        ht_ref_datapoints = pd.DataFrame(columns=OCEAN_REGIONS)
        ht_ref_datapoints.loc[2014] = ht_ref_adoption_initial
        ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
        ht_pds_adoption_initial = ht_ref_adoption_initial
        ht_regions, ht_percentages = zip(*self.ac.pds_adoption_final_percentage)
        ht_pds_adoption_final_percentage = pd.Series(list(ht_percentages), index=list(ht_regions))
        ht_pds_adoption_final = ht_pds_adoption_final_percentage * self.toa_per_region.loc[2050]
        ht_pds_datapoints = pd.DataFrame(columns=OCEAN_REGIONS)
        ht_pds_datapoints.loc[2014] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
        self.ht = helpertables.HelperTables(
            ac=self.ac,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=self.toa_per_region,
            pds_adoption_limits=self.toa_per_region,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(
            ac=self.ac)

        self.ua = unitadoption.UnitAdoption(
            ac=self.ac,
            pds_total_adoption_units=self.toa_per_region,
            electricity_unit_factor=1000000.0,
            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
            bug_cfunits_double_count=True)

        soln_pds_tot_iunits_reqd = self.ua.soln_pds_tot_iunits_reqd()
        soln_ref_tot_iunits_reqd = self.ua.soln_ref_tot_iunits_reqd()
        conv_ref_tot_iunits = self.ua.conv_ref_tot_iunits()
        soln_net_annual_funits_adopted = self.ua.soln_net_annual_funits_adopted()

        self.fc = firstcost.FirstCost(
            ac=self.ac, pds_learning_increase_mult=2,
            ref_learning_increase_mult=2, conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
            soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
            conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
            conv_ref_first_cost_uses_tot_units=True,
            fc_convert_iunit_factor=land.MHA_TO_HA)

        self.oc = operatingcost.OperatingCost(
            ac=self.ac,
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
                                    soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

        self.c2 = co2calcs.CO2Calcs(
            ac=self.ac,
            ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
            soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),
            soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),
            soln_pds_direct_co2eq_emissions_saved=self.ua.direct_co2eq_emissions_saved_land(),
            # soln_pds_direct_co2_emissions_saved=self.ua.direct_co2_emissions_saved_land(),
            # soln_pds_direct_n2o_co2_emissions_saved=self.ua.direct_n2o_co2_emissions_saved_land(),
            # soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),
            soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
            soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
            conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
            conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
            conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            regime_distribution=self.de.get_ocean_distribution())
