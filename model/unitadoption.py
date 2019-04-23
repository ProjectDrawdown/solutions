"""Unit Adoption module."""

from functools import lru_cache
import os.path
import pathlib
import pandas as pd
from model import emissionsfactors


class UnitAdoption:
  """Implementation for the Unit Adoption module.

     Arguments:
       ac: advanced_controls.py object, settings to control model operation.
       soln_ref_funits_adopted: Annual functional units adopted in the
         Reference scenario.
       soln_pds_funits_adopted: Annual functional units adopted in the
         PDS scenario.
       datadir: directory where CSV files can be found
       ref_tam_per_region: (RRS only) dataframe of total addressible market per major
         region for the Referene scenario.
       pds_tam_per_region: (RRS only) dataframe of total addressible market per major
         region for the PDS scenario.
       tla_per_region: (LAND only): dataframe of total land area per region.
       bug_pds_cfunits_double_count (bool): enable bug-for-bug compatibility
       repeated_cost_for_iunits (bool): whether there is a repeated first cost to
         maintaining implementation units at a specified level in
         soln_pds_new_iunits_reqd, soln_ref_new_iunits_reqd, & conv_ref_new_iunits.
       electricity_unit_factor (float): a factor to multiply the electricity-related
         results by. For example, Land solutions typically multiply by 1e6 because their
         basic land unit is a million hectares but the electricity use (for irrigation, etc)
         is calculated per hectare.
  """

  def __init__(self, ac, soln_ref_funits_adopted, soln_pds_funits_adopted, datadir=None, ref_tam_per_region=None,
               pds_tam_per_region=None, tla_per_region=None, bug_cfunits_double_count=False,
               repeated_cost_for_iunits=False, electricity_unit_factor=1.0):
    self.ac = ac

    # NOTE: as datadir is static for all solutions this shouldn't be an arg
    # For now it is kept in for backwards compatibility with solutions
    if datadir is None:
      self.datadir = str(pathlib.Path(__file__).parents[1].joinpath('data'))
    else:
      self.datadir = datadir

    self.ref_tam_per_region = ref_tam_per_region
    self.pds_tam_per_region = pds_tam_per_region
    self.tla_per_region = tla_per_region
    self.soln_ref_funits_adopted = soln_ref_funits_adopted
    self.soln_pds_funits_adopted = soln_pds_funits_adopted
    self.bug_cfunits_double_count = bug_cfunits_double_count
    self.repeated_cost_for_iunits = repeated_cost_for_iunits
    self.electricity_unit_factor = electricity_unit_factor

  @lru_cache()
  def ref_population(self):
    """Population by region for the reference case.
       SolarPVUtil 'Unit Adoption Calculations'!P16:Z63
    """
    filename = os.path.join(self.datadir, 'unitadoption_ref_population.csv')
    result = pd.read_csv(filename, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.index = result.index.astype(int)
    result.name = "ref_population"
    return result

  @lru_cache()
  def ref_gdp(self):
    """GDP by region for the reference case.
       SolarPVUtil 'Unit Adoption Calculations'!AB16:AL63
    """
    filename = os.path.join(self.datadir, 'unitadoption_ref_gdp.csv')
    result = pd.read_csv(filename, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.index = result.index.astype(int)
    result.name = "ref_gdp"
    return result

  @lru_cache()
  def ref_gdp_per_capita(self):
    """GDP per capita for the reference case.
       SolarPVUtil 'Unit Adoption Calculations'!AN16:AX63
    """
    result = self.ref_gdp() / self.ref_population()
    result.name = "ref_gdp_per_capita"
    return result

  @lru_cache()
  def ref_tam_per_capita(self):
    """Total Addressable Market per capita for the reference case.
       SolarPVUtil 'Unit Adoption Calculations'!BA16:BK63
    """
    result = self.ref_tam_per_region / self.ref_population()
    result.name = "ref_tam_per_capita"
    return result

  @lru_cache()
  def ref_tam_per_gdp_per_capita(self):
    """Total Addressable Market per unit of GDP per capita for the reference case.
       SolarPVUtil 'Unit Adoption Calculations'!BM16:BW63
    """
    result = self.ref_tam_per_region / self.ref_gdp_per_capita()
    result.name = "ref_tam_per_gdp_per_capita"
    return result

  @lru_cache()
  def ref_tam_growth(self):
    """Growth in Total Addressable Market for the reference case.
       SolarPVUtil 'Unit Adoption Calculations'!BY16:CI63
    """
    calc = self.ref_tam_per_region.rolling(2).apply(lambda x: x[1] - x[0], raw=True)
    calc.loc[2014] = [''] * calc.shape[1]  # empty row
    calc.name = "ref_tam_growth"
    return calc

  @lru_cache()
  def pds_population(self):
    """Population by region for the Project Drawdown Solution case.
       SolarPVUtil 'Unit Adoption Calculations'!P68:Z115
    """
    filename = os.path.join(self.datadir, 'unitadoption_pds_population.csv')
    result = pd.read_csv(filename, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.index = result.index.astype(int)
    result.name = "pds_population"
    return result

  @lru_cache()
  def pds_gdp(self):
    """GDP by region for the Project Drawdown Solution case.
       SolarPVUtil 'Unit Adoption Calculations'!AB68:AL115
    """
    filename = os.path.join(self.datadir, 'unitadoption_pds_gdp.csv')
    result = pd.read_csv(filename, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#')
    result.index = result.index.astype(int)
    result.name = "pds_gdp"
    return result

  @lru_cache()
  def pds_gdp_per_capita(self):
    """GDP per capita for the Project Drawdown Solution case.
       SolarPVUtil 'Unit Adoption Calculations'!AN68:AX115
    """
    result = self.pds_gdp() / self.pds_population()
    result.name = "pds_gdp_per_capita"
    return result

  @lru_cache()
  def pds_tam_per_capita(self):
    """Total Addressable Market per capita for the Project Drawdown Solution case.
       SolarPVUtil 'Unit Adoption Calculations'!BA68:BK115
    """
    result = self.pds_tam_per_region / self.pds_population()
    result.name = "pds_tam_per_capita"
    return result

  @lru_cache()
  def pds_tam_per_gdp_per_capita(self):
    """Total Addressable Market per unit of GDP per capita for the Project Drawdown Solution case.
       SolarPVUtil 'Unit Adoption Calculations'!BM68:BW115
    """
    result = self.pds_tam_per_region / self.pds_gdp_per_capita()
    result.name = "pds_tam_per_gdp_per_capita"
    return result

  @lru_cache()
  def pds_tam_growth(self):
    """Growth in Total Addressable Market for the Project Drawdown Solution case.
       SolarPVUtil 'Unit Adoption Calculations'!BY68:CI115
    """
    calc = self.pds_tam_per_region.rolling(2).apply(lambda x: x[1] - x[0], raw=True)
    calc.loc[2014] = [''] * calc.shape[1]  # empty row
    calc.name = "pds_tam_growth"
    return calc

  @lru_cache()
  def cumulative_reduction_in_total_degraded_land(self):
    """This is the increase in undegraded land in the PDS versus the REF (cumulatively in any year), and can be
    traced to the direct action of increasing SOLUTION adoption. Units: millions ha.
    Calculation:   Undegraded Land in the PDS Scenario - Undegraded Land in REF Scenario
    ForestProtection 'Unit Adoption Calculations'!DR253:DS298"""
    return self.pds_total_undegraded_land() - self.ref_total_undegraded_land()

  @lru_cache()
  def annual_reduction_in_total_degraded_land(self):
    """This is the decrease in  total degraded land in the PDS versus the REF in each year. Units: Millions ha.
    Note: in excel this is calculated from several tables but we can achieve the same results directly from
    cumulative_reduction_in_total_degraded_land().
    ForestProtection 'Unit Adoption Calculations'!CG253:CH298"""
    return self.cumulative_reduction_in_total_degraded_land().diff().fillna(0.)

  @lru_cache()
  def pds_cumulative_degraded_land_unprotected(self):
    """This represents the total land degraded that was never protected in the PDS assuming the rate entered
    on the Advanced Controls sheet. This rate is applied only to the land that is not covered by the SOLUTION
    (ie land not artificially protected) and that is not degraded.  The impact of protection may be delayed
    (at User's input on Advanced Controls) and therefore the degradation rate may depend on the current year's
    or previous year's protection.
    ForestProtection 'Unit Adoption Calculations'!CG135:CH181"""
    return self._cumulative_degraded_land('PDS', 'unprotected')

  @lru_cache()
  def pds_cumulative_degraded_land_protected(self):
    """Even Protected Land suffers from Degradation via Disturbances (perhaps due to natural or anthropogenic
    means such as logging, storms, fires or human settlement). The Rate of this Disturbance is Entered on
    Advanced Controls, and is assumed equal in the PDS and REF. This Disturbance Rate affects annually, the
    degradation of Protected Land, but is expected to be much less than the Degradation Rate of Unprotected Land.
    ForestProtection 'Unit Adoption Calculations'!EI135:EJ181"""
    return self._cumulative_degraded_land('PDS', 'protected')

  @lru_cache()
  def pds_total_undegraded_land(self):
    """This represents the total land that is not degraded in any particular year of the PDS. It takes the TLA and
    removes the degraded land, which is the same as summing the undegraded land under the SOLUTION and At Risk land.
    Units: Millions ha
    Calculation:
    Total land/TLA - Land Degraded that was Unprotected - Protected Land that is Degraded (via a Disturbance)
                                                                             in Current Year
    ForestProtection 'Unit Adoption Calculations'!DS135:DT181"""
    deg_land = self.pds_cumulative_degraded_land_unprotected() + self.pds_cumulative_degraded_land_protected()
    return self.tla_per_region.loc[:, ['World']] - deg_land

  @lru_cache()
  def ref_cumulative_degraded_land_unprotected(self):
    """This represents the total land degraded that was never protected in the REF assuming the rate entered
    on the Advanced Controls sheet. This rate is applied only to the land that is not covered by the SOLUTION
    (ie land not artificially protected) and that is not degraded.  The impact of protection may be delayed
    (at User's input on Advanced Controls) and therefore the degradation rate may depend on the current year's
    or previous year's protection.
    ForestProtection 'Unit Adoption Calculations'!CG197:CH244"""
    return self._cumulative_degraded_land('REF', 'unprotected')

  @lru_cache()
  def ref_cumulative_degraded_land_protected(self):
    """Even Protected Land suffers from Degradation via Disturbances (perhaps due to natural or anthropogenic
    means such as logging, storms, fires or human settlement). The Rate of this Disturbance is Entered on
    Advanced Controls, and is assumed equal in the PDS and REF. This Disturbance Rate affects annually, the
    degradation of Protected Land, but is expected to be much less than the Degradation Rate of Unprotected Land.
    ForestProtection 'Unit Adoption Calculations'!EI197:EJ244"""
    return self._cumulative_degraded_land('REF', 'protected')

  @lru_cache()
  def ref_total_undegraded_land(self):
    """This represents the total land that is not degraded in any particular year of the REF. It takes the TLA and
    removes the degraded land, which is the same as summing the undegraded land under the SOLUTION and At Risk land.
    Units: Millions ha
    Calculation:
    Total land/TLA - Land Degraded that was Unprotected - Protected Land that is Degraded (via a Disturbance)
                                                                             in Current Year
    ForestProtection 'Unit Adoption Calculations'!DS197:DT244"""
    deg_land = self.ref_cumulative_degraded_land_unprotected() + self.ref_cumulative_degraded_land_protected()
    return self.tla_per_region.loc[:, ['World']] - deg_land

  def _cumulative_degraded_land(self, ref_or_pds, protected_or_unprotected):
    """
    Calculation of annual land degradation. Units: Millions ha

    Calculation (protected land):
    Protected Land that was Degraded Up to Previous Year +
    (Land Protected by SOL  - Protected Land Degraded up to Previous Year) * Disturbance Rate

    Calculation (unprotected land):
    Land Degraded Up to Previous Year +
    (Total land/TLA - Land Protected by SOL  - Land Degraded in Previous Year) * Degradation Rate

    Args:
      ref_or_pds: whether we use 'REF' or 'PDS' unit adoption data
      protected_or_unprotected: whether we calculate for 'protected' or 'unprotected' land

    Note: we only calculate 'World' values
    See: https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#
    """
    if ref_or_pds == 'PDS':
      units_adopted = self.soln_pds_funits_adopted
    elif ref_or_pds == 'REF':
      units_adopted = self.soln_ref_funits_adopted
    else:
      raise ValueError("Must indicate 'REF' or 'PDS'")
    years = list(range(2014, 2061))
    index = pd.Index(years, name='Year')
    df = pd.DataFrame(0., columns=['World'], index=index)

    delay = 1 if self.ac.delay_protection_1yr else 0
    if protected_or_unprotected == 'protected':
      # protected table starts with nonzero value
      df.at[2014, 'World'] = units_adopted.at[2014, 'World'] * self.ac.disturbance_rate

    for y in years[1:]:
        protected_land = units_adopted.at[y - delay, 'World']
        degraded_land = df.at[y - 1, 'World']
        if protected_or_unprotected == 'protected':
          val = min(degraded_land + (protected_land - degraded_land) * self.ac.disturbance_rate, protected_land)
        elif protected_or_unprotected == 'unprotected':
          tla = self.tla_per_region.at[y, 'World']
          val = min(degraded_land + (tla - protected_land - degraded_land) * self.ac.degradation_rate, tla)
        df.at[y, 'World'] = val
    return df

  @lru_cache()
  def soln_pds_cumulative_funits(self):
    """Cumulative Functional Units Utilized.
       SolarPVUtil 'Unit Adoption Calculations'!Q134:AA181
    """
    first_year = self.soln_pds_funits_adopted.fillna(0.0)
    if self.bug_cfunits_double_count:
      # in a number of older solutions, 'Advanced Controls'!$C$61:C70 is added to
      # the 2014 soln_pds_cumulative_funits, which ends up double counting 2014.
      # We optionally enable this bug-for-bug compatibility.
      # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.z9hqutnbnigx
      omit_world = self.soln_pds_funits_adopted.iloc[[0], :].fillna(0.0).copy(deep=True)
      omit_world['World'] = 0.0
      first_year = first_year.add(omit_world, fill_value=0)
    result = first_year.cumsum(axis=0, skipna=False)
    result.name = "soln_pds_cumulative_funits"
    return result

  @lru_cache()
  def soln_pds_tot_iunits_reqd(self):
    """Total iunits required each year.
       SolarPVUtil 'Unit Adoption Calculations'!AX134:BH181
    """
    result = self.soln_pds_funits_adopted
    if self.ac.soln_avg_annual_use is not None:  # RRS models
      result = result / self.ac.soln_avg_annual_use
    result.name = "soln_pds_tot_iunits_reqd"
    return result

  @lru_cache()
  def soln_pds_new_iunits_reqd(self):
    """New implementation units required (includes replacement units)

       Should reflect the unit lifetime assumed in the First Cost tab.
       For simplicity assumed a fix lifetime rather than a gaussian
       distribution, but this can be changed if needed.

       This is used to calculate Advanced Controls Output of Solution
       Implementation Units Adopted.  This is also used to Calculate
       First Cost, Marginal First Cost and NPV.
       SolarPVUtil 'Unit Adoption Calculations'!AG136:AQ182
    """
    if self.repeated_cost_for_iunits:
      return self.soln_pds_tot_iunits_reqd().iloc[1:].copy(deep=True).clip(lower=0.0)
    result = self.soln_pds_tot_iunits_reqd().diff().clip(lower=0).iloc[1:]  # iloc[0] NA after diff
    for region, column in result.iteritems():
      for year, value in column.iteritems():
        # Add replacement units, if needed by adding the number of units
        # added N * soln_lifetime_replacement ago, that now need replacement.
        replacement_year = int(year - (self.ac.soln_lifetime_replacement_rounded + 1))
        if replacement_year in result.index:
          fa = self.soln_pds_funits_adopted
          prior_year = year - self.ac.soln_lifetime_replacement_rounded - 1
          if fa.loc[prior_year, region] <= fa.loc[year, region]:
            result.at[year, region] += result.at[replacement_year, region]
    result.name = "soln_pds_new_iunits_reqd"
    return result

  @lru_cache()
  def soln_pds_big4_iunits_reqd(self):
    """Implementation units required in USA/EU/China/India vs Rest of World.
       SolarPVUtil 'Unit Adoption Calculations'!BN136:BS182
    """
    soln_pds_tot_iunits_reqd = self.soln_pds_tot_iunits_reqd()
    result = pd.DataFrame(0, index=soln_pds_tot_iunits_reqd.index.copy(),
        columns=["Rest of World", "China", "India", "EU", "USA"],
        dtype='float64')
    result["China"] = soln_pds_tot_iunits_reqd["China"]
    result["India"] = soln_pds_tot_iunits_reqd["India"]
    result["EU"] = soln_pds_tot_iunits_reqd["EU"]
    result["USA"] = soln_pds_tot_iunits_reqd["USA"]
    result["Rest of World"] = (soln_pds_tot_iunits_reqd["World"] -
        soln_pds_tot_iunits_reqd["China"].fillna(0.0) -
        soln_pds_tot_iunits_reqd["India"].fillna(0.0) -
        soln_pds_tot_iunits_reqd["EU"].fillna(0.0) -
        soln_pds_tot_iunits_reqd["USA"].fillna(0.0))
    result.name = "soln_pds_big4_iunits_reqd"
    return result

  @lru_cache()
  def soln_ref_cumulative_funits(self):
    """Cumulative functional units.
       SolarPVUtil 'Unit Adoption Calculations'!Q197:AA244
    """
    result = self.soln_ref_funits_adopted.fillna(0.0).cumsum(axis=0)
    result.name = "soln_ref_cumulative_funits"
    return result

  @lru_cache()
  def soln_ref_tot_iunits_reqd(self):
    """Total implementation units required.
       SolarPVUtil 'Unit Adoption Calculations'!AX197:BH244"""
    result = self.soln_ref_funits_adopted
    if self.ac.soln_avg_annual_use is not None:  # RRS models
      result = result / self.ac.soln_avg_annual_use
    result.name = "soln_ref_tot_iunits_reqd"
    return result

  @lru_cache()
  def soln_ref_new_iunits_reqd(self):
    """New implementation units required (includes replacement units)

       Should reflect the unit lifetime assumed in the First Cost tab. For
       simplicity assumed a fix lifetime rather than a gaussian distribution,
       but this can be changed if needed.

       This table is also used to Calculate  Marginal First Cost and NPV.

       SolarPVUtil 'Unit Adoption Calculations'!AG197:AQ244
    """
    if self.repeated_cost_for_iunits:
      return self.soln_ref_tot_iunits_reqd().iloc[1:].copy(deep=True).clip(lower=0.0)
    result = self.soln_ref_tot_iunits_reqd().diff().clip(lower=0).iloc[1:]  # iloc[0] NA after diff
    for region, column in result.iteritems():
      for year, value in column.iteritems():
        # Add replacement units, if needed by adding the number of units
        # added N * soln_lifetime_replacement ago, that now need replacement.
        replacement_year = int(year - (self.ac.soln_lifetime_replacement_rounded + 1))
        if replacement_year in result.index:
          fa = self.soln_ref_funits_adopted
          prior_year = year - self.ac.soln_lifetime_replacement_rounded - 1
          if fa.loc[prior_year, region] <= fa.loc[year, region]:
            result.at[year, region] += result.at[replacement_year, region]
    result.name = "soln_ref_new_iunits_reqd"
    return result

  @lru_cache()
  def soln_net_annual_funits_adopted(self):
    """Net annual functional units adopted.

       Return value is a DataFrame with an index of years, columns for each
       region and floating point data values.

       This represents the total additional functional units captured either
       by the CONVENTIONAL mix of technologies/practices in the REF case
       scenario, OR total growth of the SOLUTION in the PDS scenario,
       i.e. in addition to the current growth of the SOLUTION in the REF
       scenario.

       This is used to calculate the Operating Cost, Grid, Fuel, Direct and
       (optionally) Indirect Emissions.
       SolarPVUtil 'Unit Adoption Calculations'!B251:L298
    """
    result = self.soln_pds_funits_adopted - self.soln_ref_funits_adopted
    result.name = "soln_net_annual_funits_adopted"
    return result

  def net_annual_land_units_adopted(self):
    """Similar to soln_net_annual_funits_adopted, for Land models.
       Conservation Agriculture 'Unit Adoption Calculations'!B251:L298
    """
    result = self.soln_net_annual_funits_adopted()
    result.name = 'net_annual_land_units_adopted'
    return result

  @lru_cache()
  def conv_ref_tot_iunits(self):
    """
    Note that iunits = land units for LAND models.
    From Excel:
    'Total cumulative units of the conventional or legacy practice installed by year.

    Reflects the total increase in the installed base units less the installation of
    Solution/technology units. Assumes a binary market with demand for either the
    defined Conventional Unit (or a weighted average of a mix of technologies/practices)
    or a Solution Unit. NOTE for integration: In REF case a weighted factor needs to
    account for current technology mix; for PDS case proposed technology mix needs to
    be reflected here.'

    SolarPVUtil 'Unit Adoption Calculations'!Q251:AA298
    """

    if self.tla_per_region is not None:  # LAND
        result = self.tla_per_region - self.soln_ref_funits_adopted
    else:  # RRS
        result = ((self.ref_tam_per_region - self.soln_ref_funits_adopted.fillna(0.0)) /
                self.ac.conv_avg_annual_use)
    result.name = "conv_ref_tot_iunits"
    return result

  @lru_cache()
  def conv_ref_annual_tot_iunits(self):
    """Number of Implementation Units of the Conventional practice/technology that would
       be needed in the REF Scenario to meet the Functional Unit Demand met by the PDS
       Implementation Units in the PDS Scenario. This is equivalent to the number of Annual
       Active CONVENTIONAL units that would have been needed in REF but are not needed in PDS
       scenario, since SOLUTION units are used as a direct replacement for CONVENTIONAL units.
       Implementation Conventional Units =  ((Total Annual Functional Units(PDS) -
           Total Annual Functional units (REF) ) / Average Annual Use Per Conventional Unit)

       SolarPVUtil 'Unit Adoption Calculations'!AX251:BH298
    """
    result = self.soln_net_annual_funits_adopted()
    if self.ac.conv_avg_annual_use is not None:  # RRS models
      result = result / self.ac.conv_avg_annual_use
    result.name = "conv_ref_annual_tot_iunits"
    return result

  @lru_cache()
  def conv_ref_new_iunits(self):
    """New implementation units required (includes replacement units)

       Number of Additional Implementation Units of the Conventional practice/technology
       that would be needed in the REF Scenario to meet the Functional Unit Demand met by
       the PDS Implementation Units in the PDS Scenario. This is equivalent to the number
       of Active CONVENTIONAL units that would have been sold/produced in REF but are not
       sold/produced in PDS scenario, since SOLUTION units are used as a direct
       replacement for CONVENTIONAL units.

       SolarPVUtil 'Unit Adoption Calculations'!AG251:AQ298
    """
    if self.repeated_cost_for_iunits:
      return self.conv_ref_annual_tot_iunits().iloc[1:].copy(deep=True).clip(lower=0.0)
    growth = self.conv_ref_annual_tot_iunits().diff().clip(lower=0).iloc[1:]  # iloc[0] NA after diff
    replacements = pd.DataFrame(0, index=growth.index.copy(), columns=growth.columns.copy(),
        dtype='float64')
    for region, column in replacements.iteritems():
      for year, value in column.iteritems():
        # Add replacement units, if needed by adding the number of units
        # added N * conv_lifetime_replacement ago, that now need replacement.
        replacement_year = int(year - (self.ac.conv_lifetime_replacement_rounded + 1))
        while replacement_year in growth.index:
          replacements.at[year, region] += growth.at[replacement_year, region]
          replacement_year -= (self.ac.conv_lifetime_replacement_rounded + 1)
    result = growth + replacements
    result.name = "conv_ref_new_iunits"
    return result

  @lru_cache()
  def soln_pds_net_grid_electricity_units_saved(self):
    """Energy Units (e.g. TWh, tonnes oil equivalent, million therms, etc.) are
       calculated by multiplying the net annual functional units adopted by the
       annual energy saved per unit (specified in the main controls). In some rare
       cases the energy saved per unit installed may vary by region and/or time,
       in which case a separate tab for that variable may prove necessary.

       SolarPVUtil 'Unit Adoption Calculations'!B307:L354
       Irrigation Efficiency 'Unit Adoption Calculations'!B307:L354, 10^6 electricity_unit_factor
    """
    m = (self.ac.soln_energy_efficiency_factor * self.ac.conv_annual_energy_used *
            self.electricity_unit_factor)
    result = self.soln_net_annual_funits_adopted().multiply(m)
    result.name = "soln_pds_net_grid_electricity_units_saved"
    return result

  @lru_cache()
  def soln_pds_net_grid_electricity_units_used(self):
    """Energy Units Used (TWh) are calculated by multiplying the net annual functional
       units adopted by the average annual electricity used by the solution per functional
       unit (specified in the main controls) minus  net annual functional units adopted by
       the average annual electricity used by the conventional technologies/practices
       (specified in the main controls). In some rare cases the energy saved per unit
       installed may vary by region and/or time, in which case a separate tab for that
       variable may prove necessary.

       SolarPVUtil 'Unit Adoption Calculations'!Q307:AA354
       Irrigation Efficiency 'Unit Adoption Calculations'!Q307:AA354, 10^6 electricity_unit_factor
    """
    def calc(x):
      if self.ac.soln_annual_energy_used:
        return ((self.ac.soln_annual_energy_used - self.ac.conv_annual_energy_used) *
                self.electricity_unit_factor * x)
      else:
        return 0.0
    result = self.soln_net_annual_funits_adopted().applymap(calc)
    result.name = "soln_pds_net_grid_electricity_units_used"
    return result

  @lru_cache()
  def soln_pds_fuel_units_avoided(self):
    """Fuel consumption avoided annually.
       Fuel avoided = CONVENTIONAL stock avoided * Volume consumed by CONVENTIONAL
           unit per year * Fuel Efficiency of SOLUTION

       SolarPVUtil 'Unit Adoption Calculations'!AD307:AN354
    """
    m = self.ac.conv_fuel_consumed_per_funit * self.ac.soln_fuel_efficiency_factor
    result = self.soln_net_annual_funits_adopted().multiply(m)
    result.name = "soln_pds_fuel_units_avoided"
    return result

  @lru_cache()
  def soln_pds_direct_co2_emissions_saved(self):
    """Direct emissions of CO2 avoided, in tons.
       SolarPVUtil 'Unit Adoption Calculations'!AT307:BD354
    """
    def calc(x):
      return (self.ac.conv_emissions_per_funit * x) - (self.ac.soln_emissions_per_funit * x)
    result = self.soln_net_annual_funits_adopted().applymap(calc)
    result.name = "soln_pds_direct_co2_emissions_saved"
    return result

  @lru_cache()
  def soln_pds_direct_ch4_co2_emissions_saved(self):
    """Direct emissions of CH4 avoided, in tons of equivalent CO2.

       SolarPVUtil 'Unit Adoption Calculations'!BF307:BP354
    """
    ef = emissionsfactors.CO2Equiv(self.ac.co2eq_conversion_source)
    if self.ac.ch4_is_co2eq:
      result = self.soln_net_annual_funits_adopted() * self.ac.ch4_co2_per_twh
    else:
      result = self.soln_net_annual_funits_adopted() * ef.CH4multiplier * self.ac.ch4_co2_per_twh
    result.name = "soln_pds_direct_ch4_co2_emissions_saved"
    return result

  @lru_cache()
  def soln_pds_direct_n2o_co2_emissions_saved(self):
    """Direct emissions of N2O avoided, in tons of CO2 equivalents.

       SolarPVUtil 'Unit Adoption Calculations'!BR307:CB354
    """
    ef = emissionsfactors.CO2Equiv(self.ac.co2eq_conversion_source)
    if self.ac.n2o_is_co2eq:
      result = self.soln_net_annual_funits_adopted() * self.ac.n2o_co2_per_twh
    else:
      result = self.soln_net_annual_funits_adopted() * ef.N2Omultiplier * self.ac.n2o_co2_per_twh
    result.name = "soln_pds_direct_n2o_co2_emissions_saved"
    return result

  @lru_cache()
  def net_land_units_after_emissions_lifetime(self):
    """Emissions after the calculated lifetime (which is often very long, ex: 100 years)

       This table is used to calculate the Annual Direct Emissions of all GH Gases if the User
       selects "Annual" accounting (ie the direct emissions are released for a certain number
       of years rather than only in the year of adoption).

       Conservation Agriculture 'Unit Adoption Calculations'!EI251:ES298
    """
    if self.ac.delay_protection_1yr:
      funits = self.cumulative_reduction_in_total_degraded_land()
    else:
      funits = self.net_annual_land_units_adopted()
    result = pd.DataFrame(0, index=funits.index.copy(), columns=funits.columns.copy())
    first_year = result.first_valid_index() + 1
    for year, row in result.iterrows():
      if (year - first_year) > self.ac.land_annual_emissons_lifetime:
        result.loc[year] = funits.loc[year - self.ac.land_annual_emissons_lifetime - 1]
    result.name = 'net_land_units_after_emissions_lifetime'
    return result

  @lru_cache()
  def _direct_emissions_saved_land(self, ghg, ghg_rplu, ghg_rplu_rate):
    """Emissions avoided:
      Args:
        ghg: Greenhouse gas to calculate ('CO2-eq', 'CO2', 'N2O-CO2-eq' or 'CH4-CO2-eq')
        ghg_rplu: associated val from advanced controls (self.ac.<ghg>_reduced_per_land_unit)
        ghg_rplu_rate: 'Annual' or 'One-time' (self.ac.<ghg>_rplu_rate)

      [PROTECTION MODEL (e.g. Forest Protection]
       Emissions avoided (if Annual Emissions) =
            (Cumulative Reduced Land Degradation/MHa - Cumulative Reduced Land after Emissions Lifetime/MHa)
                            * Aggregate GHG avoided rate (t GHG/ha/yr)
       Emissions avoided (if One-time Emissions) =
            Marginal Reduced Land Degradation /MHa *  Aggregate GHG avoided rate (t GHG/ha)

       [NON PROTECTION MODEL (e.g. Conservation Agriculture]
       Emissions avoided (if Annual Emissions) =
             (Net Land Units/MHa - Net Land Units after Emissions Lifetime /MHa)
                            * Aggregate GHG avoided rate (t GHG/ha/yr)
       Emissions avoided (if One-time Emissions) =
              (Net Land Units in Year x/MHa - Net Land Units in Year x-1/MHa)* Aggregate GHG avoided rate (t GHG/ha)"""
    if self.ac.delay_protection_1yr is not None:
      if ghg_rplu_rate == 'Annual':
        result = self.cumulative_reduction_in_total_degraded_land() - self.net_land_units_after_emissions_lifetime()
        result *= ghg_rplu
      else:
        result = self.annual_reduction_in_total_degraded_land() * ghg_rplu
    else:
      # same handling for One-time (Farmland Restoration) and Annual (Conservation Agriculture)
      result = self.net_annual_land_units_adopted() - self.net_land_units_after_emissions_lifetime()
      result *= ghg_rplu * (1.0 - self.ac.disturbance_rate)
    result.name = 'direct_{}_emissions_saved_land'.format(ghg)
    return result

  @lru_cache()
  def direct_co2eq_emissions_saved_land(self):
    """ForestProtection 'Unit Adoption Calculations'!AT307:AU354"""
    return self._direct_emissions_saved_land(ghg='CO2-eq', ghg_rplu=self.ac.tco2eq_reduced_per_land_unit,
                                             ghg_rplu_rate=self.ac.tco2eq_rplu_rate)

  @lru_cache()
  def direct_co2_emissions_saved_land(self):
    """ForestProtection 'Unit Adoption Calculations'!BF307:BG354"""
    return self._direct_emissions_saved_land(ghg='CO2', ghg_rplu=self.ac.tco2_reduced_per_land_unit,
                                             ghg_rplu_rate=self.ac.tco2_rplu_rate)

  @lru_cache()
  def direct_n2o_co2_emissions_saved_land(self):
    """ForestProtection 'Unit Adoption Calculations'!BR307:BS354"""
    return self._direct_emissions_saved_land(ghg='N2O-CO2-eq', ghg_rplu=self.ac.tn2o_co2_reduced_per_land_unit,
                                             ghg_rplu_rate=self.ac.tn2o_co2_rplu_rate)

  @lru_cache()
  def direct_ch4_co2_emissions_saved_land(self):
    """ForestProtection 'Unit Adoption Calculations'!CD307:CE354"""
    return self._direct_emissions_saved_land(ghg='CH4-CO2-eq', ghg_rplu=self.ac.tch4_co2_reduced_per_land_unit,
                                             ghg_rplu_rate=self.ac.tch4_co2_rplu_rate)
