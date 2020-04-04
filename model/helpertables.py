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
    def __init__(self, ac, pds_adoption_data_per_region, ref_datapoints, pds_datapoints,
                 ref_adoption_limits=None, pds_adoption_limits=None,
                 pds_adoption_trend_per_region=None, pds_adoption_is_single_source=False,
                 ref_adoption_data_per_region=None, use_first_pds_datapoint_main=True,
                 adoption_base_year=2014):
        """
        HelperTables.
           Arguments:
             ac = advanced_controls.py object, storing settings to control
               model operation.
             pds_adoption_data_per_region: dataframe with one column per region (World, OECD90, Eastern
               Europe, Latin America, etc).
             ref_datapoints: a DataFrame with columns per region and two rows for two years of data.
             pds_datapoints: a DataFrame with columns per region and two rows for two years of data.
             ref_adoption_limits: dataframe of total addressable market or total land area per major
               region for the Reference scenario.
             pds_adoption_limits: dataframe of total addressable market or total land area per major
               region for the PDS scenario.
             tla_per_region: dataframe of total land area per region
             pds_adoption_trend_per_region: adoption trend (predictions using 2nd Poly, 3rd Poly, etc
               as configured in the solution) with one column per region
             pds_adoption_is_single_source (bool): whether the adoption data comes from a single source
               or multiple, to determine how to handle stddev.
             ref_adoption_data_per_region: dataframe with one column per region (World, OECD90, Eastern
               Europe, Latin America, etc). This input is optional, only used for solutions containing
               Custom REF Adoption data. If ref_adoption_data_per_region is None, helpertables will
               interpolate between the values in ref_datapoints.
             use_first_pds_datapoint_main: Prior to the 2019 cohort updates to the solution models,
               the first year in pds_datapoints was copied into the result overriding any curve
               fitting. With the 2019 cohort, it is sometimes copied for the non-World regions
               and sometimes only copied for the regional results.
             adoption_base_year: solutions developed by the 2018 (and prior) cohorts used 2014
               as the base year for adoption. Solurions developed in the 2019 cohort use 2018
               as the base year.
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
        self.adoption_base_year = adoption_base_year

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
            first_year = self.ref_datapoints.first_valid_index()
            last_year = dd.CORE_END_YEAR
            adoption = self._linear_forecast(2014, last_year, self.ref_datapoints)

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

        if self.adoption_base_year > 2014:
            # The Drawdown 2020 models get REF data for the World region for 2014-2018 from PDS.
            funits = self.soln_pds_funits_adopted(suppress_override=True)
            main_region = list(adoption.columns)[0]
            years = np.arange(2014, self.adoption_base_year)
            adoption.loc[years, main_region] = funits.loc[years, main_region]
            adoption.sort_index(inplace=True)

            # The Drawdown 2020 models also still copy the first ref_datapoint (for 2018) into the
            # first cell of the table which is 2014. We implement bug-for-bug compatibility here.
            # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.i71c3bhbim59
            adoption.iloc[0, 1:] = self.ref_datapoints.iloc[0, 1:]
        else:
            # Where we have data, use the actual data not the interpolation. Excel model does this
            # even in Custom REF Adoption case, unlike the top of this routine where we copy Custom
            # adoption verbatim.
            # Note: this should be changed later. The jump between pds_datapoints
            # and the first row of custom adoption data causes anomalies in the regional results.
            # See: https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.c2a7v8n653ax
            adoption.update(self.ref_datapoints.iloc[[0]])

        if not suppress_override and self.ac.ref_adoption_use_pds_years:
            y = self.ac.ref_adoption_use_pds_years
            adoption.update(self.soln_pds_funits_adopted(suppress_override=True).loc[y, 'World'])

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
            adoption = self.pds_adoption_data_per_region.loc[first_year:, :].copy(deep=True)
        elif self.ac.soln_pds_adoption_basis == 'Linear':
            last_year = dd.CORE_END_YEAR
            adoption = self._linear_forecast(first_year, last_year, self.pds_datapoints)
        elif 'S-Curve' in self.ac.soln_pds_adoption_basis:
            adoption = self.pds_adoption_trend_per_region.copy(deep=True)
        elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
            adoption = self.pds_adoption_trend_per_region.fillna(0.0)
            if self.pds_adoption_is_single_source:
                # The World region can specify a single source (all the sub-regions use
                # ALL SOURCES). If it does, use that one source without curve fitting.
                adoption[main_region] = self.pds_adoption_data_per_region.loc[first_year:, main_region]
        elif self.ac.soln_pds_adoption_basis == 'Customized S-Curve Adoption':
            raise NotImplementedError('Custom S-Curve support not implemented')

        # Extend pds to match adoption's index
        pds_adoption_limits_extended = self.pds_adoption_limits.reindex(adoption.index,
                                                                        fill_value=np.inf)

        # cannot exceed the total addressable market or tla
        if self.pds_adoption_limits is not None:
            cols = adoption.columns
            adoption.loc[:, :] = np.min([adoption.values,
                                        pds_adoption_limits_extended[cols].fillna(0.).values],
                                        axis=0)

        if self.ac.soln_pds_adoption_regional_data:
            adoption.loc[:, main_region] = adoption.loc[:, dd.MAIN_REGIONS].sum(axis=1)
            if self.pds_adoption_limits is not None:
                adoption[main_region] = np.min([adoption[main_region].values,
                                                pds_adoption_limits_extended[main_region].fillna(0.0)], axis=0)

        if not suppress_override and self.ac.pds_adoption_use_ref_years:
            y = self.ac.pds_adoption_use_ref_years
            adoption.update(self.soln_ref_funits_adopted(suppress_override=True).loc[y, main_region])

        # Where we have actual data, use the actual data not the interpolation. Excel model does
        # this in all cases, even Custom PDS Adoption.
        # Note: this should be changed later. The jump between pds_datapoints
        # and the first row of custom adoption data causes anomalies in the regional results.
        # See: https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#
        zero_zero = adoption.iloc[0, 0]
        adoption.update(self.pds_datapoints.iloc[[0]])
        if not self.use_first_pds_datapoint_main:
            # Starting in Drawdown 2020 solutions, the World region computation is different
            # and no longer copies the first datapoint.
            adoption.iloc[0, 0] = zero_zero

        adoption.name = "soln_pds_funits_adopted"
        adoption.index.name = "Year"
        return adoption
