"""Convert an Advanced Controls tab from an Excel solution file
   to the appropriate parameters in advanced_controls.py.
"""

import re

import xlrd

def cell_to_offsets(cell):
  (col, row) = filter(None, re.split(r'(\d+)', cell))
  colnum = 0
  for c in col:
    colnum = colnum * 26 + (ord(c.upper()) - ord('A'))
  return (int(row) - 1, colnum)

def is_float(val):
  try:
    float(val)
    return True
  except ValueError:
    return False

def is_int(val):
  try:
    int(val)
    return True
  except ValueError:
    return False

def format_val(val):
  if val == 'Y' or val == 'Yes':
    return 'True'
  if val == 'N':
    return 'False'
  if val == 'CH4-CO2eq' or val == 'N2O-CO2eq':  # I184 & J184
    return 'True'
  if val == 'Functional':  # F184
    return 'False'
  if val == 'Implementation':  # F184
    return 'True'
  if is_int(val):
    return str(int(val))
  if is_float(val):
    return str(float(val))
  return('"' + str(val) + '"')

wb = xlrd.open_workbook(filename='SolarPVUtility_RRS_ELECGEN_v1.1d_27Aug18.xlsm')
ac_tab = wb.sheet_by_name('Advanced Controls')

ac_variables = [
    ('pds_2014_cost', 'B128'),
    ('ref_2014_cost', 'B128'),
    ('conv_2014_cost', 'B95'),
    ('soln_first_cost_efficiency_rate', 'C128'),
    ('conv_first_cost_efficiency_rate', 'C95'),
    ('soln_first_cost_below_conv', 'C132'),
    ('soln_energy_efficiency_factor', 'C159'),
    ('conv_annual_energy_used', 'B159'),
    ('soln_annual_energy_used', 'D159'),
    ('conv_fuel_consumed_per_funit', 'F159'),
    ('soln_fuel_efficiency_factor', 'G159'),
    ('fuel_emissions_factor', 'I159'),
    ('fuel_emissions_factor_2', 'I163'),
    ('conv_emissions_per_funit', 'C174'),
    ('soln_emissions_per_funit', 'D174'),
    ('ch4_is_co2eq', 'I184'),
    ('n2o_is_co2eq', 'J184'),
    ('co2eq_conversion_source', 'I185'),
    ('ch4_co2_per_twh', 'I174'),
    ('n2o_co2_per_twh', 'J174'),
    ('soln_indirect_co2_per_iunit', 'G174'),
    ('conv_indirect_co2_per_unit', 'F174'),
    ('conv_indirect_co2_is_iunits', 'F184'),
    ('soln_lifetime_capacity', 'E128'),
    ('soln_avg_annual_use', 'F128'),
    ('conv_lifetime_capacity', 'E95'),
    ('conv_avg_annual_use', 'F95'),
    ('report_start_year', 'H4'),
    ('report_end_year', 'I4'),
    ('soln_var_oper_cost_per_funit', 'H128'),
    ('soln_fixed_oper_cost_per_iunit', 'I128'),
    ('soln_fuel_cost_per_funit', 'K128'),
    ('conv_var_oper_cost_per_funit', 'H95'),
    ('conv_fixed_oper_cost_per_iunit', 'I95'),
    ('conv_fuel_cost_per_funit', 'K95'),
    ('npv_discount_rate', 'B141'),
    ('emissions_use_co2eq', 'B189'),
    ('emissions_grid_source', 'C189'),
    ('emissions_grid_range', 'D189'),
    ('soln_ref_adoption_regional_data', 'B284'),
    ('soln_pds_adoption_regional_data', 'B246'),
    ('soln_pds_adoption_basis', 'B243'),
    ('soln_pds_adoption_prognostication_source', 'B265'),
    ('soln_pds_adoption_prognostication_trend', 'B270'),
    ('soln_pds_adoption_prognostication_growth', 'C270'),
    ('solution_category', 'A159'),
]

for (name, cell) in ac_variables:
  (row, col) = cell_to_offsets(cell)
  val = ac_tab.cell_value(row, col)
  if val:
    print("    " + name + " = " + format_val(val) + ",")
