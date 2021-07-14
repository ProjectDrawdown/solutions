"""Tests for tools/health/survey.py"""
import pytest
from tools.health.survey import scenario_survey

@pytest.mark.slow
def test_survey():
    surveydata = scenario_survey()
    assert len(surveydata.index) > 0
    regional_nonzero_adoption = surveydata.loc[surveydata['RegionalFractionAdoption'] != 0.0]
    assert len(regional_nonzero_adoption) > 0
    regional_nonzero_tam = surveydata.loc[surveydata['RegionalFractionTAM'] != 0.0]
    assert len(regional_nonzero_tam) > 0
