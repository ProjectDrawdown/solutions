import argparse
import os.path
import sys

import fair
import matplotlib
import matplotlib.animation
import matplotlib.pyplot as plt
import matplotlib.style
import model.fairutil
import numpy as np
import pandas as pd


g_years = range(1850, 2061)
animation_sectors = {
    'Electricity': ['Electricity'],
    'Cogeneration': ['Electricity'],
    'Smart Thermostats': ['Electricity', 'Buildings'],
    'Building Automation Systems': ['Electricity', 'Buildings'],
    'LED Lighting': ['Electricity'],
    'LED Lighting (commercial)': ['Electricity'],
    'LED Lighting (residential)': ['Electricity'],
    'Insulation': ['Electricity', 'Buildings'],
    'Dynamic Glass': ['Electricity', 'Buildings'],
    'High-Performance Glass': ['Electricity', 'Buildings'],
    'High-Performance Glass (commercial)': ['Electricity', 'Buildings'],
    'High-Performance Glass (residential)': ['Electricity', 'Buildings'],
    'Green & Cool Roofs': ['Electricity', 'Buildings'],
    'Green Roofs': ['Electricity', 'Buildings'],
    'Cool Roofs': ['Electricity', 'Buildings'],
    'District Heating': ['Electricity', 'Buildings'],
    'High-Efficiency Heat Pumps': ['Electricity', 'Buildings'],
    'High-Efficient Heat Pumps': ['Electricity', 'Buildings'],
    'Efficient Cooling Devices': ['Electricity'],
    'Solar Hot Water': ['Electricity', 'Buildings'],
    'Low-Flow Fixtures': ['Electricity', 'Buildings'],
    'Water Distribution Efficiency': ['Electricity'],
    'Building Retrofitting': ['Electricity', 'Buildings'],
    'Net-Zero Buildings': ['Electricity', 'Buildings'],
    'Concentrated Solar Power': ['Electricity'],
    'Distributed Solar Photovoltaics': ['Electricity'],
    'Utility-Scale Solar Photovoltaics': ['Electricity'],
    'Utility-scale Solar Photovoltaics': ['Electricity'],
    'Micro WInd Turbines': ['Electricity'],
    'Micro Wind Turbines': ['Electricity'],
    'Onshore Wind Turbines': ['Electricity'],
    'Offshore WInd Turbines': ['Electricity'],
    'Offshore Wind Turbines': ['Electricity'],
    'Geothermal Power': ['Electricity'],
    'Small Hydropower': ['Electricity'],
    'Ocean Power': ['Electricity'],
    'Biomass Power': ['Electricity'],
    'Nuclear Power': ['Electricity'],
    'Waste-to-Energy': ['Electricity', 'Industry'],
    'Waste to Energy': ['Electricity', 'Industry'],
    'Landfill Methane Capture': ['Electricity', 'Industry'],
    'Methane Digesters': ['Electricity', 'Industry'],
    'Large Methane Digesters': ['Electricity', 'Industry'],
    'Grid Flexibility': ['Electricity'],
    'Microgrids': ['Electricity'],
    'Micro-Grids': ['Electricity'],
    'Distributed Energy Storage': ['Electricity'],
    'Utility-Scale Energy Storage': ['Electricity'],
    'Plant-Rich Diets': [ 'Food, Agriculture, Land Use', 'Land Sinks'],
    'Plant-Rich Diet': [ 'Food, Agriculture, Land Use', 'Land Sinks'],
    'Reduced Food Waste': [ 'Food, Agriculture, Land Use', 'Land Sinks'],
    'Macro Algal Farming': [ 'Food, Agriculture, Land Use', 'Coastal & Ocean Sinks'],
    'Avoided Land Conversion': [ 'Food, Agriculture, Land Use', 'Land Sinks'],
    'Avoided Land Use Conversion': [ 'Food, Agriculture, Land Use', 'Land Sinks'],
    'Forest Protection': ['Food, Agriculture, Land Use', 'Land Sinks'],
    "Indigenous Peoples' Forest Tenure": ['Food, Agriculture, Land Use'],
    'Sustainable Forestry': ['Food, Agriculture, Land Use', 'Land Sinks'],
    'Grassland Protection': ['Food, Agriculture, Land Use'],
    'Peatland Protection': ['Food, Agriculture, Land Use', 'Land Sinks'],
    'Peatland Protection & Rewetting': ['Food, Agriculture, Land Use', 'Land Sinks'],
    'Peatland Restoration': ['Food, Agriculture, Land Use', 'Land Sinks'],
    'Coastal Wetland Protection': ['Food, Agriculture, Land Use', 'Coastal & Ocean Sinks'],
    'Coastal Wetland Protection': ['Food, Agriculture, Land Use', 'Coastal & Ocean Sinks'],
    'Coastal Wetland Restoration': ['Food, Agriculture, Land Use', 'Coastal & Ocean Sinks'],
    'Coastal Wetlands Restoration': ['Food, Agriculture, Land Use', 'Coastal & Ocean Sinks'],
    'Sustainable Intensification for Smallholders': ['Food, Agriculture, Land Use', 'Land Sinks'],
    'Conservation Agriculture': [ 'Food, Agriculture, Land Use', 'Land Sinks'],
    'Regenerative Annual Cropping': [ 'Food, Agriculture, Land Use', 'Land Sinks'],
    'Improved Livestock Feeds': [ 'Food, Agriculture, Land Use'],
    'Nutrient Management': [ 'Food, Agriculture, Land Use'],
    'Farm Irrigation Efficiency': [ 'Food, Agriculture, Land Use'],
    'Improved Rice Production': [ 'Food, Agriculture, Land Use'],
    'System of Rice Intensification': [ 'Food, Agriculture, Land Use', 'Land Sinks'],
    'System of Rice Instensification': [ 'Food, Agriculture, Land Use', 'Land Sinks'],
    'TBD': ['Industry'],
    'Alternative Cement': ['Industry'],
    'Alternative Concrete': ['Industry'],
    'Alternative Cements': ['Industry'],
    'Bioplastics': ['Industry'],
    'Refrigerant Management': ['Industry', 'Buildings'],
    'Alternative Refrigerants': ['Industry', 'Buildings'],
    'Composting': ['Industry'],
    'Recycling': ['Industry'],
    'Recycling (commercial)': ['Industry'],
    'Recycling (residential)': ['Industry'],
    'Recycled Paper': ['Industry'],
    'Hybrid Cars': ['Transportation'],
    'Efficient Trucks': ['Transportation'],
    'Efficient Aviation': ['Transportation'],
    'Efficient Ocean Shipping': ['Transportation'],
    'Walkable Cities': ['Transportation'],
    'Bicycle Infrastructure': ['Transportation'],
    'Bike Infrastructure': ['Transportation'],
    'Electric Bicycles': ['Transportation'],
    'Carpooling': ['Transportation'],
    'Public Transit': ['Transportation'],
    'High-Speed Rail': ['Transportation'],
    'Telepresence': ['Transportation'],
    'Electric Cars': ['Transportation'],
    'Electric Trains': ['Transportation'],
    'Biogas for Cooking': ['Buildings'],
    'Improved Clean Cookstoves': ['Buildings'],
    'N/A': [ 'Other'],
    'Indigenous Peoples Forest Tenure': ['Land Sinks'],
    'Temperate Forest Restoration': ['Land Sinks'],
    'Tropical Forest Restoration': ['Land Sinks'],
    'Managed Grazing': ['Land Sinks'],
    'Silvopasture': ['Land Sinks'],
    'Multistrata Agroforestry': ['Land Sinks'],
    'Tree Intercropping': ['Land Sinks'],
    'Perennial Staple Crops': ['Land Sinks'],
    'Perennial Biomass Production': ['Land Sinks'],
    'Improved Rice Cultivation': ['Land Sinks'],
    'Abandoned Farmland Restoration': ['Land Sinks'],
    'Tree Plantations (on Degraded Land)': ['Land Sinks'],
    'Tree Plantations on Degraded Land': ['Land Sinks'],
    'Bamboo Production': ['Land Sinks'],
    'Marine Protected Areas': [ 'Coastal & Ocean Sinks'],
    'Kelp Forest Restoration': [ 'Coastal & Ocean Sinks'],
    'Marine Permaculture': [ 'Coastal & Ocean Sinks'],
    'Ocean Farming': [ 'Coastal & Ocean Sinks'],
    'Biochar Production': [ 'Engineered Sinks'],
    'Other coming attractions *': [ 'Engineered Sinks'],
    'Health & Education': ['Health & Education'],
    'Health and Education': ['Health & Education'],
    'Educating Girls': ['Health & Education'],
    'Family Planning': ['Health & Education'],
}

colors = {
    'Electricity': 'coral',
    'Food, Agriculture, Land Use': 'darkgreen',
    'Industry': 'mediumorchid',
    'Transportation': 'lightseagreen',
    'Buildings': 'steelblue',
    'Land Sinks': 'lawngreen',
    'Coastal & Ocean Sinks': 'powderblue',
    'Engineered Sinks': 'silver',
    'Health & Education': 'crimson',
}


def baseline(solutions):
    return model.fairutil.baseline_emissions().add(solutions['Health and Education'], fill_value=0.0)


def process_scenario(filename, outdir, scenario):
    sheet_name = 'Gtperyr_' + scenario
    raw = pd.read_excel(io=filename, sheet_name=sheet_name, header=None, index_col=0,
            dtype=object, skiprows=0, nrows=52, usecols='A:HR')
    solution_names = sorted([x.strip(' ') for x in list(set(raw.iloc[5, 9:].dropna()))])

    solutions = pd.DataFrame(0, index=g_years, columns=solution_names)
    solutions.index.name = 'Year'
    prev_solution = None
    for (_, col) in raw.iloc[:, 9:].iteritems():
        numeric = pd.to_numeric(col.iloc[11:], errors='coerce').fillna(0.0)
        if np.count_nonzero(numeric.to_numpy()) == 0:
            continue
        disposition = col.iloc[3]
        if disposition not in ['Avoided', 'Sequestration', 'ELC', 'F+D', 'IND']:
            continue
        mechanism = col.iloc[3] if not pd.isna(col.iloc[3]) else 'Avoided'
        solution = col.iloc[5].strip() if not pd.isna(col.iloc[5]) else prev_solution
        if solution == 'Peatland Protection' or solution == 'Peatland Restoration':
            continue
        if mechanism == 'Avoided':
            numeric.iloc[0] = 0.0
        numeric.name = solution
        solutions[solution] += ((numeric / 1000.0) / 3.664)  # Mtons CO2 -> Gtons C
        prev_solution = solution

    total = baseline(solutions)
    C,_,T = fair.forward.fair_scm(emissions=total.values, useMultigas=False,
            r0=model.fairutil.r0, tcrecs=model.fairutil.tcrecs)
    baseline_C = pd.Series(C, index=total.index.copy())
    baseline_T = pd.Series(T, index=total.index.copy())
    temperature = pd.DataFrame(index=g_years, columns=["Baseline", "Drawdown"])
    temperature.index.name = 'Year'

    concentration = pd.DataFrame(index=g_years,
            columns=["Emissions (GtC)", "Baseline (ppm)", "Drawdown (ppm)"])
    concentration.index.name = 'Year'
    concentration["Emissions (GtC)"] = baseline(solutions)
    concentration["Baseline (ppm)"] = baseline_C
    total = baseline(solutions)
    emissions = solutions.sum(axis=1)
    #emissions = raw.iloc[11:, 0:2].sum(axis=1) / 3.664
    #print(emissions.loc[2020:] * 3.664)
    total = total.subtract(emissions.fillna(0.0), fill_value=0.0)
    C,_,T = fair.forward.fair_scm(emissions=total.values, useMultigas=False,
                r0=model.fairutil.r0, tcrecs=model.fairutil.tcrecs)
    df_C = pd.Series(C, index=total.index.copy())
    df_T = pd.Series(T, index=total.index.copy())
    concentration["Drawdown (ppm)"] = df_C
    preindustrial = baseline_T.loc[1850:1900].mean()
    print(f"Pre-industrial temperature {preindustrial:.3f}C relative to {baseline_T.index[0]}")
    temperature["Drawdown"] = df_T.copy() - preindustrial
    temperature["Baseline"] = baseline_T - preindustrial

    outfile = os.path.splitext(os.path.basename(filename))[0] + '_Temperature_' + scenario + '.csv'
    temperature.to_csv(os.path.join(outdir, outfile), float_format='%.3f')
    outfile = os.path.splitext(os.path.basename(filename))[0] + '_Concentration_' + scenario + '.csv'
    concentration.to_csv(os.path.join(outdir, outfile), float_format='%.3f')

    return solutions.dropna(axis='columns', how='all').fillna(0.0)


def legend_no_duplicates(ax):
    handle, label = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handle, label)) if l not in label[:i]]
    ax.legend(*zip(*unique), loc='upper left', frameon=False)


def animate(frame, ax, start, lines, emissions, baseline_T):
    (sector_num, offset) = divmod(frame, 50)
    (sector, df_T) = emissions[sector_num]
    color = colors[sector]
    if offset == 0:
        zorder = 40 - sector_num
        line, = ax.plot([], [], color=color, label=sector, zorder=zorder)
        lines[sector] = line
        legend_no_duplicates(ax)
    else:
        line = lines[sector]

    if offset <= 40:
        end = 2020 + offset
        line.set_data(df_T.loc[2020:end].index.values, df_T.loc[2020:end].values)
        if sector_num == 0:
            prev = baseline_T
        else:
            (_, prev) = emissions[sector_num - 1]
        ax.fill_between(x=df_T.loc[2020:end].index.values, y1=prev.loc[2020:end].values,
                y2=df_T.loc[2020:end].values, color=color)


def produce_animation(solutions, filename, writer):
    sector_gtons = pd.DataFrame()
    for solution in solutions:
        sectors = animation_sectors[solution]
        for sector in sectors:
            if sector not in sector_gtons.columns:
                sector_gtons.loc[:, sector] = solutions.loc[:, solution] / len(sectors)
            else:
                sector_gtons.loc[:, sector] += solutions.loc[:, solution] / len(sectors)
    start = baseline(solutions)
    _,_,start_T = fair.forward.fair_scm(emissions=start.values, useMultigas=False,
            r0=model.fairutil.r0, tcrecs=model.fairutil.tcrecs)
    baseline_T = pd.Series(start_T, index=start.index.copy())
    preindustrial = baseline_T.loc[1850:1900].mean()
    start_T = start_T - preindustrial
    end = start.subtract(sector_gtons.sum(axis=1), fill_value=0.0)
    _,_,end_T = fair.forward.fair_scm(emissions=end.values, useMultigas=False,
            r0=model.fairutil.r0, tcrecs=model.fairutil.tcrecs)
    end_T = end_T - preindustrial
    total_reduction_T = (start_T - end_T)[255:296]
    reduction_T = np.zeros(total_reduction_T.shape)
    sectors = sector_gtons.sort_values(axis='columns', by=2050, ascending=False).columns
    emissions = []
    for sector in sectors:
        fraction = sector_gtons[sector] / sector_gtons.sum(axis=1)
        reduction_T += total_reduction_T * fraction.loc[2020:2061].fillna(0.0).values
        temperatures = start_T[255:296] - reduction_T
        df_T = pd.Series(temperatures, index=range(2020, 2061))
        emissions.append((sector, df_T))

    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_ylabel(u'°C');
    df_T = pd.Series(start_T, index=start.index)
    ax.plot(df_T.loc[2005:2060].index.values, df_T.loc[2005:2060].values,
            label='Baseline', zorder=50)
    legend_no_duplicates(ax)

    lines = {}
    frames = len(emissions) * 50
    anim = matplotlib.animation.FuncAnimation(fig=fig, func=animate, interval=10, frames=frames,
            fargs=(ax, start, lines, emissions, baseline_T - preindustrial), repeat=False)
    anim.save(filename, writer=writer)


def process_ghgs(excelfile, outdir, writer=None, ext='.mp4'):
    plt.rcParams.update({
        "lines.color": "white",
        "patch.edgecolor": "white",
        "text.color": "black",
        "axes.facecolor": "black",
        "axes.edgecolor": "lightgray",
        "axes.labelcolor": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "grid.color": "lightgray",
        "text.color": "lightgray",
        "figure.facecolor": "black",
        "figure.edgecolor": "black",
        "savefig.facecolor": "black",
        "savefig.edgecolor": "black"})
    for scenario in ['PDS1', 'PDS2']:
        print(f"{scenario} CSV")
        solutions = process_scenario(filename=excelfile, outdir=outdir, scenario=scenario)
        if writer is None:
            ffmpeg = matplotlib.animation.writers['ffmpeg']
            writer = ffmpeg(fps=15, bitrate=-1,
                    metadata={'title':'Play the Whole Field', 'subject':'Climate Change Solutions',
                        'copyright':'Copyright 2020 Project Drawdown'},
                    extra_args=['-tune', 'animation'],)
        if writer:
            print(f"{scenario} animation")
            mp4 = os.path.splitext(os.path.basename(excelfile))[0] + '_' + scenario + ext
            produce_animation(solutions=solutions, filename=os.path.join(outdir, mp4), writer=writer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Produce FaIR results from Drawdown emissions data.')
    parser.add_argument('--excelfile', help='Excel filename to process',
            default='CORE-Global_GHG_Accounting_2-1-2020_FINAL.xlsm')
    parser.add_argument('--outdir', help='output directory', default='.')

    args = parser.parse_args(sys.argv[1:])

    process_ghgs(excelfile=args.excelfile, outdir=args.outdir)
