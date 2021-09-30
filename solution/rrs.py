"""Features shared by most or all of the
   Reduction and Replacement Solution (RRS) implementations.
"""

import pathlib
from model import integration

thisdir = pathlib.Path(__file__).parents[0]
parentdir = pathlib.Path(__file__).parents[1]

def energy_ref_tam(version=None):
    if version == None:
        version = "current"
    filename = parentdir/"data"/"energy"/("ref_tam_sources_"+str(version)+".json")
    altfile = integration.integration_alt_file(filename)
    if altfile.is_file():
        filename = altfile
    return filename

def energy_pds_tam(version=None):
    if version == None:
        version = "current"
    filename = parentdir/"data"/"energy"/("pds_tam_sources_"+str(version)+".json")
    altfile = integration.integration_alt_file(filename)
    if altfile.is_file():
        filename = altfile
    return filename


class RRS:
    def __init__(self, total_energy_demand, soln_avg_annual_use, conv_avg_annual_use):
        """Data structures to support the Reduction and Replacement Solutions.
           Arguments:
             total_energy_demand: in Terawatt-Hours (TWh), value typically supplied by tam.py
             soln_avg_annual_use: average annual usage of the solution in hours.
             conv_avg_annual_use: average annual usage of the conventional technology in hours.
        """
        self.substitutions = {
            '@soln_avg_annual_use@': soln_avg_annual_use,
            '@conv_avg_annual_use@': conv_avg_annual_use,

            # source for energy mix coal, natural gas, nuclear, and oil:
            # The World Bank Data in The Shift Project Data Portal
            # http://www.tsp-data-portal.org/Breakdown-of-Electricity-Generation-by-Energy-Source#tspQvChart
            '@energy_mix_coal@': 8726.0 / total_energy_demand,
            '@energy_mix_natural_gas@': 4933.0 / total_energy_demand,
            '@energy_mix_nuclear@': 2417.0 / total_energy_demand,
            '@energy_mix_oil@': 1068.0 / total_energy_demand,

            # source for remaining energy mix data:
            # IRENA (2016) Renewable Energy Statistics
            # http://www.irena.org/DocumentDownloads/Publications/IRENA_RE_Statistics_2016.pdf
            '@energy_mix_hydroelectric@': 4019.0 / total_energy_demand,
            '@energy_mix_solar@': 188.073 / total_energy_demand,
            '@energy_mix_wave@': 0.954 / total_energy_demand,
            '@energy_mix_wind_onshore@': 688.956 / total_energy_demand,
            '@energy_mix_wind_offshore@': 24.89 / total_energy_demand,
            '@energy_mix_biomass@': 399.496 / total_energy_demand,
            '@energy_mix_concentrated_solar@': 8.735 / total_energy_demand,
            '@energy_mix_geothermal@': 74.195 / total_energy_demand,
        }
