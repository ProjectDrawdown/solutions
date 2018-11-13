"""Unit Adoption module."""

import os.path

import pandas as pd
from model import emissionsfactors


class UnitAdoption:
    """Implementation for the First Cost model.

    Arguments:
    ac = advanced_cost.py object, storing settings to control
      model operation.
    """
    csv_files_dir = os.path.dirname(__file__)

    def __init__(self, ac=None):
      self.ac = ac

    def ref_population(self):
      """Population by region for the reference case.
         'Unit Adoption Calculations'!P16:Z63
      """
      filename = os.path.join(self.csv_files_dir, 'ua_ref_pop_scenario1.csv')
      return pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
          skiprows=0, skip_blank_lines=True, comment='#')

    def ref_gdp(self):
      """GDP by region for the reference case.
         'Unit Adoption Calculations'!AB16:AL63
      """
      filename = os.path.join(self.csv_files_dir, 'ua_ref_gdp_scenario1.csv')
      return pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True,
          skiprows=0, skip_blank_lines=True, comment='#')

    def ref_gdp_per_capita(self, ref_population, ref_gdp):
      """GDP per capita for the reference case.
         'Unit Adoption Calculations'!AN16:AX63
      """
      return ref_gdp / ref_population

    def ref_tam_per_capita(self, ref_tam_per_region, ref_population):
      """Total Addressable Market per capita for the reference case.
         'Unit Adoption Calculations'!BA16:BK63
      """
      return ref_tam_per_region / ref_population

    def ref_tam_per_gdp_per_capita(self, ref_tam_per_region, ref_gdp_per_capita):
      """Total Addressable Market per unit of GDP per capita for the reference case.
         'Unit Adoption Calculations'!BM16:BW63
      """
      return ref_tam_per_region / ref_gdp_per_capita

    def ref_tam_growth(self, ref_tam_per_region):
      """Growth in Total Addressable Market for the reference case.
         'Unit Adoption Calculations'!BY16:CI63
      """
      calc = ref_tam_per_region.rolling(2).apply(lambda x: x[1] - x[0], raw=True)
      calc.loc[2014] = [''] * calc.shape[1]  # empty row
      return calc

    def pds_population(self):
      """Population by region for the Project Drawdown Solution case.
         'Unit Adoption Calculations'!P68:Z115
      """
      filename = os.path.join(self.csv_files_dir, 'ua_pds_population.csv')
      return pd.read_csv(filename, header=1, index_col=0, skipinitialspace=True,
          skiprows=0)

    def pds_gdp(self):
      """GDP by region for the Project Drawdown Solution case.
         'Unit Adoption Calculations'!AB68:AL115
      """
      filename = os.path.join(self.csv_files_dir, 'ua_pds_gdp_scenario2.csv')
      return pd.read_csv(filename, header=1, index_col=0, skipinitialspace=True,
          skiprows=0)

    def pds_gdp_per_capita(self, pds_population, pds_gdp):
      """GDP per capita for the Project Drawdown Solution case.
         'Unit Adoption Calculations'!AN68:AX115
      """
      return pds_gdp / pds_population

    def pds_tam_per_capita(self, pds_tam_per_region, pds_population):
      """Total Addressable Market per capita for the Project Drawdown Solution case.
         'Unit Adoption Calculations'!BA68:BK115
      """
      return pds_tam_per_region / pds_population

    def pds_tam_per_gdp_per_capita(self, pds_tam_per_region, pds_gdp_per_capita):
      """Total Addressable Market per unit of GDP per capita for the Project Drawdown Solution case.
         'Unit Adoption Calculations'!BM68:BW115
      """
      return pds_tam_per_region / pds_gdp_per_capita

    def pds_tam_growth(self, pds_tam_per_region):
      """Growth in Total Addressable Market for the Project Drawdown Solution case.
         'Unit Adoption Calculations'!BY68:CI115
      """
      calc = pds_tam_per_region.rolling(2).apply(lambda x: x[1] - x[0], raw=True)
      calc.loc[2014] = [''] * calc.shape[1]  # empty row
      return calc

    def soln_pds_cumulative_funits(self, soln_pds_funits_adopted):
      """Cumulative Functional Units Utilized.
      'Unit Adoption Calculations'!Q134:AA181
      """
      omit_world = self.ac.soln_funit_adoption_2014.copy(deep=True)
      omit_world['World'][2014] = 0
      first_year = soln_pds_funits_adopted.add(omit_world, fill_value=0)
      return first_year.cumsum(axis=0)

    def soln_pds_tot_iunits_reqd(self, soln_pds_funits_adopted):
      """Total iunits required each year.
      'Unit Adoption Calculations'!AX134:BH181
      """
      return soln_pds_funits_adopted / self.ac.soln_avg_annual_use

    def soln_pds_new_iunits_reqd(self, soln_pds_tot_iunits_reqd):
      """New implementation units required (includes replacement units)

      Should reflect the unit lifetime assumed in the First Cost tab.
      For simplicity assumed a fix lifetime rather than a gaussian
      distribution, but this can be changed if needed. 

      This is used to calculate Advanced Controls Output of Solution
      Implementation Units Adopted.  This is also used to Calculate
      First Cost, Marginal First Cost and NPV.
      'Unit Adoption Calculations'!AG136:AQ182
      """
      growth = soln_pds_tot_iunits_reqd.diff().clip_lower(0).dropna()
      replacements = pd.DataFrame(0, index=growth.index.copy(), columns=growth.columns.copy(),
          dtype='float64')
      for region, column in replacements.iteritems():
        for year, value in column.iteritems():
          # Add replacement units, if needed by adding the number of units
          # added soln_lifetime_replacement ago, that now need replacement.
          replacement_year = int(year - round(self.ac.soln_lifetime_replacement) - 1)
          if replacement_year in growth.index:
            replacements.at[year, region] = growth.loc[replacement_year].at[region]
      return growth + replacements

    def soln_pds_big4_iunits_reqd(self, soln_pds_tot_iunits_reqd):
      """Implementation units required in USA/EU/China/India vs Rest of World.
      'Unit Adoption Calculations'!AG136:AQ182
      """
      result = pd.DataFrame(0, index=soln_pds_tot_iunits_reqd.index.copy(),
          columns=["Rest of World", "China", "India", "EU", "USA"],
          dtype='float64')
      result["China"] = soln_pds_tot_iunits_reqd["China"]
      result["India"] = soln_pds_tot_iunits_reqd["India"]
      result["EU"] = soln_pds_tot_iunits_reqd["EU"]
      result["USA"] = soln_pds_tot_iunits_reqd["USA"]
      result["Rest of World"] = (soln_pds_tot_iunits_reqd["World"] -
          soln_pds_tot_iunits_reqd["China"] - soln_pds_tot_iunits_reqd["India"] -
          soln_pds_tot_iunits_reqd["EU"] - soln_pds_tot_iunits_reqd["USA"])
      return result

    def soln_ref_cumulative_funits(self, soln_ref_funits_adopted):
      return soln_ref_funits_adopted.cumsum(axis=0)

    def soln_ref_tot_iunits_reqd(self, soln_ref_funits_adopted):
      """Total implementation units required.
         'Unit Adoption Calculations'!AX197:BH244"""
      return soln_ref_funits_adopted / self.ac.soln_avg_annual_use

    def soln_ref_new_iunits_reqd(self, soln_ref_tot_iunits_reqd):
      """New implementation units required (includes replacement units)

      Should reflect the unit lifetime assumed in the First Cost tab. For
      simplicity assumed a fix lifetime rather than a gaussian distribution,
      but this can be changed if needed.

      This table is also used to Calculate  Marginal First Cost and NPV.

      'Unit Adoption Calculations'!AG197:AQ244
      """
      growth = soln_ref_tot_iunits_reqd.diff().clip_lower(0).dropna()
      replacements = pd.DataFrame(0, index=growth.index.copy(), columns=growth.columns.copy(),
          dtype='float64')
      for region, column in replacements.iteritems():
        for year, value in column.iteritems():
          # Add replacement units, if needed by adding the number of units
          # added soln_lifetime_replacement ago, that now need replacement.
          replacement_year = int(year - round(self.ac.soln_lifetime_replacement) - 1)
          if replacement_year in growth.index:
            replacements.at[year, region] = growth.loc[replacement_year].at[region]
      return growth + replacements

    def soln_net_annual_funits_adopted(self, soln_ref_funits_adopted, soln_pds_funits_adopted):
      """Net annual functional units adopted.

      soln_ref_funits_adopted: Reference solution: Annual functional units adopted
      soln_pds_funits_adopted: PDS solution: Annual functional units adopted

      Both inputs and return value is a DataFrame with and index of years,
      columns for each region and floating point data values.

      This represents the total additional functional units captured either
      by the CONVENTIONAL mix of technologies/practices in the REF case
      scenario, OR total growth of the SOLUTION in the PDS scenario,
      i.e. in addition to the current growth of the SOLUTION in the REF
      scenario.

      This is used to calculate the Operating Cost, Grid, Fuel, Direct and
      (optionally) Indirect Emissions.
      'Unit Adoption Calculations'!B251:L298
      """
      return soln_pds_funits_adopted - soln_ref_funits_adopted

    def conv_ref_tot_iunits_reqd(self, ref_tam_per_region, soln_ref_funits_adopted):
      """Total cumulative units of the conventional or legacy practice installed by year.
      
      Reflects the total increase in the installed base units less the installation of
      Solution/technology units. Assumes a binary market with demand for either the
      defined Conventional Unit (or a weighted average of a mix of technologies/practices)
      or a Solution Unit. NOTE for integration: In REF case a weighted factor needs to
      account for current technology mix; for PDS case proposed technology mix needs to
      be reflected here.
      
      'Unit Adoption Calculations'!Q251:AA298
      """
      return (ref_tam_per_region - soln_ref_funits_adopted) / self.ac.conv_avg_annual_use

    def conv_ref_annual_tot_iunits(self, soln_net_annual_funits_adopted):
      """Number of Implementation Units of the Conventional practice/technology that would
      be needed in the REF Scenario to meet the Functional Unit Demand met by the PDS
      Implementation Units in the PDS Scenario. This is equivalent to the number of Annual
      Active CONVENTIONAL units that would have been needed in REF but are not needed in PDS
      scenario, since SOLUTION units are used as a direct replacement for CONVENTIONAL units.
      Implementation Conventional Units =  ((Total Annual Functional Units(PDS) -
          Total Annual Functional units (REF) ) / Average Annual Use Per Conventional Unit)

      'Unit Adoption Calculations'!AX251:BH298
      """
      return soln_net_annual_funits_adopted / self.ac.conv_avg_annual_use

    def conv_ref_new_iunits_reqd(self, conv_ref_annual_tot_iunits):
      """New implementation units required (includes replacement units)

      Number of Additional Implementation Units of the Conventional practice/technology
      that would be needed in the REF Scenario to meet the Functional Unit Demand met by
      the PDS Implementation Units in the PDS Scenario. This is equivalent to the number
      of Active CONVENTIONAL units that would have been sold/produced in REF but are not
      sold/produced in PDS scenario, since SOLUTION units are used as a direct
      replacement for CONVENTIONAL units.
      'Unit Adoption Calculations'!AG251:AQ298
      """
      growth = conv_ref_annual_tot_iunits.diff().clip_lower(0).dropna()
      replacements = pd.DataFrame(0, index=growth.index.copy(), columns=growth.columns.copy(),
          dtype='float64')
      for region, column in replacements.iteritems():
        for year, value in column.iteritems():
          # Add replacement units, if needed by adding the number of units
          # added conv_lifetime_replacement ago, that now need replacement.
          replacement_year = int(year - self.ac.conv_lifetime_replacement - 1)
          if replacement_year in growth.index:
            replacements.at[year, region] = growth.loc[replacement_year].at[region]
      return growth + replacements

    def soln_pds_net_grid_electricity_units_saved(self, soln_net_annual_funits_adopted):
      """Energy Units (e.g. TWh, tonnes oil equivalent, million therms, etc.) are
      calculated by multiplying the net annual functional units adopted by the
      annual energy saved per unit (specified in the main controls). In some rare
      cases the energy saved per unit installed may vary by region and/or time,
      in which case a separate tab for that variable may prove necessary.

      'Unit Adoption Calculations'!B307:L354"""
      m = self.ac.soln_energy_efficiency_factor * self.ac.conv_annual_energy_used
      return soln_net_annual_funits_adopted.multiply(m)

    def soln_pds_net_grid_electricity_units_used(self, soln_net_annual_funits_adopted):
      """Energy Units Used (TWh) are calculated by multiplying the net annual functional
      units adopted by the average annual electricity used by the solution per functional
      unit (specified in the main controls) minus  net annual functional units adopted by
      the average annual electricity used by the conventional technologies/practices
      (specified in the main controls). In some rare cases the energy saved per unit
      installed may vary by region and/or time, in which case a separate tab for that
      variable may prove necessary.
        'Unit Adoption Calculations'!Q307:AA354
      """
      def calc(x):
        if self.ac.soln_annual_energy_used:
          return (self.ac.soln_annual_energy_used * x) - (self.ac.conv_annual_energy_used * x)
        else:
          return 0.0
      return soln_net_annual_funits_adopted.applymap(calc)

    def soln_pds_fuel_units_avoided(self, soln_net_annual_funits_adopted):
      """Fuel consumption avoided annually.
      Fuel avoided = CONVENTIONAL stock avoided * Volume consumed by CONVENTIONAL
          unit per year * Fuel Efficiency of SOLUTION
        'Unit Adoption Calculations'!AD307:AN354
      """
      m = self.ac.conv_fuel_consumed_per_funit * self.ac.soln_fuel_efficiency_factor
      return soln_net_annual_funits_adopted.multiply(m)

    def soln_pds_direct_co2_emissions_saved(self, soln_net_annual_funits_adopted):
      """Direct emissions of CO2 avoided, in tons.
        'Unit Adoption Calculations'!AT307:BD354
      """
      def calc(x):
        return (self.ac.conv_emissions_per_funit * x) - (self.ac.soln_emissions_per_funit * x)
      return soln_net_annual_funits_adopted.applymap(calc)

    def soln_pds_direct_ch4_co2_emissions_saved(self, soln_net_annual_funits_adopted,
        ch4_per_funit=0.0, ch4_co2equiv_per_funit=0.0):
      """Direct emissions of CH4 avoided, in tons of equivalent CO2.
         ch4_per_funit: tons of CH4 per funit, which this routine will convert to CO2 equivalent.
         ch4_co2equiv_per_funit: CH4 emissions per funit which have already been converted to
           CO2 equivalent outside of this routine, and will be added to the total.
        'Unit Adoption Calculations'!BF307:BP354
      """
      ef = emissionsfactors.CO2Equiv(self.ac.co2eq_conversion_source)
      converted = soln_net_annual_funits_adopted * ef.CH4multiplier * ch4_per_funit
      return converted + (soln_net_annual_funits_adopted * ch4_co2equiv_per_funit)

    def soln_pds_direct_n2o_co2_emissions_saved(self, soln_net_annual_funits_adopted,
        n2o_per_funit=0.0, n2o_co2equiv_per_funit=0.0):
      """Direct emissions of N2O avoided, in tons of CO2 equivalents.
         n2o_per_funit: tons of N2O per funit, which this routine will convert to CO2 equivalent.
         n2o_co2equiv_per_funit: N2O emissions per funit which have already been converted to
           CO2 equivalent outside of this routine, and will be added to the total.
        'Unit Adoption Calculations'!BR307:CB354
      """
      ef = emissionsfactors.CO2Equiv(self.ac.co2eq_conversion_source)
      converted = soln_net_annual_funits_adopted * ef.N2Omultiplier * n2o_per_funit
      return converted + (soln_net_annual_funits_adopted * n2o_co2equiv_per_funit)
