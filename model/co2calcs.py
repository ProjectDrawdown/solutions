"""Computes reductions for CO2 and total GHGs in CO2-equivalent emissions.
"""

from functools import lru_cache, wraps
import hashlib
import math
#from numba import jit
import json
from io import StringIO

import fair
from fair.RCPs import rcp26, rcp45, rcp60, rcp85
import numpy as np
import pandas as pd
import model.advanced_controls
import model.dd
import model.fairutil

from model.data_handler import DataHandler
from model.decorators import data_func
from model.units import map_to_unit, Mt

C_TO_CO2EQ = 3.666
# Note: a different value of 3.64 is sometimes used for certain results in Excel
# Here we will always use this value for consistency

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


###########----############----############----############----############
# CO2-EQ CALCULATIONS AND PRIOR USE OF FAIR

@lru_cache
def fair_scm_cached(json_input: str):
    input = json.loads(json_input)
    values = np.array(input['values'])
    kwargs = {}
    for k in input['kwargs']:
        if isinstance(input['kwargs'][k], list):
            kwargs[k] = np.array(input['kwargs'][k])
        else:
            kwargs[k] = input['kwargs'][k]
    return fair.forward.fair_scm(emissions=values, useMultigas=input['useMultigas'], **kwargs)

def fair_scm(values, useMultigas, **kwargs):
    key = json.dumps({
        'values': values,
        'useMultigas': useMultigas,
        'kwargs': kwargs
    }, cls=NumpyEncoder)
    return fair_scm_cached(key)

@lru_cache
def co2_ppm_calculator_cached(
    co2_vals,
    solution_category,
    report_start_year,
    ):

    co2_vals = pd.read_csv(StringIO(co2_vals), index_col=0, squeeze=True, float_precision='round_trip')

    columns = ['PPM', 'Total'] + list(range(2015, 2061))
    ppm_calculator = pd.DataFrame(0, columns=columns, index=co2_vals.index.copy(),
                                      dtype=np.float64)
    ppm_calculator.index = ppm_calculator.index.astype(int)
    ppm_calculator.index.name = 'Year'
    first_year = ppm_calculator.first_valid_index()
    last_year = ppm_calculator.last_valid_index()
    for year in ppm_calculator.index:
        if (year < report_start_year and
                solution_category != model.advanced_controls.SOLUTION_CATEGORY.LAND):
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



###########----############----############----############----############
# CO2 MODULE IMPORTS

class CO2Calcs(DataHandler):
    """Computes reductions for CO2 and total GHGs in CO2-equivalent emissions.
    """
    def __init__(self, ac, soln_net_annual_funits_adopted=None, ch4_ppb_calculator=None,
                 ch4_megatons_avoided_or_reduced=None,
                 n2o_megatons_avoided_or_reduced=None,
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
        self.ch4_megatons_avoided_or_reduced = ch4_megatons_avoided_or_reduced
        self.n2o_megatons_avoided_or_reduced = n2o_megatons_avoided_or_reduced
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



    ###########----############----############----############----############
    # CO2 EMISSIONS CALCULATIONS

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

        | CO2 MMT Reduced = 
        |    (Grid Emissions Reduced + Grid Emissions Replaced - Grid Emissions by Solution) +  
        |    Fuel Emissions Avoided + Direct Emissions Reduced - Net Indirect Emissions
        
        """
        # SolarPVUtil 'CO2 Calcs'!A9:K55
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

    @map_to_unit(Mt)
    @lru_cache()
    @data_func
    def co2eq_mmt_reduced(self):
        """CO2-eq MMT Reduced
        
        Annual CO2-eq reductions by region are calculated by multiplying the estimated energy
        unit savings by region by the emission factor of the energy unit in question by region
        and year. In this sample the values used are the regional future grid BAU CO2-eq emission
        intensity values (by year) from the AMPERE 3 MESSAGE Base model used in the IPCC 5th
        Assessment Report WG3.

        | Reduced Grid MMT CO2-eq Emissions = NEU(t) * EF(e,t)
        | where:
        |   NEU(t) = Net Energy Units at time, t
        |   EF(e,t) = CO2-eq Emissions Factor of REF energy grid at time, t

        """
        # SolarPVUtil 'CO2 Calcs'!A64:K110
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
    def co2only_mmt_reduced(self):
        """CO2 MMT Reduced

        Annual CO2 reductions by region are calculated by multiplying the estimated energy
        unit savings by region by the emission factor of the energy unit in question by region
        and year. In this sample the values used are the regional future grid BAU CO2-eq emission
        intensity values (by year) from the AMPERE 3 MESSAGE Base model used in the IPCC 5th
        Assessment Report WG3.

        Reduced Grid MMT CO2 Emissions = NEU(t) * EF(e,t)

        where
            NEU(t) = Net Energy Units at time, t
            EF(e,t) = CO2 Emissions Factor of REF energy grid at time, t
        """
        # SolarPVUtil 'CO2 Calcs'!A64:K110
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
            m = m.add(self.co2only_direct_reduced_emissions().loc[s:e], fill_value=0)
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
            if self.annual_land_area_harvested is not None:
                m = m.sub(self.direct_emissions_from_harvesting().loc[s:e], fill_value=0)
            if self.co2eq_reduced_grid_emissions() is not None:
                m = m.add(self.co2eq_reduced_grid_emissions().loc[s:e], fill_value=0)
            if self.co2eq_increased_grid_usage_emissions() is not None:
                m = m.sub(self.co2eq_increased_grid_usage_emissions().loc[s:e], fill_value=0)
        m.name = "co2only_mmt_reduced"
        return m


    @lru_cache()
    @data_func
    def co2_sequestered_global(self):
        """
        Total Carbon Sequestration (World section only)
        Returns DataFrame of net annual sequestration by thermal moisture region.       
        """
        # Tropical Forests 'CO2 Calcs'!A119:G166 (Land models)

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
        """
        #  SolarPVUtil 'CO2 Calcs'!A119:AW165 (RRS)
        #  Conservation Agriculture 'CO2 Calcs'!A172:AW218 (Land)

        if self.ac.emissions_use_co2eq:
            co2_vals = self.co2eq_mmt_reduced()['World']
        else:
            co2_vals = self.co2_mmt_reduced()['World']

        if (self.ac.solution_category == model.advanced_controls.SOLUTION_CATEGORY.LAND or
                self.ac.solution_category == model.advanced_controls.SOLUTION_CATEGORY.OCEAN):
            co2_vals = self.co2_sequestered_global()['All'] + self.co2eq_mmt_reduced()['World']
            assert self.ac.emissions_use_co2eq, 'Land/ocean models must use CO2 eq'

        return co2_ppm_calculator_cached(co2_vals.to_csv(), self.ac.solution_category, self.ac.report_start_year)

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

        """
        # SolarPVUtil 'CO2 Calcs'!A234:K280
        return self.soln_pds_net_grid_electricity_units_saved * self.conv_ref_grid_CO2_per_KWh

    @lru_cache()
    @data_func
    def co2_replaced_grid_emissions(self):
        """CO2 Replaced Grid Emissions = NAFU(Sol,t) * EF(e,t)  (i.e. only direct emissions)
        where
            NAFU(Sol,t) = Net annual functional units captured by solution at time, t 
            EF(e,t) = CO2 Emissions Factor of REF energy grid at time, t

        """
        #  SolarPVUtil 'CO2 Calcs'!R234:AB280
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

        """
        # SolarPVUtil 'CO2 Calcs'!AI234:AS280
        return self.soln_pds_net_grid_electricity_units_used * self.conv_ref_grid_CO2_per_KWh


    @lru_cache()
    @data_func
    def co2eq_reduced_grid_emissions(self):
        """Reduced Grid MMT CO2-eq Emissions = NEU(t) * EF(e,t)

           where
              NEU(t) = Net Energy Units at time, t 
              EF(e,t) = CO2-eq Emissions Factor of REF energy grid at time, t

        """
        # SolarPVUtil 'CO2 Calcs'!A288:K334
        # Irrigation Efficiency 'CO2 Calcs'!A365:K411
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
    
    @data_func
    def co2only_direct_reduced_emissions(self):
        """Direct MMT CO2-eq Emissions Reduced = [DEm(Con,t) - DEm(Sol,t)]  / 1000000

           where
              DEm(Con,t) = Direct Emissions of Conventional at time, t
              DEm(Sol,t) = Direct Emissions of Solution at time, t

              NOTE: Includes CH4-CO2-eq and N2O-CO2-eq
           SolarPVUtil 'CO2 Calcs'!A344:K390
        """
        return (self.soln_pds_direct_co2_emissions_saved / 1000000)


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



    ###########----############----############----############----############
    # UTILIZATION OF THE FaIR SIMPLE CLIMATE MODEL

    @data_func
    def FaIR_CFT_baseline_co2eq(self):
        """Return FaIR results for the baseline case in CO2eq emissions.

           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns DataFrame containing columns C, F, T:
             C: CO2 concentration in ppm for the World.
             F: Radiative forcing in watts per square meter
             T: Change in temperature since pre-industrial time in Kelvin

           Assumes all methane and nitrous oxide emissions are first converted into 
           CO2-eq emissions and then run FaIR in CO2-only mode. As a scientific note: 
           this is very crude and a bad use of the FaIR model since CH4 and N2O have 
           their own radiative forcings and lifetimes which CO2-eq poorly represents.

           Assumes only one background emission of RCP4.5
        """
        kwargs = model.fairutil.fair_scm_kwargs()
        (C, F, T) = fair_scm(self.baseline.values, False, **kwargs)
        result = pd.DataFrame({'C': C, 'F': F, 'T': T}, index=self.baseline.index)
        result.name = 'FaIR_CFT_baseline_co2eq'
        return result


    @lru_cache()
    @data_func
    def FaIR_CFT_Drawdown_co2eq(self):
        """Return FaIR results for the baseline + Drawdown solution in CO2eq emissions.

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
        (C, F, T) = fair_scm(emissions.values, False, **kwargs)
        result = pd.DataFrame({'C': C , 'F': F, 'T': T}, index=emissions.index)
        result.name = 'FaIR_CFT_Drawdown_co2eq'
        return result


    @lru_cache()
    @data_func
    def FaIR_CFT_baseline_RCP3(self):
        """Return FaIR results for the baseline case of RCP3 (formerly rcp2.6).

           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns 4 DataFrames for years 1765-2500 containing:
             1: Multigas concentrations for the World.
                 CO2(ppm), CH4(ppb), N2O(ppb)
             2: Radiative forcing in watts per square meter
                 CO2(Wm-2), CH4(Wm-2), N2O(Wm-2), others(Wm-2), total(Wm-2)
             3: Change in temperature since pre-industrial time in Celsius
             4: RCP emissions (39 individual gases)
        """
        emissions = rcp26.Emissions.emissions
        rcpemissions = pd.DataFrame(emissions, index = range(1765,2501),
                                       columns=['Year', 'FossilCO2 (Gt-C)', 'OtherCO2 (Gt-C)', 'CH4 (Mt-CH4)',
                                                'N2O (Mt-N2O)', 'SOx (Mt-S)', 'CO (Mt-CO)', 'NMVOC (Mt)',
                                                'NOx (Mt-N)', 'BC (Mt)', 'OC (Mt)', 'NH3 (Mt-N)', 'CF4 (kt)',
                                                'C2F6 (kt)', 'C6F14 (kt)', 'HFC23 (kt)', 'HFC32 (kt)',
                                                'HFC43_10 (kt)', 'HFC125 (kt)', 'HFC134a (kt)', 'HFC143a (kt)',
                                                'HFC227ea (kt)', 'HFC245fa (kt)', 'SF6 (kt)', 'CFC_11 (kt)',
                                                'CFC_12 (kt)', 'CFC_113 (kt)','CFC_114 (kt)','CFC_115 (kt)',
                                                'CARB_TET (kt)', 'MCF (kt)', 'HCFC_22 (kt)', 'HCFC_141B (kt)',
                                                'HCFC_142B (kt)', 'HALON1211 (kt)', 'HALON1202 (kt)', 
                                                'HALON1301 (kt)', 'HALON2404 (kt)', 'CH3BR (kt)', 'CH3CL (kt)'])
        rcpemissions.index.name="Year"
        rcpemissions.name = 'FaIR_CFT_baseline_emis_rcp3'
        
        (C,F,T) = fair.forward.fair_scm(emissions=emissions)
        result1 = pd.DataFrame({'CO2(ppm)': C[:,0,], 'CH4(ppb)': C[:,1,], 'N2O(ppb)': C[:,2,]}, index=rcp26.Emissions.year)
        result1.index.name="Year"
        result1.name = 'FaIR_CFT_baseline_conc_rcp3'
        result2 = pd.DataFrame({'CO2(Wm-2)': F[:,0,], 'CH4(Wm-2)': F[:,1,], 'N2O(Wm-2)': F[:,2,], 'others(Wm-2)': np.sum(F, axis=1)-F[:,0,]-F[:,1,]-F[:,2,], 'total(Wm-2)': np.sum(F, axis=1)}, index=rcp26.Emissions.year)
        result2.index.name="Year"
        result2.name = 'FaIR_CFT_baseline_forc_rcp3'
        result3 = pd.DataFrame({'TempAnomaly(C)': T}, index=rcp26.Emissions.year)
        result3.index.name="Year"
        result3.name = 'FaIR_CFT_baseline_temp_rcp3' 
        return result1, result2, result3, rcpemissions

    @lru_cache()
    @data_func
    def FaIR_CFT_baseline_RCP45(self):
        """Return FaIR results for the baseline case of RCP4.5

           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns 4 DataFrames for years 1765-2500 containing:
             1: Multigas concentrations for the World.
                 CO2(ppm), CH4(ppb), N2O(ppb)
             2: Radiative forcing in watts per square meter
                 CO2(Wm-2), CH4(Wm-2), N2O(Wm-2), others(Wm-2), total(Wm-2)
             3: Change in temperature since pre-industrial time in Celsius
             4: RCP emissions (39 individual gases)
        """        
        emissions = rcp45.Emissions.emissions
        rcpemissions = pd.DataFrame(emissions, index = range(1765,2501),
                                       columns=['Year', 'FossilCO2 (Gt-C)', 'OtherCO2 (Gt-C)', 'CH4 (Mt-CH4)',
                                                'N2O (Mt-N2O)', 'SOx (Mt-S)', 'CO (Mt-CO)', 'NMVOC (Mt)',
                                                'NOx (Mt-N)', 'BC (Mt)', 'OC (Mt)', 'NH3 (Mt-N)', 'CF4 (kt)',
                                                'C2F6 (kt)', 'C6F14 (kt)', 'HFC23 (kt)', 'HFC32 (kt)',
                                                'HFC43_10 (kt)', 'HFC125 (kt)', 'HFC134a (kt)', 'HFC143a (kt)',
                                                'HFC227ea (kt)', 'HFC245fa (kt)', 'SF6 (kt)', 'CFC_11 (kt)',
                                                'CFC_12 (kt)', 'CFC_113 (kt)','CFC_114 (kt)','CFC_115 (kt)',
                                                'CARB_TET (kt)', 'MCF (kt)', 'HCFC_22 (kt)', 'HCFC_141B (kt)',
                                                'HCFC_142B (kt)', 'HALON1211 (kt)', 'HALON1202 (kt)', 
                                                'HALON1301 (kt)', 'HALON2404 (kt)', 'CH3BR (kt)', 'CH3CL (kt)'])
        rcpemissions.index.name="Year"
        rcpemissions.name = 'FaIR_CFT_baseline_emis_rcp45'
        
        (C,F,T) = fair.forward.fair_scm(emissions=emissions)
        result1 = pd.DataFrame({'CO2(ppm)': C[:,0,], 'CH4(ppb)': C[:,1,], 'N2O(ppb)': C[:,2,]}, index=rcp45.Emissions.year)
        result1.index.name="Year"
        result1.name = 'FaIR_CFT_baseline_conc_rcp45'
        result2 = pd.DataFrame({'CO2(Wm-2)': F[:,0,], 'CH4(Wm-2)': F[:,1,], 'N2O(Wm-2)': F[:,2,], 'others(Wm-2)': np.sum(F, axis=1)-F[:,0,]-F[:,1,]-F[:,2,], 'total(Wm-2)': np.sum(F, axis=1)}, index=rcp45.Emissions.year)
        result2.index.name="Year"
        result2.name = 'FaIR_CFT_baseline_forc_rcp45'
        result3 = pd.DataFrame({'TempAnomaly(C)': T}, index=rcp45.Emissions.year)
        result3.index.name="Year"
        result3.name = 'FaIR_CFT_baseline_temp_rcp45' 
        return result1, result2, result3, rcpemissions

    @lru_cache()
    @data_func
    def FaIR_CFT_baseline_RCP6(self):
        """Return FaIR results for the baseline case of RCP6.0

           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns 4 DataFrames for years 1765-2500 containing:
             1: Multigas concentrations for the World.
                 CO2(ppm), CH4(ppb), N2O(ppb)
             2: Radiative forcing in watts per square meter
                 CO2(Wm-2), CH4(Wm-2), N2O(Wm-2), others(Wm-2), total(Wm-2)
             3: Change in temperature since pre-industrial time in Celsius
             4: RCP emissions (39 individual gases)
        """   
        emissions = rcp60.Emissions.emissions
        rcpemissions = pd.DataFrame(emissions, index = range(1765,2501),
                                       columns=['Year', 'FossilCO2 (Gt-C)', 'OtherCO2 (Gt-C)', 'CH4 (Mt-CH4)',
                                                'N2O (Mt-N2O)', 'SOx (Mt-S)', 'CO (Mt-CO)', 'NMVOC (Mt)',
                                                'NOx (Mt-N)', 'BC (Mt)', 'OC (Mt)', 'NH3 (Mt-N)', 'CF4 (kt)',
                                                'C2F6 (kt)', 'C6F14 (kt)', 'HFC23 (kt)', 'HFC32 (kt)',
                                                'HFC43_10 (kt)', 'HFC125 (kt)', 'HFC134a (kt)', 'HFC143a (kt)',
                                                'HFC227ea (kt)', 'HFC245fa (kt)', 'SF6 (kt)', 'CFC_11 (kt)',
                                                'CFC_12 (kt)', 'CFC_113 (kt)','CFC_114 (kt)','CFC_115 (kt)',
                                                'CARB_TET (kt)', 'MCF (kt)', 'HCFC_22 (kt)', 'HCFC_141B (kt)',
                                                'HCFC_142B (kt)', 'HALON1211 (kt)', 'HALON1202 (kt)', 
                                                'HALON1301 (kt)', 'HALON2404 (kt)', 'CH3BR (kt)', 'CH3CL (kt)'])
        rcpemissions.index.name="Year"
        rcpemissions.name = 'FaIR_CFT_baseline_emis_rcp6'
        
        (C,F,T) = fair.forward.fair_scm(emissions=emissions)
        result1 = pd.DataFrame({'CO2(ppm)': C[:,0,], 'CH4(ppb)': C[:,1,], 'N2O(ppb)': C[:,2,]}, index=rcp60.Emissions.year)
        result1.index.name="Year"
        result1.name = 'FaIR_CFT_baseline_conc_rcp6'
        result2 = pd.DataFrame({'CO2(Wm-2)': F[:,0,], 'CH4(Wm-2)': F[:,1,], 'N2O(Wm-2)': F[:,2,], 'others(Wm-2)': np.sum(F, axis=1)-F[:,0,]-F[:,1,]-F[:,2,], 'total(Wm-2)': np.sum(F, axis=1)}, index=rcp60.Emissions.year)
        result2.index.name="Year"
        result2.name = 'FaIR_CFT_baseline_forc_rcp6'
        result3 = pd.DataFrame({'TempAnomaly(C)': T}, index=rcp60.Emissions.year)
        result3.index.name="Year"
        result3.name = 'FaIR_CFT_baseline_temp_rcp6' 
        return result1, result2, result3, rcpemissions
    
    @data_func
    def FaIR_CFT_baseline_RCP85(self):
        """Return FaIR results for the baseline case of RCP8.5

           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns 4 DataFrames for years 1765-2500 containing:
             1: Multigas concentrations for the World.
                 CO2(ppm), CH4(ppb), N2O(ppb)
             2: Radiative forcing in watts per square meter
                 CO2(Wm-2), CH4(Wm-2), N2O(Wm-2), others(Wm-2), total(Wm-2)
             3: Change in temperature since pre-industrial time in Celsius
             4: RCP emissions (39 individual gases)
        """   
        emissions = rcp85.Emissions.emissions
        rcpemissions = pd.DataFrame(emissions, index = range(1765,2501),
                                       columns=['Year', 'FossilCO2 (Gt-C)', 'OtherCO2 (Gt-C)', 'CH4 (Mt-CH4)',
                                                'N2O (Mt-N2O)', 'SOx (Mt-S)', 'CO (Mt-CO)', 'NMVOC (Mt)',
                                                'NOx (Mt-N)', 'BC (Mt)', 'OC (Mt)', 'NH3 (Mt-N)', 'CF4 (kt)',
                                                'C2F6 (kt)', 'C6F14 (kt)', 'HFC23 (kt)', 'HFC32 (kt)',
                                                'HFC43_10 (kt)', 'HFC125 (kt)', 'HFC134a (kt)', 'HFC143a (kt)',
                                                'HFC227ea (kt)', 'HFC245fa (kt)', 'SF6 (kt)', 'CFC_11 (kt)',
                                                'CFC_12 (kt)', 'CFC_113 (kt)','CFC_114 (kt)','CFC_115 (kt)',
                                                'CARB_TET (kt)', 'MCF (kt)', 'HCFC_22 (kt)', 'HCFC_141B (kt)',
                                                'HCFC_142B (kt)', 'HALON1211 (kt)', 'HALON1202 (kt)', 
                                                'HALON1301 (kt)', 'HALON2404 (kt)', 'CH3BR (kt)', 'CH3CL (kt)'])
        rcpemissions.index.name="Year"
        rcpemissions.name = 'FaIR_CFT_baseline_emis_rcp85'
        
        (C,F,T) = fair.forward.fair_scm(emissions=emissions)
        result1 = pd.DataFrame({'CO2(ppm)': C[:,0,], 'CH4(ppb)': C[:,1,], 'N2O(ppb)': C[:,2,]}, index=rcp85.Emissions.year)
        result1.index.name="Year"
        result1.name = 'FaIR_CFT_baseline_conc_rcp85'
        result2 = pd.DataFrame({'CO2(Wm-2)': F[:,0,], 'CH4(Wm-2)': F[:,1,], 'N2O(Wm-2)': F[:,2,], 'others(Wm-2)': np.sum(F, axis=1)-F[:,0,]-F[:,1,]-F[:,2,], 'total(Wm-2)': np.sum(F, axis=1)}, index=rcp85.Emissions.year)
        result2.index.name="Year"
        result2.name = 'FaIR_CFT_baseline_forc_rcp85'
        result3 = pd.DataFrame({'TempAnomaly(C)': T}, index=rcp85.Emissions.year)
        result3.index.name="Year"
        result3.name = 'FaIR_CFT_baseline_temp_rcp85' 
        return result1, result2, result3, rcpemissions

    @lru_cache()
    @lru_cache()
    @data_func
    def ghg_emissions_reductions_global_annual(self):
        """ Return annual emission reductions for 2014-2060.
            Columns of CO2 (Gt-C), CH4 (Mt-CH4), N2O (Mt-N2O)
        """
        # N2O Emission reductions if applicable
        if self.n2o_megatons_avoided_or_reduced is not None:
            n2oreduction = self.n2o_megatons_avoided_or_reduced['World']
        else:
            n2oreduction = 0.0
        # CH4 Emission reductions if applicable
        if self.ch4_megatons_avoided_or_reduced is not None:
            ch4reduction = self.ch4_megatons_avoided_or_reduced['World']
        else:
            ch4reduction = 0.0
        
        # CO2 Emission reductions from RRS of Squestered Land
        co2only_mmt_reduced = self.co2only_mmt_reduced()
        if co2only_mmt_reduced is not None:
            co2reduction = (co2only_mmt_reduced['World'] / 1000.0) / C_TO_CO2EQ
            
        co2_sequestered_global = self.co2_sequestered_global()
        if co2_sequestered_global is not None:
            co2reduction = (co2_sequestered_global['All'] / 1000.0) / C_TO_CO2EQ
       
        co2reduction.loc[:self.ac.report_start_year - 1] = 0.0
        co2reduction.loc[self.ac.report_end_year + 1:] = 0.0

        result = pd.DataFrame({'CO2 (Gt-C)': co2reduction , 'CH4 (Mt-CH4)': ch4reduction, 'N2O (Mt-N2O)': n2oreduction})
        result.name = 'ghg_emissions_reductions_global_annual'
        return result
    
    
    @lru_cache()
    @data_func
    def ghg_emissions_reductions_global_cumulative(self):
        """ Return cumulative emission reductions for 2014-2060.
            For CO2 (Gt-C), CH4 (Mt-CH4), N2O (Mt-N2O)
        """
        annual_reductions = self.ghg_emissions_reductions_global_annual()
        result = annual_reductions.sum(axis=0)
        result.name = 'ghg_emissions_reductions_global_cumulative'
        return result
 

    @lru_cache()
    @data_func
    def FaIR_CFT_Drawdown_RCP3(self):
        """Return FaIR results for the baseline + Drawdown case of RCP3 (formerly RCP2.6)

           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns 4 DataFrames for years 1765-2500 containing:
             1: Multigas concentrations for the World.
                 CO2(ppm), CH4(ppb), N2O(ppb)
             2: Radiative forcing in watts per square meter
                 CO2(Wm-2), CH4(Wm-2), N2O(Wm-2), others(Wm-2), total(Wm-2)
             3: Change in temperature since pre-industrial time in Celsius
             4: RCP emissions (39 individual gases)

        """   
        # Call on the solution emission reductions
        annual_reductions = self.ghg_emissions_reductions_global_annual()
        # Call on the RCP scenario
        rcpemissions = rcp26.Emissions.emissions
        rcpemissionsnew = pd.DataFrame(rcpemissions, index = range(1765,2501),
                                       columns=['Year','FossilCO2 (Gt-C)', 'OtherCO2 (Gt-C)', 'CH4 (Mt-CH4)',
                                                'N2O (Mt-N2O)', 'SOx (Mt-S)', 'CO (Mt-CO)', 'NMVOC (Mt)',
                                                'NOx (Mt-N)', 'BC (Mt)', 'OC (Mt)', 'NH3 (Mt-N)', 'CF4 (kt)',
                                                'C2F6 (kt)', 'C6F14 (kt)', 'HFC23 (kt)', 'HFC32 (kt)',
                                                'HFC43_10 (kt)', 'HFC125 (kt)', 'HFC134a (kt)', 'HFC143a (kt)',
                                                'HFC227ea (kt)', 'HFC245fa (kt)', 'SF6 (kt)', 'CFC_11 (kt)',
                                                'CFC_12 (kt)', 'CFC_113 (kt)','CFC_114 (kt)','CFC_115 (kt)',
                                                'CARB_TET (kt)', 'MCF (kt)', 'HCFC_22 (kt)', 'HCFC_141B (kt)',
                                                'HCFC_142B (kt)', 'HALON1211 (kt)', 'HALON1202 (kt)', 
                                                'HALON1301 (kt)', 'HALON2404 (kt)', 'CH3BR (kt)', 'CH3CL (kt)'])
        rcpemissionsnew.index.name="Year"
        rcpemissionsnew.name = 'FaIR_CFT_Drawdown_emis_rcp3' 
        rcpemissionschopped = rcpemissionsnew.iloc[249:296,:]
        
        # Replace the CO2 emissions
        a0 = rcpemissionschopped.iloc[:,1]- annual_reductions.iloc[:,0]
        rcpemissionsnew.iloc[249:296,1] = a0
        # Replace the CH4 emissions
        a1 = rcpemissionschopped.iloc[:,3]- annual_reductions.iloc[:,1]
        rcpemissionsnew.iloc[249:296,3] = a1
        # Replace the N2O emissions
        a2 = rcpemissionschopped.iloc[:,4]- annual_reductions.iloc[:,2]
        rcpemissionsnew.iloc[249:296,4] = a2
        
        emissionsnew = rcpemissionsnew.to_numpy()
        (C,F,T) = fair.forward.fair_scm(emissions=emissionsnew)
        result1 = pd.DataFrame({'CO2(ppm)': C[:,0,], 'CH4(ppb)': C[:,1,], 'N2O(ppb)': C[:,2,]}, index=rcp26.Emissions.year)
        result1.index.name="Year"
        result1.name = 'FaIR_CFT_Drawdown_conc_rcp3'
        result2 = pd.DataFrame({'CO2(Wm-2)': F[:,0,], 'CH4(Wm-2)': F[:,1,], 'N2O(Wm-2)': F[:,2,], 'others(Wm-2)': np.sum(F, axis=1)-F[:,0,]-F[:,1,]-F[:,2,], 'total(Wm-2)': np.sum(F, axis=1)}, index=rcp26.Emissions.year)
        result2.index.name="Year"
        result2.name = 'FaIR_CFT_Drawdown_forc_rcp3'
        result3 = pd.DataFrame({'TempAnomaly(C)': T}, index=rcp26.Emissions.year)
        result3.index.name="Year"
        result3.name = 'FaIR_CFT_Drawdown_temp_rcp3' 
        return result1, result2, result3, rcpemissionsnew

    @lru_cache()
    @data_func
    def FaIR_CFT_Drawdown_RCP45(self):
        """Return FaIR results for the baseline + Drawdown case of RCP4.5

           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns 4 DataFrames for years 1765-2500 containing:
             1: Multigas concentrations for the World.
                 CO2(ppm), CH4(ppb), N2O(ppb)
             2: Radiative forcing in watts per square meter
                 CO2(Wm-2), CH4(Wm-2), N2O(Wm-2), others(Wm-2), total(Wm-2)
             3: Change in temperature since pre-industrial time in Celsius
             4: RCP emissions (39 individual gases)

        """   
        # Call on the solution emission reductions
        annual_reductions = self.ghg_emissions_reductions_global_annual()
        # Call on the RCP scenario
        rcpemissions = rcp45.Emissions.emissions
        rcpemissionsnew = pd.DataFrame(rcpemissions, index = range(1765,2501),
                                       columns=['Year','FossilCO2 (Gt-C)', 'OtherCO2 (Gt-C)', 'CH4 (Mt-CH4)',
                                                'N2O (Mt-N2O)', 'SOx (Mt-S)', 'CO (Mt-CO)', 'NMVOC (Mt)',
                                                'NOx (Mt-N)', 'BC (Mt)', 'OC (Mt)', 'NH3 (Mt-N)', 'CF4 (kt)',
                                                'C2F6 (kt)', 'C6F14 (kt)', 'HFC23 (kt)', 'HFC32 (kt)',
                                                'HFC43_10 (kt)', 'HFC125 (kt)', 'HFC134a (kt)', 'HFC143a (kt)',
                                                'HFC227ea (kt)', 'HFC245fa (kt)', 'SF6 (kt)', 'CFC_11 (kt)',
                                                'CFC_12 (kt)', 'CFC_113 (kt)','CFC_114 (kt)','CFC_115 (kt)',
                                                'CARB_TET (kt)', 'MCF (kt)', 'HCFC_22 (kt)', 'HCFC_141B (kt)',
                                                'HCFC_142B (kt)', 'HALON1211 (kt)', 'HALON1202 (kt)', 
                                                'HALON1301 (kt)', 'HALON2404 (kt)', 'CH3BR (kt)', 'CH3CL (kt)'])
        rcpemissionsnew.index.name="Year"
        rcpemissionsnew.name = 'FaIR_CFT_Drawdown_emis_rcp45' 
        rcpemissionschopped = rcpemissionsnew.iloc[249:296,:]
        
        # Replace the CO2 emissions
        a0 = rcpemissionschopped.iloc[:,1]- annual_reductions.iloc[:,0]
        rcpemissionsnew.iloc[249:296,1] = a0
        # Replace the CH4 emissions
        a1 = rcpemissionschopped.iloc[:,3]- annual_reductions.iloc[:,1]
        rcpemissionsnew.iloc[249:296,3] = a1
        # Replace the N2O emissions
        a2 = rcpemissionschopped.iloc[:,4]- annual_reductions.iloc[:,2]
        rcpemissionsnew.iloc[249:296,4] = a2
        
        emissionsnew = rcpemissionsnew.to_numpy()
        (C,F,T) = fair.forward.fair_scm(emissions=emissionsnew)
        result1 = pd.DataFrame({'CO2(ppm)': C[:,0,], 'CH4(ppb)': C[:,1,], 'N2O(ppb)': C[:,2,]}, index=rcp45.Emissions.year)
        result1.index.name="Year"
        result1.name = 'FaIR_CFT_Drawdown_conc_rcp45'
        result2 = pd.DataFrame({'CO2(Wm-2)': F[:,0,], 'CH4(Wm-2)': F[:,1,], 'N2O(Wm-2)': F[:,2,], 'others(Wm-2)': np.sum(F, axis=1)-F[:,0,]-F[:,1,]-F[:,2,], 'total(Wm-2)': np.sum(F, axis=1)}, index=rcp45.Emissions.year)
        result2.index.name="Year"
        result2.name = 'FaIR_CFT_Drawdown_forc_rcp45'
        result3 = pd.DataFrame({'TempAnomaly(C)': T}, index=rcp45.Emissions.year)
        result3.index.name="Year"
        result3.name = 'FaIR_CFT_Drawdown_temp_rcp45' 
        return result1, result2, result3, rcpemissionsnew
    
    @lru_cache()
    @data_func
    def FaIR_CFT_Drawdown_RCP6(self):
        """Return FaIR results for the baseline + Drawdown case of RCP6.0

           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns 4 DataFrames for years 1765-2500 containing:
             1: Multigas concentrations for the World.
                 CO2(ppm), CH4(ppb), N2O(ppb)
             2: Radiative forcing in watts per square meter
                 CO2(Wm-2), CH4(Wm-2), N2O(Wm-2), others(Wm-2), total(Wm-2)
             3: Change in temperature since pre-industrial time in Celsius
             4: RCP emissions (39 individual gases)

        """   
        # Call on the solution emission reductions
        annual_reductions = self.ghg_emissions_reductions_global_annual()
        # Call on the RCP scenario
        rcpemissions = rcp60.Emissions.emissions
        rcpemissionsnew = pd.DataFrame(rcpemissions, index = range(1765,2501),
                                       columns=['Year','FossilCO2 (Gt-C)', 'OtherCO2 (Gt-C)', 'CH4 (Mt-CH4)',
                                                'N2O (Mt-N2O)', 'SOx (Mt-S)', 'CO (Mt-CO)', 'NMVOC (Mt)',
                                                'NOx (Mt-N)', 'BC (Mt)', 'OC (Mt)', 'NH3 (Mt-N)', 'CF4 (kt)',
                                                'C2F6 (kt)', 'C6F14 (kt)', 'HFC23 (kt)', 'HFC32 (kt)',
                                                'HFC43_10 (kt)', 'HFC125 (kt)', 'HFC134a (kt)', 'HFC143a (kt)',
                                                'HFC227ea (kt)', 'HFC245fa (kt)', 'SF6 (kt)', 'CFC_11 (kt)',
                                                'CFC_12 (kt)', 'CFC_113 (kt)','CFC_114 (kt)','CFC_115 (kt)',
                                                'CARB_TET (kt)', 'MCF (kt)', 'HCFC_22 (kt)', 'HCFC_141B (kt)',
                                                'HCFC_142B (kt)', 'HALON1211 (kt)', 'HALON1202 (kt)', 
                                                'HALON1301 (kt)', 'HALON2404 (kt)', 'CH3BR (kt)', 'CH3CL (kt)'])
        rcpemissionsnew.index.name="Year"
        rcpemissionsnew.name = 'FaIR_CFT_Drawdown_emis_rcp6' 
        rcpemissionschopped = rcpemissionsnew.iloc[249:296,:]
        
        # Replace the CO2 emissions
        a0 = rcpemissionschopped.iloc[:,1]- annual_reductions.iloc[:,0]
        rcpemissionsnew.iloc[249:296,1] = a0
        # Replace the CH4 emissions
        a1 = rcpemissionschopped.iloc[:,3]- annual_reductions.iloc[:,1]
        rcpemissionsnew.iloc[249:296,3] = a1
        # Replace the N2O emissions
        a2 = rcpemissionschopped.iloc[:,4]- annual_reductions.iloc[:,2]
        rcpemissionsnew.iloc[249:296,4] = a2
        
        emissionsnew = rcpemissionsnew.to_numpy()
        (C,F,T) = fair.forward.fair_scm(emissions=emissionsnew)
        result1 = pd.DataFrame({'CO2(ppm)': C[:,0,], 'CH4(ppb)': C[:,1,], 'N2O(ppb)': C[:,2,]}, index=rcp60.Emissions.year)
        result1.index.name="Year"
        result1.name = 'FaIR_CFT_Drawdown_conc_rcp6'
        result2 = pd.DataFrame({'CO2(Wm-2)': F[:,0,], 'CH4(Wm-2)': F[:,1,], 'N2O(Wm-2)': F[:,2,], 'others(Wm-2)': np.sum(F, axis=1)-F[:,0,]-F[:,1,]-F[:,2,], 'total(Wm-2)': np.sum(F, axis=1)}, index=rcp60.Emissions.year)
        result2.index.name="Year"
        result2.name = 'FaIR_CFT_Drawdown_forc_rcp6'
        result3 = pd.DataFrame({'TempAnomaly(C)': T}, index=rcp60.Emissions.year)
        result3.index.name="Year"
        result3.name = 'FaIR_CFT_Drawdown_temp_rcp6' 
        return result1, result2, result3, rcpemissionsnew 
    
    @lru_cache()
    @data_func
    def FaIR_CFT_Drawdown_RCP85(self):
        """Return FaIR results for the baseline + Drawdown case of RCP8.5

           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns 4 DataFrames for years 1765-2500 containing:
             1: Multigas concentrations for the World.
                 CO2(ppm), CH4(ppb), N2O(ppb)
             2: Radiative forcing in watts per square meter
                 CO2(Wm-2), CH4(Wm-2), N2O(Wm-2), others(Wm-2), total(Wm-2)
             3: Change in temperature since pre-industrial time in Celsius
             4: RCP emissions (39 individual gases)

        """   
        # Call on the solution emission reductions
        annual_reductions = self.ghg_emissions_reductions_global_annual()
        # Call on the RCP scenario
        rcpemissions = rcp85.Emissions.emissions
        rcpemissionsnew = pd.DataFrame(rcpemissions, index = range(1765,2501),
                                       columns=['Year','FossilCO2 (Gt-C)', 'OtherCO2 (Gt-C)', 'CH4 (Mt-CH4)',
                                                'N2O (Mt-N2O)', 'SOx (Mt-S)', 'CO (Mt-CO)', 'NMVOC (Mt)',
                                                'NOx (Mt-N)', 'BC (Mt)', 'OC (Mt)', 'NH3 (Mt-N)', 'CF4 (kt)',
                                                'C2F6 (kt)', 'C6F14 (kt)', 'HFC23 (kt)', 'HFC32 (kt)',
                                                'HFC43_10 (kt)', 'HFC125 (kt)', 'HFC134a (kt)', 'HFC143a (kt)',
                                                'HFC227ea (kt)', 'HFC245fa (kt)', 'SF6 (kt)', 'CFC_11 (kt)',
                                                'CFC_12 (kt)', 'CFC_113 (kt)','CFC_114 (kt)','CFC_115 (kt)',
                                                'CARB_TET (kt)', 'MCF (kt)', 'HCFC_22 (kt)', 'HCFC_141B (kt)',
                                                'HCFC_142B (kt)', 'HALON1211 (kt)', 'HALON1202 (kt)', 
                                                'HALON1301 (kt)', 'HALON2404 (kt)', 'CH3BR (kt)', 'CH3CL (kt)'])
        rcpemissionsnew.index.name="Year"
        rcpemissionsnew.name = 'FaIR_CFT_Drawdown_emis_rcp85' 
        rcpemissionschopped = rcpemissionsnew.iloc[249:296,:]
        
        # Replace the CO2 emissions
        a0 = rcpemissionschopped.iloc[:,1]- annual_reductions.iloc[:,0]
        rcpemissionsnew.iloc[249:296,1] = a0
        # Replace the CH4 emissions
        a1 = rcpemissionschopped.iloc[:,3]- annual_reductions.iloc[:,1]
        rcpemissionsnew.iloc[249:296,3] = a1
        # Replace the N2O emissions
        a2 = rcpemissionschopped.iloc[:,4]- annual_reductions.iloc[:,2]
        rcpemissionsnew.iloc[249:296,4] = a2
        
        emissionsnew = rcpemissionsnew.to_numpy()
        (C,F,T) = fair.forward.fair_scm(emissions=emissionsnew)
        result1 = pd.DataFrame({'CO2(ppm)': C[:,0,], 'CH4(ppb)': C[:,1,], 'N2O(ppb)': C[:,2,]}, index=rcp85.Emissions.year)
        result1.index.name="Year"
        result1.name = 'FaIR_CFT_Drawdown_conc_rcp85'
        result2 = pd.DataFrame({'CO2(Wm-2)': F[:,0,], 'CH4(Wm-2)': F[:,1,], 'N2O(Wm-2)': F[:,2,], 'others(Wm-2)': np.sum(F, axis=1)-F[:,0,]-F[:,1,]-F[:,2,], 'total(Wm-2)': np.sum(F, axis=1)}, index=rcp85.Emissions.year)
        result2.index.name="Year"
        result2.name = 'FaIR_CFT_Drawdown_forc_rcp85'
        result3 = pd.DataFrame({'TempAnomaly(C)': T}, index=rcp85.Emissions.year)
        result3.index.name="Year"
        result3.name = 'FaIR_CFT_Drawdown_temp_rcp85' 
        return result1, result2, result3, rcpemissionsnew


###########----############----############----############----############
## PRIOR RADIATIVE FORCING EQUATIONS USED FOR CO2-EQ CALCULATIONS


# The following formulae come from the SolarPVUtil Excel implementation of 27Aug18.
# There was no explanation of where they came from or what they really mean.

#@jit
def co2_rf(x):
    original_co2 = 400
    return 5.35 * math.log((original_co2 + x) / original_co2)


#@jit
def f(M, N):
    return 0.47 * math.log(
        1 + 2.01 * 10 ** -5 * (M * N) ** 0.75 + 5.31 * 10 ** -15 * M * (M * N) ** 1.52)


#@jit
def ch4_rf(x):
    original_ch4 = 1800
    original_n2o = 320
    indirect_ch4_forcing_scalar = 0.97 / 0.641
    old_M = original_ch4
    new_M = original_ch4 + x
    N = original_n2o
    return (indirect_ch4_forcing_scalar * 0.036 * (new_M ** 0.5 - old_M ** 0.5) -
            f(new_M, N) + f(old_M, N))

#@jit
def co2eq_ppm(x):
    original_co2 = 400
    return (original_co2 * math.exp(x / 5.35)) - original_co2
