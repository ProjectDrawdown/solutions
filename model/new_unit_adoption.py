import pandas as pd
import numpy as np
import math
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
    disturbance_rate: np.float64
    sequestration_rate_all_ocean: np.float64
    use_area_units_for_co2_calcs: bool = False
    
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

        area_units_series = pd.Series(index= adoption_series.index, dtype= np.float64) # a.k.a. land unit adoption, ocean unit adoption.
        self._area_units = area_units_series # values are initialised to NaNs

    def get_area_units_units(self) -> pd.Series:
        return self._area_units.copy()

    def get_skeleton(self) -> pd.Series:
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

    def get_units_adopted(self) -> pd.Series:
        # 'Unit Adoption Calculations'!C136:C182 = "Land Units Adopted" - PDS
        # 'Unit Adoption Calculations'!C198:C244 = "Land Units Adopted" - REF
        return self.implementation_units.copy()


    def annual_breakout(self, end_year) -> pd.Series:

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

        
    def get_operating_cost(self, end_year) -> pd.Series:

        # After multiplying by (1+ disturbance_rate), this should equal the time series SUM($C266:$AV266) in [Operating Cost] worksheet 

        result = self.annual_breakout(end_year)
        result *= self.operating_cost

        cost_series = result.sum(axis='columns')
        return cost_series


    def get_incremental_units_per_period(self) -> pd.Series:

        incremented = self.implementation_units.loc[self.base_year-1:].diff()
        shifted = incremented.shift(self.expected_lifetime +1).fillna(0.0)
        
        return incremented + shifted

    
    def get_install_cost_per_land_unit(self) -> pd.Series:

        # $C$37 (pds) and $L$37 (ref) on First Cost spreadsheet tab.
        learning_rate = 1.0 # 100%
        how_fast = 2 # If double enter 2, if every 4 x increase, then enter 4
        param_b = math.log10(learning_rate) / math.log10(how_fast)

        # For some solutions (e.g. seaweed farming), param_b == zero. So following will produce a static series of self.first_cost.
        cost_series = self.implementation_units.loc[:].apply(lambda x: x**param_b) * self.first_cost

        return cost_series


    def get_annual_world_first_cost(self) -> pd.Series:
        
        # For the custom pds scenario, this is the time series referred to by cell $E$36 in the spreadsheet.
        # For the custom ref scenario, this is the time series referred to by cell $N$36 in the spreadsheet.

        #TODO - validate input params.

        i_units = self.get_incremental_units_per_period()        
        result = i_units * self._first_cost

        return result


    def get_lifetime_operating_savings(self, end_year) -> pd.Series:

        # After muliplying by (1 + disturbance_rate) this should match the time series in [Operating Cost]!$C$125
        
        matrix = self.annual_breakout(end_year)
        cost_series = matrix.sum(axis='columns') * self.operating_cost
        
        return cost_series


    def get_lifetime_cashflow_npv(self, purchase_year, discount_rate) -> pd.Series:
        
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
    
    def set_area_units_linear(self, total_area, change_per_period, total_area_as_of_period = None) -> None:
        
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

        df = interp.linear_trend(self._area_units)

        self._area_units = df['adoption']

        return
    
    def apply_clip(self, lower = None, upper = None) -> None:
        if lower == None and upper == None:
            print('Warning : Neither lower nor upper parameter supplied. No action taken.')
        self._area_units.clip(lower=lower, upper=upper, inplace=True)


    def get_cumulative_degraded_unprotected_area(self, delay_impact_of_protection_by_one_year: bool = True,
                     growth_rate_of_ocean_degradation: np.float64 = 1.0) -> pd.Series:
        """
        This represents the total degraded area.
        Calculation uses the rate supplied by the degradation_rate parameter.
        This rate is applied only to the area that is not covered by the solution (ie not protected) and that is not degraded.
        Units: Millions ha
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
            
            # area_degraded_previous_year = results.loc[year-1]
            # if np.isnan(area_degraded_previous_year):
            #     area_degraded_previous_year = 0.0

            # units_adopted = protected area
            units_adopted = self.implementation_units.loc[year-delay]

            result = (area_units_total_area - units_adopted - area_degraded_previous_year) * growth_rate_of_ocean_degradation
            result = area_degraded_previous_year + result
            result = min(result, area_units_total_area)

            results.loc[year] = result
            area_degraded_previous_year = result
        
        return results

    def get_total_at_risk_area(self, growth_rate_of_ocean_degradation: np.float64, 
                delay_impact_of_protection_by_one_year: bool) -> pd.Series:

        """
        This represents the total area at risk of degradation by anthropogenic or other means.
        It is calculated by identifying how much land is degraded, and how much remains undegraded.
        Units: Millions ha
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


    def get_cumulative_degraded_area_under_protection(self, delay_impact_of_protection_by_one_year: bool, disturbance_rate: np.float64) -> pd.Series:
        """
        Even protected areas suffer from degradation via disturbances (e.g. natural degradation, logging, storms, fires or human settlement).
        The disturbance rate is usually equal in the PDS adoption and reference adoption.
        This disturbance rate represents the degradation of protected area, and is expected to be much less than the
        degradation rate of unprotected area.
        This function is used to calculate the carbon sequestration, direct emissions, fuel and grid emissions, 
        indirect emissions and total reduction in area degradation result.
        Units: Millions ha
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
                disturbance_rate: np.float64 = 1.0, 
                delay_impact_of_protection_by_one_year: bool = True) -> pd.Series:

        """
        This represents the total area that is not degraded in any particular year. It takes the Total Area and removes the degraded area,
        which is the same as summing the undegraded area and at-risk area.
        Units: Millions ha
        Calculation:
            Total Area - Area Degraded that was Unprotected - Protected Land that is Degraded (via a Disturbance) in Current Year

        """
        # Returns:
        # [Unit Adoption Calculations]!$DS$135 (for PDS adoption)
        # [Unit Adoption Calculations]!$DS$197 (for reference adoption)

        # [Unit Adoption Calculations]!$CH$135 (PDS):
        cumulative_degraded_unprotected_area = self.get_cumulative_degraded_unprotected_area(delay_impact_of_protection_by_one_year, growth_rate_of_ocean_degradation)

        cumulative_degraded_area_under_protection = self.get_cumulative_degraded_area_under_protection(
                                                                    delay_impact_of_protection_by_one_year,
                                                                    disturbance_rate
                                                                    )

        result = self._area_units - cumulative_degraded_unprotected_area - cumulative_degraded_area_under_protection

        return result.clip(lower = 0.0)

####
        
    def get_annual_reduction_in_total_degraded_area(self, disturbance_rate, growth_rate_of_ocean_degradation,
                             delay_impact_of_protection_by_one_year) -> pd.Series:
        """
        This is the change in total degraded area in the adoption each year, added to the total undegraded area for t-1.
        Used to combine two adoptions, usually pds and reference solution (PDS - REF) like this:
            annual_reduction_in_total_degraded_area (REF) - annual_reduction_in_total_degraded_area (PDS).
        This is equivalent to:
            Cumulative Area Degraded in REF Scenario for year x  - Cumulative Area Degraded in PDS Scenario for year x - Cumulative Degradation Change (PDS - REF) for Year [x-1]

        Units: Millions ha.

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
        

    def get_total_emissions_reduction(self, disturbance_rate, growth_rate_of_ocean_degradation, delay_impact_of_protection_by_one_year, emissions_reduced_per_unit_area) -> pd.Series:

        # CO2-eq MMT Reduced
        # [CO2 Calcs]!B64

        total_undegraded_area = self.get_total_undegraded_area(growth_rate_of_ocean_degradation, disturbance_rate, delay_impact_of_protection_by_one_year)
        result = total_undegraded_area * emissions_reduced_per_unit_area
        
        return result
        

    def get_carbon_sequestration(self, sequestration_rate, disturbance_rate, growth_rate_of_ocean_degradation,
                             delay_impact_of_protection_by_one_year, delay_regrowth_of_degraded_land_by_one_year, use_adoption = True) ->pd.Series:
        
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

    def get_change_in_ppm_equivalent_series(self, 
                    sequestration_rate,
                    disturbance_rate,
                    growth_rate_of_ocean_degradation,
                    delay_impact_of_protection_by_one_year,
                    emissions_reduced_per_unit_area,
                    delay_regrowth_of_degraded_land_by_one_year,
                    use_adoption_for_carbon_sequestration_calculation ) -> pd.Series:
        """
            Each yearly reduction in CO2 (in million metric ton - MMT) is modeled as a discrete avoided pulse.
            A Simplified atmospheric lifetime function for CO2 is taken from Myhrvald and Caldeira (2012) based on the Bern Carbon Cycle model.
            Atmospheric tons of CO2 are converted to parts per million CO2 based on the molar mass of CO2 and the moles of atmosphere.
            CO2-eq emissions are treated as CO2 for simplicity and due to the lack of detailed information on emissions of other GHGs.
            If these other GHGs are a significant part of overall reductions, this model may not be appropriate.

        """
        # This is the implementation of the CO2 PPM Calculator in [CO2 Calcs]!A169

        # get_carbon_sequestration returns series used to build [CO2 Calcs]!$B$120
        # to match [CO2 Calcs]!$B$120, need to combine pds and ref at the ocean_solution level.
        sequestration = self.get_carbon_sequestration(
                sequestration_rate, 
                disturbance_rate, 
                growth_rate_of_ocean_degradation,
                delay_impact_of_protection_by_one_year,
                delay_regrowth_of_degraded_land_by_one_year,
                use_adoption_for_carbon_sequestration_calculation)
        
        
        total_emissions_reduction = self.get_total_emissions_reduction(disturbance_rate, growth_rate_of_ocean_degradation, delay_impact_of_protection_by_one_year, emissions_reduced_per_unit_area)

        reduction_plus_sequestration = total_emissions_reduction + sequestration

        result_years = list(range(self.base_year-1, self.end_year+1))
        results = pd.Series(index = result_years, dtype=np.float64)
        results = results.fillna(0.0)
        # (0.217 + 0.259*EXP(-(A173-$A$173+1)/172.9) + 0.338*EXP(-(A173-$A$173+1)/18.51) + 0.186*EXP(-(A173-$A$173+1)/1.186))
        # (0.217 + 0.259*EXP(-(current_year-year_zero+1)/172.9) + 0.338*EXP(-(current_year-year_zero+1)/18.51) + 0.186*EXP(-(current_year-year_zero+1)/1.186))

        for iter_year in result_years:
            year_results = []
            exponent= 0

            for _ in range(iter_year, result_years[-1] +1):
                year_net_adoption = reduction_plus_sequestration.loc[iter_year]
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
