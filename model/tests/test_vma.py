"""Tests for vma.py."""

import pytest
import io
import pathlib
import tempfile

from model import vma
import numpy as np
import pandas as pd


basedir = pathlib.Path(__file__).parents[2]
datadir = pathlib.Path(__file__).parents[0].joinpath('data')


def test_vals_from_real_soln_csv():
    """ Values from Silvopasture Variable Meta Analysis """
    f = datadir.joinpath('vma1_silvopasture.csv')
    v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0)
    result = v.avg_high_low()
    expected = (314.15, 450.0, 178.3)
    assert result == pytest.approx(expected)


class TestVMAFromXlsx:
    def test_no_title(self):
        """Check that the default title (None) raises an error."""
        with pytest.raises(ValueError) as error:
            vma.VMA(filename=datadir.joinpath('silvopasture.xlsx'))
        assert 'Title None not available' in error.exconly()

    def test_bad_title(self):
        """Check that a nonexistent title raises an error."""
        with pytest.raises(ValueError) as error:
            vma.VMA(filename=datadir.joinpath('silvopasture.xlsx'),
                    title='Not a real title')
        assert "Title 'Not a real title' not available" in error.exconly()

    @pytest.mark.parametrize('title,expected', (
        ('Current Adoption',
         (314.150, 450.0, 178.3)),
        ('SOLUTION First Cost per Implementation Unit',
         (462.45300593, 713.74365784, 211.16235403)),
        ('CONVENTIONAL Operating Cost per Functional Unit per Annum',
         (328.41585777, 706.18860047, -49.35688493)),
        ('SOLUTION Operating Cost per Functional Unit per Annum',
         (837.64313091, 1694.62599661, -19.33973480)),
        ('CONVENTIONAL Net Profit Margin per Functional Unit per Annum',
         (143.54391845, 231.31902470, 55.76881221)),
        ('SOLUTION Net Profit Margin per Functional Unit per Annum',
         (460.21969692, 732.99682009, 187.44257376)),
        ('Yield from CONVENTIONAL Practice',
         (3.42857143, 5.08534479, 1.77179807)),
        ('Yield Gain (% Increase from CONVENTIONAL to SOLUTION)',
         (0.10054497, 0.18294670, 0.01814324)),
        ('t CH4-CO2-eq Reduced per Land Unit',
         (0.0, 0.0, 0.0)),
        ('Sequestration Rates',
         (4.64561688, 8.24249349, 1.04874028)),
        ('Percent silvopasture area to the total grassland area (including potential)',
         (0.24150576, 0.36171938, 0.12129214)),
    ))
    @pytest.mark.parametrize('filetype', ('xlsx', 'xlsm'))
    def test_vals(self, filetype, title, expected):
        """
        Checks known values from Silvopasture Variable Meta Analysis, taken
        from the xlsx file.
        """
        v = vma.VMA(filename=datadir.joinpath(f'silvopasture.{filetype}'),
                    title=title,
                    low_sd=1.0,
                    high_sd=1.0)
        assert v.avg_high_low() == pytest.approx(expected)

    @pytest.mark.parametrize('title', (
        'CONVENTIONAL First Cost per Implementation Unit',
        'Electricty Consumed per CONVENTIONAL Functional Unit',
        'SOLUTION Energy Efficiency Factor',
        'Total Energy Used per SOLUTION functional unit',
        'Fuel Consumed per CONVENTIONAL Functional Unit',
        'Fuel Reduction Factor SOLUTION',
        't CO2-eq (Aggregate emissions) Reduced per Land Unit',
        't CO2 Reduced per Land Unit',
        't N2O-CO2-eq Reduced per Land Unit',
        'Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit -- CHOOSE ONLY ONE',
        'Indirect CO2 Emissions per SOLUTION Implementation Unit',
        'Indirect CO2 Emissions per SOLUTION Implementation Unit',
        'Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing',
        'Indirect CO2 Emissions per SOLUTION Implementation Unit',
        'Disturbance Rate',
        'Indirect CO2 Emissions per SOLUTION Implementation Unit',
    ))
    @pytest.mark.parametrize('filetype', ('xlsx', 'xlsm'))
    def test_empty_vmas(self, filetype, title):
        """
        Check that existing titles with no data raise an error. Titles taken
        from the test xlsx file.
        """
        filename = f'silvopasture.{filetype}'
        with pytest.raises(ValueError) as error:
            vma.VMA(filename=datadir.joinpath(filename),
                    title=title)
        assert filename in error.exconly()
        assert title in error.exconly()
        assert 'is that VMA empty?' in error.exconly()


def test_check_fixed_summary():
    # Check that None/NaN values give an empty result
    assert vma.check_fixed_summary(None, None, None) is None
    assert vma.check_fixed_summary(None, 1.1, 50) is None
    assert vma.check_fixed_summary(-4.3, np.nan, 50) is None
    # Check that we get a tuple of the given values back
    assert vma.check_fixed_summary(-4.3, 1.1, 50) == (-4.3, 1.1, 50)


def test_source_data():
    s = """Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
        Check that this text is present, 0%, %, 0, 0
        """
    f = io.StringIO(s)
    v = vma.VMA(filename=f)
    assert 'Check that this text is present' in v.source_data.to_html()


def test_invalid_discards():
    s = """Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
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
    """
    f = io.StringIO(s)
    v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0)
    result = v.avg_high_low()
    expected = (10000, 10000, 10000)  # The 10,000,000,000 and 1 values should be discarded.
    assert result == pytest.approx(expected)
    f = io.StringIO(s)
    v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0, stat_correction=False)
    result = v.avg_high_low()
    assert result != pytest.approx(expected)


def test_no_discards_if_weights():
    """Same test as test_invalid_discards but with weights, so there should be no discards."""
    s = """Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
        a, 10000, , , 1.0,
        b, 10000, , , 1.0,
        c, 10000, , , 1.0,
        d, 10000, , , 1.0,
        e, 10000, , , 1.0,
        f, 10000, , , 1.0,
        g, 10000, , , 1.0,
        h, 10000, , , 1.0,
        i, 10000, , , 1.0,
        j, 10000, , , 1.0,
        k, 10000, , , 1.0,
        l, 10000, , , 1.0,
        m, 10000, , , 1.0,
        n, 10000, , , 1.0,
        o, 10000, , , 1.0,
        p, 10000000000, , , 1.0,
        q, 1, , , 1.0,
    """
    f = io.StringIO(s)
    v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0, use_weight=True)
    result = v.avg_high_low()
    expected = (10000, 10000, 10000)
    assert result != pytest.approx(expected)


def test_excluded_data():
    s = """Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
        a, 10000, , , 1.0, False
        b, 10000, , , 1.0, False
        c, 40000, , , 1.0, True
    """
    f = io.StringIO(s)
    v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0)
    result = v.avg_high_low()
    expected = (10000, 10000, 10000)  # The 40000 value should be excluded.
    assert result == pytest.approx(expected)


def test_excluded_data_weights_are_incorrect():
    s = """Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
        a, 10000, , , 0.5, False
        b, 10000, , , 0.5, False
        c, 40000, , , 1.0, True
    """
    f = io.StringIO(s)
    v = vma.VMA(filename=f, low_sd=1.0, high_sd=1.0, use_weight=True)
    result = v.avg_high_low()
    # The 40000 value should be excluded, but its weight is included in the Excel implementation.
    # Expected value generated by entering the datapoints from this test into Excel.
    expected = (5000, 9330.127, 669.873)
    # When https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit#heading=h.qkdzs364y2t2
    # handling is removed this test will fail. It should be removed at that point, as it no longer
    # serves a purpose.
    assert result == pytest.approx(expected)


def test_single_study():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
      A, 39%, %,
      """)
    v = vma.VMA(filename=f)
    result = v.avg_high_low()
    expected = (0.39, 0.39, 0.39)
    assert result == pytest.approx(expected)


def test_missing_columns():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
      A, 1000
      """)
    v = vma.VMA(filename=f)
    result = v.avg_high_low()
    expected = (1000, 1000, 1000)
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


def test_populate_fixed_summary():
    VMAs = {
      'Testing Fixed Summary': vma.VMA(
          filename=datadir.joinpath("vma1_silvopasture.csv"),
          use_weight=False),
      }
    vma.populate_fixed_summaries(vma_dict=VMAs, filename=datadir.joinpath('VMA_info_w_summary.csv'))
    v = VMAs['Testing Fixed Summary']
    (avg, high, low) = v.avg_high_low()
    assert (avg, high, low) == (2.0, 3.0, 1.0)


def test_avg_high_low_by_regime():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
      A, 0.4, Mha,, 1.0, False, Temperate/Boreal-Humid
      B, 0.5, Mha,, 1.0, False, Temperate/Boreal-Humid
      C, 0.6, Mha,, 1.0, False, Tropical-Humid
      """)
    v = vma.VMA(filename=f)
    result = v.avg_high_low()
    assert result[0] == pytest.approx(0.5)
    result = v.avg_high_low(regime='Temperate/Boreal-Humid')
    assert result[0] == pytest.approx(0.45)


def test_avg_high_low_by_region():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
      A, 0.4, Mha,, 1.0, False, Temperate/Boreal-Humid, OECD90
      B, 0.5, Mha,, 1.0, False, Temperate/Boreal-Humid, OECD90
      C, 0.6, Mha,, 1.0, False, Tropical-Humid, Latin America
      """)
    v = vma.VMA(filename=f)
    result = v.avg_high_low()
    assert result[0] == pytest.approx(0.5)
    result = v.avg_high_low(region='OECD90')
    assert result[0] == pytest.approx(0.45)


def test_avg_high_low_by_region_with_special_countries():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
      A, 0.4, Mha,, 1.0, False, Temperate/Boreal-Humid, OECD90
      B, 0.5, Mha,, 1.0, False, Temperate/Boreal-Humid, USA
      C, 0.6, Mha,, 1.0, False, Tropical-Humid, Latin America
      """)
    v = vma.VMA(filename=f)
    result = v.avg_high_low()
    assert result[0] == pytest.approx(0.5)
    result = v.avg_high_low(region='OECD90')
    assert result[0] == pytest.approx(0.45)
    result = v.avg_high_low(region='USA')
    assert result[0] == pytest.approx(0.5)


def test_no_warnings_in_avg_high_low():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
      A, 1.0, Mha,, 0.0, False
      B, 1.0, Mha,, 0.0, False
      C, 1.0, Mha,, 0.0, False
      """)
    with pytest.warns(None) as warnings:
        v = vma.VMA(filename=f)
        _ = v.avg_high_low()
    assert len(warnings) == 0


def test_write_to_file():
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv')
    f.write(r"""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
      A, 1.0,,,,
      B, 1.0,,,,
      C, 1.0,,,,
      """)
    f.flush()
    v = vma.VMA(filename=f.name)
    df = v.source_data.copy(deep=True)
    df.loc[0, 'Source ID'] = 'updated source ID'
    v.write_to_file(df)
    with open(f.name) as fid:
        assert 'updated source ID' in fid.read()

def test_reload_from_file():
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv')
    f.write(r"""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
      original source ID, 1.0,,,,
      """)
    f.flush()
    v = vma.VMA(filename=f.name)
    df = v.source_data.copy(deep=True)
    assert df.loc[0, 'Source ID'] == 'original source ID'
    f.seek(0)
    f.write(r"""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
      updated source ID, 1.0,,,,
      """)
    f.flush()
    v.reload_from_file()
    df = v.source_data.copy(deep=True)
    assert df.loc[0, 'Source ID'] == 'updated source ID'

def test_spelling_correction():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
      A, 1.0, Mha,, 0.0, False,, Asia (sans Japan)
      B, 1.0, Mha,, 0.0, False,, Middle East & Africa
      """)
    v = vma.VMA(filename=f)
    assert v.df.loc[0, 'Region'] == 'Asia (Sans Japan)'
    assert v.df.loc[1, 'Region'] == 'Middle East and Africa'

def test_categorical_validation():
    f = io.StringIO("""Source ID, Raw Data Input, Original Units, Conversion calculation, Weight, Exclude Data?, Thermal-Moisture Regime, World / Drawdown Region
      A, 1.0, Mha,, 0.0, False, Global Arid, Invalid Region
      B, 1.0, Mha,, 0.0, False,, USA
      C, 1.0, Mha,, 0.0, False, Invalid TMR, China
      """)
    v = vma.VMA(filename=f)
    assert pd.isna(v.df.loc[0, 'Region'])
    assert v.df.loc[0, 'TMR'] == 'Global Arid'
    assert v.df.loc[1, 'Region'] == 'USA'
    assert v.df.loc[1, 'TMR'] == ''
    assert v.df.loc[2, 'Region'] == 'China'
    assert v.df.loc[2, 'TMR'] == ''
    assert pd.isna(v.source_data.loc[0, 'World / Drawdown Region'])
    assert pd.isna(v.source_data.loc[2, 'Thermal-Moisture Regime'])

def test_no_filename():
    v = vma.VMA(filename=None)
    assert v.df.empty
    (mean, high, low) = v.avg_high_low()
    assert pd.isna(mean)
    assert pd.isna(high)
    assert pd.isna(low)

def test_bad_filetype():
    with pytest.raises(ValueError) as error:
        vma.VMA(filename='file.bad')
    assert 'file.bad' in error.exconly()
    assert 'not a recognized filetype for vma.VMA' in error.exconly()
