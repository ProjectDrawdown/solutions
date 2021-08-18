
import os
import json
import pandas as pd
import numpy as np

from model.ocean_solution import OceanSolution
from solution.macroalgaeprotection.macroalgaeprotection_scenario import MacroalgaeProtectionScenario

class MacroalgaeProtectionSolution(OceanSolution):
    """ All calculations for Macroalgae protection currently implemented in the OceanSolution base class.
    """

    # Initialize from configuration file:
    def __init__(self, configuration_file_name = None):
        """
            Constructor requires a configuration file named 'macroalgaeprotection_solution_config.yaml'.
            This should be located in the same directory as the 'macroalgaeprotection_solution.py' module

        """

        if configuration_file_name is None:
            filename = os.path.basename(__file__)
            filename = filename.split('.')[0]
            configuration_file_name = os.path.join(os.path.dirname(__file__), filename + '_config.yaml')
        
        if not os.path.isfile(configuration_file_name):
            raise ValueError(f'Unable to find configuration file {configuration_file_name}.')

        super().__init__(configuration_file_name, tam = None)
        
        # Now set macroalgaeprotection-specific config values:
        self.total_area = self._config['TotalArea']
        self.total_area_as_of_period = self._config['TotalAreaAsOfPeriod']
        self.change_per_period = self._config['ChangePerPeriod']

        # Delay Regrowth of Degraded Land by 1 Year?
        self.delay_regrowth_by_one_year = True


        self._tam.set_tam_linear(total_area = self.total_area, change_per_period = self.change_per_period, total_area_as_of_period = self.total_area_as_of_period)
        self._tam.apply_clip(upper=self.total_area)
        self._tam.apply_linear_regression()
        

    def load_scenario(self, scenario_name):

        input_stream = open(self.scenarios_file, 'r')
        scen_dict = json.load(input_stream)

        if scenario_name not in scen_dict.keys():
            raise ValueError(f"Unable to find {scenario_name} in scenario file: {self.scenarios_file}")
        
        scenario = MacroalgaeProtectionScenario(**scen_dict[scenario_name])

        self.scenario = scenario

        super()._load_pds_scenario()
        
        if self.scenario.ref_scenario_name:
            self._load_ref_scenario()
        else:
            # creates a ref scenario with zeroes.
            self.ref_scenario = self.pds_scenario.get_skeleton()

        # Set scenario-specific data:
        
        self.sequestration_rate_all_ocean = self.scenario.sequestration_rate_all_ocean
        self.npv_discount_rate = self.scenario.npv_discount_rate
        self.new_growth_harvested_every = self.scenario.new_growth_harvested_every
        self.disturbance_rate = 0.0

        self.tam_build_cumulative_unprotected_ocean_pds()
        return


    def tam_build_cumulative_unprotected_ocean_pds(self):
        tam_series = self._tam.get_tam_units()
        pds_series = self.pds_scenario.get_units_adopted()
        
        pds_results = pd.Series(index = tam_series.index)
        ref_results = pds_results.copy(deep=True)
        
        first_pass = True
        for index, value in tam_series.loc[self.base_year:].iteritems():
            if first_pass:
                pds_results.loc[index] = 0.0
                ref_results.loc[index] = 0.0
                pds_prev_value = 0.0
                ref_prev_value = 0.0
                first_pass = False
                continue

            pds_val = pds_series.loc[index -1]

            pds_result = (value - pds_val - pds_prev_value) * self.new_growth_harvested_every
            pds_result = pds_prev_value + pds_result
            pds_results.loc[index] = pds_result
            pds_prev_value = pds_result

            ref_result = (value - ref_prev_value) * self.new_growth_harvested_every
            ref_result = ref_prev_value + ref_result
            ref_results.loc[index] = ref_result
            ref_prev_value = ref_result

        df = pd.concat([pds_series, tam_series, pds_results, ref_results], axis='columns', ignore_index=True)
        df.columns = ['pds_toa_units_adopted', 'tam', 'cum_unprotected_area_pds', 'cum_unprotected_area_ref']
        df['total_undegraded_land_pds'] = df['tam'] - df['cum_unprotected_area_pds']
        df['total_at_risk_land_ref'] = df['tam'] - df['cum_unprotected_area_ref']
        df['cum_reduction_degraded_land'] = df['total_undegraded_land_pds'] - df['total_at_risk_land_ref']

        self._tam.cum_unprotected_area_pds = df

    def get_total_co2_seq(self) -> np.float64:
        
        df = self._tam.cum_unprotected_area_pds
        df = df['cum_reduction_degraded_land'] * 3.666 * self.sequestration_rate_all_ocean

        start = self.start_year
        end = self.end_year

        if self.delay_regrowth_by_one_year:
            start -= 1
            end -= 1

        result = df.loc[start: end].sum()
        return result / 1000


