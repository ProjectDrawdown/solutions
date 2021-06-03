"""Top Level Solution Constructor"""

import importlib
import json
from pathlib import Path
from datetime import date
import pandas as pd


class Solution:
    """Top level solution constructor.  Convenience class to represent a 
    solution with its computed scenarios.  The primary functions performed in
    this class are to aggregate data across multiple scenarios as pandas
    DataFrames"""

    @staticmethod
    def solution_list():
        """Return a list solutions we hava access to"""
        return [ s.stem for s in Path('solution').glob('[a-z]*') if s.is_dir() ]
    
    @staticmethod
    def scenario_list(solution_name):
        """Return a list of scenarios for a given solution"""
        # Peek inside each of the scenario files and get the name out.
        result = []
        for s in Path('solution', solution_name, 'ac').glob('*.json'):
            with open(s) as f:
                j = json.loads(f.read())
                result.append(j['name'])
        return result
    
    @staticmethod
    def scenario_count(solution_name):
        return len(Path('solution', solution_name, 'ac').glob('*.json'))

    def __init__(self, solution_dir, scenario_names=None, start_year=None):
        """solution_dir: the bare name of a solution directory, e.g. 'bioplastics'
        scenario_names: optional list of scenarios to instantiate (defaults to all)
        start_year: optional year to start the results (i.e. results will be limited to start_year:2050)
        By default, the current year.
        Note: this method computes results and may take some time to complete.
        """

        # Check that the solution exists.
        # Like all the rest of the code, there is a hardwired assumption that
        # the python interpreter is running from the base directory of this
        # project.
        if not Path('./solution/' + solution_dir).exists():
            raise ValueError(f'No directory "{solution_dir}"" found in solutions.')

        self.sn = importlib.import_module('solution.' + solution_dir)
        
        self.scenario_names = scenario_names or list(self.sn.scenarios.keys()) 

        # Fetch the required scenarios.  This can take awhile
        self.scenarios = [ self.sn.Scenario(name) for name in self.scenario_names ]

        if start_year is None:
            start_year = date.today().year
        self.year_range = range(start_year, 2051)


    def available_data(self):
        """Not all solution types support all types of computed results.  This method will
        return a list of methods that do actually have data for this solution"""
        #TODO
        pass

    # TODO: could the range in the scenario be other than standard?  If so, we
    # need to intersect ranges below.
    
    def co2_reduction(self):
        """Return a pandas dataframe for the computed co2 reduction across all selected scenarios"""
        co2_red = {}
        for idx, s in enumerate(self.scenarios):
            dat = s.c2.co2eq_mmt_reduced()
            co2_red[idx] = dat.loc[self.year_range]

        # concatenates all the scenarios together, with a new scenario key
        # which is an *integer* (not the scenario name)
        return pd.concat(co2_red, names=['Scenario','Year'])

    def scenario_indexes(self):
        """Convenience method: returns pairs of (idx, scenario_name)"""
        return list(enumerate(self.scenario_names))