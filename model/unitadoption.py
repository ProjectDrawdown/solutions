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
