"""Tests for tools/health/survey.py"""
import tempfile

import pandas as pd
import pytest
import tools.health.survey

@pytest.mark.slow
def test_survey():
    (_, outfile) = tempfile.mkstemp(prefix='survey_', suffix='.csv')
    tools.health.survey.scenario_survey(outfile)
    surveydata = pd.read_csv(outfile, index_col=False, skipinitialspace=True, header=0,
            skip_blank_lines=True, comment='#')
    assert len(surveydata.index) > 0
    regional_nonzero_adoption = surveydata.loc[surveydata['RegionalFractionAdoption'] != 0.0]
    assert len(regional_nonzero_adoption) > 0
    regional_nonzero_tam = surveydata.loc[surveydata['RegionalFractionTAM'] != 0.0]
    assert len(regional_nonzero_tam) > 0
