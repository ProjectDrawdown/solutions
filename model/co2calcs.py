"""CO2 Calcs module.

Computes reductions in CO2-equivalent emissions.
"""

from functools import lru_cache
import math

import fair
import numpy as np
import pandas as pd
import model.advanced_controls
import model.dd
import model.fairutil

from model.data_handler import DataHandler
from model.decorators import data_func

C_TO_CO2EQ = 3.666
# Note: a different value of 3.64 is sometimes used for certain results in Excel
# Here we will always use this value for consistency


class CO2Calcs(DataHandler):
    """CO2 Calcs module.
        Arguments:
          ac: advanced_cost.py object, storing settings to control model operation.
          ch4_ppb_calculator:
          soln_pds_net_grid_electricity_units_saved:
          soln_pds_net_grid_electricity_units_used:
          soln_pds_direct_co2_emissions_saved:
          soln_pds_direct_ch4_co2_emissions_saved:
          soln_pds_direct_n2o_co2_emissions_saved:
          soln_pds_new_iunits_reqd:
          soln_ref_new_iunits_reqd:
          conv_ref_new_iunits:
          conv_ref_grid_CO2_per_KWh:
          conv_ref_grid_CO2eq_per_KWh:
          soln_net_annual_funits_adopted:
          fuel_in_liters:
          annual_land_area_harvested: (from unit adoption calcs)
          regime_distribution: (land/ocean distribution from aez/dez data)
      """

    def __init__(self, ac, soln_net_annual_funits_adopted=None, ch4_ppb_calculator=None,
                 soln_pds_net_grid_electricity_units_saved=None,
                 soln_pds_net_grid_electricity_units_used=None,
                 soln_pds_direct_co2eq_emissions_saved=None,
                 soln_pds_direct_co2_emissions_saved=None,
                 soln_pds_direct_ch4_co2_emissions_saved=None,
                 soln_pds_direct_n2o_co2_emissions_saved=None,
                 soln_pds_new_iunits_reqd=None, soln_ref_new_iunits_reqd=None,
                 conv_ref_new_iunits=None, conv_ref_grid_CO2_per_KWh=None,
                 conv_ref_grid_CO2eq_per_KWh=None, fuel_in_liters=None,
                 annual_land_area_harvested=None, regime_distribution=None,
                 tot_red_in_deg_land=None, pds_protected_deg_land=None,
                 ref_protected_deg_land=None, regimes=None):
        self.ac = ac
        self.ch4_ppb_calculator = ch4_ppb_calculator
        self.soln_pds_net_grid_electricity_units_saved = soln_pds_net_grid_electricity_units_saved
        self.soln_pds_net_grid_electricity_units_used = soln_pds_net_grid_electricity_units_used
        self.soln_pds_direct_co2eq_emissions_saved = soln_pds_direct_co2eq_emissions_saved
        self.soln_pds_direct_co2_emissions_saved = soln_pds_direct_co2_emissions_saved
        self.soln_pds_direct_ch4_co2_emissions_saved = soln_pds_direct_ch4_co2_emissions_saved
        self.soln_pds_direct_n2o_co2_emissions_saved = soln_pds_direct_n2o_co2_emissions_saved
        self.soln_pds_new_iunits_reqd = soln_pds_new_iunits_reqd
        self.soln_ref_new_iunits_reqd = soln_ref_new_iunits_reqd
        self.conv_ref_new_iunits = conv_ref_new_iunits
        self.conv_ref_grid_CO2_per_KWh = conv_ref_grid_CO2_per_KWh
        self.conv_ref_grid_CO2eq_per_KWh = conv_ref_grid_CO2eq_per_KWh
        self.soln_net_annual_funits_adopted = soln_net_annual_funits_adopted
        self.fuel_in_liters = fuel_in_liters

        # Land info (for sequestration calcs)
        self.annual_land_area_harvested = annual_land_area_harvested
        self.regime_distribution = regime_distribution
        self.tot_red_in_deg_land = tot_red_in_deg_land  # protection models
        self.pds_protected_deg_land = pds_protected_deg_land  # protection models
        self.ref_protected_deg_land = ref_protected_deg_land  # protection models

        if regimes is not None:
            self.regimes = regimes
        elif self.ac is None or self.ac.solution_category is None:
            self.regimes = None
        elif self.ac.solution_category == model.advanced_controls.SOLUTION_CATEGORY.LAND:
            self.regimes = model.dd.THERMAL_MOISTURE_REGIMES
        elif self.ac.solution_category == model.advanced_controls.SOLUTION_CATEGORY.OCEAN:
            self.regimes = model.dd.THERMAL_DYNAMICAL_REGIMES
        else:
            self.regimes = None

        self.baseline = model.fairutil.baseline_emissions()


    @lru_cache()
    @data_func
    def co2_mmt_reduced(self):
        """CO2 MMT Reduced
           Annual CO2 reductions by region and year are calculated by adding reduced emissions
           derived from the electric grid, the replaced emissions derived from clean renewables,
           the net direct emissions derived from non-electric/non-fuel consumption, and the reduced
           emissions derived from fuel efficiency, and then subtracting the net indirect emissions.
           Most solutions will not utilize all of the defined factors.

           NOTE: The emissions values used are from the regional future grid BAU CO2 emission
           intensity values (by year) from the AMPERE 3 MESSAGE Base model used in the IPCC 5th
           Assessment Report WG3.

           CO2 MMT Reduced = (Grid Emissions Reduced + Grid Emissions Replaced -
             Grid Emissions by Solution) + Fuel Emissions Avoided + Direct Emissions Reduced -
             Net Indirect Emissions
           SolarPVUtil 'CO2 Calcs'!A9:K55
        """
        co2_reduced_grid_emissions = self.co2_reduced_grid_emissions()
        m = pd.DataFrame(0.0, columns=co2_reduced_grid_emissions.columns.copy(),
                         index=co2_reduced_grid_emissions.index.copy(), dtype=np.float64)
        m.index = m.index.astype(int)
        s = self.ac.report_start_year
        e = self.ac.report_end_year
        m = m.add(co2_reduced_grid_emissions.loc[s:e], fill_value=0)
        m = m.add(self.co2_replaced_grid_emissions().loc[s:e], fill_value=0)
        m = m.sub(self.co2_increased_grid_usage_emissions().loc[s:e], fill_value=0)
        m = m.add(self.co2eq_direct_reduced_emissions().loc[s:e], fill_value=0)
        m = m.add(self.co2eq_reduced_fuel_emissions().loc[s:e], fill_value=0)
        m = m.sub(self.co2eq_net_indirect_emissions().loc[s:e], fill_value=0)
        m.name = "co2_mmt_reduced"
        return m

    @lru_cache()
    @data_func
    def co2eq_mmt_reduced(self):
        """CO2-eq MMT Reduced
           Annual CO2-eq reductions by region are calculated by multiplying the estimated energy
           unit savings by region by the emission factor of the energy unit in question by region
           and year. In this sample the values used are the regional future grid BAU CO2-eq emission
           intensity values (by year) from the AMPERE 3 MESSAGE Base model used in the IPCC 5th
           Assessment Report WG3.

           Reduced Grid MMT CO2-eq Emissions = NEU(t) * EF(e,t)

           where
              NEU(t) = Net Energy Units at time, t
              EF(e,t) = CO2-eq Emissions Factor of REF energy grid at time, t
           SolarPVUtil 'CO2 Calcs'!A64:K110
        """
        s = self.ac.report_start_year
        e = self.ac.report_end_year
        if (self.ac.solution_category != model.advanced_controls.SOLUTION_CATEGORY.LAND and
                self.ac.solution_category != model.advanced_controls.SOLUTION_CATEGORY.OCEAN):
            # RRS
            co2eq_reduced_grid_emissions = self.co2eq_reduced_grid_emissions()
            m = pd.DataFrame(0.0, columns=co2eq_reduced_grid_emissions.columns.copy(),
                             index=co2eq_reduced_grid_emissions.index.copy(), dtype=np.float64)
            m.index = m.index.astype(int)
            m = m.add(co2eq_reduced_grid_emissions.loc[s:e], fill_value=0)
            m = m.add(self.co2eq_replaced_grid_emissions().loc[s:e], fill_value=0)
            m = m.sub(self.co2eq_increased_grid_usage_emissions().loc[s:e], fill_value=0)
            m = m.add(self.co2eq_direct_reduced_emissions().loc[s:e], fill_value=0)
            m = m.add(self.co2eq_reduced_fuel_emissions().loc[s:e], fill_value=0)
            m = m.sub(self.co2eq_net_indirect_emissions().loc[s:e], fill_value=0)
        else:
            # LAND/OCEAN
            if self.ac.solution_category == model.advanced_controls.SOLUTION_CATEGORY.LAND:
                regions = model.dd.REGIONS
            else:
                regions = model.dd.OCEAN_REGIONS
            index = pd.Index(list(range(2015, 2061)), name='Year')
            m = pd.DataFrame(0., columns=regions, index=index, dtype=np.float64)
            if (self.soln_pds_direct_co2eq_emissions_saved is not None or
                    self.soln_pds_direct_co2_emissions_saved is not None):
                if self.ac.emissions_use_agg_co2eq is None or self.ac.emissions_use_agg_co2eq:
                    m = m.add(self.soln_pds_direct_co2eq_emissions_saved.loc[s:e], fill_value=0)
                else:
                    m = m.add(self.soln_pds_direct_co2_emissions_saved.loc[s:e], fill_value=0)
                    m = m.add(self.soln_pds_direct_n2o_co2_emissions_saved.loc[s:e], fill_value=0)
                    m = m.add(self.soln_pds_direct_ch4_co2_emissions_saved.loc[s:e], fill_value=0)
            if self.annual_land_area_harvested is not None:
                m = m.sub(self.direct_emissions_from_harvesting().loc[s:e], fill_value=0)
            if self.co2eq_reduced_grid_emissions() is not None:
                m = m.add(self.co2eq_reduced_grid_emissions().loc[s:e], fill_value=0)
            if self.co2eq_increased_grid_usage_emissions() is not None:
                m = m.sub(self.co2eq_increased_grid_usage_emissions().loc[s:e], fill_value=0)
        m.name = "co2eq_mmt_reduced"
        return m


    @lru_cache()
    @data_func
    def co2_sequestered_global(self):
        """
        Total Carbon Sequestration (World section only)
        Returns DataFrame of net annual sequestration by thermal moisture region.
        Tropical Forests 'CO2 Calcs'!A119:G166 (Land models)
        """

        if self.regimes is None:
            return None

        cols = ['All'] + self.regimes
        index = pd.Index(list(range(2015, 2061)), name='Year')
        df = pd.DataFrame(columns=cols, index=index, dtype=np.float64)
        set_regions_from_regime_distribution = False

        if self.tot_red_in_deg_land is not None:
            # regrowth calculation
            if self.ac.delay_regrowth_1yr:
                delayed_index = pd.Index(list(range(2015, 2062)), name='Year')
                undeg_land = self.tot_red_in_deg_land.reset_index(drop=True).set_index(
                        delayed_index)
                pds_deg_land = self.pds_protected_deg_land.reset_index(drop=True).set_index(
                        delayed_index)
                ref_deg_land = self.ref_protected_deg_land.reset_index(drop=True).set_index(
                        delayed_index)
            else:
                undeg_land = self.tot_red_in_deg_land
                pds_deg_land = self.pds_protected_deg_land
                ref_deg_land = self.ref_protected_deg_land

            # The xls uses tables of mature and new growth seq rates across thermal moisture
            # regimes. However, it seems like this was never fully implemented so we assume global
            # seq rate is used for mature growth and new growth is mature growth multiplied by the
            # new growth multiplier set in advanced controls. No functionality for specifying
            # regime-specific seq rates has been implemented.
            if self.ac.include_unprotected_land_in_regrowth_calcs:
                undeg_seq_rate = self.ac.seq_rate_global * (1 - self.ac.global_multi_for_regrowth)
                deg_seq_rate = self.ac.seq_rate_global * (self.ac.global_multi_for_regrowth - 1)
            else:
                undeg_seq_rate = self.ac.seq_rate_global
                deg_seq_rate = self.ac.seq_rate_global * self.ac.global_multi_for_regrowth
            df['All'] = C_TO_CO2EQ * (
                undeg_land * undeg_seq_rate + (pds_deg_land - ref_deg_land) * deg_seq_rate)
            set_regions_from_regime_distribution = True
        else:
            # simple calculation
            disturbance = 1 if self.ac.disturbance_rate is None else 1 - self.ac.disturbance_rate
            net_land = self.soln_net_annual_funits_adopted.loc[index, 'World']
            if self.annual_land_area_harvested is not None:
                net_land -= self.annual_land_area_harvested.loc[index, 'World']
            if pd.isna(self.ac.seq_rate_global):
                for reg in self.regimes:
                    seq_rate = self.ac.seq_rate_per_regime[reg]
                    df[reg] = (C_TO_CO2EQ * net_land * seq_rate * disturbance *
                               self.regime_distribution.loc['Global', reg] /
                               self.regime_distribution.loc['Global', 'All'])
                df['All'] = df.fillna(0.0).sum(axis=1)
            else:
                df['All'] = C_TO_CO2EQ * net_land * self.ac.seq_rate_global * disturbance
                set_regions_from_regime_distribution = True

        if set_regions_from_regime_distribution:
            for reg in self.regimes:
                df[reg] = (df['All'] * self.regime_distribution.loc['Global', reg] /
                        self.regime_distribution.loc['Global', 'All'])

        df.name = 'co2_sequestered_global'
        return df


    @lru_cache()
    @data_func
    def co2_ppm_calculator(self):
        """CO2 parts per million reduction over time calculator.

           Each yearly reduction in CO2 (in million metric ton - MMT) is modeled as a
           discrete avoided pulse. A Simplified atmospheric lifetime function for CO2 is
           taken from Myhrvald and Caldeira (2012) based on the Bern Carbon Cycle model.
           Atmospheric tons of CO2 are converted to parts per million CO2 based on the
           molar mass of CO2 and the moles of atmosphere. CO2-eq emissions are treated
           as CO2 for simplicity and due to the lack of detailed information on emissions
           of other GHGs. If these other GHGs are a significant part of overall reductions,
           this model may not be appropriate.

           SolarPVUtil 'CO2 Calcs'!A119:AW165 (RRS)
           Conservation Agriculture 'CO2 Calcs'!A172:AW218 (Land)
        """

        if self.ac.emissions_use_co2eq:
            co2_vals = self.co2eq_mmt_reduced()['World']
        else:
            co2_vals = self.co2_mmt_reduced()['World']

        if (self.ac.solution_category == model.advanced_controls.SOLUTION_CATEGORY.LAND or
                self.ac.solution_category == model.advanced_controls.SOLUTION_CATEGORY.OCEAN):
            co2_vals = self.co2_sequestered_global()['All'] + self.co2eq_mmt_reduced()['World']
            assert self.ac.emissions_use_co2eq, 'Land/ocean models must use CO2 eq'

        columns = ['PPM', 'Total'] + list(range(2015, 2061))
        ppm_calculator = pd.DataFrame(0, columns=columns, index=co2_vals.index.copy(),
                                      dtype=np.float64)
        ppm_calculator.index = ppm_calculator.index.astype(int)
        ppm_calculator.index.name = 'Year'
        first_year = ppm_calculator.first_valid_index()
        last_year = ppm_calculator.last_valid_index()
        for year in ppm_calculator.index:
            if (year < self.ac.report_start_year and
                    self.ac.solution_category != model.advanced_controls.SOLUTION_CATEGORY.LAND):
                # On RRS xls models this skips the calc but on LAND the calc is done anyway
                # Note that this affects the values for all years and should probably NOT be
                # skipped (i.e. LAND is the correct implementation)
                # see: https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#
                continue
            b = co2_vals[year]
            for delta in range(1, last_year - first_year + 2):
                if (year + delta - 1) > last_year:
                    break
                val = 0.217
                val += 0.259 * math.exp(-delta / 172.9)
                val += 0.338 * math.exp(-delta / 18.51)
                val += 0.186 * math.exp(-delta / 1.186)
                ppm_calculator.loc[year + delta - 1, year] = b * val
        ppm_calculator.loc[:, 'Total'] = ppm_calculator.sum(axis=1)
        for year in ppm_calculator.index:
            ppm_calculator.at[year, 'PPM'] = ppm_calculator.at[year, 'Total'] / (44.01 * 1.8 * 100)
        ppm_calculator.name = 'co2_ppm_calculator'
        return ppm_calculator


    @lru_cache()
    @data_func
    def co2eq_ppm_calculator(self):
        """PPM calculations for CO2, CH4, and CO2-eq from other sources.
           RRS: SolarPVUtil 'CO2 Calcs'!A171:F217
           LAND: Improved Rice 'CO2 Calcs'!A224:H270
        """
        co2_ppm_calculator = self.co2_ppm_calculator()
        ppm_calculator = pd.DataFrame(
                0, columns=["CO2-eq PPM", "CO2 PPM", "CH4 PPB", "CO2 RF", "CH4 RF"],
                index=co2_ppm_calculator.index.copy(), dtype=np.float64)
        ppm_calculator.index = ppm_calculator.index.astype(int)
        ppm_calculator["CO2 PPM"] = co2_ppm_calculator["PPM"]
        ppm_calculator["CO2 RF"] = ppm_calculator["CO2 PPM"].apply(co2_rf)
        ppm_calculator["CH4 PPB"] = self.ch4_ppb_calculator["PPB"]
        ppm_calculator["CH4 RF"] = ppm_calculator["CH4 PPB"].apply(ch4_rf)
        s = ppm_calculator["CO2 RF"] + ppm_calculator["CH4 RF"]
        ppm_calculator["CO2-eq PPM"] = s.apply(co2eq_ppm)
        return ppm_calculator


    @lru_cache()
    @data_func
    def co2_reduced_grid_emissions(self):
        """Reduced Grid Emissions = NE(t) * EF(e,t)

           where
              NE(t) = Net Energy Units at time, t
              EF(e,t) = CO2 Emissions Factor of REF energy grid at time, t
           SolarPVUtil 'CO2 Calcs'!A234:K280
        """
        return self.soln_pds_net_grid_electricity_units_saved * self.conv_ref_grid_CO2_per_KWh

    @lru_cache()
    @data_func
    def co2_replaced_grid_emissions(self):
        """CO2 Replaced Grid Emissions = NAFU(Sol,t) * EF(e,t)  (i.e. only direct emissions)
           where
              NAFU(Sol,t) = Net annual functional units captured by solution at time, t
              EF(e,t) = CO2 Emissions Factor of REF energy grid at time, t
           SolarPVUtil 'CO2 Calcs'!R234:AB280
        """
        if self.ac.solution_category == model.advanced_controls.SOLUTION_CATEGORY.REPLACEMENT:
            return self.soln_net_annual_funits_adopted * self.conv_ref_grid_CO2_per_KWh
        else:
            return self.soln_net_annual_funits_adopted * 0


    @lru_cache()
    @data_func
    def co2_increased_grid_usage_emissions(self):
        """Increased Grid Emissions (MMT CO2e) = NEU(t) * EF(e,t)

           where
              NEU(t) = Net Energy Units Used at time, t
              EF(e,t) = CO2 Emissions Factor of REF energy grid at time, t
           SolarPVUtil 'CO2 Calcs'!AI234:AS280
        """
        return self.soln_pds_net_grid_electricity_units_used * self.conv_ref_grid_CO2_per_KWh


    @lru_cache()
    @data_func
    def co2eq_reduced_grid_emissions(self):
        """Reduced Grid MMT CO2-eq Emissions = NEU(t) * EF(e,t)

           where
              NEU(t) = Net Energy Units at time, t
              EF(e,t) = CO2-eq Emissions Factor of REF energy grid at time, t
           SolarPVUtil 'CO2 Calcs'!A288:K334
           Irrigation Efficiency 'CO2 Calcs'!A365:K411
        """
        if (self.soln_pds_net_grid_electricity_units_saved is None or
            self.conv_ref_grid_CO2eq_per_KWh is None):
            return None
        return self.soln_pds_net_grid_electricity_units_saved * self.conv_ref_grid_CO2eq_per_KWh


    @lru_cache()
    @data_func
    def co2eq_replaced_grid_emissions(self):
        """CO2-equivalent replaced Grid MMT CO2-eq Emissions = NAFU(Sol,t) * EF(e,t)

           where
              NAFU(Sol,t) = Net annual functional units captured by solution at time, t
              EF(e,t) = CO2-eq Emissions Factor of REF energy grid at time, t
           SolarPVUtil 'CO2 Calcs'!R288:AB334
           (Not present in Land solutions)
        """
        if self.ac.solution_category == model.advanced_controls.SOLUTION_CATEGORY.REPLACEMENT:
            return self.soln_net_annual_funits_adopted * self.conv_ref_grid_CO2eq_per_KWh
        else:
            return self.soln_net_annual_funits_adopted * 0


    @lru_cache()
    @data_func
    def co2eq_increased_grid_usage_emissions(self):
        """Increased Grid Emissions (MMT CO2e) = NEU(t) * EF(e,t)

           where
              NEU(t) = Net Energy Units Used at time, t
              EF(e,t) = CO2-eq Emissions Factor of REF energy grid at time, t
           SolarPVUtil 'CO2 Calcs'!AI288:AS334
           Irrigation Efficiency 'CO2 Calcs'!R417:AB463
        """
        if (self.soln_pds_net_grid_electricity_units_used is None or
            self.conv_ref_grid_CO2eq_per_KWh is None):
            return None
        return self.soln_pds_net_grid_electricity_units_used * self.conv_ref_grid_CO2eq_per_KWh


    @lru_cache()
    @data_func
    def co2eq_direct_reduced_emissions(self):
        """Direct MMT CO2-eq Emissions Reduced = [DEm(Con,t) - DEm(Sol,t)]  / 1000000

           where
              DEm(Con,t) = Direct Emissions of Conventional at time, t
              DEm(Sol,t) = Direct Emissions of Solution at time, t

              NOTE: Includes CH4-CO2-eq and N2O-CO2-eq
           SolarPVUtil 'CO2 Calcs'!A344:K390
        """
        return (self.soln_pds_direct_co2_emissions_saved / 1000000 +
                self.soln_pds_direct_ch4_co2_emissions_saved / 1000000 +
                self.soln_pds_direct_n2o_co2_emissions_saved / 1000000)


    @lru_cache()
    @data_func
    def co2eq_reduced_fuel_emissions(self):
        """Reduced Fuel Emissions MMT CO2-eq =
            NAFU(Con,t) * Fuel(Con,t) * [Em(cf) -  (1 - FRF) * Em(sf) * if(Fuel Units are Same,
                then: 1, else:UCF)]/10^6

            where:
              NAFU(Con,t) = Net annual functional units captured by conventional mix at time, t
              Fuel(Con,t) = Conventional Fuel Consumption at time, t
              FRF = Fuel Efficiency Factor
              Em(cf) = Emissions Factor of conventional fuel type
              Em(sf) = Emissions Factor of solution fuel type
              UCF = Unit Conversion Factor (TJ per Liter or L per TJ depending on
                Conventional and Solution Fuel units.
           SolarPVUtil 'CO2 Calcs'!U344:AE390
        """
        factor = self.ac.conv_fuel_emissions_factor
        factor -= self.ac.soln_fuel_emissions_factor * self.ac.soln_fuel_learning_rate
        factor *= self.ac.conv_fuel_consumed_per_funit
        result = self.soln_net_annual_funits_adopted * factor / 1000000
        result.name = "co2eq_reduced_fuel_emissions"
        if self.fuel_in_liters:
            raise NotImplementedError("fuel_in_liters=True not handled")
        return result


    @lru_cache()
    @data_func
    def co2eq_net_indirect_emissions(self):
        """Net Indirect Emissions MMT CO2-eq by implementation unit (t) =
              [NIU (Sol,t) * IEm (Sol,t)] - [NIU (Cont.) * IEm (Con,t)]  /  1000000
           where:
              NIU(Sol,t) = New Implementation Units by solution at time, t
              IEm(Sol,t) = Indirect CO2-eq Emission of solution at time, t
              NIU(Con,t) = New Implementation Units by conventional mix at time, t
              IEm(Con,t) = Indirect CO2-eq Emission of conventional mix at time, t
           SolarPVUtil 'CO2 Calcs'!AP344:AZ390
        """
        if self.ac.conv_indirect_co2_is_iunits:
            delta = self.soln_pds_new_iunits_reqd - self.soln_ref_new_iunits_reqd
            result = (delta * self.ac.soln_indirect_co2_per_iunit)
            result -= self.conv_ref_new_iunits * self.ac.conv_indirect_co2_per_unit
        else:
            result = self.soln_net_annual_funits_adopted * self.ac.soln_indirect_co2_per_iunit
            result -= self.soln_net_annual_funits_adopted * self.ac.conv_indirect_co2_per_unit
        result /= 1000000
        return result


    @lru_cache()
    def direct_emissions_from_harvesting(self):
        """Net Land Units [Mha]* (Carbon Sequestration Rate [t C/ha/yr] *
           Years of Sequestration [yr] - Carbon Stored even After Harvesting/Clearing [t C/ha]) *
           (CO2 per C)
           Afforestation 'CO2 Calcs'!CU365:DD411"""
        return self.annual_land_area_harvested * (
                self.ac.seq_rate_global * self.ac.harvest_frequency -
                self.ac.carbon_not_emitted_after_harvesting) * C_TO_CO2EQ

    @lru_cache()
    @data_func
    def FaIR_CFT_baseline(self):
        """Return FaIR results for the baseline case.

           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns DataFrame containing columns C, F, T:
             C: CO2 concentration in ppm for the World.
             F: Radiative forcing in watts per square meter
             T: Change in temperature since pre-industrial time in Kelvin
        """
        kwargs = model.fairutil.fair_scm_kwargs()
        (C, F, T) = fair.forward.fair_scm(emissions=self.baseline.values, useMultigas=False, **kwargs)
        result = pd.DataFrame({'C': C, 'F': F, 'T': T}, index=self.baseline.index)
        result.name = 'FaIR_CFT_baseline'
        return result


    @lru_cache()
    @data_func
    def FaIR_CFT(self):
        """Return FaIR results for the baseline + Drawdown solution.

           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns DataFrame containing columns C, F, T:
             C: CO2 concentration in ppm for the World.
             F: Radiative forcing in watts per square meter
             T: Change in temperature since pre-industrial time in Kelvin
        """
        emissions = self.baseline.copy()
        co2eq_mmt_reduced = self.co2eq_mmt_reduced()
        if co2eq_mmt_reduced is not None:
            gtonsC = (co2eq_mmt_reduced['World'] / 1000.0) / C_TO_CO2EQ
            emissions = emissions.subtract(other=gtonsC, fill_value=0.0)
        co2_sequestered_global = self.co2_sequestered_global()
        if co2_sequestered_global is not None:
            gtonsC = (co2_sequestered_global['All'] / 1000.0) / C_TO_CO2EQ
            emissions = emissions.subtract(other=gtonsC, fill_value=0.0)

        kwargs = model.fairutil.fair_scm_kwargs()
        (C, F, T) = fair.forward.fair_scm(emissions=emissions.values, useMultigas=False, **kwargs)
        result = pd.DataFrame({'C': C , 'F': F, 'T': T}, index=emissions.index)
        result.name = 'FaIR_CFT'
        return result


    @lru_cache()
    @data_func
    def FaIR_CFT_RCP45(self):
        """Return FaIR results for the RCP45 case.

           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns DataFrame containing columns C, F, T:
             C: CO2 concentration in ppm for the World.
             F: Radiative forcing in watts per square meter
             T: Change in temperature since pre-industrial time in Kelvin
        """
        kwargs = model.fairutil.fair_scm_kwargs()
        (C, F, T) = fair.forward.fair_scm(emissions=fair.RCPs.rcp45.Emissions.emissions[:, 0],
                useMultigas=False, **kwargs)
        result = pd.DataFrame({'C': C, 'F': F, 'T': T}, index=fair.RCPs.rcp45.Emissions.year)
        result.name = 'FaIR_CFT_RCP45'
        return result

# The following formulae come from the SolarPVUtil Excel implementation of 27Aug18.
# There was no explanation of where they came from or what they really mean.

def co2_rf(x):
    original_co2 = 400
    return 5.35 * math.log((original_co2 + x) / original_co2)



def f(M, N):
    return 0.47 * math.log(
        1 + 2.01 * 10 ** -5 * (M * N) ** 0.75 + 5.31 * 10 ** -15 * M * (M * N) ** 1.52)



def ch4_rf(x):
    original_ch4 = 1800
    original_n2o = 320
    indirect_ch4_forcing_scalar = 0.97 / 0.641
    old_M = original_ch4
    new_M = original_ch4 + x
    N = original_n2o
    return (indirect_ch4_forcing_scalar * 0.036 * (new_M ** 0.5 - old_M ** 0.5) -
            f(new_M, N) + f(old_M, N))


def co2eq_ppm(x):
    original_co2 = 400
    return (original_co2 * math.exp(x / 5.35)) - original_co2
