"""
Silvopasture solution model (generated manually).
Excel filename: Silvopasture_L-Use_v1.1a_3Aug18.xlsm
"""

import pathlib
import pandas as pd
from os import listdir
from model import advanced_controls, aez, ch4calcs, co2calcs, customadoption, emissionsfactors, firstcost, \
    helpertables, operatingcost, tla, unitadoption, vma
from model.advanced_controls import SOLUTION_CATEGORY
from solution import land

DATADIR = str(pathlib.Path(__file__).parents[2].joinpath('data'))
THISDIR = pathlib.Path(__file__).parents[0]

VMAs = vma.generate_vma_dict(THISDIR.joinpath('vma_data'))

scenarios = {  # just 1 for now
    'PDS-45p2050-Plausible-PDScustom-low-BookVersion1': advanced_controls.AdvancedControls(
        solution_category=SOLUTION_CATEGORY.LAND,
        vmas=VMAs,
        report_start_year=2020, report_end_year=2050,

        # adoption
        soln_pds_adoption_basis='Fully Customized PDS',
        pds_adoption_use_ref_years=[2015, 2016],
        soln_expected_lifetime=30,
        conv_expected_lifetime=30,  # default for LAND models

        # financial
        soln_first_cost_efficiency_rate=0.0,  # default for LAND models
        conv_first_cost_efficiency_rate=0.0,  # default for LAND models
        conv_2014_cost=0.0,
        pds_2014_cost='mean',
        ref_2014_cost='mean',  # note that on xls this is linked to pds_2014_cost cell
        soln_fixed_oper_cost_per_iunit='mean',
        conv_fixed_oper_cost_per_iunit='mean',
        npv_discount_rate=0.1,

        # emissions
        emissions_grid_source='Meta-Analysis',
        emissions_grid_range='Mean',
        emissions_use_co2eq=True,
        soln_indirect_co2_per_iunit=0.,
        conv_indirect_co2_per_unit=0.,

        # sequestration
        seq_rate_global='mean'
    )}


class Silvopasture:
    name = 'Silvopasture'

    def __init__(self, scenario=None):
        if scenario is None:
            scenario = 'PDS-45p2050-Plausible-PDScustom-low-BookVersion1'
        self.scenario = scenario
        self.ac = scenarios[scenario]

        # TLA
        self.ae = aez.AEZ(solution_name=self.name)
        self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution())

        # This solution has Custom PDS data
        ca_pds_dir = THISDIR.joinpath('ca_pds_data')
        source_filenames = [f for f in listdir(ca_pds_dir) if f.endswith('.csv')]
        ca_pds_data_sources = []
        for f in source_filenames:
            include = True
            if f == 'High growth, linear trend.csv':
                include = False
            ca_pds_data_sources.append({'name': f, 'filename': f, 'include': include})
        self.ca_pds = customadoption.CustomAdoption(
            data_sources=ca_pds_data_sources,
            soln_adoption_custom_name='Low of All Custom Scenarios',
            filepath=ca_pds_dir)

        # Current adoption data comes from VMA
        self.current_adoption_vma = vma.VMA(THISDIR.joinpath('vma_data', 'Current_Adoption.csv'))
        adoption = [self.current_adoption_vma.avg_high_low(key='mean')] + [0] * 9
        ht_ref_datapoints = pd.DataFrame([[2014] + adoption, [2050] + adoption],
                                         columns=['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                                                  'Middle East and Africa', 'Latin America', 'China', 'India', 'EU',
                                                  'USA']).set_index('Year')
        ht_pds_datapoints = pd.DataFrame([[2014] + adoption, [2050] + [0] * 10],
                                         columns=['Year', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                                                  'Middle East and Africa', 'Latin America', 'China', 'India', 'EU',
                                                  'USA']).set_index('Year')
        self.ht = helpertables.HelperTables(
            ac=self.ac,
            pds_adoption_data_per_region=self.ca_pds.adoption_data_per_region(),
            ref_datapoints=ht_ref_datapoints,
            pds_datapoints=ht_pds_datapoints
        )

        self.ua = unitadoption.UnitAdoption(
            ac=self.ac,
            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
            tla_per_region=self.tla_per_region
        )

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
            fc_convert_iunit_factor=land.MHA_TO_HA
        )

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
            conversion_factor=land.MHA_TO_HA
        )

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac)

        # (This whole sheet is 0)
        self.c4 = ch4calcs.CH4Calcs(ac=self.ac,
                                    soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

        self.c2 = co2calcs.CO2Calcs(
            ac=self.ac,
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
            land_distribution=self.ae.get_land_distribution()
        )


if __name__ == '__main__':
    sp = Silvopasture()
