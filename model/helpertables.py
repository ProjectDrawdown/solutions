"""Helper Tables module.

Provides adoption data for use in the other modules. The source of the adoption
data is selectable according to the solution. Helper Tables can pull in one of
the Linear/2nd order poly/3rd order poly/etc curve fitting implementations
from interpolation.py, or use a simple linear fit implemented here.
"""
from functools import lru_cache
import pandas as pd
import numpy as np
import model.dd as dd


class HelperTables:
    """ Implementation for the Helper Tables module. """
    def __init__(self, ac, 
            ref_adoption_data_per_region=None, 
            pds_adoption_data_per_region=None, 
            ref_datapoints=None, 
            pds_datapoints=None,
            pds_adoption_trend_per_region=None, 
            ref_adoption_limits=None, 
            pds_adoption_limits=None,
            pds_adoption_is_single_source=False,
            copy_ref_datapoint=True,
            copy_pds_datapoint=True,
            copy_datapoint_to_year=None,
            copy_pds_to_ref=False,
            use_first_ref_datapoint_main=False,
            use_first_pds_datapoint_main=True,           
            adoption_base_year=2014):
        """
        Helper Tables are the final step in constructing Adoption Prognostications.  The select between
        the different types of REF and PDS adoption that can be configured, and they handle the 
        interrelationship between the two.
        Helper Tables code in the Excel diverged in some cases, and so this code has variations that
        are controlled by parameter (listed in the second section below)

        Normal Parameters: 
         * ac = AdvancedControls.  A number of crucial parameters are retrieved from ac:
             * ac.soln_ref_adoption_basis:  choice of REF adoption type
             * ac.soln_pds_adoption_basis:  choice of PDS adoption type
             * ac.soln_ref_adoption_regional_data:  whether REF world data should be summed from regions
             * ac.soln_pds_adoption_regional_data:  whether PDS world data should be summed from regions
             * ac.ref_adoption_use_pds_years: if set to years ys, copy pds[ys,'World'] to ref (from AC!F26, Y-REF)
             * ac.pds_adoption_use_ref_years: if set to years ys, copy ref[ys,'World'] to pds (from AC!F26, Y-PDS)

         * ref_adoption_data_per_region: The REF adoption data to use for Fully Custom REF adoptions only.
           Not required for default REF adoptions.  (Year x Region) dataframe.
         * pds_adoption_data_per_region: The PDS adoption data to use, for Fully Custom PDS adoptions and sometimes
           for Existing Prognostications (see `single_source` option below).  
           Not required when PDS adoption is forecast. (Year x Region) dataframe.
         * pds_adoption_trend_per_region: The PDS adoption data to use for forecast or Existing Prognostication
           PDS adoptions.  (Year x Region) dataframe.

         * ref_datapoints: The first and last adoption estimates per region.  Used for default REF forecasting;  
           otherwise not required.  (2 x Region) dataframe  (from HT!C21:L22)
         * pds_datapoints: The first and last adoption estimates per region.  Used for PDS _Linear_ forecast only;
           otherwise not required.  (2 x Region) dataframe  (from HT!C85:L86)

         * ref_adoption_limits: TAM or TLA limits for REF adoption.  If set, bounds REF adoption. (1 x Regions) dataframe
         * pds_adoption_limits: TAM or TLA limits for PDS adoption.  If set, bounds PDS adoption. (1 x Regions) dataframe

        Weird Case Fitting Parameters:  
        The following parameters all handle weirdnesses in how various Excel spreadsheets evolved.  The automated
        generation code attempts to automatically figure out which of these options apply, but it should not be 
        trusted.  You should look at the _formulas_ in the Excel workbook to determine how to set these parameters:

         * copy_ref_datapoint: In some models, the 'current adoption' data is copied from the ref datapoints to the
           results, overriding them.  Can be detected in the Excel by formula (=<col>21) in the first row of the REF table
           (where <col> is standing in for the current column)

         * copy_pds_datapoint: The same idea, but in the PDS table.  There is one additional quirk, however: if
           the value of copy_pds_datapoint is 'Ref Table' (instead of just True), the value is copied from the first
           row of the REF _table_ instead of the PDS current adoption.  Look at the actual row number of the Excel
           formula to see which kind of copy is being done.
        
         * copy_datapoint_to_year: The year in which the datapoint gets copied _to_.  Defaults to the base adoption year.
           But there are also models that copy it to the year 2014, even if that is not the base adoption year.
           Affects both copy_ref_datapoint and copy_pds_datapoint.
        
         * use_first_pds_datapoint_main: This parameter determines whether copy_pds_datapoint applies to the 'World'
           column or not.  If True (the default), copy_pds_datapoint overrides the 'World' column.  If False, 
           copy_pds_datapoint only overrides regional data.  
         * use_first_ref_datapoint_main: Ditto but for ref.  Note the default value for these options are opposite
           each other.  That is unfortunately necessary for backwards compatibility.
        
         * copy_pds_to_ref: In some models, World data (only) is copied from the PDS model to the REF model for 
           years before base year. This can be detected in the Excel by formula of the form =Cxx in the first
           column of the REF table, extending from 2014 through some number of years.  The number of years to copy is
           determined by the parameter adoption_base_year, below.

         * adoption_base_year: THIS PARAMETER IS MISLEADINGLY NAMED.  Setting it does _not_ alter the base year of
           the adoption.  What it does do is determine how many years copy_pds_to_ref should copy.  If set to 2018
           (the default), it will copy years 2014-2017.  Set it to one year past the last year copy_pds_to_ref
           should modify.  If copy_pds_to_ref is False, this parameter has no effect.
         
         * pds_adoption_is_single_source: (bool): whether the adoption data comes from a single source
           or multiple, to determine how to handle stddev.   See the inline comment.
        
        """
        self.ac = ac
        self.ref_datapoints = ref_datapoints
        self.pds_datapoints = pds_datapoints
        self.ref_adoption_limits = ref_adoption_limits
        self.pds_adoption_limits = pds_adoption_limits
        self.pds_adoption_data_per_region = pds_adoption_data_per_region
        self.pds_adoption_trend_per_region = pds_adoption_trend_per_region
        self.pds_adoption_is_single_source = pds_adoption_is_single_source
        self.ref_adoption_data_per_region = ref_adoption_data_per_region
        self.use_first_pds_datapoint_main = use_first_pds_datapoint_main
        self.use_first_ref_datapoint_main = use_first_ref_datapoint_main
        self.copy_pds_to_ref = copy_pds_to_ref
        self.copy_through_year = adoption_base_year     # Note rename, so as not to conflict with defined function
        self.copy_ref_datapoint = copy_ref_datapoint
        self.copy_pds_datapoint = copy_pds_datapoint
        self.copy_datapoint_to_year = copy_datapoint_to_year


    def ref_adoption_type(self):
      return self.ac.soln_ref_adoption_basis
    
    def pds_adoption_type(self):
      return self.ac.soln_pds_adoption_basis
    
    def adoption_base_year(self):
      """The year from which adoption is prognosticated.  The adoption at the base year is assumed to be historical data."""
      return self.pds_datapoints.first_valid_index()


    @lru_cache()
    def soln_ref_funits_adopted(self, suppress_override=False):
        """Cumulative Adoption in funits, interpolated between two ref_datapoints.

           Arguments:
             suppress_override: disable ref_adoption_use_pds_years processing. This is
               used to avoid an infinite loop if both pds_adoption_use_ref_years and
               ref_adoption_use_pds_years are set.

           SolarPVUtil 'Helper Tables'!B26:L73
        """

        if self.ac.soln_ref_adoption_basis == 'Custom':
            assert self.ref_adoption_data_per_region is not None
            adoption = self.ref_adoption_data_per_region.loc[2014:, :].copy(deep=True)
        else:
            last_year = dd.CORE_END_YEAR
            adoption = self._linear_forecast(2014, last_year, self.ref_datapoints)
        #print(f"REF A: {adoption.loc[2014,'World']}")

        # cannot exceed tam or tla
        if self.ref_adoption_limits is not None:
            cols = adoption.columns
            adoption.loc[:, :] = np.min([adoption.values, 
                                         self.ref_adoption_limits[cols].fillna(0.).values], 
                                        axis=0)

        if self.ac.soln_ref_adoption_regional_data:
            adoption.loc[:, 'World'] = adoption[dd.MAIN_REGIONS].sum(axis=1)
            if self.ref_adoption_limits is not None:
                adoption['World'] = np.min([adoption['World'], 
                                            self.ref_adoption_limits['World'].fillna(0.0)],
                                            axis=0)

        if self.copy_through_year > 2014 and self.copy_pds_to_ref:
            # The Drawdown 2020 models get REF data for the World region for 2014-2018 from PDS.
            funits = self.soln_pds_funits_adopted(suppress_override=True)
            main_region = list(adoption.columns)[0]
            years = np.arange(2014, self.copy_through_year)
            adoption.loc[years, main_region] = funits.loc[years, main_region]
            adoption.sort_index(inplace=True)

            # The Drawdown 2020 models also still copy the first ref_datapoint (for 2018) into the
            # first cell of the table which is 2014. We implement bug-for-bug compatibility here.
            # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.i71c3bhbim59
            adoption.iloc[0, 1:] = self.ref_datapoints.iloc[0, 1:]
            #print(f"REF B: {adoption.loc[2014,'World']}")
        elif self.copy_ref_datapoint:
            copy_year = self.copy_datapoint_to_year or self.ref_datapoints.first_valid_index()
            override = self.ref_datapoints.iloc[0]
            if not self.use_first_ref_datapoint_main:
                override = override[1:]  # Remove main region (World) from series
            adoption.loc[copy_year].update(override)
            #print(f"REF C: {adoption.loc[2014,'World']}")

        if not suppress_override and self.ac.ref_adoption_use_pds_years:
            # This option is currently never used.
            y = self.ac.ref_adoption_use_pds_years
            adoption.update(self.soln_pds_funits_adopted(suppress_override=True).loc[y, 'World'])
            #print(f"REF D: {adoption.loc[2014,'World']}")

        adoption.name = "soln_ref_funits_adopted"
        adoption.index.name = "Year"
        return adoption

    def _linear_forecast(self, first_year, last_year, datapoints):
        """Interpolates a line between datapoints, and fills in adoption.
           first_year: an integer, the first year to interpolate data for.
           last_year: an integer, the last year to interpolate data for.
           datapoints: a Pandas DataFrame with two rows of adoption data, indexed by year.
             The columns are expected to be regions like 'World', 'EU', 'India', etc.
             There can be as many columns as desired, but the columns in datapoints
             must match the columns in adoption.
             The year+adoption data provide the X,Y coordinates for a line to interpolate.
        """
        year1 = datapoints.index.values[0]
        year2 = datapoints.index.values[1]

        years = np.arange(first_year, last_year + 1).reshape(-1, 1)
        adopt1 = datapoints.iloc[[0]].values
        adopt2 = datapoints.iloc[[1]].values

        fract_years = (years - year1) / (year2 - year1)
        fract_adopt = fract_years * (adopt2 - adopt1)

        adoption = pd.DataFrame(fract_adopt + adopt1,
                                columns=datapoints.columns, 
                                index=years.squeeze(), 
                                dtype="float")
        return adoption

    @lru_cache()
    def soln_pds_funits_adopted(self, suppress_override=False):
        """Cumulative Adoption in funits in the PDS.

           Arguments:
             suppress_override: disable pds_adoption_use_ref_years processing. This is
               used to avoid an infinite loop if both pds_adoption_use_ref_years and
               ref_adoption_use_pds_years are set.

           SolarPVUtil 'Helper Tables'!B90:L137
        """
        main_region = dd.REGIONS[0]
        first_year = self.pds_datapoints.first_valid_index()
        if self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
            adoption = self.pds_adoption_data_per_region.loc[2014:, :].copy(deep=True)
        elif self.ac.soln_pds_adoption_basis == 'Linear':
            last_year = dd.CORE_END_YEAR
            adoption = self._linear_forecast(2014, last_year, self.pds_datapoints)
        elif 'S-Curve' in self.ac.soln_pds_adoption_basis:
            adoption = self.pds_adoption_trend_per_region.copy(deep=True)
        elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
            adoption = self.pds_adoption_trend_per_region.fillna(0.0)
            if self.pds_adoption_is_single_source:
                # The World region can specify a single source (all the sub-regions use
                # ALL SOURCES). If it does, use that one source without curve fitting.
                adoption[main_region] = self.pds_adoption_data_per_region[main_region]
        elif self.ac.soln_pds_adoption_basis == 'Customized S-Curve Adoption':
            raise NotImplementedError('Custom S-Curve support not implemented')
        #print(f"A: {adoption.loc[2014,'World']}")

        # cannot exceed the total addressable market or tla
        if self.pds_adoption_limits is not None:
            # Extend pds to match adoption's index
            pds_adoption_limits_extended = self.pds_adoption_limits.reindex(adoption.index,
                                                                        fill_value=np.inf)
            cols = adoption.columns
            adoption.loc[:, :] = np.min([adoption.values,
                                        pds_adoption_limits_extended[cols].fillna(0.).values],
                                        axis=0)
            #print(f"B: {adoption.loc[2014,'World']}")

        if self.ac.soln_pds_adoption_regional_data:
            adoption.loc[:, main_region] = adoption.loc[:, dd.MAIN_REGIONS].sum(axis=1)
            if self.pds_adoption_limits is not None:
                adoption[main_region] = np.min([adoption[main_region].values,
                                                pds_adoption_limits_extended[main_region].fillna(0.0)], axis=0)
            #print(f"C: {adoption.loc[2014,'World']}")

        if not suppress_override and self.ac.pds_adoption_use_ref_years:
            y = self.ac.pds_adoption_use_ref_years
            adoption.update(self.soln_ref_funits_adopted(suppress_override=True).loc[y, main_region])
            #print(f"D: {adoption.loc[2014,'World']}")

        if self.copy_pds_datapoint:
            #breakpoint()

            #print(f"params are {self.copy_pds_datapoint} and {self.use_first_pds_datapoint_main}")
            copy_year = self.copy_datapoint_to_year or self.adoption_base_year()
            if self.copy_pds_datapoint == 'Ref Table':
                override = self.soln_ref_funits_adopted(suppress_override=True).loc[copy_year]
            else:
                override = self.pds_datapoints.iloc[0]

            if not self.use_first_pds_datapoint_main:
                override = override[1:]  # Remove main region (World) from series
            adoption.loc[copy_year].update(override)
            #print(f"E: {adoption.loc[2014,'World']}")

        adoption.name = "soln_pds_funits_adopted"
        adoption.index.name = "Year"
        return adoption
