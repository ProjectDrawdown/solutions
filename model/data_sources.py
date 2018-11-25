"""Categorizes data sources into Baseline, Conservative, Ambitious, etc cases."""

# This data structure contains the study names for all data sources,
# from all solutions (yes, all of them). We do this because the same
# source material is used in a large number of Project Drawdown
# Solutions, so keeping the sets separated per solution results in
# substantial duplication.
#
# Remove any prepended text like "Based on-" and "Baseline Case:",
# and leave only the name of the study. The prefixes vary between
# solutions, but the study name is sometimes the same. This
# implementation looks for substrings, it only needs the study name.
#
# Different researchers have capitalized differently when entering
# data, so we convert to lower case before searching.
#
_cases = {
    'ambitious': set([
      'IEA ETP 2016 2DS', 'AMPERE (2014) IMAGE 450',
      'AMPERE IMAGE/TIMER 450', 'AMPERE (2014) MESSAGE 450',
      'AMPERE MESSAGE-MACRO 450', 'AMPERE (2014) GEM E3 450',
      'AMPERE GEM E3 450', 'Greenpeace (2015) Energy Revolution',
      'Greenpeace Energy [R]evolution',
      'Drawdown TAM: Drawdown TAM - Post Integration - Plausible Scenario',
      'Drawdown TAM: Drawdown TAM - Post Integration - Drawdown Scenario',
      'Drawdown TAM: Drawdown TAM - Post Integration - Optimum Scenario',
    ]),

    'baseline': set([
      'IEA ETP 2016 6DS', 'AMPERE (2014) IMAGE Refpol',
      'AMPERE IMAGE/TIMER Reference', 'AMPERE (2014) MESSAGE REFPol',
      'AMPERE MESSAGE-MACRO Reference', 'AMPERE (2014) GEM E3 REFpol',
      'AMPERE GEM E3 Reference',
    ]),

    'conservative': set([
      'IEA ETP 2016 4DS', 'AMPERE (2014) IMAGE 550',
      'AMPERE IMAGE/TIMER 550', 'AMPERE (2014) MESSAGE 550',
      'AMPERE MESSAGE-MACRO 550', 'AMPERE (2014) GEM E3 550',
      'AMPERE GEM E3 550', 'Greenpeace (2015) Reference',
      'Greenpeace 2015 Reference',
    ]),

    '100%': set([
      'Greenpeace (2015) Advanced Energy Revolution',
      'Greenpeace Advanced [R]evolution',
    ])
}

name_mapping = {
    'ambitious cases': 'ambitious',
    'ambitious case': 'ambitious',
    'baseline cases': 'baseline',
    'baseline case': 'baseline',
    'conservative cases': 'conservative',
    'conservative case': 'conservative',
}

def matching_columns(columns, name, groups_only=False):
  """Return a list of columns which match name.
     If name is a group, return all entries from columns which are part of that group.
     If name is an individual case and groups_only=False, return it by itself.
     If groups_only=True and name is not a group, return columns.

     Arguments:
       columns: a list of strings which name data sources.
       name: a name of an individual data source, or the name of a grouping
         like 'Ambitious Cases'
       groups_only: only return a group, or all columns if no group is found.
         This is typically useful for stddev calculations, which are never done
         (and are nonsensical) on an individual data source only on a specific
         group or over all sources.

     The name passed in can have prefixed or suffixed text. For example,
     'Baseline: Based on- IEA ETP 2016 6DS' will match 'IEA ETP 2016 6DS'
  """
  name = name_mapping.get(name.lower(), name)
  if name.lower() in _cases:
    candidates = _cases[name.lower()]
  elif name.lower() == 'all sources':
    return columns
  elif groups_only:
    return columns
  else:
    candidates = [name]
  result = []
  for col in columns:
    if any(candidate.lower() in col.lower() for candidate in candidates):
      result.append(col)
  return result

def is_group_name(name):
  """Return True if name is a group."""
  name = name.lower()
  name = name_mapping.get(name, name)
  if name in _cases:
    return True
  if name == "all sources":
    return True
  return False
