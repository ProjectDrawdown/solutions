
from typing import List
from dataclasses import dataclass
import pandas as pd
import numpy as np
import math


@dataclass()
class UnitAdoption:
    description : str
    columns : List[str]
    data: List[List[float]]
    base_year: int
    _first_cost : float
    _operating_cost :  float
    _net_profit_margin :  float
    _expected_lifetime : float
    
    def _validate_inputs(self):
        
        if self.expected_lifetime is None:
            raise ValueError(f'No expected lifetime specified for {self.description}')
    
    def __post_init__(self):
        self._validate_inputs()

        df = pd.DataFrame.from_dict(self.data)
        df.columns = self.columns
        df.set_index(df.columns[0], inplace=True)

        # ditch everything earlier than the base year.
        df = df.loc[self.base_year-1:]

        self.implementation_units = df

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

    def get_units_adopted(self, region):

        return self.implementation_units.loc[:, region].copy()


    def annual_breakout(self, region, end_year):

        # Following code based on annual_breakout function in model\operatingcost.py
        
        """Breakout of operating cost per year, including replacements.
        """

        new_funits_per_year = self.implementation_units.loc[self.base_year:, region].diff()

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

        
    def get_operating_cost(self, region, end_year):

        result = self.annual_breakout(region, end_year)
        result *= self.operating_cost

        cost_series = result.sum(axis='columns')
        return cost_series


    def get_incremental_units_per_period(self, region):

        incremented = self.implementation_units.loc[self.base_year-1:, region].diff()
        shifted = incremented.shift(self.expected_lifetime +1).fillna(0.0)
        
        return incremented + shifted

    
    def get_install_cost_per_land_unit(self, region):

        # $C$37 (pds) and $L$37 (ref) on First Cost spreadsheet tab.
        learning_rate = 1.0 # 100%
        how_fast = 2 # If double enter 2, if every 4 x increase, then enter 4
        param_b = math.log10(learning_rate) / math.log10(how_fast)

        # For some solutions (e.g. seaweed farming), param_b == zero. So following will produce a static series of self.first_cost.
        cost_series = self.implementation_units.loc[:,region].apply(lambda x: x**param_b) * self.first_cost

        return cost_series


    def get_annual_world_first_cost(self, region):

        #TODO - validate input params.

        i_units = self.get_incremental_units_per_period(region)        
        result = i_units * self._first_cost

        return result


    def get_lifetime_operating_savings(self, region, end_year):
        
        matrix = self.annual_breakout(region, end_year)
        cost_series = matrix.sum(axis='columns') * self.operating_cost
        
        return cost_series


    def get_lifetime_cashflow_npv(self, region, purchase_year, discount_rate):
        
        years_old_at_start =  purchase_year - self.base_year + 1

        discount_factor = 1/(1+discount_rate)

        first_cost_series = self.get_install_cost_per_land_unit(region)
        first_cost_series = first_cost_series.loc[self.base_year:]

        first_val = first_cost_series.loc[self.base_year] + self.operating_cost
        first_val = first_val * discount_factor**(years_old_at_start)

        results = [first_val]
        
        for row in range(self.expected_lifetime-1):
            to_append = self.operating_cost * discount_factor**(years_old_at_start + row+1)
            results.append(to_append)

        result = pd.Series(results,index=first_cost_series[:self.expected_lifetime].index)
        
        return result


    def get_net_profit_margin(self, region, end_year):

        matrix = self.annual_breakout(region, end_year)

        margin_series = matrix.sum(axis='columns')
        margin_series *= self.net_profit_margin

        return margin_series


    def get_carbon_sequestration(self, region, sequestration_rate, disturbance_rate) ->pd.DataFrame:

        co2_mass_to_carbon_mass = 3.666 # carbon weighs 12, oxygen weighs 16 => (12+16+16)/12

        adoption = self.get_units_adopted(region)
        sequestration = adoption * sequestration_rate
        sequestration *= co2_mass_to_carbon_mass * (1 - disturbance_rate)

        return sequestration
