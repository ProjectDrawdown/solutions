"""Code shared by all integrations."""

import os
import numpy as np
import pandas as pd
from model import integration
from solution import factory
from pathlib import Path

# #######################################################################################################
#
# Set up integrations

integration_suffix = "int2021"
"""Suffix to add to scenario and other names when saving updated versions.
Make it sufficiently unique that it will not conflict with any existing filename suffixes."""

testmode = False
"""If True, integration will try to load data from snapshots first, and only use live data if snapshots are unavailable.
This mode is intended for testing against original Excel."""

def integration_start(settestmode=False):
    os.environ["DDINTEGRATE"] = integration_suffix
    global testmode
    testmode = settestmode

def integration_clean():
    # remove any integration files in solution/, data/ and this directories
    # we have our own version of this code so it can operate even if there's no current integration...
    root = Path(__file__).parents[1]
    for f in (root/'solution').glob(f'**/*_{integration_suffix}.*'):
        f.unlink()
    for f in (root/'data').glob(f'**/*_{integration_suffix}.*'):
        f.unlink()
    for f in (root/'integrations').glob(f'**/*_{integration_suffix}.*'):
        f.unlink()


# #######################################################################################################
#
# Audit logs

integration_name = None
auditlog = {}

def start_audit(name):
    global integration_name
    integration_name = name
    auditlog[name] = {}
    def audit(result_name, result):
        auditlog[name][result_name] = result.copy()
    return audit

def _shortform(item):
    vals = item.iloc[0] if isinstance(item, pd.DataFrame) else item
    sz = min(len(vals),5)
    return f"{item.shape}: {vals.to_numpy()[:sz]}"


def show_log(name=None):
    for logname in auditlog.keys():
        if name is None or name == logname:
            print("-----------------------")
            print(logname)
            for (title, value) in auditlog[logname].items():
                if value is None:
                    print(f"{title:>30}: empty")
                else:
                    print(f"{title:>30}: {_shortform(value)}")

def get_logitem(itemname, lname=None):
    for logname in auditlog.keys():
        if lname is None or lname == logname:
            for (title, value) in auditlog[logname].items():
                if title.startswith(itemname):
                    return value
    return None


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

def pdsify(df) -> pd.DataFrame:
    """Take a df or series and replicate it to PDS1, PDS2, PDS3 dims"""
    return pd.concat({'PDS1':df, 'PDS2':df, 'PDS3':df}, axis=1)

def df_isclose(df1, df2):
    """Return True if the dfs are within a tolerance of one another"""
    return np.allclose(df1.to_numpy(), df2.to_numpy(), atol=1e-06, equal_nan=True)


def read_as_series( datadir, file ):
    return pd.read_csv(datadir/file, index_col="Year")['World']

def demand_adjustment(title, demand, supply):
    """Essentially return the minimum of suppy and demand.  Also prints if supply is less than demand"""
    # Note the demand>supply condition *should* be sufficient, but for whatever weird
    # reason it is copying if supply is nan.  Hence the added condition.
    # I'm sure I'm overlooking something stupid, as I can't see how this bug could exist.
    newdemand = demand.mask((demand>supply)&~supply.isna(), supply)
    if (newdemand<demand).any(axis=None):
        overshoot = (demand - newdemand)
        print(f"{title} adjusted for {(overshoot>0).sum().sum()}/{overshoot.size} items by max {overshoot.max().max()}")
    return newdemand

# #######################################################################################################
#
# Reading data

testdir = Path(__file__).parent/"testmodedata"

def load_solution_adoptions(solution_name, scenario_names) -> pd.DataFrame :
    """Return the adoption of solution in three scenarios, labeled PDS1, PDS2 and PDS3.
    Returns Year x (PDS1,PDS2,PDS3) dataframe."""
    if testmode: # look for a saved snapshot
        filename = testdir/f"{integration_name}_{solution_name}_adoption.csv"
        if filename.is_file():
            return pd.read_csv(filename, index_col="Year")
    # else
    pds1 = factory.load_scenario(solution_name, scenario_names[0]).ht.soln_pds_funits_adopted()['World']
    pds2 = factory.load_scenario(solution_name, scenario_names[1]).ht.soln_pds_funits_adopted()['World']
    pds3 = factory.load_scenario(solution_name, scenario_names[2]).ht.soln_pds_funits_adopted()['World']
    return pd.DataFrame({"PDS1": pds1, "PDS2": pds2, "PDS3": pds3})

def load_solution_tam(solution_name, scenario_name) -> pd.Series:
    """Return the Total Addressable Market for solution as a series"""
    if testmode: # look for a saved snapshot
        filename = testdir/f"{integration_name}_{solution_name}_tam.csv"
        if filename.is_file():
            return pd.read_csv(filename, index_col="Year")['World']
    # else
    return factory.load_scenario(solution_name, scenario_name).tm.pds_tam_per_region()['World']
