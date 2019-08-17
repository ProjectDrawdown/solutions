"""Finite Amplitude Impulse Response (FaIR) Calcs module.

Computes impacts of CO2 + CH4 + N2O (et al) emissions using
https://fair.readthedocs.io/en/latest/examples.html
"""

from functools import lru_cache
import math

import fair
import numpy as np
import pandas as pd


# Columns in FaIR Emissions.emissions
YEAR      = 0
CO2_FOSSIL= 1
CO2_LAND  = 2
CH4       = 3
N2O       = 4
SOX       = 5
CO        = 6
NMVOC     = 7
NOX       = 8
BC        = 9
OC        = 10
NH3       = 11
CF4       = 12
C2F6      = 13
C6F14     = 14
HFC23     = 15
HFC32     = 16
HFC43_10  = 17
HFC125    = 18
HFC134A   = 19
HFC143A   = 20
HFC227EA  = 21
HFC245FA  = 22
SF6       = 23
CFC11     = 24
CFC12     = 25
CFC113    = 26
CFC114    = 27
CFC115    = 28
CARB_TET  = 29
MCF       = 30
HCFC22    = 31
HCFC141B  = 32
HCFC142B  = 33
HALON1211 = 34
HALON1202 = 35
HALON1301 = 36
HALON2402 = 37
CH3BR     = 38
CH3CL     = 39

class FaIRcalcs:
    """FaIR Calcs module.
        Arguments:
          co2eq_mmt_reduced: millions of metric tons CO2eq reduced in the World, a Pandas Series
                with index == year.
          baseline: string name of the RCP baseline case to use like 'RCP60' or 'RCP85'.
      """

    def __init__(self, co2eq_mmt_reduced=None, co2_sequestered_global=None, baseline=None):
        self.co2eq_mmt_reduced = co2eq_mmt_reduced
        self.co2_sequestered_global = co2_sequestered_global
        if baseline == 'RCP26' or baseline == 'RCP3':  # 'RCP3' refers to RCP3PD, which is RCP26.
            self.baseline = fair.RCPs.rcp26.Emissions
            self.baseline_name = 'RCP2.6'
        elif baseline == 'RCP45' or baseline is None:
            self.baseline = fair.RCPs.rcp45.Emissions
            self.baseline_name = 'RCP4.5'
        elif baseline == 'RCP6' or baseline == 'RCP60':
            self.baseline = fair.RCPs.rcp60.Emissions
            self.baseline_name = 'RCP6.0'
        elif baseline == 'RCP85':
            self.baseline = fair.RCPs.rcp85.Emissions
            self.baseline_name = 'RCP8.5'
        else:
            raise ValueError(f'Unknown baseline: {baseline}')


    def _baseline_indexes(self, df):
        first_year = list(df.index)[0]
        last_year = list(df.index)[-1]
        first_year_idx = last_year_idx = -1
        for (index, year) in enumerate(self.baseline.year):
            if year == first_year:
                first_year_idx = index
            if year == last_year:
                last_year_idx = index
        if first_year_idx == -1:
            raise ValueError(f'Year={first_year} is not in baseline model {self.baseline_name}')
        if last_year_idx == -1:
            raise ValueError(f'Year={last_year} is not in baseline model {self.baseline_name}')
        return (first_year_idx, last_year_idx)


    @lru_cache()
    def CFT_baseline(self):
        """Return FaIR results for the baseline case (typically an RCP case).
        
           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns (C, F, T):
             C: CO2 concentration in ppm for the World. 
             F: Radiative forcing in watts per square meter
             T: Change in temperature since pre-industrial time in Kelvin
        """
        emissions = self.baseline.emissions[:, CO2_FOSSIL] + self.baseline.emissions[:, CO2_LAND]
        (C, F, T) = fair.forward.fair_scm(emissions=emissions, useMultigas=False)
        df_C = pd.Series(C, index=self.baseline.year)
        df_C.index = df_C.index.astype(int)
        df_C.name = 'C'
        df_F = pd.Series(F, index=self.baseline.year)
        df_F.index = df_F.index.astype(int)
        df_C.name = 'F'
        df_T = pd.Series(T, index=self.baseline.year)
        df_T.index = df_T.index.astype(int)
        df_C.name = 'T'
        return (df_C, df_F, df_T)


    @lru_cache()
    def CFT(self):
        """Return FaIR results for the baseline + Drawdown solution.
        
           Finite Amplitude Impulse-Response simple climate-carbon-cycle model.
           https://github.com/OMS-NetZero/FAIR

           Returns (C, F, T):
             C: CO2 concentration in ppm for the World. 
             F: Radiative forcing in watts per square meter
             T: Change in temperature since pre-industrial time in Kelvin
        """
        emissions = self.baseline.emissions[:, CO2_FOSSIL] + self.baseline.emissions[:, CO2_LAND]
        if self.co2eq_mmt_reduced is not None:
            (first_year_idx, last_year_idx) = self._baseline_indexes(self.co2eq_mmt_reduced)
            gtons = self.co2eq_mmt_reduced.values / 1000.0
            emissions[first_year_idx:last_year_idx+1] -= gtons
        if self.co2_sequestered_global is not None:
            (first_year_idx, last_year_idx) = self._baseline_indexes(self.co2_sequestered_global)
            gtons = self.co2_sequestered_global.values / 1000.0
            emissions[first_year_idx:last_year_idx+1] -= gtons

        (C, F, T) = fair.forward.fair_scm(emissions=emissions, useMultigas=False)
        df_C = pd.Series(C, index=self.baseline.year)
        df_C.index = df_C.index.astype(int)
        df_C.name = 'C'
        df_F = pd.Series(F, index=self.baseline.year)
        df_F.index = df_F.index.astype(int)
        df_F.name = 'F'
        df_T = pd.Series(T, index=self.baseline.year)
        df_T.index = df_T.index.astype(int)
        df_T.name = 'T'
        return (df_C, df_F, df_T)
