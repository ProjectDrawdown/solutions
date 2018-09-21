"""Test advanced_controls.py."""

import pytest

import advanced_controls


def test_learning_rate():
    """Test efficiency versus learning rate."""
    ac = advanced_controls.AdvancedControls(
        pds_2014_cost=0, conv_2014_cost=0,
        pds_first_cost_efficiency_rate=0.2,
        pds_first_cost_below_conv=True,
        conv_first_cost_efficiency_rate=0.4786)
    assert ac.pds_first_cost_learning_rate == pytest.approx(0.8)
    assert ac.conv_first_cost_learning_rate == pytest.approx(0.5214)
    ac = advanced_controls.AdvancedControls(
        pds_2014_cost=0, conv_2014_cost=0,
        pds_first_cost_efficiency_rate=0.33333333,
        pds_first_cost_below_conv=True,
        conv_first_cost_efficiency_rate=1.0)
    assert ac.pds_first_cost_learning_rate == pytest.approx(0.66666667)
    assert ac.conv_first_cost_learning_rate == pytest.approx(0.0)
