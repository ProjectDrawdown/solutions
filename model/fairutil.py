"""Utilities and definitions for https://github.com/OMS-NetZero/FAIR"""

import copy
import pathlib

import fair
import fair.RCPs.rcp26
import fair.RCPs.rcp45
import fair.RCPs.rcp60
import fair.RCPs.rcp85
import numpy as np
import pandas as pd


topdir = pathlib.Path(__file__).parents[1]
baselineCO2_path = topdir.joinpath('data', 'baselineCO2.csv')
tcrecs = np.array([1.7, 3.2])  # GRL https://doi.org/10.1029/2019GL082442
r0 = 35  # https://github.com/OMS-NetZero/FAIR/issues/19

# AR5 without climate-carbon feedback
CO2_MULT = 3.664
CH4_MULT = 28
N2O_MULT = 265

ghg = {
    "Year": 0,
    "FossilCO2": 1,
    "OtherCO2": 2,
    "CH4": 3,
    "N2O": 4,
    "SOx": 5,
    "CO": 6,
    "NMVOC": 7,
    "NOx": 8,
    "BC": 9,
    "OC": 10,
    "NH3": 11,
    "CF4": 12,
    "C2F6": 13,
    "C6F14": 14,
    "HFC23": 15,
    "HFC32": 16,
    "HFC43_10": 17,
    "HFC125": 18,
    "HFC134a": 19,
    "HFC143a": 20,
    "HFC227ea": 21,
    "HFC245fa": 22,
    "SF6": 23,
    "CFC11": 24,
    "CFC12": 25,
    "CFC113": 26,
    "CFC114": 27,
    "CFC115": 28,
    "CARB_TET": 29,
    "MCF": 30,
    "HCFC22": 31,
    "HCFC141B": 32,
    "HCFC142B": 33,
    "HALON1211": 34,
    "HALON1202": 35,
    "HALON1301": 36,
    "HALON2402": 37,
    "CH3BR": 38,
    "CH3CL": 39,
}


def baseline_emissions():
    """Return emissions to use as a baseline for Drawdown solutions."""
    rcp = pd.DataFrame(fair.RCPs.rcp45.Emissions.emissions.copy(), columns=ghg.keys(),
            index=fair.RCPs.rcp45.Emissions.year)
    baseline = (rcp['FossilCO2']  + rcp['OtherCO2'] +
             # Global Warming Potential of individual GHGs in CO2 equivalence
             # CH4 and N2O values from Project Drawdown, noted as "AR5 with feedback"
            ((rcp['CH4']       * 34      / 1000.0) +
             (rcp['N2O']       * 298     / 1000.0) +
             # GHGs after this point are from IPCC AR5
             # https://www.ghgprotocol.org/sites/default/files/ghgp/Global-Warming-Potential-Values%20%28Feb%2016%202016%29_1.pdf
             (rcp['CF4']       * 6630    / 1000000.0) +
             (rcp['C2F6']      * 11100   / 1000000.0) +
             (rcp['C6F14']     * 7910    / 1000000.0) +
             (rcp['HFC23']     * 12400   / 1000000.0) +
             (rcp['HFC32']     * 677     / 1000000.0) +
             (rcp['HFC43_10']  * 1650    / 1000000.0) +
             (rcp['HFC125']    * 3170    / 1000000.0) +
             (rcp['HFC134a']   * 1300    / 1000000.0) +
             (rcp['HFC143a']   * 4800    / 1000000.0) +
             (rcp['HFC227ea']  * 3350    / 1000000.0) +
             (rcp['HFC245fa']  * 858     / 1000000.0) +
             (rcp['SF6']       * 23500   / 1000000.0) +
             (rcp['CFC11']     * 4660    / 1000000.0) +
             (rcp['CFC12']     * 10200   / 1000000.0) +
             (rcp['CFC113']    * 5820    / 1000000.0) +
             (rcp['CFC114']    * 8590    / 1000000.0) +
             (rcp['CFC115']    * 7670    / 1000000.0) +
             (rcp['CARB_TET']  * 1730    / 1000000.0) +
             (rcp['HCFC22']    * 1760    / 1000000.0) +
             (rcp['HCFC141B']  * 782     / 1000000.0) +
             (rcp['HCFC142B']  * 1980    / 1000000.0) +
             (rcp['HALON1211'] * 1750    / 1000000.0) +
             (rcp['HALON1301'] * 6290    / 1000000.0) +
             (rcp['HALON2402'] * 1470    / 1000000.0) +
             (rcp['CH3BR']     * 2       / 1000000.0) +
             (rcp['CH3CL']     * 12      / 1000000.0) +
             # Halon 1202 from https://en.wikipedia.org/wiki/Dibromodifluoromethane
             (rcp['HALON1202'] * 231     / 1000000.0) +
             # NOx https://www.ncbi.nlm.nih.gov/pubmed/24234471
             (rcp['NOx']       * 7       / 1000.0) +
             # gasses with a GWP of close to zero or with very short atmospheric lifetimes.
             (rcp['CO']        * 0) +
             (rcp['BC']        * 0) +
             (rcp['NH3']       * 0) +
             (rcp['NMVOC']     * 0) +
             (rcp['OC']        * 0) +
             (rcp['MCF']       * 0) +
             (rcp['SOx']       * 0) +
             0
            ) / CO2_MULT)
    baseline.index = baseline.index.astype(int)
    baseline.index.name = 'Year'
    ddCO2 = pd.read_csv(str(baselineCO2_path), header=0, index_col=0, skipinitialspace=True,
            skip_blank_lines=True, comment='#', squeeze=True)
    ddCO2.index = ddCO2.index.astype(int)
    baseline.update(ddCO2 / CO2_MULT)
    return baseline


def fair_scm_kwargs():
    return {"r0": r0, "tcrecs": tcrecs}
