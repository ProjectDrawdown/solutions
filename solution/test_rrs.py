"""Test rrs.py."""

import pytest
from . import rrs


def test_rrs():
    tam_data = rrs.energy_ref_tam().read_text(encoding='utf-8')
    assert 'Baseline Cases' in tam_data
    assert 'Conservative Cases' in tam_data
    assert 'Ambitious Cases' in tam_data


def test_rrs_vma():
    r = rrs.RRS(total_energy_demand=22548.30, soln_avg_annual_use=1841.66857142857,
        conv_avg_annual_use=4946.840187342)
    assert r.substitutions['@energy_mix_coal@'] == pytest.approx(0.38699149767)
