"""Utility Scale Solar Photovoltaics solution model.
   solarpvutil_*
"""

import pathlib

import advanced_controls
from model import firstcost
from model import helpertables
from model import operatingcost
from model import tam
from model import unitadoption


class SolarPVUtil:
  def __init__(self):
    super()
    self.ac = advanced_controls.AdvancedControls(
        pds_2014_cost=1444.93954421485,
        ref_2014_cost=1444.93954421485,
        conv_2014_cost=2010.03170851964,
        soln_first_cost_efficiency_rate=0.196222222222222,
        soln_first_cost_below_conv=True,
        conv_first_cost_efficiency_rate=0.02,

        report_end_year=2050,
        soln_lifetime_capacity=48343.8,
        soln_avg_annual_use=1841.66857142857,
        conv_lifetime_capacity=182411.275767661,
        conv_avg_annual_use=4946.840187342,
        conv_var_oper_cost_per_funit=0.00375269040,
        conv_fuel_cost_per_funit=0.0731,
        conv_fixed_oper_cost_per_iunit=32.95140431108,
        soln_var_oper_cost_per_funit=0.0,
        soln_fuel_cost_per_funit=0.0,
        soln_fixed_oper_cost_per_iunit=23.18791293579,

        ref_adoption_regional_data=False,
        npv_discount_rate=0.094,

        emissions_grid_source="ipcc_only",
        emissions_grid_range="mean"
        )

    solution_dir = pathlib.Path(__file__)
    ref_tam_per_region_filename = solution_dir.joinpath('solarpvutil_ref_tam_per_region.csv')
    pds_tam_per_region_filename = solution_dir.joinpath('solarpvutil_pds_tam_per_region.csv')
    self.tm = tam.TAM(ref_tam_per_region_filename=ref_tam_per_region_filename,
        pds_tam_per_region_filename=pds_tam_per_region_filename)
    self.ht = helpertables.HelperTables(ac=self.ac)
    self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=2,
        ref_learning_increase_mult=2, conv_learning_increase_mult=2)
    self.oc = operatingcost.OperatingCost(ac=self.ac)
    self.ua = unitadoption.UnitAdoption(ac=self.ac)
