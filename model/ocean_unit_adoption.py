import pandas as pd
import numpy as np
import math
import json
import copy

import model.interpolation as interp

# Code originally based of seaweed farming solution, but is intended to be general.

class UnitAdoption:
    """This is the base class that contains the calculations for Ocean-related Unit Adoption scenarios.
    Used for both PDS adoption and REF adoption.
    """
    description : str
    _tam: pd.Series
    disturbance_rate: np.float64
    sequestration_rate_all_ocean: np.float64
    use_tam_for_co2_calcs: bool = False
    
    def _validate_inputs(self):        
        pass

    def __init__(self, base_year, end_year, adoption_scenario_to_load, adoption_input_file):
        self._validate_inputs()

        self.base_year = base_year
        self.end_year = end_year
        
        stream = open(adoption_input_file,'r')
        json_dict = json.load(stream)

        if len(json_dict.keys()) == 0:
            raise ValueError(f'Empty file {adoption_input_file}')

        if adoption_scenario_to_load not in json_dict.keys():
            raise ValueError(f'Unable to find scenario name {adoption_scenario_to_load} in {adoption_input_file} keys - {json_dict.keys()}')
 
        adoption_scenario_desc = json_dict[adoption_scenario_to_load]['description']
                
        self.description = adoption_scenario_desc

        idx, vals = zip(*json_dict[adoption_scenario_to_load]['data']) # list of two-element lists
        adoption_series = pd.Series(data=vals, index=idx)

        # ditch everything earlier than the base year -1.
        adoption_series = adoption_series.loc[self.base_year-1:]

        self.implementation_units = adoption_series
        self.expected_lifetime = 0.0
        self.first_cost = 0.0
        self.net_profit_margin = 0.0
        self.operating_cost = 0.0

        tam_series = pd.Series(index= adoption_series.index, dtype= np.float64)
        self._tam = tam_series # values are initialised to NaNs

    def get_tam_units(self) -> pd.Series:
        return self._tam.copy()

    def get_skeleton(self):
        # This is used to create empty unit adoption objects. Sometimes ref unit adoption is zero, often conventional unit adoption is also zero.
        # Having zero unit adoption objects enables addition & subtraction without changing formulae.

        new_obj = copy.deepcopy(self)
        
        series = new_obj.implementation_units
        series[:] = 0.0
        
        new_obj.implementation_units = series

        return new_obj

    ##############
    
    @property
    def expected_lifetime(self):
        return self._expected_lifetime
    
    @expected_lifetime.setter
    def expected_lifetime(self, value):
        self._expected_lifetime = value
    
    @property
    def first_cost(self):
        return self._first_cost
    
    @first_cost.setter
    def first_cost(self, value):
        self._first_cost = value

    @property
    def operating_cost(self):
        return self._operating_cost
    
    @operating_cost.setter
    def operating_cost(self, value):
        self._operating_cost = value

    @property
    def net_profit_margin(self):
        return self._net_profit_margin
    
    @net_profit_margin.setter
    def net_profit_margin(self, value):
        self._net_profit_margin = value
    
    ##########

    def get_units_adopted(self):
        # 'Unit Adoption Calculations'!C136:C182 = "Land Units Adopted" - PDS
        # 'Unit Adoption Calculations'!C198:C244 = "Land Units Adopted" - REF
        return self.implementation_units.copy()


    def annual_breakout(self, end_year):

        """Breakout of operating cost per year, including replacements.
        """
        
        # Following code based on annual_breakout function in model\operatingcost.py
        # See range starting in cell [Operating Cost]!$C$261. Also used by Net Profit Margin calculation.

        new_funits_per_year = self.implementation_units.loc[self.base_year:].diff()

        breakout = pd.DataFrame(0, index=np.arange(self.base_year, end_year),
                                columns=np.arange(self.base_year, new_funits_per_year.index[-1]), dtype='float')
        breakout.index.name = 'Year'
        breakout.index = breakout.index.astype(int)

        for year in range(self.base_year, end_year + 1): # iterates over columns (fewer columns than rows)

            # within the years of interest, assume replacement of worn out equipment.
            lifetime = self.expected_lifetime
            assert lifetime != 0, 'Cannot have a lifetime replacement of 0 and non-zero costs'
            while math.ceil(lifetime) <= (end_year - year):
                lifetime += self.expected_lifetime # This usually doubles the lifetime for the first year or two.

            total = new_funits_per_year.loc[year]

            # for each year, add in values for equipment purchased in that
            # starting year through the year where it wears out.
            for row in range(year, end_year + self.expected_lifetime): # iterates over rows
                remaining_lifetime = np.clip(lifetime, 0, 1)
                val = total * remaining_lifetime
                breakout.loc[row, year] = val if math.fabs(val) > 0.01 else 0.0
                lifetime -= 1
                if lifetime <= 0:
                    break
        return breakout

        
    def get_operating_cost(self, end_year):

        # After multiplying by (1+ disturbance_rate), this should equal the time series SUM($C266:$AV266) in [Operating Cost] worksheet 

        result = self.annual_breakout(end_year)
        result *= self.operating_cost

        cost_series = result.sum(axis='columns')
        return cost_series


    def get_incremental_units_per_period(self):

        incremented = self.implementation_units.loc[self.base_year-1:].diff()
        shifted = incremented.shift(self.expected_lifetime +1).fillna(0.0)
        
        return incremented + shifted

    
    def get_install_cost_per_land_unit(self):

        # $C$37 (pds) and $L$37 (ref) on First Cost spreadsheet tab.
        learning_rate = 1.0 # 100%
        how_fast = 2 # If double enter 2, if every 4 x increase, then enter 4
        param_b = math.log10(learning_rate) / math.log10(how_fast)

        # For some solutions (e.g. seaweed farming), param_b == zero. So following will produce a static series of self.first_cost.
        cost_series = self.implementation_units.loc[:].apply(lambda x: x**param_b) * self.first_cost

        return cost_series


    def get_annual_world_first_cost(self):
        
        # For the custom pds scenario, this is the time series referred to by cell $E$36 in the spreadsheet.
        # For the custom ref scenario, this is the time series referred to by cell $N$36 in the spreadsheet.

        #TODO - validate input params.

        i_units = self.get_incremental_units_per_period()        
        result = i_units * self._first_cost

        return result


    def get_lifetime_operating_savings(self, end_year):

        # After muliplying by (1 + disturbance_rate) this should match the time series in [Operating Cost]!$C$125
        
        matrix = self.annual_breakout(end_year)
        cost_series = matrix.sum(axis='columns') * self.operating_cost
        
        return cost_series


    def get_lifetime_cashflow_npv(self, purchase_year, discount_rate):
        
        # "result" should match time series in [Operating Cost]!$J$125 = "NPV of Single Cashflows (to 2014)"
        years_old_at_start =  purchase_year - self.base_year + 1

        discount_factor = 1/(1+discount_rate)

        first_cost_series = self.get_install_cost_per_land_unit()
        first_cost_series = first_cost_series.loc[self.base_year:]

        first_val = first_cost_series.loc[self.base_year] + self.operating_cost
        first_val = first_val * discount_factor**(years_old_at_start)

        results = [first_val]
        
        for row in range(self.expected_lifetime-1):
            to_append = self.operating_cost * discount_factor**(years_old_at_start + row+1)
            results.append(to_append)

        result = pd.Series(results,index=first_cost_series[:self.expected_lifetime].index)
        
        return result


    def get_net_profit_margin(self, end_year):

        # For PDS = [Net Profit Margin]!SUM(C266:AV266)
        # For REF = [Net Profit Margin]!SUM(C403:AV403)

        # (PDS - REF) = [Net Profit Margin]!$C$125 = "Difference in Net Profit Margin (PDS minus Reference)""

        matrix = self.annual_breakout(end_year)

        margin_series = matrix.sum(axis='columns')
        margin_series *= self.net_profit_margin

        return margin_series

###########
    
    def set_tam_linear(self, total_area, change_per_period, total_area_as_of_period = None) -> None:
        
        if total_area_as_of_period is None:
            total_area_as_of_period = self.base_year
        
        m = change_per_period
        c = total_area - m * total_area_as_of_period

        # self.tam_df[region] is a series. Convert this to a dataframe. Then apply a function using straight line formula y = m*x +c.
        # x.name returns index value (the year).
        series = pd.DataFrame(self._tam).apply(lambda x: m * x.name + c, axis='columns')

        self._tam = series
        return 

    def apply_linear_regression(self) -> None:

        df = interp.linear_trend(self._tam)

        self._tam = df['adoption']

        return
    
    def apply_clip(self, lower = None, upper = None) -> None:
        if lower == None and upper == None:
            print('Warning : Neither lower nor upper parameter supplied. No action taken.')
        self._tam.clip(lower=lower, upper=upper, inplace=True)

    
    def tam_build_cumulative_unprotected_area(self, new_growth_harvested_every: np.float64) -> None:
        
        results = pd.Series(index = self._tam.index, dtype=float)
        
        first_pass = True
        for index, value in self._tam.loc[self.base_year:].iteritems():
            if first_pass:
                results.loc[index] = 0.0
                prev_value = 0.0
                first_pass = False
                continue

            val = self.implementation_units.loc[index -1]

            result = (value - val - prev_value) * new_growth_harvested_every
            result = prev_value + result
            results.loc[index] = result
            prev_value = result

        series = pd.Series(results, index=self.implementation_units.index)
        self.cumulative_unprotected_area = series

        # "total_at_risk_area" = "total_undegraded_area" for pds; "total_at_risk_area" for ref scenario
        self.total_at_risk_area = self._tam - self.cumulative_unprotected_area

####
    def get_carbon_sequestration(self, sequestration_rate, disturbance_rate) ->pd.DataFrame:
        
        co2_mass_to_carbon_mass = 3.666 # carbon weighs 12, oxygen weighs 16 => (12+16+16)/12

        if self.use_tam_for_co2_calcs:
            adoption = self.total_at_risk_area
        else:
            adoption = self.get_units_adopted()
        
        sequestration = adoption * sequestration_rate
        sequestration *= co2_mass_to_carbon_mass * (1 - disturbance_rate)

        # When this function is netted out [pds - ref], sequestration should match the time series in [CO2 Calcs]!$B$120

        return sequestration

    def get_change_in_ppm_equiv_series(self) -> np.float64:

        sequestration = self.get_carbon_sequestration(self.sequestration_rate_all_ocean, self.disturbance_rate)

        result_years = list(range(self.base_year-1, self.end_year+1))
        results = pd.Series(index = result_years, dtype=np.float64)
        results = results.fillna(0.0)
        # (0.217 + 0.259*EXP(-(A173-$A$173+1)/172.9) + 0.338*EXP(-(A173-$A$173+1)/18.51) + 0.186*EXP(-(A173-$A$173+1)/1.186))
        # (0.217 + 0.259*EXP(-(current_year-year_zero+1)/172.9) + 0.338*EXP(-(current_year-year_zero+1)/18.51) + 0.186*EXP(-(current_year-year_zero+1)/1.186))

        for iter_year in result_years:
            year_results = []
            exponent= 0

            for _ in range(iter_year, result_years[-1] +1):
                year_net_adoption = sequestration.loc[iter_year]
                exponent += 1
                val =  0.217 + 0.259*np.exp(-(exponent)/172.9) 
                val += 0.338*np.exp(-(exponent)/18.51) 
                val += 0.186*np.exp(-(exponent)/1.186)
                year_results.append(year_net_adoption * val)

            year_results_series = pd.Series(index = range(iter_year, self.end_year+1), dtype=np.float64)
            year_results_series = year_results_series.fillna(0.0)
            year_results_series = year_results_series.add(year_results)

            results = results.add(year_results_series, fill_value=0.0)

        factor = (1_000_000 * 10**6 ) / 44.01
        factor = factor / (1.8 * 10**20)
        factor = factor * 10**6
        results = results * factor
        return results
