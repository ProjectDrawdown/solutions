"""Tests for emissions_factors.py."""

from model import emissions_factors as ef

def test_CO2Equiv():
  c = ef.CO2Equiv(ef.SOURCE.AR5_WITH_FEEDBACK)
  assert c.CH4multiplier == 34
  assert c.N2Omultiplier == 298
  c = ef.CO2Equiv(ef.SOURCE.AR4)
  assert c.CH4multiplier == 25
  assert c.N2Omultiplier == 298
  c = ef.CO2Equiv(ef.SOURCE.SAR)
  assert c.CH4multiplier == 21
  assert c.N2Omultiplier == 310

def test_string_to_conversion_source():
  assert ef.string_to_conversion_source("AR5 with feedback") == ef.SOURCE.AR5_WITH_FEEDBACK
  assert ef.string_to_conversion_source("AR4") == ef.SOURCE.AR4
  assert ef.string_to_conversion_source("SAR") == ef.SOURCE.SAR
