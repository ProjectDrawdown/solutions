"""Tests for vma.py."""

import io
import pathlib
import tempfile

from model import vma
import pytest


basedir = pathlib.Path(__file__).parents[2]
datadir = pathlib.Path(__file__).parents[0].joinpath('data')


def test_vals_from_real_soln():
    """ Values from Silvopasture Variable Meta Analysis """
    f = datadir.joinpath('vma1_silvopasture.csv')
    v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0)
    result = v.avg_high_low()
    expected = (314.15, 450.0, 178.3)
    assert result == pytest.approx(expected)


def test_source_data():
    s = """Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime
        Check that this text is present, 0%, %, 0, 0
        """
    f = io.StringIO(s)
    v = vma.VMA(filename=f)
    assert 'Check that this text is present' in v.source_data.to_html()


def test_invalid_discards():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime
        a, 10000, , 
        b, 10000, , 
        c, 10000, , 
        d, 10000, , 
        e, 10000, , 
        f, 10000, , 
        g, 10000, , 
        h, 10000, , 
        i, 10000, , 
        j, 10000, , 
        k, 10000, , 
        l, 10000, , 
        m, 10000, , 
        n, 10000, , 
        o, 10000, , 
        p, 10000000000, , 
        q, 1, , 
    """)
    v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0)
    result = v.avg_high_low()
    expected = (10000, 10000, 10000)  # The 10,000,000,000 and 1 values should be discarded.
    assert result == pytest.approx(expected)


def test_single_study():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime
      A, 39%, %, 
      """)
    v = vma.VMA(filename=f)
    result = v.avg_high_low()
    expected = (0.39, 0.39, 0.39)
    assert result == pytest.approx(expected)


def test_missing_columns():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime
      A, 1000
      """)
    v = vma.VMA(filename=f)
    result = v.avg_high_low()
    expected = (1000, 1000, 1000)
    assert result == pytest.approx(expected)


def test_inverse():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime
      A, 43%, %, 
      """)
    postprocess = lambda x, y, z: (1.0 - x, 1.0 - y, 1.0 - z)
    v = vma.VMA(filename=f, postprocess=postprocess)
    result = v.avg_high_low()
    expected = (0.57, 0.57, 0.57)
    assert result == pytest.approx(expected)


def test_avg_high_low_key():
    f = datadir.joinpath('vma1_silvopasture.csv')
    v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0)
    avg = v.avg_high_low(key='mean')
    assert avg == pytest.approx(314.15)
    low = v.avg_high_low(key='low')
    assert low == pytest.approx(178.3)
    with pytest.raises(ValueError):
        v.avg_high_low(key='not a key')


def test_avg_high_low_exclude():
    f = datadir.joinpath('vma21_silvopasture.csv')
    v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0)
    assert v.avg_high_low()[0] == pytest.approx(4.64561688311688)


def test_generate_vma_dict():
    vma_dict = vma.generate_vma_dict(datadir)
    assert len(vma_dict) == 2
    assert 'Current Adoption' in vma_dict


def test_fixed_summary():
    vma_dict = vma.generate_vma_dict(datadir)
    v = vma_dict['Testing Fixed Summary']
    (avg, high, low) = v.avg_high_low()
    assert (avg, high, low) == (2.0, 3.0, 1.0)


def test_avg_high_low_by_regime():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime
      A, 0.4, Mha,, 1.0, False, Temperate/Boreal-Humid
      B, 0.5, Mha,, 1.0, False, Temperate/Boreal-Humid
      C, 0.6, Mha,, 1.0, False, Tropical-Humid
      """)
    v = vma.VMA(filename=f)
    result = v.avg_high_low()
    assert result[0] == pytest.approx(0.5)
    result = v.avg_high_low(regime='Temperate/Boreal-Humid')
    assert result[0] == pytest.approx(0.45)


def test_no_warnings_in_avg_high_low():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime
      A, 1.0, Mha,, 0.0, False
      B, 1.0, Mha,, 0.0, False
      C, 1.0, Mha,, 0.0, False
      """)
    with pytest.warns(None) as warnings:
        v = vma.VMA(filename=f)
        _ = v.avg_high_low()
    assert len(warnings) == 0


def test_write_to_file():
    f = tempfile.NamedTemporaryFile(mode='w')
    f.write(r"""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime
      A, 1.0,,,,
      B, 1.0,,,,
      C, 1.0,,,,
      """)
    f.flush()
    v = vma.VMA(filename=f.name)
    df = v.source_data.copy(deep=True)
    df.loc[0, 'Source ID'] = 'updated source ID'
    v.write_to_file(df)
    assert 'updated source ID' in open(f.name).read()
