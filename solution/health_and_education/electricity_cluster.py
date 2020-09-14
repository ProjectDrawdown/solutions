"""Health & Education solution model for Electricity Cluster
   Excel filename: CORE_PopulationChange_29Jan2020 (version 1.4).xlsx
   Excel sheet name: Electricity_cluster
"""
import pathlib

import numpy as np
import pandas as pd

# import sys
# sys.path.append('c:\\Users\\sunishchal.dev\\Documents\\solutions')

# import solarpvutil

DATADIR = pathlib.Path(__file__).parents[0].joinpath('data')
THISDIR = pathlib.Path(__file__).parents[0]

name = 'Health and Education - Electricity Cluster'
# solution_category = ac.SOLUTION_CATEGORY.REDUCTION #TODO: Confirm this is a reduction solution

# Assumptions:
# % impact of educational attainment on uptake of Family Planning:
fixed_weighting_factor = None
pct_impact = 0.50
use_fixed_weight = 'N'
## TODO: Move above block to advanced_controls.py after we figure out if it varies by scenario

# Regions included as LLDC+HighNRR:
lldc_high_nrr_config = {
    'OECD90': 'N', 
    'Eastern Europe': 'N', 
    'Asia (Sans Japan)': 'Y', 
    'Middle East and Africa': 'Y', 
    'Latin America': 'N'
}
lldc_high_nrr_regions_y = dict(filter(lambda x: x[1] == 'Y', lldc_high_nrr_config.items())).keys()
lldc_high_nrr_regions_n = dict(filter(lambda x: x[1] == 'N', lldc_high_nrr_config.items())).keys()

# TABLE 1: Current TAM Mix
current_tam_mix_list = [
        ['Energy Source', '2018', 'Include in SOL?', 'Include in CONV?'],
        ['Coal', 39.28, 'N', 'Y'],
        ['Natural gas', 22.72, 'N', 'Y'],
        ['Nuclear', 10.45, 'N', 'N'],
        ['Oil', 3.41, 'N', 'Y'],
        ['Hydroelectric', 15.52, 'N', 'Y'],
        ['Solar Photovoltaic', 1.73, 'N', 'N'],
        ['Wave and Tidal', 0.00, 'N', 'N'],
        ['Wind Onshore', 4.36, 'N', 'N'],
        ['Wind Offshore', 0.24, 'N', 'N'],
        ['Biomass and Waste', 1.90, 'N', 'N'],
        ['Concentrated Solar Power', 0.05, 'N', 'N'],
        ['Geothermal', 0.34, 'N', 'N']]

class Scenario:
    name = name
    # solution_category = solution_category

    def __init__(self, scenario=None):

        # Load in population scenarios
        
        # REF1 Population
        # Population_Tables!C2:L49
        self.ref1_population = pd.read_csv(DATADIR.joinpath('ref1_population.csv'),
            index_col='Year', dtype=np.float64)
        self.ref1_population.index = self.ref1_population.index.astype(int)        

        # REF 2 Population Table
        # Population_Tables!O2:X49
        self.ref2_population = pd.read_csv(DATADIR.joinpath('ref2_population.csv'),
            index_col='Year', dtype=np.float64)
        self.ref2_population.index = self.ref2_population.index.astype(int)
        
        # Population in Countries with <0.96 gender partiy in completing upper secondary education, by IPCC Region, REF1_population_scenario (millions)
        # Population_Tables!C61:L108
        self.ref1_low_edu = pd.read_csv(DATADIR.joinpath('ref1_low_edu_gender_parity.csv'),
            index_col='Year', dtype=np.float64)
        self.ref1_low_edu.index = self.ref1_low_edu.index.astype(int)
    
        # Population in Countries with <0.96 gender partiy in completing upper secondary education, by IPCC Region, REF2_population_scenario (millions)
        # Population_Tables!O61:X108
        self.ref2_low_edu = pd.read_csv(DATADIR.joinpath('ref2_low_edu_gender_parity.csv'),
            index_col='Year', dtype=np.float64)
        self.ref2_low_edu.index = self.ref2_low_edu.index.astype(int)

        # TABLE 1: Current TAM Mix
        self.current_tam_mix = pd.DataFrame(current_tam_mix_list[1:], columns=current_tam_mix_list[1])

        # Table 2: REF2, Electricity Generation TAM (TWh)										 
        # Electricity_cluster!B26:K73
        # obj = solarpvutil.Scenario() # Not using electricity TAM output due to slight discrepancy in Asia values
        # self.ref2_tam = obj.tm.ref_tam_per_region()
        self.ref2_tam = pd.DataFrame(ref2_tam_list[1:],
            columns=ref2_tam_list[0],
            index=list(range(2014, 2061)), dtype=np.float64)
            
        # Table 3: REF1 ,Electricity Generation TAM (TWh)	
        # (a) FOR POPULATIONS IN REGIONS WITH LOW EDUCATIONAL ATTAINMENT ONLY!	
        ref1_tam_low_edu = (self.ref2_tam / self.ref2_population) * self.ref1_low_edu
        ref1_tam_low_edu.loc[:, 'Asia (Sans Japan)'] = ((self.ref2_tam.loc[:, 'Asia (Sans Japan)'] - self.ref2_tam.loc[:, 'China']) / self.ref2_population.loc[:, 'Asia (Sans Japan)']) * self.ref1_low_edu.loc[:, 'Asia (Sans Japan)']
        ref1_tam_low_edu.loc[:, 'World'] = ref1_tam_low_edu.loc[:, ref1_tam_low_edu.columns[1:6]].sum(axis=1)									
								
        # Electricity_cluster!M26:W73
        self.ref1_tam_low_edu = ref1_tam_low_edu

        # Table 3: REF1 ,Electricity Generation TAM (TWh)
        # (b) FOR REGIONS WITH HIGHER EDUCATIONAL ATTAINMENT										
        ref1_tam_high_edu = ((self.ref2_tam / self.ref2_population) * self.ref1_population) - ref1_tam_low_edu

        # Electricity_cluster!@26:AI73
        self.ref1_tam_high_edu = ref1_tam_high_edu

        # Table 3: REF1 ,Electricity Generation TAM (TWh)	
        # (c) FOR ALL REGIONS										
        ref1_tam_all_regions = ref1_tam_low_edu + ref1_tam_high_edu

        # Electricity_cluster!AL26:AU73
        self.ref1_tam_all_regions = ref1_tam_all_regions

        # Table 4: Total REF2 Electricity Generation by Economic Development Status (TWh)					
        ref2_elec_gen = pd.DataFrame(None,
                    columns=['LLDC+HighNRR', 'China', 'MDC + LAC + EE', 'Total Electricity Demand in Countries with Higher Educational Attainment (TWh)', 'Total Electricity Demand in Countries with Higher Educational Attainment (TWh) % LLDC'],
                    index=list(range(2014, 2061)), dtype=np.float64)

        ref2_elec_gen.loc[:, 'LLDC+HighNRR'] = self.ref2_tam.loc[:, lldc_high_nrr_regions_y].sum(axis=1) - self.ref2_tam.loc[:, 'China']
        ref2_elec_gen.loc[:, 'China'] = self.ref2_tam.loc[:, 'China']
        ref2_elec_gen.loc[:, 'MDC + LAC + EE'] = self.ref2_tam.loc[:, lldc_high_nrr_regions_n].sum(axis=1) 
        if lldc_high_nrr_config['Asia (Sans Japan)'] == 'N':
            ref2_elec_gen.loc[:, 'MDC + LAC + EE'] = ref2_elec_gen.loc[:, 'MDC + LAC + EE'] - self.ref2_tam.loc[:, 'China']
        ref2_elec_gen.loc[:, 'Total Electricity Demand in Countries with Higher Educational Attainment (TWh)'] = ref2_elec_gen.loc[:, ['LLDC+HighNRR', 'China', 'MDC + LAC + EE']].sum(axis=1)
        ref2_elec_gen.loc[:, 'Total Electricity Demand in Countries with Higher Educational Attainment (TWh) % LLDC'] = ref2_elec_gen.loc[:, 'LLDC+HighNRR'] / ref2_elec_gen.loc[:, 'Total Electricity Demand in Countries with Higher Educational Attainment (TWh)']

        # Electricity_cluster!B77:F124
        self.ref2_elec_gen = ref2_elec_gen

        # Table 5: Total REF1 Electricity Generation by Economic Development Status (TWh)												
        ref1_elec_gen = pd.DataFrame(None,
                    columns=['LLDC with low educational attainment, excluding China', 'MDC + EE + LAC with low educational attainment, excluding China', 'China', 'LLDC with higher educational attainment, excluding China', 'MDC + EE + LAC with higher educational attainment', 'Total Electricity Demand in Countries with Low Educational Attainment (TWh), exluding China', 'Total Electricity Demand in Countries with Low Educational Attainment (TWh), exluding China % LLDC', 'Total Electricity Demand in Countries with Higher Educational Attainment (TWh)', 'Total Electricity Demand in Countries with Higher Educational Attainment (TWh) % LLDC', 'Total Electricity Demand (TWh)', 'Total Electricity Demand (TWh) % LLDC'],
                    index=list(range(2014, 2061)), dtype=np.float64)

        ref1_elec_gen.loc[:, 'LLDC with low educational attainment, excluding China'] = ref1_tam_low_edu.loc[:, lldc_high_nrr_regions_y].sum(axis=1) - ref1_tam_low_edu.loc[:, 'China']
        ref1_elec_gen.loc[:, 'MDC + EE + LAC with low educational attainment, excluding China'] = ref1_tam_low_edu.loc[:, lldc_high_nrr_regions_n].sum(axis=1)
        if lldc_high_nrr_config['Asia (Sans Japan)'] == 'N':
            ref1_elec_gen.loc[:, 'MDC + LAC + EE'] = ref1_elec_gen.loc[:, 'MDC + LAC + EE'] - self.ref1_tam_low_edu.loc[:, 'China']
        ref1_elec_gen.loc[:, 'China'] = ref1_tam_high_edu.loc[:, 'China']

        ref1_elec_gen.loc[:, 'LLDC with higher educational attainment, excluding China'] = ref1_tam_high_edu.loc[:, lldc_high_nrr_regions_y].sum(axis=1) - ref1_tam_high_edu.loc[:, 'China']
        ref1_elec_gen.loc[:, 'MDC + EE + LAC with higher educational attainment'] = ref1_tam_high_edu.loc[:, lldc_high_nrr_regions_n].sum(axis=1)
        if lldc_high_nrr_config['Asia (Sans Japan)'] == 'N':
            ref1_elec_gen.loc[:, 'MDC + EE + LAC with higher educational attainment'] = ref1_elec_gen.loc[:, 'MDC + EE + LAC with higher educational attainment'] - self.ref1_tam_high_edu.loc[:, 'China']

        ref1_elec_gen.loc[:, 'Total Electricity Demand in Countries with Low Educational Attainment (TWh), exluding China'] = ref1_elec_gen.loc[:, 'LLDC with low educational attainment, excluding China'] + ref1_elec_gen.loc[:, 'MDC + EE + LAC with low educational attainment, excluding China']
        ref1_elec_gen.loc[:, 'Total Electricity Demand in Countries with Low Educational Attainment (TWh), exluding China % LLDC'] = ref1_elec_gen.loc[:, 'LLDC with low educational attainment, excluding China'] / ref1_elec_gen.loc[:, 'Total Electricity Demand in Countries with Low Educational Attainment (TWh), exluding China']

        ref1_elec_gen.loc[:, 'Total Electricity Demand in Countries with Higher Educational Attainment (TWh)'] = ref1_elec_gen.loc[:, 'China'] + ref1_elec_gen.loc[:, 'LLDC with higher educational attainment, excluding China'] + ref1_elec_gen.loc[:, 'MDC + EE + LAC with higher educational attainment']
        ref1_elec_gen.loc[:, 'Total Electricity Demand in Countries with Higher Educational Attainment (TWh) % LLDC'] = ref1_elec_gen.loc[:, 'LLDC with higher educational attainment, excluding China'] / ref1_elec_gen.loc[:, 'Total Electricity Demand in Countries with Higher Educational Attainment (TWh)']

        ref1_elec_gen.loc[:, 'Total Electricity Demand (TWh)'] = ref1_elec_gen.loc[:, 'Total Electricity Demand in Countries with Low Educational Attainment (TWh), exluding China'] + ref1_elec_gen.loc[:, 'Total Electricity Demand in Countries with Higher Educational Attainment (TWh)']
        ref1_elec_gen.loc[:, 'Total Electricity Demand (TWh) % LLDC'] = ref1_elec_gen.loc[:, 'Total Electricity Demand in Countries with Low Educational Attainment (TWh), exluding China'] / ref1_elec_gen.loc[:, 'Total Electricity Demand (TWh)']

        # Electricity_cluster!H77:T124
        self.ref1_elec_gen = ref1_elec_gen

        # Table 6: Change in Electricity Generation by MDC vs. LLDC Regions, REF1-REF2 (TWh)							
        change_elec_gen = pd.DataFrame(None,
                    columns=['LLDC', 'China', 'MDC + EE +LAC', 'Total change in REF1-REF2', '% LLDC with higher educational attainment', '% LLDC with Low Educational Attainment', '% LLDC', '% MDC + LAC + EE + China'],
                    index=list(range(2014, 2061)), dtype=np.float64)

        change_elec_gen.loc[:, 'LLDC'] = (ref1_elec_gen.loc[:, 'LLDC with low educational attainment, excluding China'] + ref1_elec_gen.loc[:, 'LLDC with higher educational attainment, excluding China']) - ref2_elec_gen.loc[:, 'LLDC+HighNRR']
        change_elec_gen.loc[:, 'China'] = ref1_elec_gen.loc[:, 'China'] - ref2_elec_gen.loc[:, 'China']
        change_elec_gen.loc[:, 'MDC + EE +LAC'] = (ref1_elec_gen.loc[:, 'MDC + EE + LAC with higher educational attainment'] + ref1_elec_gen.loc[:, 'MDC + EE + LAC with low educational attainment, excluding China']) - ref2_elec_gen.loc[:, 'MDC + LAC + EE']
        change_elec_gen.loc[[2014, 2015], 'MDC + EE +LAC'] = 0

        change_elec_gen.loc[:, 'Total change in REF1-REF2'] = change_elec_gen.loc[:, 'LLDC'] + change_elec_gen.loc[:, 'China'] + change_elec_gen.loc[:, 'MDC + EE +LAC']

        change_elec_gen.loc[:, '% LLDC with higher educational attainment'] = (change_elec_gen.loc[:, 'LLDC'] * (ref1_elec_gen.loc[:, 'LLDC with higher educational attainment, excluding China'] / (ref1_elec_gen.loc[:, 'LLDC with low educational attainment, excluding China'] + ref1_elec_gen.loc[:, 'LLDC with higher educational attainment, excluding China']))) / change_elec_gen.loc[:, 'Total change in REF1-REF2']

        change_elec_gen.loc[:, '% LLDC with Low Educational Attainment'] = (change_elec_gen.loc[:, 'LLDC'] / change_elec_gen.loc[:, 'Total change in REF1-REF2']) * (ref1_elec_gen.loc[:, 'LLDC with low educational attainment, excluding China'] / (ref1_elec_gen.loc[:, 'LLDC with higher educational attainment, excluding China'] + ref1_elec_gen.loc[:, 'LLDC with low educational attainment, excluding China'])) 
        change_elec_gen.loc[:, '% LLDC'] = (change_elec_gen.loc[:, 'LLDC'] / change_elec_gen.loc[:, 'Total change in REF1-REF2'])
        change_elec_gen.loc[:, '% MDC + LAC + EE + China'] = (change_elec_gen.loc[:, 'China'] + change_elec_gen.loc[:, 'MDC + EE +LAC']) / change_elec_gen.loc[:, 'Total change in REF1-REF2']

        # Electricity_cluster!W77:AD124
        self.change_elec_gen = change_elec_gen

        # Table 7: Difference in FUNCTIONAL & IMPLEMENTATION UNITS between REF1 and REF2 populations in LLDC+HighNRR+HighED	
        # CONVENTIONAL												
        addl_func_units_highed = pd.DataFrame(None,
                    columns=['Additional Functional Units in REF2 vs REF2 (TWh)', 'Annual Functional Units Increase (TWh)', 'Change in TAM (%)', 'Annual Implementation Units Increase + Replacement (TW)'],
                    index=list(range(2014, 2061)), dtype=np.float64)
        



# Table 2: REF2, Electricity Generation TAM (TWh)										
# Electricity_cluster!B26:K73
ref2_tam_list = [
        ['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)', 'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
        [22548.00000, 9630.94132, 2021.81456, 8068.09850, 1750.27240, 1681.57391, 5262.77320, 1324.87968, 3379.55071, 4226.08258],
        [23915.29474, 9686.06712, 2046.08149, 8518.24480, 1813.43945, 1729.37357, 5577.46645, 1407.75811, 3402.87973, 4238.15940],
        [24739.34640, 9726.59905, 2070.42874, 8971.48190, 1887.43392, 1782.38592, 5868.27237, 1508.56127, 3423.02929, 4238.12779],
        [25546.28067, 9770.88424, 2095.77922, 9418.25671, 1964.77842, 1837.98642, 6148.15200, 1613.15158, 3443.15125, 4240.90633],
        [26336.89072, 9818.79572, 2122.08509, 9858.95275, 2045.58829, 1896.13291, 6417.38657, 1721.48637, 3463.30080, 4246.39976],
        [27111.96969, 9870.20653, 2149.29851, 10293.95356, 2129.97886, 1956.78323, 6676.25733, 1833.52292, 3483.53313, 4254.51283],
        [27872.31074, 9924.98972, 2177.37163, 10723.64264, 2218.06547, 2019.89524, 6925.04552, 1949.21857, 3503.90343, 4265.15027],
        [28618.70702, 9983.01832, 2206.25661, 11148.40352, 2309.96345, 2085.42679, 7164.03237, 2068.53061, 3524.46690, 4278.21684],
        [29351.95169, 10044.16537, 2235.90560, 11568.61971, 2405.78813, 2153.33573, 7393.49912, 2191.41636, 3545.27873, 4293.61727],
        [30072.83791, 10108.30392, 2266.27077, 11984.67474, 2505.65485, 2223.57990, 7613.72702, 2317.83312, 3566.39411, 4311.25631],
        [30782.15882, 10175.30699, 2297.30426, 12396.95213, 2609.67894, 2296.11715, 7824.99730, 2447.73821, 3587.86825, 4331.03871],
        [31480.70758, 10245.04764, 2328.95824, 12805.83539, 2717.97573, 2370.90533, 8027.59121, 2581.08893, 3609.75633, 4352.86921],
        [32169.27735, 10317.39891, 2361.18485, 13211.70805, 2830.66056, 2447.90230, 8221.78998, 2717.84260, 3632.11354, 4376.65255],
        [32848.66128, 10392.23382, 2393.93626, 13614.95362, 2947.84876, 2527.06589, 8407.87486, 2857.95652, 3654.99508, 4402.29347],
        [33519.65253, 10469.42543, 2427.16462, 14015.95562, 3069.65567, 2608.35396, 8586.12709, 3001.38800, 3678.45614, 4429.69673],
        [34183.04424, 10548.84677, 2460.82209, 14415.09758, 3196.19661, 2691.72436, 8756.82789, 3148.09436, 3702.55192, 4458.76706],
        [34839.62958, 10630.37088, 2494.86082, 14812.76302, 3327.58693, 2777.13494, 8920.25852, 3298.03290, 3727.33762, 4489.40921],
        [35490.20169, 10713.87080, 2529.23298, 15209.33545, 3463.94195, 2864.54354, 9076.70022, 3451.16094, 3752.86841, 4521.52793],
        [36135.55373, 10799.21958, 2563.89071, 15605.19839, 3605.37701, 2953.90802, 9226.43422, 3607.43578, 3779.19950, 4555.02795],
        [36776.47886, 10886.29024, 2598.78617, 16000.73536, 3752.00744, 3045.18622, 9369.74177, 3766.81473, 3806.38608, 4589.81402],
        [37413.77023, 10974.95584, 2633.87152, 16396.32989, 3903.94858, 3138.33599, 9506.90409, 3929.25510, 3834.48334, 4625.79089],
        [38048.22099, 11065.08941, 2669.09891, 16792.36549, 4061.31575, 3233.31518, 9638.20245, 4094.71421, 3863.54649, 4662.86330],
        [38680.62430, 11156.56399, 2704.42051, 17189.22569, 4224.22430, 3330.08164, 9763.91807, 4263.14936, 3893.63070, 4700.93599],
        [39311.77332, 11249.25262, 2739.78846, 17587.29399, 4392.78956, 3428.59321, 9884.33219, 4434.51785, 3924.79118, 4739.91371],
        [39942.46119, 11343.02835, 2775.15493, 17986.95393, 4567.12685, 3528.80776, 9999.72605, 4608.77701, 3957.08311, 4779.70121],
        [40573.48107, 11437.76420, 2810.47206, 18388.58902, 4747.35152, 3630.68312, 10110.38090, 4785.88414, 3990.56170, 4820.20321],
        [41205.62612, 11533.33323, 2845.69203, 18792.58278, 4933.57890, 3734.17715, 10216.57798, 4965.79655, 4025.28213, 4861.32448],
        [41839.68949, 11629.60846, 2880.76697, 19199.31873, 5125.92432, 3839.24769, 10318.59852, 5148.47155, 4061.29960, 4902.96975],
        [42476.46433, 11726.46295, 2915.64905, 19609.18039, 5324.50311, 3945.85259, 10416.72376, 5333.86645, 4098.66931, 4945.04377],
        [43116.74380, 11823.76973, 2950.29042, 20022.55128, 5529.43060, 4053.94970, 10511.23495, 5521.93856, 4137.44643, 4987.45129],
        [43761.32106, 11921.40184, 2984.64325, 20439.81493, 5740.82214, 4163.49688, 10602.41332, 5712.64519, 4177.68618, 5030.09703],
        [44410.98925, 12019.23231, 3018.65968, 20861.35484, 5958.79306, 4274.45196, 10690.54011, 5905.94365, 4219.44374, 5072.88576],
        [45066.54153, 12117.13420, 3052.29187, 21287.55454, 6183.45868, 4386.77280, 10775.89657, 6101.79125, 4262.77431, 5115.72222],
        [45728.77106, 12214.98054, 3085.49198, 21718.79755, 6414.93434, 4500.41725, 10858.76393, 6300.14529, 4307.73308, 5158.51114],
        [46398.47098, 12312.64437, 3118.21217, 22155.46740, 6653.33538, 4615.34315, 10939.42343, 6500.96309, 4354.37524, 5201.15727],
        [47076.43447, 12409.99873, 3150.40458, 22597.94759, 6898.77713, 4731.50836, 11018.15632, 6704.20196, 4402.75599, 5243.56536],
        [47763.45466, 12506.91666, 3182.02139, 23046.62165, 7151.37491, 4848.87072, 11095.24383, 6909.81921, 4452.93051, 5285.64015],
        [48460.32471, 12603.27120, 3213.01473, 23501.87309, 7411.24408, 4967.38809, 11170.96721, 7117.77215, 4504.95402, 5327.28639],
        [49167.83778, 12698.93539, 3243.33678, 23964.08545, 7678.49995, 5087.01830, 11245.60769, 7328.01808, 4558.88169, 5368.40881],
        [49886.78702, 12793.78227, 3272.93968, 24433.64223, 7953.25787, 5207.71922, 11319.44651, 7540.51431, 4614.76872, 5408.91217],
        [50617.96559, 12887.68488, 3301.77559, 24910.92696, 8235.63316, 5329.44868, 11392.76492, 7755.21817, 4672.67030, 5448.70121],
        [51362.16663, 12980.51625, 3329.79667, 25396.32316, 8525.74117, 5452.16454, 11465.84415, 7972.08695, 4732.64164, 5487.68066],
        [52120.18332, 13072.14944, 3356.95508, 25890.21435, 8823.69721, 5575.82465, 11538.96544, 8191.07796, 4794.73791, 5525.75528],
        [52892.80878, 13162.45748, 3383.20296, 26392.98404, 9129.61663, 5700.38686, 11612.41004, 8412.14852, 4859.01432, 5562.82981],
        [53680.83620, 13251.31340, 3408.49248, 26905.01576, 9443.61477, 5825.80901, 11686.45918, 8635.25594, 4925.52606, 5598.80900],
        [54485.05871, 13338.59025, 3432.77580, 27426.69302, 9765.80695, 5952.04895, 11761.39410, 8860.35752, 4994.32832, 5633.59758],
        [55306.26947, 13424.16108, 3456.00506, 27958.39935, 10096.30850, 6079.06453, 11837.49604, 9087.41057, 5065.47630, 5667.10030]]


