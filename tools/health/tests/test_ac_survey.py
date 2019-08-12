"""Tests for tools/health/ac_survey.py"""
import tempfile

import pandas as pd
import pytest
import tools.health.ac_survey

@pytest.mark.slow
def test_ac_survey():
    (_, outfile) = tempfile.mkstemp(prefix='scenario_uniq_values_', suffix='.csv')
    tools.health.ac_survey.survey(outfile)
    scn_df = pd.read_csv(outfile, index_col=0)
    assert len(scn_df.index) > 0
    assert not scn_df.eq(0.0).all(axis=None)
