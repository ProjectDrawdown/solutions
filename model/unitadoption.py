class UnitAdoption:
    def na_funits(self, ref_sol_funits, pds_sol_funits):
        '''Net annual functional units adopted.

        ref_sol_funits: Reference solution: Annual functional units adopted
        pds_sol_funits: PDS solution: Annual functional units adopted

        Both inputs and return value is a DataFrame with and index of years,
        columns for each region and floating point data values.

        This represents the total additional functional units captured either
        by the CONVENTIONAL mix of technologies/practices in the REF case
        scenario, OR total growth of the SOLUTION in the PDS scenario,
        i.e. in addition to the current growth of the SOLUTION in the REF
        scenario.

        This is used to calculate the Operating Cost, Grid, Fuel, Direct and
        (optionally) Indirect Emissions.
        '''
        return pds_sol_funits - ref_sol_funits

    def life_rep_years(self, life_cap_funits, aau_funits):
        '''Lifetime Replacement for solution/conventional in years

        life_cap_funits: Lifetime Capacity per implementation unit
        aau_funits: Average Annual Capacity per implementation unit
        '''
        return round(life_cap_funits / aau_funits, 0)

    def sol_cum_iunits(self, sol_funits, aau_funits):
        '''Cumulative solution implemenetation units installed

        sol_funits: Total annual solution functional units
        aau_funits: Average Annual Capacity per implementation unit

        This takes the Total Annual Functional Units PDS or REF and divides that by
        the Average Annual Use/production per Solution Implementation Unit
        to derive the Total Implementation Units Required in each given year PDS or REF.

        This table is used to calculate the yearly increase in Implementation
        Units Adopted of Solution in PDS or REF.  
        '''
        return sol_funits / aau_funits

    def sol_ann_iunits(self, sol_cum_iunits, life_rep_years):
        '''New implementation units required (includes replacement Units)

        sol_cum_iunits: Cumulative solution implementation units installed
        life_rep_years: Lifetime Replacement in years

        Should reflect the unit lifetime assumed in the First Cost tab.
        For simplicity assumed a fix lifetime rather than a gaussian
        distribution, but this can be changed if needed. 

        This is used to calculate Advanced Controls Output of Solution
        Implementation Units Adopted.  This is also used to Calculate
        First Cost, Marginal First Cost and NPV.
        '''
        # for index, row in sol_cum_iunits.iterrows():

        return
