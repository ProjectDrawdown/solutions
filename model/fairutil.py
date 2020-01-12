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

# AR5 w/ feedback
CO2_MULT = 3.664
CH4_MULT = 34
N2O_MULT = 298

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
    baseline = (rcp['FossilCO2']  + rcp['OtherCO2'] + (rcp['CH4'] * CH4_MULT / 1000.0) +
            (rcp['N2O'] * N2O_MULT / 1000.0))
    baseline.index = baseline.index.astype(int)
    baseline.index.name = 'Year'
    ddCO2 = pd.read_csv(str(baselineCO2_path), header=0, index_col=0, skipinitialspace=True,
            skip_blank_lines=True, comment='#', squeeze=True)
    ddCO2.index = ddCO2.index.astype(int)
    baseline.update(ddCO2 / CO2_MULT)
    return baseline


def fair_scm_kwargs():
    return {"r0": r0, "tcrecs": tcrecs}
