"""Unit Adoption module."""  # by Denton Gentry
# by Denton Gentry
from functools import lru_cache  # by Denton Gentry
import os.path  # by Denton Gentry
import pathlib
import pandas as pd  # by Owen Barton
from model import emissionsfactors  # by Denton Gentry


# by Owen Barton
# by Owen Barton
class UnitAdoption:  # by Owen Barton
    """Implementation for the Unit Adoption module.  # by Denton Gentry
    # by Denton Gentry
       Arguments:  # by Denton Gentry
         ac: advanced_controls.py object, settings to control model operation.  # by Denton Gentry
         soln_ref_funits_adopted: Annual functional units adopted in the  # by Denton Gentry
           Reference scenario.  # by Denton Gentry
         soln_pds_funits_adopted: Annual functional units adopted in the  # by Denton Gentry
           PDS scenario.  # by Denton Gentry
         datadir: directory where CSV files can be found
         ref_tam_per_region: (RRS only) dataframe of total addressible market per major
           region for the Referene scenario.
         pds_tam_per_region: (RRS only) dataframe of total addressible market per major
           region for the PDS scenario.
         tla_per_region: (LAND only): dataframe of total land area per region.
         bug_pds_cfunits_double_count (bool): enable bug-for-bug compatibility  # by Denton Gentry
         repeated_cost_for_iunits (bool): whether there is a repeated first cost to  # by Denton Gentry
           maintaining implementation units at a specified level in  # by Denton Gentry
           soln_pds_new_iunits_reqd, soln_ref_new_iunits_reqd, & conv_ref_new_iunits.  # by Denton Gentry
         electricity_unit_factor (float): a factor to multiply the electricity-related  # by Denton Gentry
           results by. For example, Land solutions typically multiply by 1e6 because their  # by Denton Gentry
           basic land unit is a million hectares but the electricity use (for irrigation, etc)  # by Denton Gentry
           is calculated per hectare.  # by Denton Gentry
    """  # by Denton Gentry

    def __init__(self, ac, soln_ref_funits_adopted, soln_pds_funits_adopted, datadir=None, ref_tam_per_region=None,

                 pds_tam_per_region=None, tla_per_region=None, bug_cfunits_double_count=False,  # by Denton Gentry
                 repeated_cost_for_iunits=False, electricity_unit_factor=1.0):  # by Denton Gentry
        self.ac = ac  # by Denton Gentry

        # NOTE: as datadir is static for all solutions this shouldn't be an arg
        # For now it is kept in for backwards compatibility with solutions
        if datadir is None:
            self.datadir = str(pathlib.Path(__file__).parents[1].joinpath('data'))
        else:
            self.datadir = datadir

        self.ref_tam_per_region = ref_tam_per_region  # by Denton Gentry
        self.pds_tam_per_region = pds_tam_per_region  # by Denton Gentry
        self.tla_per_region = tla_per_region
        self.soln_ref_funits_adopted = soln_ref_funits_adopted  # by Denton Gentry
        self.soln_pds_funits_adopted = soln_pds_funits_adopted  # by Denton Gentry
        self.bug_cfunits_double_count = bug_cfunits_double_count  # by Denton Gentry
        self.repeated_cost_for_iunits = repeated_cost_for_iunits  # by Denton Gentry
        self.electricity_unit_factor = electricity_unit_factor  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def ref_population(self):  # by Denton Gentry
        """Population by region for the reference case.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!P16:Z63  # by Denton Gentry
        """  # by Denton Gentry
        filename = os.path.join(self.datadir, 'unitadoption_ref_population.csv')  # by Denton Gentry
        result = pd.read_csv(filename, index_col=0, skipinitialspace=True,  # by Denton Gentry
                             skip_blank_lines=True, comment='#')  # by Denton Gentry
        result.index = result.index.astype(int)  # by Denton Gentry
        result.name = "ref_population"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def ref_gdp(self):  # by Denton Gentry
        """GDP by region for the reference case.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!AB16:AL63  # by Denton Gentry
        """  # by Denton Gentry
        filename = os.path.join(self.datadir, 'unitadoption_ref_gdp.csv')  # by Denton Gentry
        result = pd.read_csv(filename, index_col=0, skipinitialspace=True,  # by Denton Gentry
                             skip_blank_lines=True, comment='#')  # by Denton Gentry
        result.index = result.index.astype(int)  # by Denton Gentry
        result.name = "ref_gdp"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def ref_gdp_per_capita(self):  # by Denton Gentry
        """GDP per capita for the reference case.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!AN16:AX63  # by Denton Gentry
        """  # by Denton Gentry
        result = self.ref_gdp() / self.ref_population()  # by Denton Gentry
        result.name = "ref_gdp_per_capita"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def ref_tam_per_capita(self):  # by Denton Gentry
        """Total Addressable Market per capita for the reference case.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!BA16:BK63  # by Denton Gentry
        """  # by Denton Gentry
        result = self.ref_tam_per_region / self.ref_population()  # by Denton Gentry
        result.name = "ref_tam_per_capita"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def ref_tam_per_gdp_per_capita(self):  # by Denton Gentry
        """Total Addressable Market per unit of GDP per capita for the reference case.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!BM16:BW63  # by Denton Gentry
        """  # by Denton Gentry
        result = self.ref_tam_per_region / self.ref_gdp_per_capita()  # by Denton Gentry
        result.name = "ref_tam_per_gdp_per_capita"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def ref_tam_growth(self):  # by Denton Gentry
        """Growth in Total Addressable Market for the reference case.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!BY16:CI63  # by Denton Gentry
        """  # by Denton Gentry
        calc = self.ref_tam_per_region.rolling(2).apply(lambda x: x[1] - x[0], raw=True)  # by Denton Gentry
        calc.loc[2014] = [''] * calc.shape[1]  # empty row  # by Denton Gentry
        calc.name = "ref_tam_growth"  # by Denton Gentry
        return calc  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def pds_population(self):  # by Denton Gentry
        """Population by region for the Project Drawdown Solution case.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!P68:Z115  # by Denton Gentry
        """  # by Denton Gentry
        filename = os.path.join(self.datadir, 'unitadoption_pds_population.csv')  # by Denton Gentry
        result = pd.read_csv(filename, index_col=0, skipinitialspace=True,  # by Denton Gentry
                             skip_blank_lines=True, comment='#')  # by Denton Gentry
        result.index = result.index.astype(int)  # by Denton Gentry
        result.name = "pds_population"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def pds_gdp(self):  # by Denton Gentry
        """GDP by region for the Project Drawdown Solution case.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!AB68:AL115  # by Denton Gentry
        """  # by Denton Gentry
        filename = os.path.join(self.datadir, 'unitadoption_pds_gdp.csv')  # by Denton Gentry
        result = pd.read_csv(filename, index_col=0, skipinitialspace=True,  # by Denton Gentry
                             skip_blank_lines=True, comment='#')  # by Denton Gentry
        result.index = result.index.astype(int)  # by Denton Gentry
        result.name = "pds_gdp"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def pds_gdp_per_capita(self):  # by Denton Gentry
        """GDP per capita for the Project Drawdown Solution case.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!AN68:AX115  # by Denton Gentry
        """  # by Denton Gentry
        result = self.pds_gdp() / self.pds_population()  # by Denton Gentry
        result.name = "pds_gdp_per_capita"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def pds_tam_per_capita(self):  # by Denton Gentry
        """Total Addressable Market per capita for the Project Drawdown Solution case.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!BA68:BK115  # by Denton Gentry
        """  # by Denton Gentry
        result = self.pds_tam_per_region / self.pds_population()  # by Denton Gentry
        result.name = "pds_tam_per_capita"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def pds_tam_per_gdp_per_capita(self):  # by Denton Gentry
        """Total Addressable Market per unit of GDP per capita for the Project Drawdown Solution case.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!BM68:BW115  # by Denton Gentry
        """  # by Denton Gentry
        result = self.pds_tam_per_region / self.pds_gdp_per_capita()  # by Denton Gentry
        result.name = "pds_tam_per_gdp_per_capita"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def pds_tam_growth(self):  # by Denton Gentry
        """Growth in Total Addressable Market for the Project Drawdown Solution case.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!BY68:CI115  # by Denton Gentry
        """  # by Denton Gentry
        calc = self.pds_tam_per_region.rolling(2).apply(lambda x: x[1] - x[0], raw=True)  # by Denton Gentry
        calc.loc[2014] = [''] * calc.shape[1]  # empty row  # by Denton Gentry
        calc.name = "pds_tam_growth"  # by Denton Gentry
        return calc  # by Denton Gentry

    # by Denton Gentry
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
                val = min(degraded_land + (protected_land - degraded_land) * self.ac.disturbance_rate,
                          protected_land)
            elif protected_or_unprotected == 'unprotected':
                tla = self.tla_per_region.at[y, 'World']
                val = min(degraded_land + (tla - protected_land - degraded_land) * self.ac.degradation_rate,
                          tla)
            df.at[y, 'World'] = val
        return df

    @lru_cache()  # by Denton Gentry
    def soln_pds_cumulative_funits(self):  # by Denton Gentry
        """Cumulative Functional Units Utilized.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!Q134:AA181  # by Denton Gentry
        """  # by Denton Gentry
        first_year = self.soln_pds_funits_adopted.fillna(0.0)  # by Denton Gentry
        if self.bug_cfunits_double_count:  # by Denton Gentry
            # in a number of older solutions, 'Advanced Controls'!$C$61:C70 is added to  # by Denton Gentry
            # the 2014 soln_pds_cumulative_funits, which ends up double counting 2014.  # by Denton Gentry
            # We optionally enable this bug-for-bug compatibility.  # by Denton Gentry
            # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.z9hqutnbnigx  # by Denton Gentry
            omit_world = self.soln_pds_funits_adopted.iloc[[0], :].fillna(0.0).copy(deep=True)  # by Denton Gentry
            omit_world['World'] = 0.0  # by Denton Gentry
            first_year = first_year.add(omit_world, fill_value=0)  # by Denton Gentry
        result = first_year.cumsum(axis=0, skipna=False)  # by Denton Gentry
        result.name = "soln_pds_cumulative_funits"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_tot_iunits_reqd(self):  # by Denton Gentry
        """Total iunits required each year.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!AX134:BH181  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_pds_funits_adopted
        if self.ac.soln_avg_annual_use is not None:  # RRS models
            result = result / self.ac.soln_avg_annual_use
        result.name = "soln_pds_tot_iunits_reqd"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_new_iunits_reqd(self):  # by Denton Gentry
        """New implementation units required (includes replacement units)  # by Denton Gentry
      # by Denton Gentry
           Should reflect the unit lifetime assumed in the First Cost tab.  # by Denton Gentry
           For simplicity assumed a fix lifetime rather than a gaussian  # by Denton Gentry
           distribution, but this can be changed if needed.  # by Denton Gentry
      # by Denton Gentry
           This is used to calculate Advanced Controls Output of Solution  # by Denton Gentry
           Implementation Units Adopted.  This is also used to Calculate  # by Denton Gentry
           First Cost, Marginal First Cost and NPV.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!AG136:AQ182  # by Denton Gentry
        """  # by Denton Gentry
        if self.repeated_cost_for_iunits:  # by Denton Gentry
            return self.soln_pds_tot_iunits_reqd().iloc[1:].copy(deep=True).clip(lower=0.0)  # by Denton Gentry
        result = self.soln_pds_tot_iunits_reqd().diff().clip(lower=0).iloc[
                 1:]  # iloc[0] NA after diff  # by Denton Gentry
        for region, column in result.iteritems():  # by Denton Gentry
            for year, value in column.iteritems():  # by Denton Gentry
                # Add replacement units, if needed by adding the number of units  # by Denton Gentry
                # added N * soln_lifetime_replacement ago, that now need replacement.  # by Denton Gentry
                replacement_year = int(year - (self.ac.soln_lifetime_replacement_rounded + 1))  # by Denton Gentry
                if replacement_year in result.index:  # by Denton Gentry
                    fa = self.soln_pds_funits_adopted  # by Denton Gentry
                    prior_year = year - self.ac.soln_lifetime_replacement_rounded - 1  # by Denton Gentry
                    if fa.loc[prior_year, region] <= fa.loc[year, region]:  # by Denton Gentry
                        result.at[year, region] += result.at[replacement_year, region]  # by Denton Gentry
        result.name = "soln_pds_new_iunits_reqd"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_big4_iunits_reqd(self):  # by Denton Gentry
        """Implementation units required in USA/EU/China/India vs Rest of World.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!BN136:BS182  # by Denton Gentry
        """  # by Denton Gentry
        soln_pds_tot_iunits_reqd = self.soln_pds_tot_iunits_reqd()  # by Denton Gentry
        result = pd.DataFrame(0, index=soln_pds_tot_iunits_reqd.index.copy(),  # by Denton Gentry
                              columns=["Rest of World", "China", "India", "EU", "USA"],  # by Denton Gentry
                              dtype='float64')  # by Denton Gentry
        result["China"] = soln_pds_tot_iunits_reqd["China"]  # by Denton Gentry
        result["India"] = soln_pds_tot_iunits_reqd["India"]  # by Denton Gentry
        result["EU"] = soln_pds_tot_iunits_reqd["EU"]  # by Denton Gentry
        result["USA"] = soln_pds_tot_iunits_reqd["USA"]  # by Denton Gentry
        result["Rest of World"] = (soln_pds_tot_iunits_reqd["World"] -  # by Denton Gentry
                                   soln_pds_tot_iunits_reqd["China"].fillna(0.0) -  # by Denton Gentry
                                   soln_pds_tot_iunits_reqd["India"].fillna(0.0) -  # by Denton Gentry
                                   soln_pds_tot_iunits_reqd["EU"].fillna(0.0) -  # by Denton Gentry
                                   soln_pds_tot_iunits_reqd["USA"].fillna(0.0))  # by Denton Gentry
        result.name = "soln_pds_big4_iunits_reqd"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_ref_cumulative_funits(self):  # by Denton Gentry
        """Cumulative functional units.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!Q197:AA244  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_ref_funits_adopted.fillna(0.0).cumsum(axis=0)  # by Denton Gentry
        result.name = "soln_ref_cumulative_funits"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_ref_tot_iunits_reqd(self):  # by Denton Gentry
        """Total implementation units required.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!AX197:BH244"""  # by Denton Gentry
        result = self.soln_ref_funits_adopted
        if self.ac.soln_avg_annual_use is not None:  # RRS models
            result = result / self.ac.soln_avg_annual_use
        result.name = "soln_ref_tot_iunits_reqd"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_ref_new_iunits_reqd(self):  # by Denton Gentry
        """New implementation units required (includes replacement units)  # by Denton Gentry
      # by Denton Gentry
           Should reflect the unit lifetime assumed in the First Cost tab. For  # by Denton Gentry
           simplicity assumed a fix lifetime rather than a gaussian distribution,  # by Denton Gentry
           but this can be changed if needed.  # by Denton Gentry
      # by Denton Gentry
           This table is also used to Calculate  Marginal First Cost and NPV.  # by Denton Gentry
      # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!AG197:AQ244  # by Denton Gentry
        """  # by Denton Gentry
        if self.repeated_cost_for_iunits:  # by Denton Gentry
            return self.soln_ref_tot_iunits_reqd().iloc[1:].copy(deep=True).clip(lower=0.0)  # by Denton Gentry
        result = self.soln_ref_tot_iunits_reqd().diff().clip(lower=0).iloc[
                 1:]  # iloc[0] NA after diff  # by Denton Gentry
        for region, column in result.iteritems():  # by Denton Gentry
            for year, value in column.iteritems():  # by Denton Gentry
                # Add replacement units, if needed by adding the number of units  # by Denton Gentry
                # added N * soln_lifetime_replacement ago, that now need replacement.  # by Denton Gentry
                replacement_year = int(year - (self.ac.soln_lifetime_replacement_rounded + 1))  # by Denton Gentry
                if replacement_year in result.index:  # by Denton Gentry
                    fa = self.soln_ref_funits_adopted  # by Denton Gentry
                    prior_year = year - self.ac.soln_lifetime_replacement_rounded - 1  # by Denton Gentry
                    if fa.loc[prior_year, region] <= fa.loc[year, region]:  # by Denton Gentry
                        result.at[year, region] += result.at[replacement_year, region]  # by Denton Gentry
        result.name = "soln_ref_new_iunits_reqd"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_net_annual_funits_adopted(self):  # by Denton Gentry
        """Net annual functional units adopted.  # by Denton Gentry
      # by Denton Gentry
           Return value is a DataFrame with an index of years, columns for each  # by Denton Gentry
           region and floating point data values.  # by Denton Gentry
      # by Denton Gentry
           This represents the total additional functional units captured either  # by Denton Gentry
           by the CONVENTIONAL mix of technologies/practices in the REF case  # by Denton Gentry
           scenario, OR total growth of the SOLUTION in the PDS scenario,  # by Denton Gentry
           i.e. in addition to the current growth of the SOLUTION in the REF  # by Denton Gentry
           scenario.  # by Denton Gentry
      # by Denton Gentry
           This is used to calculate the Operating Cost, Grid, Fuel, Direct and  # by Denton Gentry
           (optionally) Indirect Emissions.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!B251:L298  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_pds_funits_adopted - self.soln_ref_funits_adopted  # by Denton Gentry
        result.name = "soln_net_annual_funits_adopted"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()
    def net_annual_land_units_adopted(self):  # by Denton Gentry
        """Similar to soln_net_annual_funits_adopted, for Land models.  # by Denton Gentry
           Conservation Agriculture 'Unit Adoption Calculations'!B251:L298  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_net_annual_funits_adopted()  # by Denton Gentry
        result.name = 'net_annual_land_units_adopted'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def conv_ref_tot_iunits(self):
        """  # by Denton Gentry
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
            result = ((self.ref_tam_per_region - self.soln_ref_funits_adopted.fillna(0.0)) /  # by Denton Gentry
                      self.ac.conv_avg_annual_use)  # by Denton Gentry
        result.name = "conv_ref_tot_iunits"
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def conv_ref_annual_tot_iunits(self):  # by Denton Gentry
        """Number of Implementation Units of the Conventional practice/technology that would  # by Denton Gentry
           be needed in the REF Scenario to meet the Functional Unit Demand met by the PDS  # by Denton Gentry
           Implementation Units in the PDS Scenario. This is equivalent to the number of Annual  # by Denton Gentry
           Active CONVENTIONAL units that would have been needed in REF but are not needed in PDS  # by Denton Gentry
           scenario, since SOLUTION units are used as a direct replacement for CONVENTIONAL units.  # by Denton Gentry
           Implementation Conventional Units =  ((Total Annual Functional Units(PDS) -  # by Denton Gentry
               Total Annual Functional units (REF) ) / Average Annual Use Per Conventional Unit)  # by Denton Gentry
      # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!AX251:BH298  # by Denton Gentry
        """  # by Denton Gentry
        result = self.soln_net_annual_funits_adopted()
        if self.ac.conv_avg_annual_use is not None:  # RRS models
            result = result / self.ac.conv_avg_annual_use  # by Denton Gentry
        result.name = "conv_ref_annual_tot_iunits"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def conv_ref_new_iunits(self):
        """New implementation units required (includes replacement units)  # by Denton Gentry
      # by Denton Gentry
           Number of Additional Implementation Units of the Conventional practice/technology  # by Denton Gentry
           that would be needed in the REF Scenario to meet the Functional Unit Demand met by  # by Denton Gentry
           the PDS Implementation Units in the PDS Scenario. This is equivalent to the number  # by Denton Gentry
           of Active CONVENTIONAL units that would have been sold/produced in REF but are not  # by Denton Gentry
           sold/produced in PDS scenario, since SOLUTION units are used as a direct  # by Denton Gentry
           replacement for CONVENTIONAL units.  # by Denton Gentry
      # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!AG251:AQ298  # by Denton Gentry
        """  # by Denton Gentry
        if self.repeated_cost_for_iunits:  # by Denton Gentry
            return self.conv_ref_annual_tot_iunits().iloc[1:].copy(deep=True).clip(lower=0.0)  # by Denton Gentry
        growth = self.conv_ref_annual_tot_iunits().diff().clip(lower=0).iloc[
                 1:]  # iloc[0] NA after diff  # by Denton Gentry
        replacements = pd.DataFrame(0, index=growth.index.copy(), columns=growth.columns.copy(),  # by Denton Gentry
                                    dtype='float64')  # by Denton Gentry
        for region, column in replacements.iteritems():  # by Denton Gentry
            for year, value in column.iteritems():  # by Denton Gentry
                # Add replacement units, if needed by adding the number of units  # by Denton Gentry
                # added N * conv_lifetime_replacement ago, that now need replacement.  # by Denton Gentry
                replacement_year = int(year - (self.ac.conv_lifetime_replacement_rounded + 1))  # by Denton Gentry
                while replacement_year in growth.index:  # by Denton Gentry
                    replacements.at[year, region] += growth.at[replacement_year, region]  # by Denton Gentry
                    replacement_year -= (self.ac.conv_lifetime_replacement_rounded + 1)  # by Denton Gentry
        result = growth + replacements  # by Denton Gentry
        result.name = "conv_ref_new_iunits"
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_net_grid_electricity_units_saved(self):  # by Denton Gentry
        """Energy Units (e.g. TWh, tonnes oil equivalent, million therms, etc.) are  # by Denton Gentry
           calculated by multiplying the net annual functional units adopted by the  # by Denton Gentry
           annual energy saved per unit (specified in the main controls). In some rare  # by Denton Gentry
           cases the energy saved per unit installed may vary by region and/or time,  # by Denton Gentry
           in which case a separate tab for that variable may prove necessary.  # by Denton Gentry
      # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!B307:L354  # by Denton Gentry
           Irrigation Efficiency 'Unit Adoption Calculations'!B307:L354, 10^6 electricity_unit_factor  # by Denton Gentry
        """  # by Denton Gentry
        m = (self.ac.soln_energy_efficiency_factor * self.ac.conv_annual_energy_used *  # by Denton Gentry
             self.electricity_unit_factor)  # by Denton Gentry
        result = self.soln_net_annual_funits_adopted().multiply(m)  # by Denton Gentry
        result.name = "soln_pds_net_grid_electricity_units_saved"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_net_grid_electricity_units_used(self):  # by Denton Gentry
        """Energy Units Used (TWh) are calculated by multiplying the net annual functional  # by Denton Gentry
           units adopted by the average annual electricity used by the solution per functional  # by Denton Gentry
           unit (specified in the main controls) minus  net annual functional units adopted by  # by Denton Gentry
           the average annual electricity used by the conventional technologies/practices  # by Denton Gentry
           (specified in the main controls). In some rare cases the energy saved per unit  # by Denton Gentry
           installed may vary by region and/or time, in which case a separate tab for that  # by Denton Gentry
           variable may prove necessary.  # by Denton Gentry
      # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!Q307:AA354  # by Denton Gentry
           Irrigation Efficiency 'Unit Adoption Calculations'!Q307:AA354, 10^6 electricity_unit_factor  # by Denton Gentry
        """  # by Denton Gentry

        def calc(x):  # by Denton Gentry
            if self.ac.soln_annual_energy_used:  # by Denton Gentry
                return ((self.ac.soln_annual_energy_used - self.ac.conv_annual_energy_used) *  # by Denton Gentry
                        self.electricity_unit_factor * x)  # by Denton Gentry
            else:  # by Denton Gentry
                return 0.0  # by Denton Gentry

        result = self.soln_net_annual_funits_adopted().applymap(calc)  # by Denton Gentry
        result.name = "soln_pds_net_grid_electricity_units_used"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_fuel_units_avoided(self):  # by Denton Gentry
        """Fuel consumption avoided annually.  # by Denton Gentry
           Fuel avoided = CONVENTIONAL stock avoided * Volume consumed by CONVENTIONAL  # by Denton Gentry
               unit per year * Fuel Efficiency of SOLUTION  # by Denton Gentry
      # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!AD307:AN354  # by Denton Gentry
        """  # by Denton Gentry
        m = self.ac.conv_fuel_consumed_per_funit * self.ac.soln_fuel_efficiency_factor  # by Denton Gentry
        result = self.soln_net_annual_funits_adopted().multiply(m)  # by Denton Gentry
        result.name = "soln_pds_fuel_units_avoided"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_direct_co2_emissions_saved(self):  # by Denton Gentry
        """Direct emissions of CO2 avoided, in tons.  # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!AT307:BD354  # by Denton Gentry
        """  # by Denton Gentry

        def calc(x):  # by Denton Gentry
            return (self.ac.conv_emissions_per_funit * x) - (self.ac.soln_emissions_per_funit * x)  # by Denton Gentry

        result = self.soln_net_annual_funits_adopted().applymap(calc)  # by Denton Gentry
        result.name = "soln_pds_direct_co2_emissions_saved"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_direct_ch4_co2_emissions_saved(self):  # by Denton Gentry
        """Direct emissions of CH4 avoided, in tons of equivalent CO2.  # by Denton Gentry
      # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!BF307:BP354  # by Denton Gentry
        """  # by Denton Gentry
        ef = emissionsfactors.CO2Equiv(self.ac.co2eq_conversion_source)  # by Denton Gentry
        if self.ac.ch4_is_co2eq:  # by Denton Gentry
            result = self.soln_net_annual_funits_adopted() * self.ac.ch4_co2_per_twh  # by Denton Gentry
        else:  # by Denton Gentry
            result = self.soln_net_annual_funits_adopted() * ef.CH4multiplier * self.ac.ch4_co2_per_twh  # by Denton Gentry
        result.name = "soln_pds_direct_ch4_co2_emissions_saved"  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def soln_pds_direct_n2o_co2_emissions_saved(self):  # by Denton Gentry
        """Direct emissions of N2O avoided, in tons of CO2 equivalents.  # by Denton Gentry
      # by Denton Gentry
           SolarPVUtil 'Unit Adoption Calculations'!BR307:CB354  # by Denton Gentry
        """  # by Denton Gentry
        ef = emissionsfactors.CO2Equiv(self.ac.co2eq_conversion_source)  # by Denton Gentry
        if self.ac.n2o_is_co2eq:  # by Denton Gentry
            result = self.soln_net_annual_funits_adopted() * self.ac.n2o_co2_per_twh  # by Denton Gentry
        else:  # by Denton Gentry
            result = self.soln_net_annual_funits_adopted() * ef.N2Omultiplier * self.ac.n2o_co2_per_twh  # by Denton Gentry
        result.name = "soln_pds_direct_n2o_co2_emissions_saved"  # by Denton Gentry
        return result  # by Denton Gentry

    @lru_cache()  # by Denton Gentry
    def net_land_units_after_emissions_lifetime(self):  # by Denton Gentry
        """Emissions after the calculated lifetime (which is often very long, ex: 100 years)  # by Denton Gentry
      # by Denton Gentry
           This table is used to calculate the Annual Direct Emissions of all GH Gases if the User  # by Denton Gentry
           selects "Annual" accounting (ie the direct emissions are released for a certain number  # by Denton Gentry
           of years rather than only in the year of adoption).  # by Denton Gentry
      # by Denton Gentry
           Conservation Agriculture 'Unit Adoption Calculations'!EI251:ES298  # by Denton Gentry
        """  # by Denton Gentry
        if self.ac.delay_protection_1yr:  # by Denton Gentry
            funits = self.cumulative_reduction_in_total_degraded_land()
        else:
            funits = self.net_annual_land_units_adopted()
        result = pd.DataFrame(0, index=funits.index.copy(), columns=funits.columns.copy())  # by Denton Gentry
        first_year = result.first_valid_index() + 1  # by Denton Gentry
        for year, row in result.iterrows():  # by Denton Gentry
            if (year - first_year) > self.ac.land_annual_emissons_lifetime:  # by Denton Gentry
                result.loc[year] = funits.loc[year - self.ac.land_annual_emissons_lifetime - 1]  # by Denton Gentry
        result.name = 'net_land_units_after_emissions_lifetime'  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()
    def soln_pds_annual_land_area_harvested(self):
        """Land Area Harvested is used to estimate the impact of harvesting the product of the land on
           Carbon Sequestration (CO2 Calcs) and on Emissions (CO2 Calcs):
    
           Since some land is cleared every x years, it cannot sequester Carbon in that year, not until
           the land is fully re-planted by the following year. When land is cleared, there are emissions created from at
           least some of the material on the land, these emissions are calculated based on this table.
    
           There is a year's delay before the x-year harvesting frequency begins due to planting time in the first year.
           After that, the x-year frequency continues.
           Afforestation 'Unit Adoption Calculations'!EH135:ER182 """
        funits = self.soln_pds_new_iunits_reqd()
        result = pd.DataFrame(0, index=funits.index.copy(), columns=funits.columns.copy())
        if self.ac.harvest_frequency is None:
            return result
        first_year = result.first_valid_index() + 1
        for year, row in result.iterrows():
            if (year - first_year) > self.ac.harvest_frequency:
                year_last_harvested = year - 1
                total_amount_harvested = 0
                for _ in range(100):  # arbitrary finite range
                    year_last_harvested -= self.ac.harvest_frequency
                    if year_last_harvested < first_year:
                        break
                    total_amount_harvested += funits.loc[year_last_harvested]
                else:
                    raise ValueError(
                        'Check value for harvest frequency: {}'.format(self.ac.harvest_frequency))
                result.loc[year] = total_amount_harvested
        result.name = 'annual_land_harvested_in_pds'
        return result

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
                result = self.annual_reduction_in_total_degraded_land() * ghg_rplu  # by Denton Gentry
        else:  # by Denton Gentry
            # same handling for One-time (Farmland Restoration) and Annual (Conservation Agriculture)  # by Denton Gentry
            result = self.net_annual_land_units_adopted() - self.net_land_units_after_emissions_lifetime()  # by Denton Gentry
            result *= ghg_rplu * (1.0 - self.ac.disturbance_rate)
        result.name = 'direct_{}_emissions_saved_land'.format(ghg)
        return result  # by Denton Gentry

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
                                                 ghg_rplu_rate=self.ac.tch4_co2_rplu_rate)  # by Denton Gentry
