"""Test cases for data_sources.py"""

import glob

from model import data_sources
import pandas as pd

def test_matching_columns():
  columns = ['Based on: IEA ETP 2016 6DS', 'Based on: IEA ETP 2016 4DS',
      'Ambitious: Based on- IEA ETP 2016 2DS',
      'Baseline: Based on- AMPERE GEM E3 Reference',
      'Based on: Greenpeace (2015) Advanced Energy Revolution']
  assert data_sources.matching_columns(columns, 'Ambitious') == [
      'Ambitious: Based on- IEA ETP 2016 2DS']
  assert data_sources.matching_columns(columns, 'baseline') == [
      'Based on: IEA ETP 2016 6DS', 'Baseline: Based on- AMPERE GEM E3 Reference']
  assert data_sources.matching_columns(columns, 'Conservative') == [
      'Based on: IEA ETP 2016 4DS']
  assert data_sources.matching_columns(columns, '100%') == [
      'Based on: Greenpeace (2015) Advanced Energy Revolution']

def test_groups_only():
  columns = ['Based on: IEA ETP 2016 6DS', 'Based on: IEA ETP 2016 4DS',
      'Ambitious: Based on- IEA ETP 2016 2DS',
      'Baseline: Based on- AMPERE GEM E3 Reference',
      'Based on: Greenpeace (2015) Advanced Energy Revolution']
  assert data_sources.matching_columns(columns, 'Ambitious: Based on- IEA ETP 2016 2DS',
      groups_only=False) == ['Ambitious: Based on- IEA ETP 2016 2DS']
  assert data_sources.matching_columns(columns, 'Ambitious: Based on- IEA ETP 2016 2DS',
      groups_only=True) == columns

def test_case_name_alias():
  columns = ['Ambitious: Based on- IEA ETP 2016 2DS',
      'Baseline: Based on- AMPERE GEM E3 Reference']
  assert data_sources.matching_columns(columns, 'Ambitious Cases') == [
      'Ambitious: Based on- IEA ETP 2016 2DS']

def test_all_sources_included():
  """Checks that every source from every solution is included."""
  all_columns = set()
  filenames = set()
  filenames.update(glob.glob('solution/*/adoption*.csv'))
  filenames.update(glob.glob('solution/*/tam*.csv'))
  for filename in filenames:
    df = pd.read_csv(filename, header=0, index_col=0, skipinitialspace=True, comment='#')
    all_columns.update(df.columns)

  # a few of the CSV files contain what look like harmless but incomplete entries.
  ignore = set(['[Source 6 - Ambitious]',])
  all_columns = all_columns.difference(ignore)

  for column in all_columns:
    assert data_sources.matching_columns(columns=all_columns, name=column) == [column]

def test_all_and_empty_result():
  columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
  assert data_sources.matching_columns(columns, 'Ambitious') == []
  assert data_sources.matching_columns(columns, 'ALL SOURCES') == columns

def test_is_group_name():
  assert data_sources.is_group_name("Ambitious Cases") == True
  assert data_sources.is_group_name("Ambitious") == True
  assert data_sources.is_group_name("ALL SOURCES") == True
  assert data_sources.is_group_name("not a group name") == False

