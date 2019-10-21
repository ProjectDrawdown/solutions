import argparse
import copy
import os
import pathlib
import sys

import fair
import fair.RCPs
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation
import numpy as np
import tempfile
import pandas as pd
import solution.factory
import ui.color


topdir = pathlib.Path(__file__).parents[1]
default_file = topdir.joinpath('data', 'images', 'play_the_whole_field.mp4')
baselineCO2_path = topdir.joinpath('data', 'baselineCO2.csv')
tcrecs = np.array([1.7, 3.2])  # GRL https://doi.org/10.1029/2019GL082442

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


# TODO: https://github.com/OMS-NetZero/FAIR/issues/19 set r0=35
# set TCR as Dr Forest recommends.


def legend_no_duplicates(ax):
    handle, label = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handle, label)) if l not in label[:i]]
    ax.legend(*zip(*unique), loc='upper left', frameon=False)


def init():
    """Return emissions with data per sector."""
    mmt = pd.DataFrame()

    solutions = solution.factory.all_solutions_scenarios()
    for name in solutions.keys():
        (constructor, _) = solutions[name]
        obj = constructor(scenario=None)
        m = obj.c2.co2eq_mmt_reduced()
        mmt[name] = m['World']

    sector_gt = pd.DataFrame()
    everything = pd.read_csv(os.path.join('data', 'overview', 'solutions.csv'),
        index_col=False, skipinitialspace=True, header=0, skip_blank_lines=True, comment='#')

    for sector in everything.Sector.unique():
        column_names = everything.loc[everything['Sector'] == sector, 'DirName'].dropna()
        sector_members = list(set(column_names).intersection(set(mmt.columns)))
        sector_gt.loc[:, sector] = (mmt.loc[:, sector_members].sum(axis=1) / 1000.0) / 3.664

    # Baseline emissions in Gtons
    total = fair.RCPs.rcp45.Emissions.emissions.copy()
    ddCO2 = pd.read_csv(str(baselineCO2_path), header=0, index_col=0, skipinitialspace=True,
            skip_blank_lines=True, comment='#', squeeze=True)
    for idx, year in enumerate(fair.RCPs.rcp45.Emissions.year):
        if year not in ddCO2.index:
            continue
        if not np.isnan(ddCO2.loc[year, 'Fossil-GtC']):
            total[idx, CO2_FOSSIL] = ddCO2.loc[year, 'Fossil-GtC']
        if not np.isnan(ddCO2.loc[year, 'LandUse-GtC']):
            total[idx, CO2_LAND] = ddCO2.loc[year, 'LandUse-GtC']
        if not np.isnan(ddCO2.loc[year, 'MtCH4']):
            total[idx, CH4] = ddCO2.loc[year, 'MtCH4']
        if not np.isnan(ddCO2.loc[year, 'MtN2O']):
            total[idx, N2O] = ddCO2.loc[year, 'MtN2O']

    emissions = []
    remaining = total.copy()
    sectors = sector_gt.sort_values(axis='columns', by=2050, ascending=False).columns
    for sector in sectors:
        for idx, year in enumerate(fair.RCPs.rcp45.Emissions.year):
            if int(year) in sector_gt.index:
                remaining[idx, CO2_FOSSIL] -= sector_gt.loc[int(year), sector]
        _,_,T = fair.forward.fair_scm(emissions=remaining, useMultigas=True, r0=35, tcrecs=tcrecs)
        df_T = pd.Series(T, index=fair.RCPs.rcp45.Emissions.year)
        emissions.append((sector, df_T))

    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_ylabel('Temperature anomaly (K)');
    _,_,T = fair.forward.fair_scm(emissions=total, useMultigas=True, r0=35, tcrecs=tcrecs)
    df_T = pd.Series(T, index=fair.RCPs.rcp45.Emissions.year)
    ax.plot(df_T.loc[2005:2050].index.values, df_T.loc[2005:2050].values,
            color='black', label='Baseline')
    legend_no_duplicates(ax)
    return (fig, ax, total, emissions)


def animate(frame, ax, total, lines, emissions):
    (sector_num, offset) = divmod(frame, 50)
    (sector, df_T) = emissions[sector_num]
    color = ui.color.get_sector_color(sector)
    if offset == 0:
        line, = ax.plot([], [], color=color, label=sector)
        lines[sector] = line
        legend_no_duplicates(ax)
    else:
        line = lines[sector]

    if offset <= 30:
        end = 2020 + offset
        line.set_data(df_T.loc[2020:end].index.values, df_T.loc[2020:end].values)
        if sector_num == 0:
            _,_,T = fair.forward.fair_scm(emissions=total, useMultigas=True, r0=35, tcrecs=tcrecs)
            prev = pd.Series(T, index=fair.RCPs.rcp45.Emissions.year)
        else:
            (_, prev) = emissions[sector_num - 1]
        ax.fill_between(x=df_T.loc[2020:end].index.values, y1=prev.loc[2020:end].values,
                y2=df_T.loc[2020:end].values, color=color)


def main(filename, writer):
    (fig, ax, total, emissions) = init()
    lines = {}
    frames = len(emissions) * 50
    anim = matplotlib.animation.FuncAnimation(fig=fig, func=animate, interval=10, frames=frames,
            fargs=(ax, total, lines, emissions), repeat=False)
    anim.save(filename, writer=writer)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create animation play_the_whole_field.mp4')
    parser.add_argument('--filename', default=str(default_file), required=False,
        help='Filename to write generated video to')
    args = parser.parse_args(sys.argv[1:])

    ffmpeg = matplotlib.animation.writers['ffmpeg']
    writer = ffmpeg(fps=15, bitrate=-1,
            metadata={'title':'Play the Whole Field', 'subject':'Climate Change Solutions',
                'copyright':'Copyright 2019 Project Drawdown'},
            extra_args=['-tune', 'animation'],)

    main(filename=args.filename, writer=writer)
