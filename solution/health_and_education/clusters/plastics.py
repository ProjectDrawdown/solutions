"""Health & Education solution model for Plastics Cluster
   Excel filename: CORE_PopulationChange_29Jan2020 (version 1.5).xlsx
   Excel sheet name: Plastics_cluster
"""
import pathlib
import numpy as np
import pandas as pd
import sys
__file__ = 'c:\\Users\\sunishchal.dev\\Documents\\solutions\\solution\\health_and_education\\clusters'
repo_path = str(pathlib.Path(__file__).parents[2])
sys.path.append(repo_path)
# sys.path.append('c:\\Users\\sunishchal.dev\\Documents\\solutions')

from model import advanced_controls as ac
from solution.health_and_education.clusters import cluster_model

DATADIR = pathlib.Path(__file__).parents[0].joinpath('data')
THISDIR = pathlib.Path(__file__).parents[0]

name = 'Health and Education - Plastics Cluster'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION 
period_start = 2020
period_end = 2050

# % impact of educational attainment on uptake of Family Planning:
assumptions = {
    'fixed_weighting_factor': 1.0,
    'pct_impact': 0.50,
    'use_fixed_weight': 'Y',
    'Direct Emissions': 2449285.71429, # t CO2-eq per MMt of Plastic Produced Annually
    'period_start': 2020,
    'period_end': 2050,
    'Grid': 'N',
    'Fuel': 'N',
    'Other Direct': 'Y',
    'Indirect': 'N'
}

# TABLE 1: Current TAM Mix
current_tam_mix_list = [
        ['Energy Source', 'Weighting Factor', 'Include in SOL?', 'Include in CONV?'],
        ['Conventional plastic', 99.46, 'N', 'Y']]

# Table 2: REF2, Plastics Demand TAM (TWh Therms)										
# WaterHeating_cluster!B28:K75
# TODO: Replace this with solarpvutil.Scenario.ref_tam_per_region once we resolve the data mismatch
ref2_tam_list = [
        ['World'],
        [311],
        [318.4319049],
        [325.9923898],
        [333.9539254],
        [342.3106818],
        [351.0568292],
        [360.1865377],
        [369.6939775],
        [379.5733188],
        [389.8187316],
        [400.4243862],
        [411.3844527],
        [422.6931012],
        [434.344502],
        [446.3328251],
        [458.6522408],
        [471.2969191],
        [484.2610303],
        [497.5387444],
        [511.1242317],
        [525.0116623],
        [539.1952064],
        [553.669034],
        [568.4273155],
        [583.4642208],
        [598.7739202],
        [614.3505839],
        [630.1883819],
        [646.2814845],
        [662.6240618],
        [679.2102839],
        [696.034321],
        [713.0903433],
        [730.3725209],
        [747.8750239],
        [765.5920226],
        [783.5176871],
        [801.6461875],
        [819.971694],
        [838.4883767],
        [857.1904058],
        [876.0719515],
        [895.1271839],
        [914.3502732],
        [933.7353894],
        [953.2767029],
        [972.9683837]]


class Cluster:

    def __init__(self):
        self.name = name

    def run_cluster(self):
        scenario = cluster_model.Scenario(name, assumptions)
        scenario.load_pop_data(DATADIR)
        scenario.load_tam_mix(current_tam_mix_list)
        scenario.load_ref2_tam(ref2_tam_list)
        scenario.calc_ref1_tam_plastics()
        scenario.calc_addl_units_mdc()
        scenario.calc_emis_diff_mdc_paper()
        scenario.calc_emis_alloc_mdc()
        scenario.calc_total_emis(lldc=False)
        scenario.print_total_emis(lldc=False)
        return scenario
        
if __name__ == "__main__":
    cluster = Cluster()
    cluster.run_cluster()