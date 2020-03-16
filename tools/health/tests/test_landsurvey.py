"""Tests for tools/health/landsurvey.py"""
import tempfile

import pandas as pd
import pytest

from tools.health.landsurvey import full_survey, get_land_scenarios, land_alloc_sum


@pytest.mark.slow
def test_survey():
    land_scenarios = get_land_scenarios()
    (_, outfile) = tempfile.mkstemp(prefix='survey_', suffix='.csv')
    full_survey(land_scenarios, outfile)
    ls_df = pd.read_csv(outfile, index_col=0)
    assert len(ls_df.index) > 0

    (_, outfile) = tempfile.mkstemp(prefix='survey_', suffix='.csv')
    land_alloc_sum(land_scenarios, outfile=outfile)
    ls_df = pd.read_csv(outfile, index_col=0)
    assert len(ls_df.index) > 0
