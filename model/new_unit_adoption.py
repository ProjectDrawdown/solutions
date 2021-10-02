
import pandas as pd
from math import exp, ceil, floor, log10
from numpy import arange, clip, isnan
import json
import copy

import model.interpolation as interp

# Code originally based of seaweed farming solution, but is intended to be general.
class NewUnitAdoption:
    """This is the base class that contains the calculations for Ocean-related Unit Adoption scenarios.
    Used for both PDS adoption and REF adoption.
    """
    description : str
    _area_units: pd.Series
    disturbance_rate: float
    sequestration_rate_all_ocean: float
    
    def __init__(self, base_year: int, start_year: int, end_year: int, adoption_scenario_to_load: str, adoption_input_file: str):
        """Initialise with base year, start year, end year, the name of the adoption scenario to load, and the adoption input file (either pds scenario or reference scenario).
        
        "base year" specifies the year the time series should start. Start year is the start of the reporting period, end year specifies the end of the reporting period.
        adoption_scenario_to_load is a string used to load the relevant scenario - e.g. for the pds scenario "AverageOfAllScenarios".
        adoption_input_file is a path to the file used to store the data for this adoption_scenario_to_load.
        """
        self.base_year = base_year
        self.start_year = start_year
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
        
        area_units_series = pd.Series(index= adoption_series.index, dtype= float) # a.k.a. land unit adoption, ocean unit adoption.
        self._area_units = area_units_series # values are initialised to NaNs

    def get_area_units(self) -> pd.Series:
        """Return a copy of the total land or ocean area time series."""
        return self._area_units.copy()

    def get_skeleton(self) -> pd.Series:
        """Return a deep copy of the unit adoption time series with all values replaced with zeroes."""
        # This is used to create empty unit adoption objects. Sometimes ref unit adoption is zero, often conventional unit adoption is also zero.
        # Having zero unit adoption objects enables addition & subtraction without changing formulae.
        new_obj = copy.deepcopy(self)        
        series = new_obj.implementation_units
        series[:] = 0.0
        new_obj.implementation_units = series
        return new_obj

    def get_units_adopted(self) -> pd.Series:
        """Return a copy of the implementation units adopted."""
        # 'Unit Adoption Calculations'!C136:C182 = "Land Units Adopted" - PDS
        # 'Unit Adoption Calculations'!C198:C244 = "Land Units Adopted" - REF
        return self.implementation_units.copy()

    def annual_breakout(self, expected_lifetime) -> pd.Series:
        """Return a time series breakout of new units per year, including replacements. Use to calculate operating cost, lifetime operating savings, and net profit margin.

        Calculate the number of new sets of SOLUTION implementation units installed over the lifetime of the units,
        but only for new or replacement units installed during the analysis period. Fixed and Variable costs are not applied here, but can then be applied by the function caller.

        This calculation assumes that:
        1. No units installed after the end year are included
        2. Only units installed in year X are accounted for in year X.

        Note:
        1. Each column represents the sum of all units (and their replacements) initially installed in the year at top of column.
        2. Each row represents a particular year of attribution
        3. Number of units depends on year of installation, and restarts for replacement units
        4. For the last year, calculates the fraction of a year remaining in the lifetime
        
        Implementation:
        Include installed units for this column in this row year if all are true:
        1. row year >= Initial Installation Year + delay years required until start of period
        2. row year < final lifetime year of all initial and replacement units  for this column (=period of analysis + # years this column expected to last past end of period)

        """
        
        # Following code based on annual_breakout function in model\operatingcost.py
        # See range starting in cell [Operating Cost]!$C$261. Also used by Net Profit Margin calculation.

        new_funits_per_year = self.implementation_units.loc[self.base_year:].diff()
        breakout = pd.DataFrame(0, index=arange(self.base_year, self.end_year),
                                columns=arange(self.base_year, new_funits_per_year.index[-1]), dtype='float')
        breakout.index.name = 'Year'
        breakout.index = breakout.index.astype(int)

        for year in range(self.base_year, self.end_year + 1): # iterates over columns (fewer columns than rows)
            # within the years of interest, assume replacement of worn out equipment.
            lifetime = expected_lifetime
            assert lifetime != 0, 'Cannot have a lifetime replacement of 0 and non-zero costs'
            while ceil(lifetime) <= (self.end_year - year):
                lifetime += expected_lifetime # This usually doubles the lifetime for the first year or two.

            total = new_funits_per_year.loc[year]
            # for each year, add in values for equipment purchased in that
            # starting year through the year where it wears out.
            for row in range(year, self.end_year + ceil(expected_lifetime)): # iterates over rows
                remaining_lifetime = clip(lifetime, 0, 1)
                val = total * remaining_lifetime
                if isnan(val):
                    val = 0.0
                breakout.loc[row, year] = val
                lifetime -= 1
                if lifetime <= 0:
                    break
        return breakout
        
    def get_operating_cost(self, expected_lifetime, operating_cost) -> pd.Series:
        """Return a time series of the operating costs, summed by year."""

        # After multiplying by (1+ disturbance_rate), this should equal the time series SUM($C266:$AV266) in [Operating Cost] worksheet 
        result = self.annual_breakout(expected_lifetime)
        result *= operating_cost
        cost_series = result.sum(axis='columns')
        return cost_series

    def get_incremental_units_per_period(self, expected_lifetime) -> pd.Series:
        """Return a time series of implementation units for each year"""
        incremented = self.implementation_units.loc[self.base_year-1:].diff()
        lifetime = floor(0.5 + expected_lifetime)
        shifted = incremented.shift(lifetime +1).fillna(0.0)                
        return incremented + shifted

    def get_install_cost_per_land_unit(self, first_cost) -> pd.Series:
        """Return a time series of installation costs per year."""
        # $C$37 (pds) and $L$37 (ref) on First Cost spreadsheet tab.
        learning_rate = 1.0 # 100%
        how_fast = 2 # If double enter 2, if every 4 x increase, then enter 4
        param_b = log10(learning_rate) / log10(how_fast)

        # For some solutions (e.g. seaweed farming), param_b == zero. So following will produce a static series of self.first_cost.
        cost_series = self.implementation_units.loc[:].apply(lambda x: x**param_b) * first_cost
        return cost_series

    def get_annual_world_first_cost(self, expected_lifetime, first_cost) -> pd.Series:
        """Return a time series of the number of units implemented per year multiplied by the first cost"""
        # For the custom pds scenario, this is the time series referred to by cell $E$36 in the spreadsheet.
        # For the custom ref scenario, this is the time series referred to by cell $N$36 in the spreadsheet.
        i_units = self.get_incremental_units_per_period(expected_lifetime)
        result = i_units * first_cost
        return result


    def get_lifetime_operating_savings(self, expected_lifetime, operating_cost) -> pd.Series:
        """Return a time series of operating savings over the reporting period by year, multiplied by the operating cost."""
        # After muliplying by (1 + disturbance_rate) this should match the time series in [Operating Cost]!$C$125
        matrix = self.annual_breakout(expected_lifetime)
        cost_series = matrix.sum(axis='columns') * operating_cost
        return cost_series

    def get_lifetime_cashflow_npv(self, purchase_year, discount_rate, conventional_expected_lifetime, solution_expected_lifetime, operating_cost, conventional_first_cost, solution_first_cost) -> pd.Series:
        """Return a time series of discounted cash flows for the solution expected lifetime. Calculate using first cost and operating cost."""
        # "result" should match time series in [Operating Cost]!$J$125 = "NPV of Single Cashflows (to 2014)"
        years_old_at_start =  purchase_year - self.base_year + 1
        discount_factor = 1/(1+discount_rate)

        first_cost_series = self.get_install_cost_per_land_unit(solution_first_cost)
        first_cost_series = first_cost_series.loc[self.base_year:]
        first_val = first_cost_series.loc[self.base_year] + operating_cost
        first_val = first_val * discount_factor**(years_old_at_start)
        results = [first_val]
        solution_lifetime = ceil(solution_expected_lifetime)

        for year in range(ceil(solution_lifetime)-1):
            to_append = 0.0
            effective_operating_cost = operating_cost
            remaining_solution_life = solution_expected_lifetime - year - 1
            remaining_conventional_life = conventional_expected_lifetime - year - 1
            if remaining_conventional_life < 1.0 and remaining_conventional_life > 0.0:
                to_append += conventional_first_cost * min(1.0, (solution_expected_lifetime - year - 1) / conventional_expected_lifetime)
                results.append(to_append - effective_operating_cost)
                continue
                
            if remaining_solution_life < 1.0:
                effective_operating_cost *= remaining_solution_life
            to_append += effective_operating_cost * discount_factor**(years_old_at_start + year + 1)
            results.append(to_append)

        result = pd.Series(results,index=first_cost_series[:solution_lifetime].index)
        
        return result


    def get_net_profit_margin(self, expected_lifetime, net_profit_margin) -> pd.Series:
        """Return a time series breakdown of net profit margin per year over the reporting period."""
        # For PDS = [Net Profit Margin]!SUM(C266:AV266)
        # For REF = [Net Profit Margin]!SUM(C403:AV403)

        # (PDS - REF) = [Net Profit Margin]!$C$125 = "Difference in Net Profit Margin (PDS minus Reference)""
        matrix = self.annual_breakout(expected_lifetime)
        margin_series = matrix.sum(axis='columns')
        margin_series *= net_profit_margin

        return margin_series

###########
    
    def set_area_units_linear(self, total_area, change_per_period, total_area_as_of_period = None) -> None:
        """Apply a straight line formula to the time series representing the total land/ocean area."""
        if total_area_as_of_period is None:
            total_area_as_of_period = self.base_year
        
        m = change_per_period
        c = total_area - m * total_area_as_of_period

        # self.area_units_df[region] is a series. Convert this to a dataframe. Then apply a function using straight line formula y = m*x +c.
        # x.name returns index value (the year).
        series = pd.DataFrame(self._area_units).apply(lambda x: m * x.name + c, axis='columns')

        self._area_units = series
        return 

    def apply_linear_regression(self) -> None:
        """Apply a linear regression to the time series representing the total land/ocean area."""
        df = interp.linear_trend(self.get_area_units())
        self._area_units = df['adoption']
        return
    
    def apply_clip(self, lower = None, upper = None) -> None:
        """Apply upper and lower bounds to the time series representing the total land/ocean area."""
        if lower == None and upper == None:
            print('Warning : Neither lower nor upper parameter supplied. No action taken.')
        self._area_units.clip(lower=lower, upper=upper, inplace=True)

    def get_cumulative_degraded_unprotected_area(self, delay_impact_of_protection_by_one_year: bool,
                     growth_rate_of_ocean_degradation: float) -> pd.Series:
        """Return a time series representing the total degraded area. (Millions ha)

        Calculation uses the rate supplied by the degradation_rate parameter.
        This rate is applied only to the area that is not covered by the solution (ie not protected) and that is not degraded.
        
        Calculation:
            Area Degraded in Previous Year + (Total Area - Protected Area - Area Degraded in Previous Year) * Degradation Rate 
        """

        # [Unit Adoption Calculations]!$CH$135 (for solution adoption)
        # [Unit Adoption Calculations]!$CH$197 (for reference adoption)

        if delay_impact_of_protection_by_one_year:
            delay = 1
        else:
            delay = 0
        
        results = pd.Series(index = self._area_units.index, dtype=float)        
        first_pass = True
        for year, area_units_total_area in self._area_units.loc[self.base_year - 1:].iteritems():
            if first_pass:
                results.loc[year] = 0.0
                area_degraded_previous_year = 0.0 # prev_value = Area Degraded in Previous Year
                first_pass = False
                continue
            
            # units_adopted = protected area
            units_adopted = self.implementation_units.loc[year-delay]

            result = (area_units_total_area - units_adopted - area_degraded_previous_year) * growth_rate_of_ocean_degradation
            result = area_degraded_previous_year + result
            result = min(result, area_units_total_area)

            results.loc[year] = result
            area_degraded_previous_year = result
        
        return results

    def get_total_at_risk_area(self, growth_rate_of_ocean_degradation: float, 
                delay_impact_of_protection_by_one_year: bool) -> pd.Series:

        """Return a time series representing the total area at risk of degradation by anthropogenic or other means. (Millions ha.)

        Calculated by identifying how much land is degraded, and how much remains undegraded.
        
        Calculation:
            Total Area - Area Protected in Current Year - Area Degraded in Current Year

        """

        # [Unit Adoption Calculations]!$CZ$135 (for solution adoption)
        # [Unit Adoption Calculations]!$CZ$197 (for reference adoption)

        cumulative_unprotected_area = self.get_cumulative_degraded_unprotected_area(
                delay_impact_of_protection_by_one_year= delay_impact_of_protection_by_one_year,
                growth_rate_of_ocean_degradation= growth_rate_of_ocean_degradation)

        total_at_risk_area = self._area_units - cumulative_unprotected_area - self.implementation_units
        total_at_risk_area = total_at_risk_area.clip(lower=0.0)

        return total_at_risk_area


    def get_cumulative_degraded_area_under_protection(self, delay_impact_of_protection_by_one_year: bool, disturbance_rate: float) -> pd.Series:
        """Return a time series representing the cumulative degraded area under protection. (Millions ha)

        Even protected areas suffer from degradation via disturbances (e.g. natural degradation, logging, storms, fires or human settlement).
        The disturbance rate is usually equal in the PDS adoption and reference adoption.
        This disturbance rate represents the degradation of protected area, and is expected to be much less than the degradation rate of unprotected area.
        Use this to calculate the carbon sequestration, direct emissions, fuel and grid emissions, indirect emissions and total reduction in area degradation result.
        
        Calculation:
            Protected area that was degraded in Previous Year + (area protected by soln - protected area degraded in previous year) * disturbance tate
        """

        # [Unit Adoption Calculations]!$EJ$135 (for PDS adoption)
        # [Unit Adoption Calculations]!$EJ$197 (for reference adoption)

        if delay_impact_of_protection_by_one_year:
            delay = 1
        else:
            delay = 0
        
        results = pd.Series(index = self._area_units.index, dtype=float)
        
        first_pass = True
        for year, _ in self.implementation_units.loc[self.base_year:].iteritems():
            if first_pass:
                results.loc[year] = 0.0
                area_degraded_previous_year = 0.0 # prev_value = Area Degraded in Previous Year
                first_pass = False
                continue

            protected_area = self.implementation_units.loc[year - delay]

            result = area_degraded_previous_year + (protected_area - area_degraded_previous_year) * disturbance_rate
            result = min(result, protected_area)
            results.loc[year] = result
            area_degraded_previous_year = result
        
        series = pd.Series(results, index=self.implementation_units.index)

        return series


    def get_total_undegraded_area(self, growth_rate_of_ocean_degradation,
                disturbance_rate: float = 1.0, 
                delay_impact_of_protection_by_one_year: bool = True) -> pd.Series:

        """ Return a time series representing the total area that is not degraded in any particular year. (Millions ha)
        
        Calculated by taking the Total Area and removing the degraded area, which is the same as summing the undegraded area and at-risk area.
        
        Calculation:
            Total Area - Area Degraded that was Unprotected - Protected Land that is Degraded (via a Disturbance) in Current Year

        """
        # Returns:
        # [Unit Adoption Calculations]!$DS$135 (for PDS adoption)
        # [Unit Adoption Calculations]!$DS$197 (for reference adoption)

        # [Unit Adoption Calculations]!$CH$135 (PDS):
        cumulative_degraded_unprotected_area = self.get_cumulative_degraded_unprotected_area(delay_impact_of_protection_by_one_year, growth_rate_of_ocean_degradation)
        
        # [Unit Adoption Calculations]!$EJ$135 (PDS):
        cumulative_degraded_area_under_protection = self.get_cumulative_degraded_area_under_protection(
                                                                    delay_impact_of_protection_by_one_year,
                                                                    disturbance_rate
                                                                    )

        result = self._area_units - cumulative_degraded_unprotected_area - cumulative_degraded_area_under_protection

        return result.clip(lower = 0.0)

####
        
    def get_annual_reduction_in_total_degraded_area(self, disturbance_rate, growth_rate_of_ocean_degradation,
                             delay_impact_of_protection_by_one_year) -> pd.Series:
        """Return a time series representing the change in total degraded area in the adoption each year, added to the total undegraded area for t-1. (Millions ha.)

        Used to combine two adoptions, usually pds and reference solution (PDS - REF) like this:
            annual_reduction_in_total_degraded_area (REF) - annual_reduction_in_total_degraded_area (PDS).
        This is equivalent to:
            Cumulative Area Degraded in REF Scenario for year x  - Cumulative Area Degraded in PDS Scenario for year x - Cumulative Degradation Change (PDS - REF) for Year [x-1]

        """

        # [Unit Adoption Calculations]!$CG$249
        # (cumulative degraded area unprotected + cumulative degraded area under protection + total undegraded area [t-1])
        # ( CG135 + EJ135 + DS135 )
        cumulative_degraded_unprotected_area = self.get_cumulative_degraded_unprotected_area(
                                delay_impact_of_protection_by_one_year,
                                growth_rate_of_ocean_degradation
                                )

        cumulative_degraded_area_under_protection = self.get_cumulative_degraded_area_under_protection(
                                delay_impact_of_protection_by_one_year,
                                disturbance_rate
                                )

        total_undegraded_area = self.get_total_undegraded_area(
                                growth_rate_of_ocean_degradation,
                                disturbance_rate,
                                delay_impact_of_protection_by_one_year
                                )

        cumulative_degraded_area = cumulative_degraded_unprotected_area + cumulative_degraded_area_under_protection + total_undegraded_area.shift(1)

        return cumulative_degraded_area
        

    def get_emissions_reduction_series(self, disturbance_rate, growth_rate_of_ocean_degradation, delay_impact_of_protection_by_one_year, emissions_reduced_per_unit_area, use_aggregate_CO2_equivalent_instead_of_individual_GHG: bool) -> pd.Series:
        """Return a time series representing the amount of emissions reduced for each year in the reporting period. (MMT CO2 equivalent).
        
        Calculated by taking the total undegraded area and muliplying by the emissions reduced per unit area.
        """
        # CO2-eq MMT Reduced
        # Used to calculate [CO2 Calcs]!$B64

        if use_aggregate_CO2_equivalent_instead_of_individual_GHG:
        # For PDS, total_undegraded_area will equal ['Unit Adoption Calculations']!DS135
        # For REF, total_undegraded_area will equal ['Unit Adoption Calculations']!DS197
            area = self.get_annual_reduction_in_total_degraded_area(growth_rate_of_ocean_degradation, disturbance_rate, delay_impact_of_protection_by_one_year)
        else:
            area = self.get_total_undegraded_area(growth_rate_of_ocean_degradation, disturbance_rate, delay_impact_of_protection_by_one_year)

        result = area * emissions_reduced_per_unit_area
            
        return result
    
    def get_carbon_sequestration(
            self,
            sequestration_rate,
            disturbance_rate,
            growth_rate_of_ocean_degradation,
            delay_impact_of_protection_by_one_year,
            delay_regrowth_of_degraded_land_by_one_year,
            use_adoption
            ) ->pd.Series:

        """Return a time series representing the total carbon sequestered by year across the reporting period.
        
        Calculates the total undegraded area and muliplying by sequestration rate multiplied by (1-disturbance rate)"""

        co2_mass_to_carbon_mass = 3.666 # carbon weighs 12, oxygen weighs 16 => (12+16+16)/12

        if use_adoption:
            total_undegraded_area = self.get_units_adopted()
        else:
            total_undegraded_area = self.get_total_undegraded_area(growth_rate_of_ocean_degradation, disturbance_rate, delay_impact_of_protection_by_one_year)
        
        #adoption = 'Unit Adoption Calculations'! [DS258 + EJ142 - EJ204]
        
        sequestration = total_undegraded_area * sequestration_rate
        sequestration *= co2_mass_to_carbon_mass * (1 - disturbance_rate)

        if delay_regrowth_of_degraded_land_by_one_year:
            sequestration = sequestration.shift(1)

        # When this function is netted out [pds - ref], sequestration should match the time series in [CO2 Calcs]!$B$120
        return sequestration
