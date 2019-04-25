"""CO2 Calcs module.  # by Denton Gentry
  # by Denton Gentry
Computes reductions in CO2-equivalent emissions.  # by Denton Gentry
"""  # by Denton Gentry
# by Denton Gentry
from functools import lru_cache  # by Denton Gentry
import math  # by Denton Gentry
import numpy as np  # by Denton Gentry
import pandas as pd  # by Denton Gentry
from model.advanced_controls import SOLUTION_CATEGORY

# by Denton Gentry
THERMAL_MOISTURE_REGIMES = ['Tropical-Humid', 'Temperate/Boreal-Humid', 'Tropical-Semi-Arid',
                            'Temperate/Boreal-Semi-Arid', 'Global Arid', 'Global Arctic']
C_TO_CO2EQ = 3.666


# by Denton Gentry
class CO2Calcs:  # by Denton Gentry
    """CO2 Calcs module.  # by Denton Gentry
        Arguments:  # by Denton Gentry
          ac: advanced_cost.py object, storing settings to control model operation.  # by Denton Gentry
          ch4_ppb_calculator:  # by Denton Gentry
          soln_pds_net_grid_electricity_units_saved:  # by Denton Gentry
          soln_pds_net_grid_electricity_units_used:  # by Denton Gentry
          soln_pds_direct_co2_emissions_saved:  # by Denton Gentry
          soln_pds_direct_ch4_co2_emissions_saved:  # by Denton Gentry
          soln_pds_direct_n2o_co2_emissions_saved:  # by Denton Gentry
          soln_pds_new_iunits_reqd:  # by Denton Gentry
          soln_ref_new_iunits_reqd:  # by Denton Gentry
          conv_ref_new_iunits:
          conv_ref_grid_CO2_per_KWh:  # by Denton Gentry
          conv_ref_grid_CO2eq_per_KWh:  # by Denton Gentry
          soln_net_annual_funits_adopted:  # by Denton Gentry
          fuel_in_liters:  # by Denton Gentry
          annual_land_area_harvested: (from unit adoption calcs)
          land_distribution: (from aez data)
      """  # by Denton Gentry

    def __init__(self, ac, soln_net_annual_funits_adopted=None, ch4_ppb_calculator=None,
                 soln_pds_net_grid_electricity_units_saved=None, soln_pds_net_grid_electricity_units_used=None,

                 soln_pds_direct_co2eq_emissions_saved=None,
                 soln_pds_direct_co2_emissions_saved=None, soln_pds_direct_ch4_co2_emissions_saved=None,

                 soln_pds_direct_n2o_co2_emissions_saved=None, soln_pds_new_iunits_reqd=None,
                 soln_ref_new_iunits_reqd=None, conv_ref_new_iunits=None, conv_ref_grid_CO2_per_KWh=None,

                 conv_ref_grid_CO2eq_per_KWh=None, fuel_in_liters=None, annual_land_area_harvested=None,

                 land_distribution=None, tot_red_in_deg_land=None, pds_protected_deg_land=None,
                 ref_protected_deg_land=None):
        self.ac = ac  # by Denton Gentry
        self.ch4_ppb_calculator = ch4_ppb_calculator  # by Denton Gentry
        self.soln_pds_net_grid_electricity_units_saved = soln_pds_net_grid_electricity_units_saved  # by Denton Gentry
        self.soln_pds_net_grid_electricity_units_used = soln_pds_net_grid_electricity_units_used  # by Denton Gentry
        self.soln_pds_direct_co2eq_emissions_saved = soln_pds_direct_co2eq_emissions_saved
        self.soln_pds_direct_co2_emissions_saved = soln_pds_direct_co2_emissions_saved  # by Denton Gentry
        self.soln_pds_direct_ch4_co2_emissions_saved = soln_pds_direct_ch4_co2_emissions_saved  # by Denton Gentry
        self.soln_pds_direct_n2o_co2_emissions_saved = soln_pds_direct_n2o_co2_emissions_saved  # by Denton Gentry
        self.soln_pds_new_iunits_reqd = soln_pds_new_iunits_reqd  # by Denton Gentry
        self.soln_ref_new_iunits_reqd = soln_ref_new_iunits_reqd  # by Denton Gentry
        self.conv_ref_new_iunits = conv_ref_new_iunits
        self.conv_ref_grid_CO2_per_KWh = conv_ref_grid_CO2_per_KWh  # by Denton Gentry
        self.conv_ref_grid_CO2eq_per_KWh = conv_ref_grid_CO2eq_per_KWh  # by Denton Gentry
        self.soln_net_annual_funits_adopted = soln_net_annual_funits_adopted  # by Denton Gentry
        self.fuel_in_liters = fuel_in_liters  # by Denton Gentry
        # by Denton Gentry
        # Land info (for sequestration calcs)
        self.annual_land_area_harvested = annual_land_area_harvested
        self.land_distribution = land_distribution
        self.tot_red_in_deg_land = tot_red_in_deg_land  # protection models
        self.pds_protected_deg_land = pds_protected_deg_land  # protection models
        self.ref_protected_deg_land = ref_protected_deg_land  # protection models

    @lru_cache()  # by Denton Gentry
    def co2_mmt_reduced(self):  # by Denton Gentry
        """CO2 MMT Reduced  # by Denton Gentry
           Annual CO2 reductions by region and year are calculated by adding reduced emissions  # by Denton Gentry
           derived from the electric grid, the replaced emissions derived from clean renewables,  # by Denton Gentry
           the net direct emissions derived from non-electric/non-fuel consumption, and the reduced  # by Denton Gentry
           emissions derived from fuel efficiency, and then subtracting the net indirect emissions.  # by Denton Gentry
           Most solutions will not utilize all of the defined factors.  # by Denton Gentry
      # by Denton Gentry
           NOTE: The emissions values used are from the regional future grid BAU CO2 emission  # by Denton Gentry
           intensity values (by year) from the AMPERE 3 MESSAGE Base model used in the IPCC 5th  # by Denton Gentry
           Assessment Report WG3.  # by Denton Gentry
      # by Denton Gentry
           CO2 MMT Reduced = (Grid Emissions Reduced + Grid Emissions Replaced - Grid Emissions by Solution)  # by Denton Gentry
             + Fuel Emissions Avoided + Direct Emissions Reduced - Net Indirect Emissions  # by Denton Gentry
           SolarPVUtil 'CO2 Calcs'!A9:K55  # by Denton Gentry
        """  # by Denton Gentry
        co2_reduced_grid_emissions = self.co2_reduced_grid_emissions()  # by Denton Gentry
        m = pd.DataFrame(0.0, columns=co2_reduced_grid_emissions.columns.copy(),  # by Denton Gentry
                         index=co2_reduced_grid_emissions.index.copy(), dtype=np.float64)  # by Denton Gentry
        m.index = m.index.astype(int)  # by Denton Gentry
        s = self.ac.report_start_year  # by Denton Gentry
        e = self.ac.report_end_year  # by Denton Gentry
        m = m.add(co2_reduced_grid_emissions.loc[s:e], fill_value=0)  # by Denton Gentry
        m = m.add(self.co2_replaced_grid_emissions().loc[s:e], fill_value=0)  # by Denton Gentry
        m = m.sub(self.co2_increased_grid_usage_emissions().loc[s:e], fill_value=0)  # by Denton Gentry
        m = m.add(self.co2eq_direct_reduced_emissions().loc[s:e], fill_value=0)  # by Denton Gentry
        m = m.add(self.co2eq_reduced_fuel_emissions().loc[s:e], fill_value=0)  # by Denton Gentry
        m = m.sub(self.co2eq_net_indirect_emissions().loc[s:e], fill_value=0)  # by Denton Gentry
        m.name = "co2_mmt_reduced"  # by Denton Gentry
        return m  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def co2eq_mmt_reduced(self):  # by Denton Gentry
        """CO2-eq MMT Reduced  # by Denton Gentry
           Annual CO2-eq reductions by region are calculated by multiplying the estimated energy  # by Denton Gentry
           unit savings by region by the emission factor of the energy unit in question by region  # by Denton Gentry
           and year. In this sample the values used are the regional future grid BAU CO2-eq emission  # by Denton Gentry
           intensity values (by year) from the AMPERE 3 MESSAGE Base model used in the IPCC 5th  # by Denton Gentry
           Assessment Report WG3.  # by Denton Gentry
      # by Denton Gentry
           Reduced Grid MMT CO2-eq Emissions = NEU(t) * EF(e,t)  # by Denton Gentry
      # by Denton Gentry
           where  # by Denton Gentry
              NEU(t) = Net Energy Units at time, t  # by Denton Gentry
              EF(e,t) = CO2-eq Emissions Factor of REF energy grid at time, t  # by Denton Gentry
           SolarPVUtil 'CO2 Calcs'!A64:K110  # by Denton Gentry
        """  # by Denton Gentry
        s = self.ac.report_start_year  # by Denton Gentry
        e = self.ac.report_end_year  # by Denton Gentry
        if self.ac.solution_category != SOLUTION_CATEGORY.LAND:
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
            # LAND
            index = pd.Index(list(range(2015, 2061)), name='Year')
            m = pd.DataFrame(0., columns=['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                                          'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],

                             index=index, dtype=np.float64)
            if self.soln_pds_direct_co2eq_emissions_saved is not None or self.soln_pds_direct_co2_emissions_saved is not None:
                if self.ac.emissions_use_agg_co2eq is None or self.ac.emissions_use_agg_co2eq:
                    m['World'] = m['World'].add(self.soln_pds_direct_co2eq_emissions_saved['World'].loc[s:e],
                                                fill_value=0)
                else:
                    m['World'] = m['World'].add(self.soln_pds_direct_co2_emissions_saved['World'].loc[s:e],
                                                fill_value=0)
                    m['World'] = m['World'].add(self.soln_pds_direct_n2o_co2_emissions_saved['World'].loc[s:e],
                                                fill_value=0)
                    m['World'] = m['World'].add(self.soln_pds_direct_ch4_co2_emissions_saved['World'].loc[s:e],
                                                fill_value=0)
            if self.annual_land_area_harvested is not None:
                m = m.sub(self.direct_emissions_from_harvesting().loc[s:e], fill_value=0)
            if self.co2eq_reduced_grid_emissions() is not None:  # by Denton Gentry
                m = m.add(self.co2eq_reduced_grid_emissions().loc[s:e], fill_value=0)  # by Denton Gentry
            if self.co2eq_increased_grid_usage_emissions() is not None:  # by Denton Gentry
                m = m.sub(self.co2eq_increased_grid_usage_emissions().loc[s:e], fill_value=0)  # by Denton Gentry
        m.name = "co2eq_mmt_reduced"  # by Denton Gentry
        return m  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()
    def co2_sequestered_global(self):
        """
        Total Carbon Sequestration (World section only)
        Returns DataFrame of net annual sequestration by thermal moisture region.
        Tropical Forests 'CO2 Calcs'!A119:G166 (Land models)  # by Denton Gentry
        """
        assert self.ac.seq_rate_global is not None, 'No sequestration rate set in Advanced Controls'
        cols = ['All'] + THERMAL_MOISTURE_REGIMES
        index = pd.Index(list(range(2015, 2061)), name='Year')
        df = pd.DataFrame(columns=cols, index=index, dtype=np.float64)  # by Denton Gentry
        set_regions_from_distribution = False  # by Denton Gentry

        if self.tot_red_in_deg_land is not None:
            # regrowth calculation
            if self.ac.delay_regrowth_1yr:
                delayed_index = pd.Index(list(range(2015, 2062)), name='Year')
                undeg_land = self.tot_red_in_deg_land.reset_index(drop=True).set_index(delayed_index)
                pds_deg_land = self.pds_protected_deg_land.reset_index(drop=True).set_index(
                    delayed_index)
                ref_deg_land = self.ref_protected_deg_land.reset_index(drop=True).set_index(
                    delayed_index)
            else:
                undeg_land = self.tot_red_in_deg_land
                pds_deg_land = self.pds_protected_deg_land
                ref_deg_land = self.ref_protected_deg_land

            # The xls uses tables of mature and new growth seq rates across thermal moisture regimes. However, it seems
            # like this was never fully implemented so we assume global seq rate is used for mature growth and new growth
            # is mature growth multiplied by the new growth multiplier set in advanced controls. No functionality for
            # specifying regime-specific seq rates has been implemented.
            if self.ac.include_unprotected_land_in_regrowth_calcs:
                undeg_seq_rate = self.ac.seq_rate_global * (1 - self.ac.global_multi_for_regrowth)
                deg_seq_rate = self.ac.seq_rate_global * (self.ac.global_multi_for_regrowth - 1)
            else:
                undeg_seq_rate = self.ac.seq_rate_global
                deg_seq_rate = self.ac.seq_rate_global * self.ac.global_multi_for_regrowth
            df['All'] = C_TO_CO2EQ * (
                undeg_land * undeg_seq_rate + (pds_deg_land - ref_deg_land) * deg_seq_rate)
            set_regions_from_distribution = True  # by Denton Gentry
        else:
            # simple calculation
            disturbance = 1 if self.ac.disturbance_rate is None else 1 - self.ac.disturbance_rate
            net_land = self.soln_net_annual_funits_adopted.loc[index, 'World']
            if self.annual_land_area_harvested is not None:
                net_land -= self.annual_land_area_harvested.loc[index, 'World']
            if pd.isna(self.ac.seq_rate_global):  # by Denton Gentry
                for tmr in THERMAL_MOISTURE_REGIMES:  # by Denton Gentry
                    seq_rate = pd.Series(self.ac.seq_rate_per_regime).loc[tmr]  # by Denton Gentry
                    df[tmr] = (C_TO_CO2EQ * net_land * seq_rate * disturbance *
                               self.land_distribution.loc['Global', tmr] /
                               self.land_distribution.loc['Global', 'All'])
                df['All'] = df.fillna(0.0).sum(axis=1)  # by Denton Gentry
                set_regions_from_distribution = False  # by Denton Gentry
            else:  # by Denton Gentry
                df['All'] = C_TO_CO2EQ * net_land * self.ac.seq_rate_global * disturbance
                set_regions_from_distribution = True  # by Denton Gentry
        # by Denton Gentry
        if set_regions_from_distribution:  # by Denton Gentry
            for tmr in THERMAL_MOISTURE_REGIMES:  # by Denton Gentry
                df[tmr] = df['All'] * self.land_distribution.loc['Global', tmr] / self.land_distribution.loc[
                    'Global', 'All']  # by Denton Gentry

        df.name = 'co2_sequestered_global'  # by Denton Gentry
        return df

    @lru_cache()  # by Denton Gentry
    def co2_ppm_calculator(self):  # by Denton Gentry
        """CO2 parts per million reduction over time calculator.  # by Denton Gentry
      # by Denton Gentry
           Each yearly reduction in CO2 (in million metric ton - MMT) is modeled as a  # by Denton Gentry
           discrete avoided pulse. A Simplified atmospheric lifetime function for CO2 is  # by Denton Gentry
           taken from Myhrvald and Caldeira (2012) based on the Bern Carbon Cycle model.  # by Denton Gentry
           Atmospheric tons of CO2 are converted to parts per million CO2 based on the  # by Denton Gentry
           molar mass of CO2 and the moles of atmosphere. CO2-eq emissions are treated  # by Denton Gentry
           as CO2 for simplicity and due to the lack of detailed information on emissions  # by Denton Gentry
           of other GHGs. If these other GHGs are a significant part of overall reductions,  # by Denton Gentry
           this model may not be appropriate.  # by Denton Gentry
      # by Denton Gentry
           SolarPVUtil 'CO2 Calcs'!A119:AW165 (RRS)  # by Denton Gentry
           Conservation Agriculture 'CO2 Calcs'!A172:AW218 (Land)  # by Denton Gentry
        """  # by Denton Gentry

        if self.ac.emissions_use_co2eq:
            co2_vals = self.co2eq_mmt_reduced()['World']
        else:
            co2_vals = self.co2_mmt_reduced()['World']

        if self.ac.solution_category == SOLUTION_CATEGORY.LAND:
            co2_vals = self.co2_sequestered_global()['All'] + self.co2eq_mmt_reduced()['World']
            assert self.ac.emissions_use_co2eq, 'Land models must use CO2 eq'

        columns = ['PPM', 'Total'] + list(range(2015, 2061))
        ppm_calculator = pd.DataFrame(0, columns=columns, index=co2_vals.index.copy(),
                                      dtype=np.float64)
        ppm_calculator.index = ppm_calculator.index.astype(int)  # by Denton Gentry
        ppm_calculator.index.name = 'Year'  # by Denton Gentry
        first_year = ppm_calculator.first_valid_index()  # by Denton Gentry
        last_year = ppm_calculator.last_valid_index()  # by Denton Gentry
        for year in ppm_calculator.index:  # by Denton Gentry
            if year < self.ac.report_start_year and self.ac.solution_category != SOLUTION_CATEGORY.LAND:
                # On RRS xls models this skips the calc but on LAND the calc is done anyway
                # Note that this affects the values for all years and should probably NOT be skipped
                # (i.e. LAND is the correct implementation)
                # see: https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#
                continue
            b = co2_vals[year]
            for delta in range(1, last_year - first_year + 2):
                if (year + delta - 1) > last_year:  # by Denton Gentry
                    break  # by Denton Gentry
                val = 0.217  # by Denton Gentry
                val += 0.259 * math.exp(-delta / 172.9)  # by Denton Gentry
                val += 0.338 * math.exp(-delta / 18.51)  # by Denton Gentry
                val += 0.186 * math.exp(-delta / 1.186)  # by Denton Gentry
                ppm_calculator.loc[year + delta - 1, year] = b * val  # by Denton Gentry
        ppm_calculator.loc[:, 'Total'] = ppm_calculator.sum(axis=1)
        for year in ppm_calculator.index:  # by Denton Gentry
            ppm_calculator.at[year, 'PPM'] = ppm_calculator.at[year, 'Total'] / (44.01 * 1.8 * 100)
        ppm_calculator.name = 'co2_ppm_calculator'
        return ppm_calculator  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def co2eq_ppm_calculator(self):  # by Denton Gentry
        """PPM calculations for CO2, CH4, and CO2-eq from other sources.  # by Denton Gentry
           RRS: SolarPVUtil 'CO2 Calcs'!A171:F217  # by Denton Gentry
           LAND: Improved Rice 'CO2 Calcs'!A224:H270  # by Denton Gentry
        """  # by Denton Gentry
        co2_ppm_calculator = self.co2_ppm_calculator()  # by Denton Gentry
        ppm_calculator = pd.DataFrame(0,  # by Denton Gentry
                                      columns=["CO2-eq PPM", "CO2 PPM", "CH4 PPB", "CO2 RF", "CH4 RF"],
                                      # by Denton Gentry
                                      index=co2_ppm_calculator.index.copy(), dtype=np.float64)  # by Denton Gentry
        ppm_calculator.index = ppm_calculator.index.astype(int)  # by Denton Gentry
        ppm_calculator["CO2 PPM"] = co2_ppm_calculator["PPM"]  # by Denton Gentry
        ppm_calculator["CO2 RF"] = ppm_calculator["CO2 PPM"].apply(co2_rf)  # by Denton Gentry
        ppm_calculator["CH4 PPB"] = self.ch4_ppb_calculator["PPB"]  # by Denton Gentry
        ppm_calculator["CH4 RF"] = ppm_calculator["CH4 PPB"].apply(ch4_rf)  # by Denton Gentry
        s = ppm_calculator["CO2 RF"] + ppm_calculator["CH4 RF"]  # by Denton Gentry
        ppm_calculator["CO2-eq PPM"] = s.apply(co2eq_ppm)  # by Denton Gentry
        return ppm_calculator  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def co2_reduced_grid_emissions(self):  # by Denton Gentry
        """Reduced Grid Emissions = NE(t) * EF(e,t)  # by Denton Gentry
      # by Denton Gentry
           where  # by Denton Gentry
              NE(t) = Net Energy Units at time, t  # by Denton Gentry
              EF(e,t) = CO2 Emissions Factor of REF energy grid at time, t  # by Denton Gentry
           SolarPVUtil 'CO2 Calcs'!A234:K280  # by Denton Gentry
        """  # by Denton Gentry
        return self.soln_pds_net_grid_electricity_units_saved * self.conv_ref_grid_CO2_per_KWh  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def co2_replaced_grid_emissions(self):  # by Denton Gentry
        """CO2 Replaced Grid Emissions = NAFU(Sol,t) * EF(e,t)  (i.e. only direct emissions)  # by Denton Gentry
           where  # by Denton Gentry
              NAFU(Sol,t) = Net annual functional units captured by solution at time, t  # by Denton Gentry
              EF(e,t) = CO2 Emissions Factor of REF energy grid at time, t  # by Denton Gentry
           SolarPVUtil 'CO2 Calcs'!R234:AB280  # by Denton Gentry
        """  # by Denton Gentry
        if self.ac.solution_category == SOLUTION_CATEGORY.REPLACEMENT:
            return self.soln_net_annual_funits_adopted * self.conv_ref_grid_CO2_per_KWh  # by Denton Gentry
        else:  # by Denton Gentry
            return self.soln_net_annual_funits_adopted * 0  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def co2_increased_grid_usage_emissions(self):  # by Denton Gentry
        """Increased Grid Emissions (MMT CO2e) = NEU(t) * EF(e,t)  # by Denton Gentry
      # by Denton Gentry
           where  # by Denton Gentry
              NEU(t) = Net Energy Units Used at time, t  # by Denton Gentry
              EF(e,t) = CO2 Emissions Factor of REF energy grid at time, t  # by Denton Gentry
           SolarPVUtil 'CO2 Calcs'!AI234:AS280  # by Denton Gentry
        """  # by Denton Gentry
        return self.soln_pds_net_grid_electricity_units_used * self.conv_ref_grid_CO2_per_KWh  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def co2eq_reduced_grid_emissions(self):  # by Denton Gentry
        """Reduced Grid MMT CO2-eq Emissions = NEU(t) * EF(e,t)  # by Denton Gentry
      # by Denton Gentry
           where  # by Denton Gentry
              NEU(t) = Net Energy Units at time, t  # by Denton Gentry
              EF(e,t) = CO2-eq Emissions Factor of REF energy grid at time, t  # by Denton Gentry
           SolarPVUtil 'CO2 Calcs'!A288:K334  # by Denton Gentry
           Irrigation Efficiency 'CO2 Calcs'!A365:K411  # by Denton Gentry
        """  # by Denton Gentry
        if (self.soln_pds_net_grid_electricity_units_saved is None or  # by Denton Gentry
            self.conv_ref_grid_CO2eq_per_KWh is None):  # by Denton Gentry
            return None  # by Denton Gentry
        return self.soln_pds_net_grid_electricity_units_saved * self.conv_ref_grid_CO2eq_per_KWh  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def co2eq_replaced_grid_emissions(self):  # by Denton Gentry
        """CO2-equivalent replaced Grid MMT CO2-eq Emissions = NAFU(Sol,t) * EF(e,t)  # by Denton Gentry
      # by Denton Gentry
           where  # by Denton Gentry
              NAFU(Sol,t) = Net annual functional units captured by solution at time, t  # by Denton Gentry
              EF(e,t) = CO2-eq Emissions Factor of REF energy grid at time, t  # by Denton Gentry
           SolarPVUtil 'CO2 Calcs'!R288:AB334  # by Denton Gentry
           (Not present in Land solutions)  # by Denton Gentry
        """  # by Denton Gentry
        if self.ac.solution_category == SOLUTION_CATEGORY.REPLACEMENT:
            return self.soln_net_annual_funits_adopted * self.conv_ref_grid_CO2eq_per_KWh  # by Denton Gentry
        else:  # by Denton Gentry
            return self.soln_net_annual_funits_adopted * 0  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def co2eq_increased_grid_usage_emissions(self):  # by Denton Gentry
        """Increased Grid Emissions (MMT CO2e) = NEU(t) * EF(e,t)  # by Denton Gentry
      # by Denton Gentry
           where  # by Denton Gentry
              NEU(t) = Net Energy Units Used at time, t  # by Denton Gentry
              EF(e,t) = CO2-eq Emissions Factor of REF energy grid at time, t  # by Denton Gentry
           SolarPVUtil 'CO2 Calcs'!AI288:AS334  # by Denton Gentry
           Irrigation Efficiency 'CO2 Calcs'!R417:AB463  # by Denton Gentry
        """  # by Denton Gentry
        if (self.soln_pds_net_grid_electricity_units_used is None or  # by Denton Gentry
            self.conv_ref_grid_CO2eq_per_KWh is None):  # by Denton Gentry
            return None  # by Denton Gentry
        return self.soln_pds_net_grid_electricity_units_used * self.conv_ref_grid_CO2eq_per_KWh  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def co2eq_direct_reduced_emissions(self):  # by Denton Gentry
        """Direct MMT CO2-eq Emissions Reduced = [DEm(Con,t) - DEm(Sol,t)]  / 1000000  # by Denton Gentry
      # by Denton Gentry
           where  # by Denton Gentry
              DEm(Con,t) = Direct Emissions of Conventional at time, t  # by Denton Gentry
              DEm(Sol,t) = Direct Emissions of Solution at time, t  # by Denton Gentry
      # by Denton Gentry
              NOTE: Includes CH4-CO2-eq and N2O-CO2-eq  # by Denton Gentry
           SolarPVUtil 'CO2 Calcs'!A344:K390  # by Denton Gentry
        """  # by Denton Gentry
        return (self.soln_pds_direct_co2_emissions_saved / 1000000 +  # by Denton Gentry
                self.soln_pds_direct_ch4_co2_emissions_saved / 1000000 +  # by Denton Gentry
                self.soln_pds_direct_n2o_co2_emissions_saved / 1000000)  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def co2eq_reduced_fuel_emissions(self):  # by Denton Gentry
        """Reduced Fuel Emissions MMT CO2-eq =  # by Denton Gentry
            NAFU(Con,t) * Fuel(Con,t) * [Em(cf) -  (1 - FRF) * Em(sf) * if(Fuel Units are Same,  # by Denton Gentry
                then: 1, else:UCF)]/10^6  # by Denton Gentry
      # by Denton Gentry
            where:  # by Denton Gentry
              NAFU(Con,t) = Net annual functional units captured by conventional mix at time, t  # by Denton Gentry
              Fuel(Con,t) = Conventional Fuel Consumption at time, t  # by Denton Gentry
              FRF = Fuel Efficiency Factor  # by Denton Gentry
              Em(cf) = Emissions Factor of conventional fuel type  # by Denton Gentry
              Em(sf) = Emissions Factor of solution fuel type  # by Denton Gentry
              UCF = Unit Conversion Factor (TJ per Liter or L per TJ depending on  # by Denton Gentry
                Conventional and Solution Fuel units.  # by Denton Gentry
           SolarPVUtil 'CO2 Calcs'!U344:AE390  # by Denton Gentry
        """  # by Denton Gentry
        factor = self.ac.conv_fuel_emissions_factor  # by Denton Gentry
        factor -= self.ac.soln_fuel_emissions_factor * self.ac.soln_fuel_learning_rate  # by Denton Gentry
        factor *= self.ac.conv_fuel_consumed_per_funit  # by Denton Gentry
        result = self.soln_net_annual_funits_adopted * factor / 1000000  # by Denton Gentry
        result.name = "co2eq_reduced_fuel_emissions"  # by Denton Gentry
        if self.fuel_in_liters:  # by Denton Gentry
            raise NotImplementedError("fuel_in_liters=True not handled")  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()  # by Denton Gentry
    def co2eq_net_indirect_emissions(self):  # by Denton Gentry
        """Net Indirect Emissions MMT CO2-eq by implementation unit (t) =  # by Denton Gentry
              [NIU (Sol,t) * IEm (Sol,t)] - [NIU (Cont.) * IEm (Con,t)]  /  1000000  # by Denton Gentry
           where:  # by Denton Gentry
              NIU(Sol,t) = New Implementation Units by solution at time, t  # by Denton Gentry
              IEm(Sol,t) = Indirect CO2-eq Emission of solution at time, t  # by Denton Gentry
              NIU(Con,t) = New Implementation Units by conventional mix at time, t  # by Denton Gentry
              IEm(Con,t) = Indirect CO2-eq Emission of conventional mix at time, t  # by Denton Gentry
           SolarPVUtil 'CO2 Calcs'!AP344:AZ390  # by Denton Gentry
        """  # by Denton Gentry
        if self.ac.conv_indirect_co2_is_iunits:  # by Denton Gentry
            delta = self.soln_pds_new_iunits_reqd - self.soln_ref_new_iunits_reqd  # by Denton Gentry
            result = (delta * self.ac.soln_indirect_co2_per_iunit)  # by Denton Gentry
            result -= self.conv_ref_new_iunits * self.ac.conv_indirect_co2_per_unit  # by Denton Gentry
        else:  # by Denton Gentry
            result = self.soln_net_annual_funits_adopted * self.ac.soln_indirect_co2_per_iunit  # by Denton Gentry
            result -= self.soln_net_annual_funits_adopted * self.ac.conv_indirect_co2_per_unit  # by Denton Gentry
        result /= 1000000  # by Denton Gentry
        return result  # by Denton Gentry

    # by Denton Gentry
    @lru_cache()
    def direct_emissions_from_harvesting(self):
        """Net Land Units [Mha]* (Carbon Sequestration Rate [t C/ha/yr] * Years of Sequestration [yr]-
           Carbon Stored even After Harvesting/Clearing [t C/ha]) * (CO2 per C)
           Afforestation 'CO2 Calcs'!CU365:DD411"""
        return self.annual_land_area_harvested * (self.ac.seq_rate_global * self.ac.harvest_frequency -
                                                  self.ac.carbon_not_emitted_after_harvesting) * C_TO_CO2EQ

    # by Denton Gentry


# The following formulae come from the SolarPVUtil Excel implementation of 27Aug18.  # by Denton Gentry
# There was no explanation of where they came from or what they really mean.  # by Denton Gentry
# by Denton Gentry
def co2_rf(x):  # by Denton Gentry
    original_co2 = 400  # by Denton Gentry
    return 5.35 * math.log((original_co2 + x) / original_co2)  # by Denton Gentry
    # by Denton Gentry


def f(M, N):  # by Denton Gentry
    return 0.47 * math.log(
        1 + 2.01 * 10 ** -5 * (M * N) ** 0.75 + 5.31 * 10 ** -15 * M * (M * N) ** 1.52)  # by Denton Gentry
    # by Denton Gentry


def ch4_rf(x):  # by Denton Gentry
    original_ch4 = 1800  # by Denton Gentry
    original_n2o = 320  # by Denton Gentry
    indirect_ch4_forcing_scalar = 0.97 / 0.641  # by Denton Gentry
    old_M = original_ch4  # by Denton Gentry
    new_M = original_ch4 + x  # by Denton Gentry
    N = original_n2o  # by Denton Gentry
    return indirect_ch4_forcing_scalar * 0.036 * (new_M ** 0.5 - old_M ** 0.5) - f(new_M, N) + f(old_M,
                                                                                                 N)  # by Denton Gentry
    # by Denton Gentry


def co2eq_ppm(x):  # by Denton Gentry
    original_co2 = 400  # by Denton Gentry
    return (original_co2 * math.exp(x / 5.35)) - original_co2  # by Denton Gentry


if __name__ == '__main__':
    # debug use only
    pass
