"""Health & Education solution model for Residential Light Cluster
   Excel filename: CORE_PopulationChange_29Jan2020 (version 1.5).xlsx
   Excel sheet name: ResLight_cluster
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

name = 'Health and Education - Residential Light Cluster'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION 
period_start = 2020
period_end = 2050

# % impact of educational attainment on uptake of Family Planning:
assumptions = {
    'fixed_weighting_factor': None,
    'pct_impact': 0.50,
    'use_fixed_weight': 'N',
    'Twh_per_TWh': 42.34,
    'period_start': 2020,
    'period_end': 2050,
    'Grid': 'Y',
    'Fuel': 'Y',
    'Other Direct': 'N',
    'Indirect': 'N'
}

# TABLE 1: Current TAM Mix
current_tam_mix_list = [
        ['Energy Source', 'Weighting Factor', 'Include in SOL?', 'Include in CONV?'],
        ['Incandescent', 19.1167883211679, 'N', 'Y'],
        ['Halogen', 31.8613138686131, 'N', 'Y'],
        ['LFL', 14.1605839416058, 'N', 'Y'],
        ['CFL', 31.8613138686131, 'N', 'Y']]

# Table 2: REF2, Residential Lighting Demand TAM (Plmh)										
# ComLight_cluster!B28:K75
# TODO: Replace this with solarpvutil.Scenario.ref_tam_per_region once we resolve the data mismatch
ref2_tam_list = [
        ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
        [35.4547221, 9.794373552, 1.964518584, 13.19266535, 3.581666314, 1.56105251, 8.641704421, 2.530072744, 3.871085331, 4.030950662], 
        [35.13686627, 10.01766303, 1.951154263, 13.85151143, 3.747134398, 1.654489288, 8.916478443, 2.670750172, 3.880729963, 4.117565504], 
        [35.59044879, 10.05068271, 1.96410343, 13.92690104, 3.835573099, 1.667797468, 8.945605217, 2.70691206, 3.891812362, 4.1404158], 
        [36.03815483, 10.08559572, 1.976302369, 14.0086474, 3.925481129, 1.682035514, 8.976640258, 2.744266293, 3.902526858, 4.163828968], 
        [36.47998439, 10.1222983, 1.987781847, 14.09642286, 4.016800375, 1.697156622, 9.009457738, 2.782751518, 3.912879003, 4.187768353], 
        [36.91593747, 10.1606867, 1.998572631, 14.18989976, 4.109472727, 1.713113985, 9.043931829, 2.82230638, 3.92287435, 4.212197297], 
        [37.34601407, 10.20065716, 2.008705487, 14.28875046, 4.203440071, 1.729860796, 9.079936705, 2.862869527, 3.932518451, 4.237079145], 
        [37.77021419, 10.24210593, 2.018211183, 14.39264732, 4.298644297, 1.74735025, 9.117346537, 2.904379605, 3.941816859, 4.262377239], 
        [38.18853783, 10.28492925, 2.027120484, 14.50126268, 4.395027292, 1.765535541, 9.156035497, 2.94677526, 3.950775126, 4.288054923], 
        [38.60098498, 10.32902338, 2.035464158, 14.61426891, 4.492530946, 1.784369861, 9.195877759, 2.989995138, 3.959398805, 4.314075541], 
        [39.00755566, 10.37428456, 2.043272971, 14.73133834, 4.591097146, 1.803806406, 9.236747494, 3.033977886, 3.967693448, 4.340402435], 
        [39.40824985, 10.42060903, 2.05057769, 14.85214334, 4.69066778, 1.823798369, 9.278518876, 3.07866215, 3.975664608, 4.36699895], 
        [39.80306757, 10.46789305, 2.057409081, 14.97635626, 4.791184738, 1.844298943, 9.321066075, 3.123986577, 3.983317838, 4.39382843], 
        [40.1920088, 10.51603285, 2.063797912, 15.10364945, 4.892589907, 1.865261324, 9.364263266, 3.169889813, 3.990658689, 4.420854216], 
        [40.57507355, 10.5649247, 2.069774949, 15.23369526, 4.994825175, 1.886638703, 9.407984619, 3.216310504, 3.997692715, 4.448039653], 
        [40.95226183, 10.61446483, 2.075370959, 15.36616604, 5.097832431, 1.908384276, 9.452104309, 3.263187296, 4.004425468, 4.475348085], 
        [41.32357362, 10.66454948, 2.080616708, 15.50073416, 5.201553564, 1.930451237, 9.496496506, 3.310458837, 4.010862501, 4.502742854], 
        [41.68900893, 10.71507492, 2.085542963, 15.63707195, 5.305930461, 1.952792778, 9.541035383, 3.358063772, 4.017009365, 4.530187305], 
        [42.04856775, 10.76593738, 2.090180491, 15.77485178, 5.410905011, 1.975362094, 9.585595114, 3.405940748, 4.022871615, 4.55764478], 
        [42.4022501, 10.81703311, 2.094560058, 15.913746, 5.516419101, 1.998112379, 9.630049869, 3.454028411, 4.028454801, 4.585078623], 
        [42.75005597, 10.86825836, 2.098712431, 16.05342695, 5.622414622, 2.020996826, 9.674273822, 3.502265408, 4.033764477, 4.612452179], 
        [43.09198536, 10.91950937, 2.102668378, 16.193567, 5.72883346, 2.04396863, 9.718141145, 3.550590384, 4.038806195, 4.639728789], 
        [43.42803826, 10.97068239, 2.106458664, 16.3338385, 5.835617504, 2.066980984, 9.76152601, 3.598941987, 4.043585508, 4.666871797], 
        [43.75821469, 11.02167367, 2.110114056, 16.47391379, 5.942708642, 2.089987083, 9.80430259, 3.647258862, 4.048107968, 4.693844548], 
        [44.08251463, 11.07237946, 2.113665321, 16.61346523, 6.050048763, 2.112940119, 9.846345058, 3.695479657, 4.052379127, 4.720610384], 
        [44.40093809, 11.12269599, 2.117143226, 16.75216517, 6.157579755, 2.135793287, 9.887527585, 3.743543017, 4.056404539, 4.747132649], 
        [44.71348507, 11.17251953, 2.120578537, 16.88968598, 6.265243506, 2.158499781, 9.927724343, 3.791387588, 4.060189756, 4.773374687], 
        [45.02015557, 11.22174631, 2.124002021, 17.02569999, 6.372981905, 2.181012794, 9.966809507, 3.838952018, 4.06374033, 4.79929984], 
        [45.32094959, 11.27027258, 2.127444444, 17.15987956, 6.480736839, 2.203285521, 10.00465725, 3.886174952, 4.067061815, 4.824871453], 
        [45.61586713, 11.31799459, 2.130936574, 17.29189705, 6.588450198, 2.225271155, 10.04114174, 3.932995037, 4.070159761, 4.850052869], 
        [45.90490819, 11.36480858, 2.134509178, 17.4214248, 6.696063869, 2.246922889, 10.07613715, 3.979350919, 4.073039722, 4.87480743], 
        [46.18807277, 11.41061081, 2.138193021, 17.54813517, 6.803519741, 2.268193919, 10.10951765, 4.025181245, 4.075707251, 4.899098482], 
        [46.46536087, 11.45529752, 2.14201887, 17.67170052, 6.910759702, 2.289037438, 10.14115742, 4.070424661, 4.0781679, 4.922889366], 
        [46.73677248, 11.49876495, 2.146017493, 17.79179319, 7.01772564, 2.309406639, 10.17093063, 4.115019814, 4.080427222, 4.946143428], 
        [47.00230762, 11.54090935, 2.150219655, 17.90808554, 7.124359444, 2.329254716, 10.19871145, 4.158905349, 4.082490768, 4.968824009], 
        [47.26196627, 11.58162697, 2.154656125, 18.02024992, 7.230603002, 2.348534864, 10.22437406, 4.202019913, 4.084364092, 4.990894454], 
        [47.51574844, 11.62081406, 2.159357667, 18.12795869, 7.336398202, 2.367200276, 10.24779262, 4.244302153, 4.086052746, 5.012318106], 
        [47.76365413, 11.65836686, 2.164355049, 18.23088419, 7.441686933, 2.385204146, 10.26884131, 4.285690714, 4.087562283, 5.033058309], 
        [48.00568334, 11.69418162, 2.169679038, 18.32869878, 7.546411082, 2.402499667, 10.2873943, 4.326124244, 4.088898255, 5.053078405], 
        [48.24183608, 11.72815459, 2.1753604, 18.42107481, 7.650512539, 2.419040035, 10.30332576, 4.365541388, 4.090066215, 5.072341739], 
        [48.47211232, 11.76018201, 2.181429903, 18.50768464, 7.753933192, 2.434778442, 10.31650987, 4.403880794, 4.091071715, 5.090811654], 
        [48.69651209, 11.79016013, 2.187918312, 18.58820061, 7.856614928, 2.449668082, 10.32682079, 4.441081107, 4.091920307, 5.108451493], 
        [48.91503538, 11.8179852, 2.194856394, 18.66229509, 7.958499636, 2.463662149, 10.33413271, 4.477080973, 4.092617545, 5.1252246], 
        [49.12768219, 11.84355345, 2.202274917, 18.72964042, 8.059529205, 2.476713838, 10.33831979, 4.511819039, 4.093168981, 5.141094318], 
        [49.33445251, 11.86676115, 2.210204646, 18.78990895, 8.159645522, 2.488776341, 10.33925621, 4.545233952, 4.093580167, 5.156023991], 
        [49.53534636, 11.88750454, 2.218676349, 18.84277304, 8.258790476, 2.499802853, 10.33681613, 4.577264358, 4.093856656, 5.169976962], 
        [49.73036372, 11.90567986, 2.227720792, 18.88790505, 8.356905956, 2.509746568, 10.33087373, 4.607848903, 4.094004, 5.182916574]]


# GRID EMISSIONS FACTORS: REF Grid EFs kg CO2-eq per kwh									
# Emissions Factors!B11:K57
# TODO: Replace this with emissions_factors module once interface is better understood
ef_co2_eq_list = [
        ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
        [None, None, None, None, None, None, None, None, None, None],
        [0.617381628, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.613053712, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.605559021, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.599823764, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.596692109, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.592956465, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.589394210, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.585889941, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.582469966, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.579126508, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.576180724, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.572640473, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.569484654, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.566378788, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.563317175, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.560425096, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.557305440, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.554345365, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.551409592, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.548493724, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.545513743, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.542688056, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.539794403, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.536903541, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.533998347, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.530880184, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.528185055, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.525268472, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.522337859, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.519390128, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.516316183, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.513431317, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.510414389, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.507368630, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.504753472, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.503017663, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.501095098, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.499244741, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.497355610, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.495425752, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.493412239, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.491436597, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.489373931, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.487263794, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.485104746, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666], 
        [0.483057065, 0.454068989, 0.724747956, 0.457658947, 0.282243907, 0.564394712, 0.535962403, 0.787832379, 0.360629290, 0.665071666]]

class Cluster:

    def __init__(self):
        self.name = name

    def run_cluster(self):
        scenario = cluster_model.Scenario(name, assumptions)
        scenario.load_pop_data(DATADIR)
        scenario.load_tam_mix(current_tam_mix_list)
        scenario.load_ref2_tam(ref2_tam_list)
        scenario.calc_ref1_tam()
        scenario.calc_ref2_demand()
        scenario.calc_ref1_demand()
        scenario.calc_change_demand()
        scenario.calc_addl_units_highed()
        scenario.calc_addl_units_lowed()
        scenario.calc_emis_diff_highed_comlight(ef_co2_eq_list)
        scenario.calc_emis_diff_lowed_comlight()
        scenario.calc_emis_alloc_lldc()
        scenario.calc_addl_units_mdc()
        scenario.calc_emis_diff_mdc_comlight()
        scenario.calc_emis_alloc_mdc()
        scenario.calc_total_emis()
        scenario.print_total_emis()
        return scenario
        
if __name__ == "__main__":
    cluster = Cluster()
    cluster.run_cluster()