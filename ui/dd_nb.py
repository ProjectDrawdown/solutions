"""Functions to support the Drawdown models in Jupyter notebooks."""

def scenario_sort_key(name):
  (solution, scenario) = name.split(':')
  if 'Plausible' in scenario:
    return solution + ':1:' + scenario
  if 'Optimum' in scenario or 'Optimal' in scenario:
    # 'Drawdown Optimum Scenario' must match Optimum before Drawdown
    return solution + ':3:' + scenario
  if 'Drawdown' in scenario:
    return solution + ':2:' + scenario
  return solution + ':4:' + scenario

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
