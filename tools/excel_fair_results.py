import argparse
import os.path
import pathlib
import sys

import fair
import numpy as np
import pandas as pd

import model.fairutil

def process_scenario(filename, scenario):
    sheet_name = 'Gtperyr_' + scenario
    raw = pd.read_excel(io=filename, sheet_name=sheet_name, header=None, index_col=0,
            dtype=object, skiprows=0, nrows=52, usecols='A:EF')
    years = raw.index[11:]
    solution_names = sorted(list(set(raw.iloc[5, 3:].dropna())))

    solutions = pd.DataFrame(0, index=range(1850, 2101), columns=solution_names)
    solutions.index.name = 'Year'
    prev_solution = None
    prev_sector = None
    for (_, col) in raw.iloc[:, 3:].iteritems():
        numeric = pd.to_numeric(col.iloc[11:], errors='coerce').fillna(0.0)
        if np.count_nonzero(numeric.to_numpy()) == 0:
            continue
        mechanism = col.iloc[3] if not pd.isna(col.iloc[3]) else 'Avoided'
        sector = col.iloc[4] if not pd.isna(col.iloc[4]) else prev_sector
        solution = col.iloc[5] if not pd.isna(col.iloc[5]) else prev_solution
        if mechanism == 'Avoided':
            numeric.iloc[0] = 0.0
        numeric.name = solution
        solutions[solution] += ((numeric / 1000.0) / 3.664)  # Mtons CO2 -> Gtons C
        prev_solution = solution
        prev_sector = sector

    total = model.fairutil.baseline_emissions()
    _,_,T = fair.forward.fair_scm(emissions=total.values, useMultigas=True,
            r0=model.fairutil.r0, tcrecs=model.fairutil.tcrecs)
    baseline_T = pd.Series(T, index=total.index)
    impacts = pd.DataFrame(index=range(1850, 2101), columns=solution_names)
    impacts.index.name = 'Year'
    for solution, emissions in solutions.iteritems():
        total = model.fairutil.baseline_emissions()
        emissions.loc[2061:2100] = emissions.loc[2060]
        total['FossilCO2'] = total['FossilCO2'].subtract(emissions.fillna(0.0), fill_value=0.0)
        _,_,T = fair.forward.fair_scm(emissions=total.values, useMultigas=True,
                r0=model.fairutil.r0, tcrecs=model.fairutil.tcrecs)
        df_T = pd.Series(T, index=total.index)
        impacts[solution] = df_T - baseline_T

    total = model.fairutil.baseline_emissions()
    emissions = solutions.sum(axis=1)
    baseline_total = total['FossilCO2'] + total['OtherCO2']
    solutions.insert(loc=len(solutions.columns), column="Baseline", value=baseline_total)
    solutions.insert(loc=len(solutions.columns), column="Total", value=emissions)
    impacts.insert(loc=len(impacts.columns), column="Baseline", value=baseline_T)
    total['FossilCO2'] = total['FossilCO2'].subtract(emissions.fillna(0.0), fill_value=0.0)
    _,_,T = fair.forward.fair_scm(emissions=total.values, useMultigas=True,
                r0=model.fairutil.r0, tcrecs=model.fairutil.tcrecs)
    df_T = pd.Series(T, index=total.index)
    impacts.insert(loc=len(impacts.columns), column="Total", value=df_T.copy())

    outfile = os.path.splitext(os.path.basename(filename))[0] + '_Totals_' + scenario + '.csv'
    solutions.to_csv(outfile, float_format='%.3f')
    outfile = os.path.splitext(os.path.basename(filename))[0] + '_FaIR_' + scenario + '.csv'
    impacts.to_csv(outfile, float_format='%.3f')

def process_ghgs(filename):
    for scenario in ['PDS1', 'PDS2', 'PDS3']:
        process_scenario(filename=filename, scenario=scenario)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Produce FaIR results from Drawdown emissions data.')
    parser.add_argument('--excelfile', help='Excel filename to process',
            default='CORE-Global_GHG_Accounting_12-1-2019.xlsm')
    args = parser.parse_args(sys.argv[1:])

    process_ghgs(filename=args.excelfile)
