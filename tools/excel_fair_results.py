import argparse
import os.path
import pathlib
import sys

import fair
import matplotlib
import matplotlib.animation
import matplotlib.pyplot as plt
import matplotlib.style
import model.fairutil
import numpy as np
import tempfile
import pandas as pd
import solution.factory
import ui.color


g_years = range(1850, 2061)


def process_scenario(filename, outdir, scenario):
    sheet_name = 'Gtperyr_' + scenario
    raw = pd.read_excel(io=filename, sheet_name=sheet_name, header=None, index_col=0,
            dtype=object, skiprows=0, nrows=52, usecols='A:EF')
    years = raw.index[11:]
    solution_names = sorted(list(set(raw.iloc[5, 3:].dropna())))

    solutions = pd.DataFrame(0, index=g_years, columns=solution_names)
    solutions.index.name = 'Year'
    sectors = {}
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
        sector_list = sectors.get(sector, [])
        sectors[sector] = sector_list + [solution]
        prev_solution = solution
        prev_sector = sector

    total = model.fairutil.baseline_emissions()
    C,_,T = fair.forward.fair_scm(emissions=total.values, useMultigas=False,
            r0=model.fairutil.r0, tcrecs=model.fairutil.tcrecs)
    baseline_C = pd.Series(C, index=total.index.copy())
    baseline_T = pd.Series(T, index=total.index.copy())
    temperature = pd.DataFrame(index=g_years, columns=solution_names)
    temperature.index.name = 'Year'
    for solution, emissions in solutions.iteritems():
        total = model.fairutil.baseline_emissions()
        total = total.subtract(emissions.fillna(0.0), fill_value=0.0)
        _,_,T = fair.forward.fair_scm(emissions=total.values, useMultigas=False,
                r0=model.fairutil.r0, tcrecs=model.fairutil.tcrecs)
        df_T = pd.Series(T, index=total.index.copy())
        temperature[solution] = df_T - baseline_T

    concentration = pd.DataFrame(index=g_years,
            columns=["Emissions (GtC)", "Baseline (ppm)", "Drawdown (ppm)"])
    concentration.index.name = 'Year'
    concentration["Emissions (GtC)"] = model.fairutil.baseline_emissions()
    concentration["Baseline (ppm)"] = baseline_C
    total = model.fairutil.baseline_emissions()
    emissions = solutions.sum(axis=1)
    total = total.subtract(emissions.fillna(0.0), fill_value=0.0)
    C,_,T = fair.forward.fair_scm(emissions=total.values, useMultigas=False,
                r0=model.fairutil.r0, tcrecs=model.fairutil.tcrecs)
    df_C = pd.Series(C, index=total.index.copy())
    df_T = pd.Series(T, index=total.index.copy())
    concentration["Drawdown (ppm)"] = df_C
    preindustrial = baseline_T.loc[1850:1900].mean()
    print(f"Pre-industrial temperature {preindustrial:.3f}C relative to {baseline_T.index[0]}")
    temperature.insert(loc=0, column="Total", value=(df_T.copy() - preindustrial))
    temperature.insert(loc=0, column="Baseline", value=(baseline_T - preindustrial))

    outfile = os.path.splitext(os.path.basename(filename))[0] + '_Temperature_' + scenario + '.csv'
    temperature.to_csv(os.path.join(outdir, outfile), float_format='%.3f')
    outfile = os.path.splitext(os.path.basename(filename))[0] + '_Concentration_' + scenario + '.csv'
    concentration.to_csv(os.path.join(outdir, outfile), float_format='%.3f')

    return (solutions, sectors)


def legend_no_duplicates(ax):
    handle, label = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handle, label)) if l not in label[:i]]
    ax.legend(*zip(*unique), loc='upper left', frameon=False)


def animate(frame, ax, total, lines, emissions):
    (sector_num, offset) = divmod(frame, 50)
    (sector, df_T) = emissions[sector_num]
    color = ui.color.get_sector_color(sector)
    if offset == 0:
        zorder = 40 - sector_num
        line, = ax.plot([], [], color=color, label=sector, zorder=zorder)
        lines[sector] = line
        legend_no_duplicates(ax)
    else:
        line = lines[sector]

    if offset <= 30:
        end = 2020 + offset
        line.set_data(df_T.loc[2020:end].index.values, df_T.loc[2020:end].values)
        if sector_num == 0:
            _,_,T = fair.forward.fair_scm(emissions=total.values, useMultigas=False,
                    r0=model.fairutil.r0, tcrecs=model.fairutil.tcrecs)
            prev = pd.Series(T, index=total.index)
        else:
            (_, prev) = emissions[sector_num - 1]
        ax.fill_between(x=df_T.loc[2020:end].index.values, y1=prev.loc[2020:end].values,
                y2=df_T.loc[2020:end].values, color=color)


def produce_animation(solutions, sectors, filename, writer):
    sector_gtons = pd.DataFrame()
    for sector, solution_list in sectors.items():
        sector_gtons.loc[:, sector] = solutions.loc[:, solution_list].sum(axis=1)

    total = model.fairutil.baseline_emissions()
    remaining = total.copy()
    sectors = sector_gtons.sort_values(axis='columns', by=2050, ascending=False).columns
    emissions = []
    for sector in sectors:
        remaining = remaining.subtract(sector_gtons[sector], fill_value=0.0)
        _,_,T = fair.forward.fair_scm(emissions=remaining.values, useMultigas=False,
                r0=model.fairutil.r0, tcrecs=model.fairutil.tcrecs)
        df_T = pd.Series(T, index=remaining.index)
        emissions.append((sector, df_T))

    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_ylabel(u'°C');
    _,_,T = fair.forward.fair_scm(emissions=total.values, useMultigas=False, r0=model.fairutil.r0,
            tcrecs=model.fairutil.tcrecs)
    df_T = pd.Series(T, index=total.index)
    ax.plot(df_T.loc[2005:2050].index.values, df_T.loc[2005:2050].values,
            color='black', label='Baseline', zorder=50)
    legend_no_duplicates(ax)

    lines = {}
    frames = len(emissions) * 50
    anim = matplotlib.animation.FuncAnimation(fig=fig, func=animate, interval=10, frames=frames,
            fargs=(ax, total, lines, emissions), repeat=False)
    anim.save(filename, writer=writer)


def process_ghgs(excelfile, outdir, writer=None, ext='.mp4'):
    matplotlib.style.use('ggplot')
    for scenario in ['PDS1', 'PDS2', 'PDS3']:
        print(f"{scenario} CSV")
        (solutions, sectors) = process_scenario(filename=excelfile, outdir=outdir,
                scenario=scenario)
        if writer is None:
            ffmpeg = matplotlib.animation.writers['ffmpeg']
            writer = ffmpeg(fps=15, bitrate=-1,
                    metadata={'title':'Play the Whole Field', 'subject':'Climate Change Solutions',
                        'copyright':'Copyright 2020 Project Drawdown'},
                    extra_args=['-tune', 'animation'],)
        if writer:
            print(f"{scenario} animation")
            mp4 = os.path.splitext(os.path.basename(excelfile))[0] + '_' + scenario + ext
            produce_animation(solutions=solutions, sectors=sectors,
                    filename=os.path.join(outdir, mp4), writer=writer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Produce FaIR results from Drawdown emissions data.')
    parser.add_argument('--excelfile', help='Excel filename to process',
            default='CORE-Global_GHG_Accounting_12-1-2019.xlsm')
    parser.add_argument('--outdir', help='output directory', default='.')

    args = parser.parse_args(sys.argv[1:])

    process_ghgs(excelfile=args.excelfile, outdir=args.outdir)
