import argparse
import os
import pathlib
import sys

import fair
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

emissions = []
lines = {}

# Baseline emissions in Gtons CO2
total = pd.read_csv(str(baselineCO2_path), header=0, index_col=0, skipinitialspace=True,
        skip_blank_lines=True, comment='#', squeeze=True)


def legend_no_duplicates(ax):
    handle, label = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handle, label)) if l not in label[:i]]
    ax.legend(*zip(*unique), loc='upper left', frameon=False)


def init():
    """Prepare emissions dict with data per sector."""
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
        sector_gt.loc[:, sector] = mmt.loc[:, sector_members].sum(axis=1) / 1000.0

    remaining = total['Gtons'].copy()
    sectors = sector_gt.sort_values(axis='columns', by=2050, ascending=False).columns
    for sector in sectors:
        remaining = remaining.subtract(other=sector_gt[sector], fill_value=0.0)
        _,_,T = fair.forward.fair_scm(emissions=remaining.values, useMultigas=False)
        df_T = pd.Series(T, index=remaining.index.copy())
        emissions.append((sector, df_T))

    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_ylabel('Temperature anomaly (K)');
    _,_,T = fair.forward.fair_scm(emissions=total['Gtons'].values, useMultigas=False)
    df_T = pd.Series(T, index=total.index.copy())
    ax.plot(df_T.loc[2005:2050].index.values, df_T.loc[2005:2050].values,
            color='black', label='Baseline')
    legend_no_duplicates(ax)
    return (fig, ax)


def animate(frame, ax):
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
            _,_,T = fair.forward.fair_scm(emissions=total['Gtons'].values, useMultigas=False)
            prev = pd.Series(T, index=total.index.copy())
        else:
            (_, prev) = emissions[sector_num - 1]
        ax.fill_between(x=df_T.loc[2020:end].index.values, y1=prev.loc[2020:end].values,
                y2=df_T.loc[2020:end].values, color=color)


def main(filename, writer):
    (fig, ax) = init()
    frames = len(emissions) * 50
    anim = matplotlib.animation.FuncAnimation(fig=fig, func=animate, interval=10, frames=frames,
            fargs=(ax,), repeat=False)
    anim.save(filename, writer=writer)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create animation play_the_whole_field.mp4')
    parser.add_argument('--filename', default=str(default_file), required=False,
        help='Filename to write generated video to')
    args = parser.parse_args(sys.argv[1:])

    ffmpeg = matplotlib.animation.writers['ffmpeg']
    writer = ffmpeg(fps=15, bitrate=-1,
            metadata={'title':'Play the Whole Board', 'subject':'Climate Change Solutions',
                'copyright':'Copyright 2019 Project Drawdown'},
            extra_args=['-tune', 'animation'],)

    main(filename=args.filename, writer=writer)
