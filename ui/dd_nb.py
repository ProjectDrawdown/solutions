"""Functions to support the Drawdown models in Jupyter notebooks."""

import pandas as pd

pd.set_option('display.max_columns', 200)
pd.set_option('display.max_rows', 200)

# ----------------------------------------------------------

def scenario_sort_key(name):
  """Generate a key to sort Plausible first, then Drawdown, then Optimum.

    Arguments:
      name: string of the form 'solarpvutil:PDS3-16p2050-Optimum (Updated)'

    Figures out if the name is a Plausible, Drawdown, or Optimum case
    and returns a key of the form:
      <solution>:#:<scenario>

    where '#' will sort plausible cases first, followed by Drawdown,
    and finally Optimum cases.

    The intent is to sort by solution name first, by {Plausible, Drawdown, Optimum}
    scenarios within the solution next, and finally by the name of the scenario.
  """
  (solution, scenario) = name.split(':')
  if 'Plausible' in scenario:
    return solution + ':1:' + scenario
  if 'Optimum' in scenario or 'Optimal' in scenario:
    # 'Drawdown Optimum Scenario' must match Optimum before Drawdown
    return solution + ':3:' + scenario
  if 'Drawdown' in scenario:
    return solution + ':2:' + scenario
  return solution + ':4:' + scenario

# ----------------------------------------------------------

# CSS styling to be applied when rendering a DataFrame.
dataframe_css_styles = [
  dict(selector="th", props=[
    ('font-size', '16px'),
    ('text-align', 'right'),
    ('font-weight', 'bold'),
    ('color', '#6d6d6d'),
    ('background-color', '#f7f7f9')
    ]),
  dict(selector="td", props=[
    ('font-size', '13px'),
    ('font-weight', 'bold'),
    ('font-family', 'Monaco, monospace')
    ]),
  ]
