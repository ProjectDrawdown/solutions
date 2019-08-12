"""Tests for tools/health/landsurvey.py"""
import tempfile

import pandas as pd
import pytest
import tools.health.landsurvey

@pytest.mark.slow
def test_survey():
    (_, outfile) = tempfile.mkstemp(prefix='survey_', suffix='.csv')
    tools.health.landsurvey.full_survey(outfile)
    ls_df = pd.read_csv(outfile, index_col=0)
    assert len(ls_df.index) > 0

    (_, outfile) = tempfile.mkstemp(prefix='survey_', suffix='.csv')
    tools.health.landsurvey.land_alloc_sum(outfile=outfile)
    ls_df = pd.read_csv(outfile, index_col=0)
    assert len(ls_df.index) > 0
