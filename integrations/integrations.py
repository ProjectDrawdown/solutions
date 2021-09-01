"""Code shared by all integrations."""

import numpy as np
import pandas as pd
from solution import factory

# #######################################################################################################
#
# Set up integrations

suffix = "int"
"""Suffix to add to scenario and other names when saving updated versions."""

# #######################################################################################################
#
# Updating Solutions

def update_solution(solution_name, scenarios_names, tam, adoptions):
    pass

# #######################################################################################################
#
# Utilities

# A few common operations written as functions to keep the code more readable.
# This is all about making the dimensions match up properly.

def series_outer_product(series1, series2) -> pd.DataFrame :
    """Compute the outer product of series1 and series2, where series1 becomes the rows and series2 the columns."""
    return pd.DataFrame(np.outer(series1, series2), columns=series2.index, index=series1.index)

def series_sub_df(series, df) -> pd.DataFrame :
    """Compute  series-df  keeping the columns of the df.  Used when the 2nd operand has columns for 
    PDS1, PDS2, PDS3, but the first does not."""
    # We could duplicate the first operand, but inverting the subtraction lets us do this in a single operation.
    return -df.sub(series, axis=0)

def df_mult_series(df, series) -> pd.DataFrame :
    """Compute df*series by column (that is, each column of df is multiplied by series)"""
    return df.mul(series, axis=0)

def load_solution_tam(solution_name, scenario_name=None) -> pd.Series :
    """Return the REF TAM for the solution, using PDS2 unless otherwise specified.
    Returns Worldwide data only."""
    if scenario_name is None:
        scenario_name = "PDS2"
    return factory.load_scenario(solution_name, scenario_name).tm.ref_tam_per_region()['World']

def load_solution_adoptions(solution_name, scenario_names) -> pd.DataFrame :
    """Return the adoption of solution in three scenarios, labeled PDS1, PDS2 and PDS3.
    Returns Year x (PDS1,PDS2,PDS3) dataframe."""
    pds1 = factory.load_scenario(solution_name, scenario_names[0]).ht.soln_pds_funits_adopted()['World']
    pds2 = factory.load_scenario(solution_name, scenario_names[1]).ht.soln_pds_funits_adopted()['World']
    pds3 = factory.load_scenario(solution_name, scenario_names[2]).ht.soln_pds_funits_adopted()['World']
    return pd.DataFrame({"PDS1": pds1, "PDS2": pds2, "PDS3": pds3})

