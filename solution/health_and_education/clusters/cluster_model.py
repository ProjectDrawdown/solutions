import pandas as pd
import numpy as np
import pathlib
import sys
__file__ = 'c:\\Users\\sunishchal.dev\\Documents\\solutions\\solution\\health_and_education\\clusters'
repo_path = str(pathlib.Path(__file__).parents[2])
sys.path.append(repo_path)
from model import dd
from model import advanced_controls as ac
from model import emissionsfactors as ef

class Scenario():
    # solution_category = solution_category

    def __init__(self, name, assumptions, scenario=None):
        self.name = name
        self.assumptions = assumptions
        self.period_start = assumptions['period_start']
        self.period_end = assumptions['period_end']

    # Load in population scenarios   
    def load_pop_data(self, DATADIR):
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


    def load_tam_mix(self, current_tam_mix_list):
        # TABLE 1: Current TAM Mix
        self.current_tam_mix = pd.DataFrame(current_tam_mix_list[1:], columns=current_tam_mix_list[0])
        self.conv_weight_sum = self.current_tam_mix.loc[self.current_tam_mix['Include in CONV?'] == 'Y', 'Weighting Factor'].sum()


    def load_ref2_tam(self, ref2_tam_list):
        # Table 2: REF2 TAM							
        # obj = solarpvutil.Scenario() # Not using electricity TAM output due to slight discrepancy in Asia values
        # self.ref2_tam = obj.tm.ref_tam_per_region()
        self.ref2_tam = pd.DataFrame(ref2_tam_list[1:],
            columns=ref2_tam_list[0],
            index=list(range(2014, 2061)), dtype=np.float64)
    

    def calc_ref1_tam(self):
        # Table 3: REF1 TAM FOR POPULATIONS IN REGIONS WITH LOW EDUCATIONAL ATTAINMENT ONLY
        ref1_tam_low_edu = (self.ref2_tam / self.ref2_population) * self.ref1_low_edu
        ref1_tam_low_edu.loc[:, 'Asia (Sans Japan)'] = ((self.ref2_tam.loc[:, 'Asia (Sans Japan)'] - self.ref2_tam.loc[:, 'China']) \
            / self.ref2_population.loc[:, 'Asia (Sans Japan)']) * self.ref1_low_edu.loc[:, 'Asia (Sans Japan)']
        ref1_tam_low_edu.loc[:, 'World'] = ref1_tam_low_edu.loc[:, ref1_tam_low_edu.columns[1:6]].sum(axis=1)									
								
        self.ref1_tam_low_edu = ref1_tam_low_edu

        # Table 3: REF1 TAM FOR REGIONS WITH HIGHER EDUCATIONAL ATTAINMENT										
        ref1_tam_high_edu = ((self.ref2_tam / self.ref2_population) * self.ref1_population) - ref1_tam_low_edu

        self.ref1_tam_high_edu = ref1_tam_high_edu

        # Table 3: REF1 TAM FOR ALL REGIONS										
        ref1_tam_all_regions = ref1_tam_low_edu + ref1_tam_high_edu

        # SpaceHeating_cluster!AL28:AU75
        self.ref1_tam_all_regions = ref1_tam_all_regions


    def calc_ref2_demand(self):
        # Table 4: Total REF2 Demand by Economic Development Status					
        ref2_demand = pd.DataFrame(None,
            columns=['LLDC+HighNRR', 'China', 'MDC + LAC + EE', 'Demand in Countries with Higher Educational Attainment', 'Demand in Countries with Higher Educational Attainment % LLDC'],
            index=list(range(2014, 2061)), dtype=np.float64) # TODO: remove hard coded year indices

        ref2_demand.loc[:, 'LLDC+HighNRR'] = self.ref2_tam.loc[:, dd.LLDC_HIGH_NRR_REGION_Y].sum(axis=1) - self.ref2_tam.loc[:, 'China']
        ref2_demand.loc[:, 'China'] = self.ref2_tam.loc[:, 'China']
        ref2_demand.loc[:, 'MDC + LAC + EE'] = self.ref2_tam.loc[:, dd.LLDC_HIGH_NRR_REGION_N].sum(axis=1) 
        if dd.LLDC_HIGH_NRR_CONFIG['Asia (Sans Japan)'] == 'N':
            ref2_demand.loc[:, 'MDC + LAC + EE'] = ref2_demand.loc[:, 'MDC + LAC + EE'] - self.ref2_tam.loc[:, 'China']
        ref2_demand.loc[:, 'Demand in Countries with Higher Educational Attainment'] = ref2_demand.loc[:, ['LLDC+HighNRR', 'China', 'MDC + LAC + EE']].sum(axis=1)
        ref2_demand.loc[:, 'Demand in Countries with Higher Educational Attainment % LLDC'] = ref2_demand.loc[:, 'LLDC+HighNRR'] \
            / ref2_demand.loc[:, 'Demand in Countries with Higher Educational Attainment']

        # SpaceHeating_cluster!B77:F124
        self.ref2_demand = ref2_demand


    def calc_ref1_demand(self):
        # Table 5: Total REF1 Demand by Economic Development Status												
        ref1_demand = pd.DataFrame(None,
            columns=['LLDC with low educational attainment, excluding China', 'MDC + EE + LAC with low educational attainment, excluding China', 'China', 
                'LLDC with higher educational attainment, excluding China', 'MDC + EE + LAC with higher educational attainment', 
                'Demand in Countries with Low Educational Attainment, exluding China', 'Demand in Countries with Low Educational Attainment, exluding China % LLDC', 
                'Demand in Countries with Higher Educational Attainment', 'Demand in Countries with Higher Educational Attainment % LLDC', 'Demand', 'Demand % LLDC'],
            index=list(range(2014, 2061)), dtype=np.float64)

        ref1_demand.loc[:, 'LLDC with low educational attainment, excluding China'] = self.ref1_tam_low_edu.loc[:, dd.LLDC_HIGH_NRR_REGION_Y].sum(axis=1) - self.ref1_tam_low_edu.loc[:, 'China']
        ref1_demand.loc[:, 'MDC + EE + LAC with low educational attainment, excluding China'] = self.ref1_tam_low_edu.loc[:, dd.LLDC_HIGH_NRR_REGION_N].sum(axis=1)
        if dd.LLDC_HIGH_NRR_CONFIG['Asia (Sans Japan)'] == 'N':
            ref1_demand.loc[:, 'MDC + LAC + EE'] = ref1_demand.loc[:, 'MDC + LAC + EE'] - self.ref1_tam_low_edu.loc[:, 'China']
        ref1_demand.loc[:, 'China'] = self.ref1_tam_high_edu.loc[:, 'China']

        ref1_demand.loc[:, 'LLDC with higher educational attainment, excluding China'] = self.ref1_tam_high_edu.loc[:, dd.LLDC_HIGH_NRR_REGION_Y].sum(axis=1) \
            - self.ref1_tam_high_edu.loc[:, 'China']
        ref1_demand.loc[:, 'MDC + EE + LAC with higher educational attainment'] = self.ref1_tam_high_edu.loc[:, dd.LLDC_HIGH_NRR_REGION_N].sum(axis=1)
        if dd.LLDC_HIGH_NRR_CONFIG['Asia (Sans Japan)'] == 'N':
            ref1_demand.loc[:, 'MDC + EE + LAC with higher educational attainment'] = ref1_demand.loc[:, 'MDC + EE + LAC with higher educational attainment'] \
                - self.ref1_tam_high_edu.loc[:, 'China']

        ref1_demand.loc[:, 'Demand in Countries with Low Educational Attainment, exluding China'] = ref1_demand.loc[:, 'LLDC with low educational attainment, excluding China'] \
            + ref1_demand.loc[:, 'MDC + EE + LAC with low educational attainment, excluding China']
        ref1_demand.loc[:, 'Demand in Countries with Low Educational Attainment, exluding China % LLDC'] = ref1_demand.loc[:, 'LLDC with low educational attainment, excluding China'] \
            / ref1_demand.loc[:, 'Demand in Countries with Low Educational Attainment, exluding China']

        ref1_demand.loc[:, 'Demand in Countries with Higher Educational Attainment'] = ref1_demand.loc[:, 'China'] \
            + ref1_demand.loc[:, 'LLDC with higher educational attainment, excluding China'] \
            + ref1_demand.loc[:, 'MDC + EE + LAC with higher educational attainment']
        ref1_demand.loc[:, 'Demand in Countries with Higher Educational Attainment % LLDC'] = ref1_demand.loc[:, 'LLDC with higher educational attainment, excluding China'] \
            / ref1_demand.loc[:, 'Demand in Countries with Higher Educational Attainment']

        ref1_demand.loc[:, 'Demand'] = ref1_demand.loc[:, 'Demand in Countries with Low Educational Attainment, exluding China'] \
            + ref1_demand.loc[:, 'Demand in Countries with Higher Educational Attainment']
        ref1_demand.loc[:, 'Demand % LLDC'] = ref1_demand.loc[:, 'Demand in Countries with Low Educational Attainment, exluding China'] / ref1_demand.loc[:, 'Demand']

        # SpaceHeating_cluster!H77:T124
        self.ref1_demand = ref1_demand


    def calc_change_demand(self):
        # Table 6: Change in Demand by MDC vs. LLDC Regions, REF1-REF2							
        change_demand = pd.DataFrame(None,
            columns=['LLDC', 'China', 'MDC + EE +LAC', 'Total change in REF1-REF2', '% LLDC with higher educational attainment', 
                '% LLDC with Low Educational Attainment', '% LLDC', '% MDC + LAC + EE + China'],
            index=list(range(2014, 2061)), dtype=np.float64)

        change_demand.loc[:, 'LLDC'] = (self.ref1_demand.loc[:, 'LLDC with low educational attainment, excluding China'] \
            + self.ref1_demand.loc[:, 'LLDC with higher educational attainment, excluding China']) - self.ref2_demand.loc[:, 'LLDC+HighNRR']

        change_demand.loc[:, 'China'] = self.ref1_demand.loc[:, 'China'] - self.ref2_demand.loc[:, 'China']
        change_demand.loc[:, 'MDC + EE +LAC'] = (self.ref1_demand.loc[:, 'MDC + EE + LAC with higher educational attainment'] \
            + self.ref1_demand.loc[:, 'MDC + EE + LAC with low educational attainment, excluding China']) - self.ref2_demand.loc[:, 'MDC + LAC + EE']

        change_demand.loc[:, 'Total change in REF1-REF2'] = change_demand.loc[:, 'LLDC'] + change_demand.loc[:, 'China'] + change_demand.loc[:, 'MDC + EE +LAC']

        change_demand.loc[:, '% LLDC with higher educational attainment'] = (change_demand.loc[:, 'LLDC'] \
            * (self.ref1_demand.loc[:, 'LLDC with higher educational attainment, excluding China'] \
                / (self.ref1_demand.loc[:, 'LLDC with low educational attainment, excluding China'] \
                + self.ref1_demand.loc[:, 'LLDC with higher educational attainment, excluding China']))) \
            / change_demand.loc[:, 'Total change in REF1-REF2']

        change_demand.loc[:, '% LLDC with Low Educational Attainment'] = (change_demand.loc[:, 'LLDC'] / change_demand.loc[:, 'Total change in REF1-REF2']) \
            * (self.ref1_demand.loc[:, 'LLDC with low educational attainment, excluding China'] \
                / (self.ref1_demand.loc[:, 'LLDC with higher educational attainment, excluding China'] \
                + self.ref1_demand.loc[:, 'LLDC with low educational attainment, excluding China'])) 

        change_demand.loc[:, '% LLDC'] = (change_demand.loc[:, 'LLDC'] / change_demand.loc[:, 'Total change in REF1-REF2'])
        change_demand.loc[:, '% MDC + LAC + EE + China'] = (change_demand.loc[:, 'China'] + change_demand.loc[:, 'MDC + EE +LAC']) \
            / change_demand.loc[:, 'Total change in REF1-REF2']
        change_demand = change_demand.fillna(0).replace((-np.inf, np.inf), np.nan)
        
        # Force valuesin order to pass test against Excel, which seems to have been zerod out manually for the first 2 rows
        change_demand.iloc[0:2, :] = 0

        # SpaceHeating_cluster!W77:AD124
        self.change_demand = change_demand


    def calc_addl_units_highed(self):
        # Table 7: Difference in FUNCTIONAL & IMPLEMENTATION UNITS between REF1 and REF2 populations in LLDC+HighNRR+HighED	
        # CONVENTIONAL								
        addl_func_units_highed = pd.DataFrame(None,
            columns=['Additional Functional Units in REF2 vs REF2', 'Annual Functional Units Increase', 'Change in TAM'],
            index=list(range(2014, 2061)), dtype=np.float64)

        if self.assumptions['use_fixed_weight'] == 'N':
            conv_weight_factor = self.change_demand.loc[:, '% LLDC with higher educational attainment']
        elif self.assumptions['use_fixed_weight'] == 'Y':
            conv_weight_factor = self.assumptions['fixed_weighting_factor']
        else:
            raise Exception('Invalid value passed for "use_fixed_weight", please use Y or N')
        
        addl_func_units_highed.loc[:, 'Additional Functional Units in REF2 vs REF2'] = conv_weight_factor * (self.conv_weight_sum \
             * ((self.ref1_tam_high_edu['World'] + self.ref1_tam_low_edu['World']) - self.ref2_tam['World']))
        addl_func_units_highed.loc[:, 'Annual Functional Units Increase'] = addl_func_units_highed['Additional Functional Units in REF2 vs REF2'].diff()
        addl_func_units_highed.loc[2016, 'Annual Functional Units Increase'] = addl_func_units_highed.loc[2016, 'Additional Functional Units in REF2 vs REF2'] 
        addl_func_units_highed.loc[:, 'Change in TAM'] = addl_func_units_highed['Additional Functional Units in REF2 vs REF2'] \
             / ((self.ref1_tam_high_edu['World'] + self.ref1_tam_low_edu['World']) - self.ref2_tam['World'])

        # Convert to TWh
        addl_func_units_highed = addl_func_units_highed / 100

        # SpaceHeating_cluster!E131:G179
        self.addl_func_units_highed = addl_func_units_highed


    def calc_addl_units_lowed(self):
        # Table 8: Difference in FUNCTIONAL & IMPLEMENTATION UNITS between REF1 and REF2 populations in LLDC+HighNRR+LowED
        # CONVENTIONAL									
        addl_func_units_lowed = pd.DataFrame(None,
            columns=['Additional Functional Units in REF2 vs REF2', 'Annual Functional Units Increase', 'Change in TAM'],
            index=list(range(2014, 2061)), dtype=np.float64)
                    
        if self.assumptions['use_fixed_weight'] == 'N':
            conv_weight_factor = self.change_demand.loc[:, '% LLDC with Low Educational Attainment']
        elif self.assumptions['use_fixed_weight'] == 'Y':
            conv_weight_factor = self.assumptions['fixed_weighting_factor']
        else:
            raise Exception('Invalid value passed for "use_fixed_weight", please use Y or N')

        addl_func_units_lowed.loc[:, 'Additional Functional Units in REF2 vs REF2'] = conv_weight_factor * (self.conv_weight_sum \
             * ((self.ref1_tam_high_edu['World'] + self.ref1_tam_low_edu['World']) - self.ref2_tam['World']))
        addl_func_units_lowed.loc[:, 'Annual Functional Units Increase'] = addl_func_units_lowed['Additional Functional Units in REF2 vs REF2'].diff()
        addl_func_units_lowed.loc[2016, 'Annual Functional Units Increase'] = addl_func_units_lowed.loc[2016, 'Additional Functional Units in REF2 vs REF2'] 
        addl_func_units_lowed.loc[:, 'Change in TAM'] = addl_func_units_lowed['Additional Functional Units in REF2 vs REF2'] \
             / ((self.ref1_tam_high_edu['World'] + self.ref1_tam_low_edu['World']) - self.ref2_tam['World'])

        # Convert to TWh
        addl_func_units_lowed = addl_func_units_lowed / 100

        # SpaceHeating_cluster!M131:O179
        self.addl_func_units_lowed = addl_func_units_lowed


    def calc_emis_diff_highed(self, ef_co2_eq_list):
        # Table 9: Difference in EMISSIONS between REF1 and REF2 populations in LLDC+HighNRR+HighED
        # CONVENTIONAL Avoided Emissions/ Million Metric Tons CO2
        # emissions_factors_ref1_co2eq = ef.ElectricityGenOnGrid(ac.AdvancedControls()).conv_ref_grid_CO2eq_per_KWh()
        self.emissions_factors_ref1_co2eq = pd.DataFrame(ef_co2_eq_list[1:],
            columns=ef_co2_eq_list[0],
            index=list(range(2014, 2061)), dtype=np.float64)

        emis_diff_highed = pd.DataFrame(None,
            columns=['Conventional: Grid','Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect', 'Emission Reductions: Conv Total'],
            index=list(range(2014, 2061)), dtype=np.float64)

        emis_diff_highed['Conventional: Grid'] = self.addl_func_units_highed['Additional Functional Units in REF2 vs REF2'] * self.emissions_factors_ref1_co2eq['World']
        emis_diff_highed['Emission Reductions: Conv Total'] = emis_diff_highed[['Conventional: Grid', 'Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect']].sum(axis=1, min_count=1)
        
        # SpaceHeating_cluster!V131:Z179
        self.emis_diff_highed = emis_diff_highed


    def calc_emis_diff_highed_spaceheating(self, ef_co2_eq_list):
        self.emissions_factors_ref1_co2eq = pd.DataFrame(ef_co2_eq_list[1:],
            columns=ef_co2_eq_list[0],
            index=list(range(2014, 2061)), dtype=np.float64)

        emis_diff_highed = pd.DataFrame(None,
            columns=['Conventional: Grid','Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect', 'Emission Reductions: Conv Total'],
            index=list(range(2014, 2061)), dtype=np.float64)
        
        if self.assumptions['Grid'] == 'Y':
            emis_diff_highed['Conventional: Grid'] = self.addl_func_units_highed['Additional Functional Units in REF2 vs REF2'] \
                * (self.current_tam_mix.loc[self.current_tam_mix['Energy Source'] == 'Electricity (Heating & Cooling)', 'Weighting Factor'].values[0] / self.conv_weight_sum) \
                * self.assumptions['Twh_per_TWh'] * self.emissions_factors_ref1_co2eq['World']
        
        if self.assumptions['Fuel'] == 'Y':
            emis_diff_highed['Conventional: Fuel'] = self.addl_func_units_highed['Additional Functional Units in REF2 vs REF2'] \
                * (self.current_tam_mix.loc[self.current_tam_mix['Energy Source'].isin(['Coal', 'Oil Products', 'Natural Gas', 'Biomass, waste and other renewables']), 'Weighting Factor'].sum() \
                    / self.conv_weight_sum) \
                * (self.assumptions['Weighted Emission Factor for Space Heating and Cooling'] * self.assumptions['TJ_per_TWh']) / 10**6
        
        emis_diff_highed['Emission Reductions: Conv Total'] = emis_diff_highed[['Conventional: Grid', 'Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect']].sum(axis=1, min_count=1)
        
        # SpaceHeating_cluster!V131:Z179
        self.emis_diff_highed = emis_diff_highed


    def calc_emis_diff_highed_spacecooling(self, ef_co2_eq_list):
        self.emissions_factors_ref1_co2eq = pd.DataFrame(ef_co2_eq_list[1:],
            columns=ef_co2_eq_list[0],
            index=list(range(2014, 2061)), dtype=np.float64)

        emis_diff_highed = pd.DataFrame(None,
            columns=['Conventional: Grid','Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect', 'Emission Reductions: Conv Total'],
            index=list(range(2014, 2061)), dtype=np.float64)
        
        if self.assumptions['Grid'] == 'Y':
            emis_diff_highed['Conventional: Grid'] = self.addl_func_units_highed['Additional Functional Units in REF2 vs REF2'] \
                * self.current_tam_mix.loc[self.current_tam_mix['Energy Source'] == 'Electricity', 'Weighting Factor'].values[0] \
                * self.assumptions['Twh_per_TWh'] * self.emissions_factors_ref1_co2eq['World'] / 100
        
        emis_diff_highed['Emission Reductions: Conv Total'] = emis_diff_highed[['Conventional: Grid', 'Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect']].sum(axis=1, min_count=1)
        
        # SpaceHeating_cluster!V131:Z179
        self.emis_diff_highed = emis_diff_highed


    def calc_emis_diff_highed_cleancookstoves(self):
        emis_diff_highed = pd.DataFrame(None,
            columns=['Conventional: Grid','Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect', 'Emission Reductions: Conv Total'],
            index=list(range(2014, 2061)), dtype=np.float64)
        
        if self.assumptions['Fuel'] == 'Y':
            emis_diff_highed['Conventional: Fuel'] = self.addl_func_units_highed['Additional Functional Units in REF2 vs REF2'] \
                * (self.assumptions['CO2-eq Emissions for Solid Biofuels'] * self.assumptions['TJ_per_TWh']) / 10**6
        
        emis_diff_highed['Emission Reductions: Conv Total'] = emis_diff_highed[['Conventional: Grid', 'Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect']].sum(axis=1, min_count=1)
        
        # SpaceHeating_cluster!V131:Z179
        self.emis_diff_highed = emis_diff_highed


    def calc_emis_diff_lowed(self):
        # Table 10: Difference in EMISSIONS between REF1 and REF2 populations in LLDC+HighNRR+LowED
        # CONVENTIONAL  - Least and Less Developed Countries (sans LAC, EE, China)	
        emis_diff_lowed = pd.DataFrame(None,
            columns=['Conventional: Grid','Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect', 'Emission Reductions: Conv Total'],
            index=list(range(2014, 2061)), dtype=np.float64)

        emis_diff_lowed['Conventional: Grid'] = self.addl_func_units_lowed['Additional Functional Units in REF2 vs REF2'] * self.emissions_factors_ref1_co2eq['World']
        emis_diff_lowed['Emission Reductions: Conv Total'] = emis_diff_lowed[['Conventional: Grid', 'Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect']].sum(axis=1, min_count=1)
        
        # SpaceHeating_cluster!AI131:AM179
        self.emis_diff_lowed = emis_diff_lowed
        

    def calc_emis_diff_lowed_spaceheating(self):
        emis_diff_lowed = pd.DataFrame(None,
            columns=['Conventional: Grid','Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect', 'Emission Reductions: Conv Total'],
            index=list(range(2014, 2061)), dtype=np.float64)

        if self.assumptions['Grid'] == 'Y':
            emis_diff_lowed['Conventional: Grid'] = self.addl_func_units_lowed['Additional Functional Units in REF2 vs REF2'] \
                * (self.current_tam_mix.loc[self.current_tam_mix['Energy Source'] == 'Electricity (Heating & Cooling)', 'Weighting Factor'].values[0] / self.conv_weight_sum) \
                * self.assumptions['Twh_per_TWh'] *  self.emissions_factors_ref1_co2eq['World']

        if self.assumptions['Fuel'] == 'Y':
            emis_diff_lowed['Conventional: Fuel'] = self.addl_func_units_lowed['Additional Functional Units in REF2 vs REF2'] \
                * (self.current_tam_mix.loc[self.current_tam_mix['Energy Source'].isin(['Coal', 'Oil Products', 'Natural Gas', 'Biomass, waste and other renewables']), 'Weighting Factor'].sum() / self.conv_weight_sum) \
                * (self.assumptions['Weighted Emission Factor for Space Heating and Cooling'] * self.assumptions['TJ_per_TWh']) / 10**6

        emis_diff_lowed['Emission Reductions: Conv Total'] = emis_diff_lowed[['Conventional: Grid', 'Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect']].sum(axis=1, min_count=1)
        
        # SpaceHeating_cluster!AI131:AM179
        self.emis_diff_lowed = emis_diff_lowed
        

    def calc_emis_diff_lowed_spacecooling(self):	
        emis_diff_lowed = pd.DataFrame(None,
            columns=['Conventional: Grid','Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect', 'Emission Reductions: Conv Total'],
            index=list(range(2014, 2061)), dtype=np.float64)

        if self.assumptions['Grid'] == 'Y':
            emis_diff_lowed['Conventional: Grid'] = self.addl_func_units_lowed['Additional Functional Units in REF2 vs REF2'] \
                * self.current_tam_mix.loc[self.current_tam_mix['Energy Source'] == 'Electricity', 'Weighting Factor'].values[0] \
                * self.assumptions['Twh_per_TWh'] *  self.emissions_factors_ref1_co2eq['World'] / 100

        emis_diff_lowed['Emission Reductions: Conv Total'] = emis_diff_lowed[['Conventional: Grid', 'Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect']].sum(axis=1, min_count=1)
        
        self.emis_diff_lowed = emis_diff_lowed
        

    def calc_emis_diff_lowed_cleancookstoves(self):
        emis_diff_lowed = pd.DataFrame(None,
            columns=['Conventional: Grid','Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect', 'Emission Reductions: Conv Total'],
            index=list(range(2014, 2061)), dtype=np.float64)

        if self.assumptions['Fuel'] == 'Y':
            emis_diff_lowed['Conventional: Fuel'] = self.addl_func_units_lowed['Additional Functional Units in REF2 vs REF2'] \
                * (self.assumptions['CO2-eq Emissions for Solid Biofuels'] * self.assumptions['TJ_per_TWh']) / 10**6

        emis_diff_lowed['Emission Reductions: Conv Total'] = emis_diff_lowed[['Conventional: Grid', 'Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect']].sum(axis=1, min_count=1)
        
        self.emis_diff_lowed = emis_diff_lowed

        
    def calc_emis_alloc_lldc(self):
        # Table 11: EMISSIONS ALLOCATIONS TO (a) Health & Education; (b) Education ONLY; (c) Family Planning (excluding education)
        # Least and less developed countries
        emissions_allocations_lldc = pd.DataFrame(None,
            columns=['Health & Education: Conv Total', 'Health & Education: Solution Total', 'Education: Conv Total', 'Education: Solution Total', 'Family Planning: Conv Total', 'Family Planning: Solution Total', '% Allocation to Education: Conv Total', '% Allocation to Education: Solution Total'],
            index=list(range(2014, 2061)), dtype=np.float64)

        emissions_allocations_lldc['Health & Education: Conv Total'] = self.emis_diff_lowed['Emission Reductions: Conv Total'] + self.emis_diff_highed['Emission Reductions: Conv Total']
        emissions_allocations_lldc['Health & Education: Conv Total'] = emissions_allocations_lldc['Health & Education: Conv Total'].fillna(0.0)
        emissions_allocations_lldc['Health & Education: Solution Total'] = 0.0
        emissions_allocations_lldc['Education: Conv Total'] = self.emis_diff_lowed['Emission Reductions: Conv Total'] * self.assumptions['pct_impact']
        emissions_allocations_lldc['Education: Conv Total'] = emissions_allocations_lldc['Education: Conv Total'].fillna(0.0)
        emissions_allocations_lldc['Education: Solution Total'] = 0.0
        emissions_allocations_lldc['Family Planning: Conv Total'] = emissions_allocations_lldc['Health & Education: Conv Total'] - emissions_allocations_lldc['Education: Conv Total']
        emissions_allocations_lldc['Family Planning: Conv Total'] = emissions_allocations_lldc['Family Planning: Conv Total'].fillna(0.0)
        emissions_allocations_lldc['Family Planning: Solution Total'] = 0.0
        emissions_allocations_lldc['% Allocation to Education: Conv Total'] = emissions_allocations_lldc['Education: Conv Total'] / emissions_allocations_lldc['Health & Education: Conv Total']
        # emissions_allocations_lldc['% Allocation to Education: Conv Total'] = emissions_allocations_lldc['% Allocation to Education: Conv Total'].round(2)
        emissions_allocations_lldc['% Allocation to Education: Solution Total'] = np.nan

        # SpaceHeating_cluster!AR131:BD179
        self.emissions_allocations_lldc = emissions_allocations_lldc
        

    def calc_addl_units_mdc(self):
        # Table 12: Difference in FUNCTIONAL & IMPLEMENTATION UNITS between REF1 and REF2 populations in MDC + LAC + EE + China
        # CONVENTIONAL Avoided Emissions/ Million Metric Tons CO2									
        addl_func_units_mdc = pd.DataFrame(None,
            columns=['Additional Functional Units in REF2 vs REF2', 'Annual Functional Units Increase', 'Change in TAM'],
            index=list(range(2014, 2061)), dtype=np.float64)

        if self.assumptions['use_fixed_weight'] == 'N':
            conv_weight_factor = self.change_demand.loc[:, '% MDC + LAC + EE + China']
        elif self.assumptions['use_fixed_weight'] == 'Y':
            conv_weight_factor = self.assumptions['fixed_weighting_factor']
        else:
            raise Exception('Invalid value passed for "use_fixed_weight", please use Y or N')

        conv_weight_sum = self.current_tam_mix.loc[self.current_tam_mix['Include in CONV?'] == 'Y', 'Weighting Factor'].sum()
        
        addl_func_units_mdc.loc[:, 'Additional Functional Units in REF2 vs REF2'] = conv_weight_factor * (conv_weight_sum \
             * (self.ref1_tam_all_regions['World']  - self.ref2_tam['World']))
        addl_func_units_mdc.loc[:, 'Annual Functional Units Increase'] = addl_func_units_mdc['Additional Functional Units in REF2 vs REF2'].diff()
        addl_func_units_mdc.loc[2016, 'Annual Functional Units Increase'] = addl_func_units_mdc.loc[2016, 'Additional Functional Units in REF2 vs REF2'] 
        addl_func_units_mdc.loc[:, 'Change in TAM'] = addl_func_units_mdc['Additional Functional Units in REF2 vs REF2'] \
             / (self.ref1_tam_all_regions['World'] - self.ref2_tam['World'])

        # Convert to TWh
        addl_func_units_mdc = addl_func_units_mdc / 100

        # SpaceHeating_cluster!E190:G238
        self.addl_func_units_mdc = addl_func_units_mdc


    def calc_emis_diff_mdc(self):
        # Table 13: Difference in EMISSIONS between REF1 and REF2 populations in MDC + LAC + EE + China
        # CONVENTIONAL Avoided Emissions/ Million Metric Tons CO2
        emis_diff_mdc = pd.DataFrame(None,
            columns=['Conventional: Grid','Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect', 'Emission Reductions: Conv Total'],
            index=list(range(2014, 2061)), dtype=np.float64)

        emis_diff_mdc['Conventional: Grid'] = self.addl_func_units_mdc['Additional Functional Units in REF2 vs REF2'] * self.emissions_factors_ref1_co2eq['World']
        emis_diff_mdc['Emission Reductions: Conv Total'] = emis_diff_mdc[['Conventional: Grid', 'Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect']].sum(axis=1, min_count=1)
        
        # SpaceHeating_cluster!O190:S238
        self.emis_diff_mdc = emis_diff_mdc


    def calc_emis_diff_mdc_spaceheating(self):
        # Table 13: Difference in EMISSIONS between REF1 and REF2 populations in MDC + LAC + EE + China
        # CONVENTIONAL Avoided Emissions/ Million Metric Tons CO2
        emis_diff_mdc = pd.DataFrame(None,
            columns=['Conventional: Grid','Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect', 'Emission Reductions: Conv Total'],
            index=list(range(2014, 2061)), dtype=np.float64)

        if self.assumptions['Grid'] == 'Y':
            emis_diff_mdc['Conventional: Grid'] = self.addl_func_units_mdc['Additional Functional Units in REF2 vs REF2'] \
                * (self.current_tam_mix.loc[self.current_tam_mix['Energy Source'] == 'Electricity (Heating & Cooling)', 'Weighting Factor'].values[0] / self.conv_weight_sum) \
                * self.assumptions['Twh_per_TWh'] *  self.emissions_factors_ref1_co2eq['World']

        if self.assumptions['Fuel'] == 'Y':
            emis_diff_mdc['Conventional: Fuel'] = self.addl_func_units_mdc['Additional Functional Units in REF2 vs REF2'] \
                * (self.current_tam_mix.loc[self.current_tam_mix['Energy Source'].isin(['Coal', 'Oil Products', 'Natural Gas', 'Biomass, waste and other renewables']), 'Weighting Factor'].sum() / self.conv_weight_sum) \
                * (self.assumptions['Weighted Emission Factor for Space Heating and Cooling'] * self.assumptions['TJ_per_TWh']) / 10**6

        emis_diff_mdc['Emission Reductions: Conv Total'] = emis_diff_mdc[['Conventional: Grid', 'Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect']].sum(axis=1, min_count=1)
        
        # SpaceHeating_cluster!O190:S238
        self.emis_diff_mdc = emis_diff_mdc


    def calc_emis_diff_mdc_spacecooling(self):
        # Table 13: Difference in EMISSIONS between REF1 and REF2 populations in MDC + LAC + EE + China
        # CONVENTIONAL Avoided Emissions/ Million Metric Tons CO2
        emis_diff_mdc = pd.DataFrame(None,
            columns=['Conventional: Grid','Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect', 'Emission Reductions: Conv Total'],
            index=list(range(2014, 2061)), dtype=np.float64)

        if self.assumptions['Grid'] == 'Y':
            emis_diff_mdc['Conventional: Grid'] = self.addl_func_units_mdc['Additional Functional Units in REF2 vs REF2'] \
                * self.current_tam_mix.loc[self.current_tam_mix['Energy Source'] == 'Electricity', 'Weighting Factor'].values[0] \
                * self.assumptions['Twh_per_TWh'] *  self.emissions_factors_ref1_co2eq['World'] / 100

        emis_diff_mdc['Emission Reductions: Conv Total'] = emis_diff_mdc[['Conventional: Grid', 'Conventional: Fuel', 'Conventional: Other Direct', 'Conventional: Indirect']].sum(axis=1, min_count=1)
        
        # SpaceHeating_cluster!O190:S238
        self.emis_diff_mdc = emis_diff_mdc


    def calc_emis_alloc_mdc(self):
        # Table 14: EMISSIONS ALLOCATIONS TO (a) Health & Education; (b) Education ONLY; (c) Family Planning (excluding education)
        # More developed countries
        emissions_allocations_mdc = pd.DataFrame(None,
            columns=['Health & Education: Conv Total', 'Health & Education: Solution Total', 'Education: Conv Total', 'Education: Solution Total', 'Family Planning: Conv Total', 'Family Planning: Solution Total', '% Allocation to Education: Conv Total', '% Allocation to Education: Solution Total'],
            index=list(range(2014, 2061)), dtype=np.float64)

        emissions_allocations_mdc['Health & Education: Conv Total'] = self.emis_diff_mdc['Emission Reductions: Conv Total'].fillna(0.0)
        emissions_allocations_mdc['Health & Education: Solution Total'] = 0.0 # emis_diff_mdc['Emission Reductions: Solution Total']
        emissions_allocations_mdc['Education: Conv Total'] = np.nan
        emissions_allocations_mdc['Education: Solution Total'] = np.nan
        emissions_allocations_mdc['Family Planning: Conv Total'] = emissions_allocations_mdc['Health & Education: Conv Total'] - emissions_allocations_mdc['Education: Conv Total'].fillna(0.0)
        # emissions_allocations_mdc['Family Planning: Conv Total'] = emissions_allocations_mdc['Family Planning: Conv Total'].fillna(0.0)
        emissions_allocations_mdc['Family Planning: Solution Total'] = emissions_allocations_mdc['Health & Education: Solution Total'] - emissions_allocations_mdc['Education: Solution Total'].fillna(0.0)
        emissions_allocations_mdc['% Allocation to Education: Conv Total'] = emissions_allocations_mdc['Education: Conv Total'].fillna(0.0) / emissions_allocations_mdc['Health & Education: Conv Total']
        emissions_allocations_mdc['% Allocation to Education: Conv Total'] = emissions_allocations_mdc['% Allocation to Education: Conv Total'].fillna(0.0)
        emissions_allocations_mdc['% Allocation to Education: Solution Total'] = emissions_allocations_mdc['Family Planning: Solution Total'] / (emissions_allocations_mdc['Education: Solution Total'] + emissions_allocations_mdc['Family Planning: Solution Total'])

        # SpaceHeating_cluster!X192:AI238
        self.emissions_allocations_mdc = emissions_allocations_mdc


    def calc_total_emis(self, mdc=True):
        # Total Emissions Avoided due to Health & Education (Gt CO2-eq)
        emissions_avoided_lldc_period = self.emissions_allocations_lldc.loc[self.assumptions['period_start']:self.assumptions['period_end'], 'Health & Education: Conv Total'].sum()
        emissions_avoided_lldc_full = self.emissions_allocations_lldc.loc[:, 'Health & Education: Conv Total'].sum()
        
        if mdc:
            emissions_avoided_mdc_period = self.emissions_allocations_mdc.loc[self.assumptions['period_start']:self.assumptions['period_end'], 'Health & Education: Conv Total'].sum()
            emissions_avoided_mdc_full = self.emissions_allocations_mdc.loc[:, 'Health & Education: Conv Total'].sum()

        # Electricity_cluster!N4:O12
        self.emissions_avoided_lldc_period = round(emissions_avoided_lldc_period/1000, 2)
        self.emissions_avoided_lldc_full = round(emissions_avoided_lldc_full/1000, 2)
        
        if mdc:
            self.emissions_avoided_mdc_period = round(emissions_avoided_mdc_period/1000, 2)
            self.emissions_avoided_mdc_full = round(emissions_avoided_mdc_full/1000, 2)
        else: 
            self.emissions_avoided_mdc_period = 0
            self.emissions_avoided_mdc_full = 0


        self.emissions_avoided_total_period = round(self.emissions_avoided_lldc_period + self.emissions_avoided_mdc_period, 2)
        self.emissions_avoided_total_full = round(self.emissions_avoided_lldc_full + self.emissions_avoided_mdc_full, 2)


    def print_total_emis(self, mdc=True):
        # To avoid the hard coded 2015 - 2060 date range in Excel, infer the min/max years from the dataframe
        min_range = min(self.emissions_allocations_lldc.index)
        max_range = max(self.emissions_allocations_lldc.index)

        print('\n', self.name)
        print('Total Emissions Avoided due to Health & Education (Gt CO2-eq)')
        print('\nLeast & Less Developed Countries (Conventional):')
        print(f'{min_range} - {max_range}:', self.emissions_avoided_lldc_full)
        print(f'{self.period_start} - {self.period_end}:', self.emissions_avoided_lldc_period)

        if mdc:
            print('\nMore Developed Countries (Conventional):')
            print(f'{min_range} - {max_range}:', self.emissions_avoided_mdc_full)
            print(f'{self.period_start} - {self.period_end}:', self.emissions_avoided_mdc_period)

        print('\nTotal (Conventional):')
        print(f'{min_range} - {max_range}:', self.emissions_avoided_total_full)
        print(f'{self.period_start} - {self.period_end}:', self.emissions_avoided_total_period)