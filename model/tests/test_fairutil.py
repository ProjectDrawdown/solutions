"""Tests for fairutil.py."""

import fair
import pandas as pd

from model import fairutil


def test_baseline_emissions():
    b = fairutil.baseline_emissions()
    assert 2015 in b.index
    r = pd.DataFrame(fair.RCPs.rcp45.Emissions.emissions.copy(), columns=fairutil.ghg.keys(),
            index=fair.RCPs.rcp45.Emissions.year)
    r.index = r.index.astype(int)
    assert not b.equals(r)

def test_fair_scm_kwargs():
    k = fairutil.fair_scm_kwargs()
    assert 'r0' in k
