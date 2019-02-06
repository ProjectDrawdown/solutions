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
