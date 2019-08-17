"""Tests for faircalc.py.

Finite Amplitude Impulse Response (FaIR) Calcs module.

Computes impacts of CO2 + CH4 + N2O (et al) emissions using
https://fair.readthedocs.io/en/latest/examples.html
"""

import numpy as np
import pandas as pd
from model import co2calcs
from model import faircalcs

def assert_series_not_equal(*args, **kwargs):
    try:
        pd.testing.assert_series_equal(*args, **kwargs)
    except AssertionError:
        pass
    else:
        raise AssertionError

def test_fair():
    co2eq_mmt_reduced = pd.Series(range(100, 330, 5), index=range(2015, 2061))
    fr = faircalcs.FaIRcalcs(co2eq_mmt_reduced=co2eq_mmt_reduced)
    C,F,T = fr.CFT()
    # we deliberately do not test the values; that is a job for libFaIR's unit tests.
    # we check that the result is rational. It should be changes since pre-industrial time, which
    # should be 1780 - present. Assert it is at least 230 years.
    assert len(C) > 230
    assert len(F) > 230
    assert len(T) > 230


def test_co2_sequestered_global():
    co2eq_mmt_reduced = pd.Series(range(100, 330, 5), index=range(2015, 2061))
    co2_sequestered_global = pd.Series(range(101, 423, 7), index=range(2015, 2061))
    fr = faircalcs.FaIRcalcs(co2eq_mmt_reduced=co2eq_mmt_reduced, co2_sequestered_global=None)
    C,F,T = fr.CFT()
    fr = faircalcs.FaIRcalcs(co2eq_mmt_reduced=co2eq_mmt_reduced,
            co2_sequestered_global=co2_sequestered_global)
    C1,F1,T1 = fr.CFT()
    fr = faircalcs.FaIRcalcs(co2eq_mmt_reduced=None, co2_sequestered_global=co2_sequestered_global)
    C2,F2,T2 = fr.CFT()
    assert_series_not_equal(C, C1)
    assert_series_not_equal(F, F1)
    assert_series_not_equal(T, T1)
    assert_series_not_equal(C1, C2)
    assert_series_not_equal(F1, F2)
    assert_series_not_equal(T1, T2)
    assert_series_not_equal(C, C2)
    assert_series_not_equal(F, F2)
    assert_series_not_equal(T, T2)


def test_fair_baseline():
    co2eq_mmt_reduced = pd.Series(np.nan, index=range(2015, 2061))
    fr = faircalcs.FaIRcalcs(co2eq_mmt_reduced=co2eq_mmt_reduced)
    C,F,T = fr.CFT_baseline()
    # We do not have asserts about values from the RCP, just assert that there is something there.
    assert len(C) > 230
    assert len(F) > 230
    assert len(T) > 230
