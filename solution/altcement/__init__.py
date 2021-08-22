"""Alternative Cements solution model.
   Excel filename: AlternativeCements_v1.1c_IntegrationJune2020.xlsm
"""

import pathlib

import numpy as np
import pandas as pd
import openpyxl

from model import adoptiondata
from model import advanced_controls as ac
from model import ch4calcs
from model import co2calcs
from model import customadoption
from model import dd
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import operatingcost
from model import s_curve
from model import scenario
from model import unitadoption
from model import vma
from model import tam
from solution import rrs

DATADIR = pathlib.Path(__file__).parents[2].joinpath('data')
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = {
    'Current Adoption': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Current_Adoption.csv"),
        use_weight=False),
    'CONVENTIONAL First Cost per Implementation Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_First_Cost_per_Implementation_Unit.csv"),
        use_weight=False),
    'SOLUTION First Cost per Implementation Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_First_Cost_per_Implementation_Unit.csv"),
        use_weight=False),
    'CONVENTIONAL Lifetime Capacity': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Lifetime_Capacity.csv"),
        use_weight=False),
    'SOLUTION Lifetime Capacity': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Lifetime_Capacity.csv"),
        use_weight=False),
    'CONVENTIONAL Average Annual Use': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Average_Annual_Use.csv"),
        use_weight=False),
    'SOLUTION Average Annual Use': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Average_Annual_Use.csv"),
        use_weight=False),
    'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Variable Operating Cost (VOM) per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Fixed Operating Cost (FOM)': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Fixed Operating Cost (FOM)': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Total Energy Used per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Total_Energy_Used_per_Functional_Unit.csv"),
        use_weight=False),
    'SOLUTION Energy Efficiency Factor': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Total Energy Used per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Total_Energy_Used_per_Functional_Unit.csv"),
        use_weight=False),
    'CONVENTIONAL Fuel Consumed per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Fuel_Consumed_per_Functional_Unit.csv"),
        use_weight=False),
    'SOLUTION Fuel Efficiency Factor': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Fuel_Efficiency_Factor.csv"),
        use_weight=False),
    'CONVENTIONAL Direct Emissions per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Direct_Emissions_per_Functional_Unit.csv"),
        use_weight=False),
    'SOLUTION Direct Emissions per Functional Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Direct_Emissions_per_Functional_Unit.csv"),
        use_weight=False),
    'CONVENTIONAL Indirect CO2 Emissions per Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "CONVENTIONAL_Indirect_CO2_Emissions_per_Unit.csv"),
        use_weight=False),
    'SOLUTION Indirect CO2 Emissions per Unit': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "SOLUTION_Indirect_CO2_Emissions_per_Unit.csv"),
        use_weight=False),
    'CH4-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'N2O-CO2eq Tons Reduced': vma.VMA(
        filename=None, use_weight=False),
    'CONVENTIONAL Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'SOLUTION Revenue per Functional Unit': vma.VMA(
        filename=None, use_weight=False),
    'Discount Rate - Commercial': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Discount_Rate_Commercial.csv"),
        use_weight=False),
    'Clinker to Cement Ratio in Year 2': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Clinker_to_Cement_Ratio_in_Year_2.csv"),
        use_weight=True),
    'Clinker to Cement Ratio of Conventional Technology': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Clinker_to_Cement_Ratio_of_Conventional_Technology.csv"),
        use_weight=False),
    'Clinker Ratio Range Selection': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Clinker_Ratio_Range_Selection.csv"),
        use_weight=False),
    'Variable 29': vma.VMA(
        filename=None, use_weight=False),
    'Percent Adoption of Blended Cements in Year 2 (2050)': vma.VMA(
        filename=THISDIR.joinpath("vma_data", "Percent_Adoption_of_Blended_Cements_in_Year_2_2050.csv"),
        use_weight=False),
}
vma.populate_fixed_summaries(vma_dict=VMAs, filename=THISDIR.joinpath('vma_data', 'VMA_info.csv'))

units = {
    "implementation unit": "MMt",
    "functional unit": "MMt Cement",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Alternative Cements'
solution_category = ac.SOLUTION_CATEGORY.REDUCTION

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS1-100p2050-0.6Clinker/Cement-postintJune2020"
PDS2 = "PDS2-100p2050-0.46clinker/cement-postintjune2020"
PDS3 = "PDS-100p2050-0.27clinker/cement-postintjune2020"

class Scenario(scenario.Scenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category

    def __init__(self, scenario=None):
        if isinstance(scenario, ac.AdvancedControls):
            self.scenario = scenario.name
            self.ac = scenario
        else:
            self.scenario = scenario or PDS2
            self.ac = scenarios[self.scenario]

        # TAM
        tamconfig_list = [
            ['param', 'World', 'PDS World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
            ['source_until_2014', self.ac.source_until_2014, self.ac.source_until_2014,
                'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
                'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
            ['source_after_2014', self.ac.ref_source_post_2014, self.ac.pds_source_post_2014,
                'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES',
                'ALL SOURCES', 'ALL SOURCES', 'ALL SOURCES'],
            ['trend', '3rd Poly', '3rd Poly',
                '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
                '3rd Poly', '3rd Poly', '3rd Poly'],
            ['growth', 'Medium', 'Medium', 'Medium', 'Medium',
                'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium', 'Medium'],
            ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
        tamconfig = pd.DataFrame(tamconfig_list[1:], columns=tamconfig_list[0]).set_index('param')
        tam_ref_data_sources = {
              'Baseline Cases': {
                  'Project Drawdown - Based on Data from Several Sources. (See HVFAC Links Sheet and HVFAC Material Availability Models)': THISDIR.joinpath('tam', 'tam_Project_Drawdown_based_on_Data_from_Several_Sources__See_HVFAC_Links_Sheet_and_HVFAC_Mat_2961774c.csv'),
            },
              'Conservative Cases': {
                  'IEA 2018 Low-Variability': THISDIR.joinpath('tam', 'tam_IEA_2018_LowVariability.csv'),
                  'Farfan et al. 2019': THISDIR.joinpath('tam', 'tam_Farfan_et_al__2019.csv'),
                  'van Ruijven et al. 2016': THISDIR.joinpath('tam', 'tam_van_Ruijven_et_al__2016.csv'),
            },
              'Ambitious Cases': {
                  'IEA 2018 High-Variability': THISDIR.joinpath('tam', 'tam_IEA_2018_HighVariability.csv'),
            },
              'Maximum Cases': {
                  'WBCSD Cement 2002': THISDIR.joinpath('tam', 'tam_WBCSD_Cement_2002.csv'),
            },
        }
        self.tm = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=tam_ref_data_sources,
            tam_pds_data_sources=tam_ref_data_sources)
        ref_tam_per_region=self.tm.ref_tam_per_region()
        pds_tam_per_region=self.tm.pds_tam_per_region()

        adconfig_list = [
            ['param', 'World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
             'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'],
            ['trend', self.ac.soln_pds_adoption_prognostication_trend, '3rd Poly',
             '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly',
             '3rd Poly', '3rd Poly', '3rd Poly'],
            ['growth', self.ac.soln_pds_adoption_prognostication_growth, 'Medium',
             'Medium', 'Medium', 'Medium', 'Medium', 'Medium',
             'Medium', 'Medium', 'Medium'],
            ['low_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            ['high_sd_mult', 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]]
        adconfig = pd.DataFrame(adconfig_list[1:], columns=adconfig_list[0]).set_index('param')
        ad_data_sources = {
        }
        self.ad = adoptiondata.AdoptionData(ac=self.ac, data_sources=ad_data_sources,
            adconfig=adconfig)

        # Custom PDS Data
        wb = openpyxl.load_workbook(filename=THISDIR.joinpath('data.xlsx'), data_only=True, keep_links=False)
        def isint(x):
            try:
                int(x)
                return True
            except ValueError:
                return False
        def demangle(name):
            # Pandas tries to be helpful by mangling duplicate column names, so the first
            # read_excel returns 'Latin America' and the second 'Latin America.1'
            if not '.' in name:
                return name
            new, suffix = name.rsplit('.', 1)
            return new if isint(suffix) else name
        clinker_pct = self.ac.lookup_vma(vma_title='Clinker to Cement Ratio in Year 2')

        # Data Source 1
        #breakpoint()
        hvfac_mmt_pds1 = pd.read_excel(wb, sheet_name='HVFAC Links', header=0, index_col=0,
                usecols='B:L', dtype='float', engine='openpyxl', skiprows=62, nrows=46
                ).rename(mapper=demangle, axis='columns').rename(columns={
                    'Asia (sans Japan)': 'Asia (Sans Japan)',
                    'Middle East & Africa': 'Middle East and Africa',
                    })
        hvfac_mmt_pds1.index.name = 'Year'
        hvfac_mmt_pds1.loc[2014] = 0.0
        ds1_df = hvfac_mmt_pds1.sort_index() / clinker_pct

        # Data Source 2
        hvfac_mmt_pds2 = pd.read_excel(wb, sheet_name='HVFAC Links', header=0, index_col=0,
                usecols='O:Y', dtype='float', engine='openpyxl', skiprows=62, nrows=46
                ).rename(mapper=demangle, axis='columns').rename(columns={
                    'Asia (sans Japan)': 'Asia (Sans Japan)',
                    'Middle East & Africa': 'Middle East and Africa',
                    })
        hvfac_mmt_pds2.index.name = 'Year'
        hvfac_mmt_pds2.loc[2014] = 0.0
        ds2_df = hvfac_mmt_pds2.sort_index() / clinker_pct

        # Data Source 3
        hvfac_mmt_pds3 = pd.read_excel(wb, sheet_name='HVFAC Links', header=0, index_col=0,
                usecols='AB:AL', dtype='float', engine='openpyxl', skiprows=62, nrows=46
                ).rename(mapper=demangle, axis='columns').rename(columns={
                    'Asia (sans Japan)': 'Asia (Sans Japan)',
                    'Middle East & Africa': 'Middle East and Africa',
                    })
        hvfac_mmt_pds3.index.name = 'Year'
        hvfac_mmt_pds3.loc[2014] = 0.0
        ds3_df = hvfac_mmt_pds3.sort_index() / clinker_pct

        # Data Source 4
        filename_ds4 = THISDIR.joinpath('ca_pds_data', 'pds_adoption_scenario_4.csv')
        book_mmt = pd.read_csv(filename_ds4, header=0, index_col=0, skipinitialspace=True,
                         skip_blank_lines=True, comment='#', dtype=np.float64)
        book_mmt.index = book_mmt.index.astype(int)
        ds4_df = book_mmt / clinker_pct

        ca_pds_data_sources = [
            {'name': 'Adoption Based on Fly Ash Availability Analysis/ PDS 1', 'include': True,
                'description': (
                    'Fly Ash (FA) is a waste product of coal fired power stations. FA that is '
                    'not reused, is disposed in dry landfills or wet ponds. FA is valuable '
                    'because it can be used to replace Ordinary Portland Cement (OPC) in the '
                    'cement mix (up to a certain percentage) and hence it can be used to reduce '
                    'the CO2 footprint of concrete. The separate HVFAC model evaluates the total '
                    'amount of FA available in a market based on projected coal demand and '
                    "coal's fly ash concentration. The model divides the total FA supply into "
                    "three streams (i) landfill; (ii)  'other uses' (i.e. reuse but not cement); "
                    'and (iii) cement mixes. The total addressable market for cement '
                    'production/demand is initially defined as the total cement demand (assumed '
                    'OPC) plus that portion of FA that is reused for cement. A higher ratio of '
                    'FA:OPC (e.g. 45%:55%) for the cement mix is the adopted solution for CO2 '
                    'mitigation. The target FA:OPC ratio is input into the model to define the '
                    'PDS scenario. The model calculates the annual mass of OPC that can be '
                    'avoided, the energy saved, and the CO2 emissions avoided.  There are two '
                    'factors (cement demand and FA supply) that have the potential to limit OPC '
                    'replacement with FA. Model input includes the PDS transition period (e.g. 5 '
                    'years) to implement the new policy for cement production, concrete '
                    'standards, and FA reuse infrastructure. The model allows an addtional '
                    'policy option: to utilise FA in landfill when the 100% of FA waste stream '
                    'is utilised in cement production and other uses. For this scenario, '
                    'reduction of coal demand for electricity generation in the PDS1 affects the '
                    'total amount of fly ash available. '
                    ),
                'dataframe': ds1_df},
            {'name': 'Adoption Based on Fly Ash Availability Analysis/ PDS 2', 'include': True,
                'description': (
                    'Fly Ash (FA) is a waste product of coal fired power stations. FA that is '
                    'not reused, is disposed in dry landfills or wet ponds. FA is valuable '
                    'because it can be used to replace Ordinary Portland Cement (OPC) in the '
                    'cement mix (up to a certain percentage) and hence it can be used to reduce '
                    'the CO2 footprint of concrete. The separate HVFAC model evaluates the total '
                    'amount of FA available in a market based on projected coal demand and '
                    "coal's fly ash concentration. The model divides the total FA supply into "
                    "three streams (i) landfill; (ii)  'other uses' (i.e. reuse but not cement); "
                    'and (iii) cement mixes. The total addressable market for cement '
                    'production/demand is initially defined as the total cement demand (assumed '
                    'OPC) plus that portion of FA that is reused for cement. A higher ratio of '
                    'FA:OPC (e.g. 45%:55%) for the cement mix is the adopted solution for CO2 '
                    'mitigation. The target FA:OPC ratio is input into the model to define the '
                    'PDS scenario. The model calculates the annual mass of OPC that can be '
                    'avoided, the energy saved, and the CO2 emissions avoided.  There are two '
                    'factors (cement demand and FA supply) that have the potential to limit OPC '
                    'replacement with FA. Model input includes the PDS transition period (e.g. 5 '
                    'years) to implement the new policy for cement production, concrete '
                    'standards, and FA reuse infrastructure. The model allows an addtional '
                    'policy option: to utilise FA in landfill when the 100% of FA waste stream '
                    'is utilised in cement production and other uses. For this scenario, '
                    'reduction of coal demand for electricity generation in the PDS2 affects the '
                    'total amount of fly ash available. '
                    ),
                'dataframe': ds2_df},
            {'name': 'Adoption Based on Fly Ash Availability Analysis/ PDS 3', 'include': True,
                'description': (
                    'Fly Ash (FA) is a waste product of coal fired power stations. FA that is '
                    'not reused, is disposed in dry landfills or wet ponds. FA is valuable '
                    'because it can be used to replace Ordinary Portland Cement (OPC) in the '
                    'cement mix (up to a certain percentage) and hence it can be used to reduce '
                    'the CO2 footprint of concrete. The separate HVFAC model evaluates the total '
                    'amount of FA available in a market based on projected coal demand and '
                    "coal's fly ash concentration. The model divides the total FA supply into "
                    "three streams (i) landfill; (ii)  'other uses' (i.e. reuse but not cement); "
                    'and (iii) cement mixes. The total addressable market for cement '
                    'production/demand is initially defined as the total cement demand (assumed '
                    'OPC) plus that portion of FA that is reused for cement. A higher ratio of '
                    'FA:OPC (e.g. 45%:55%) for the cement mix is the adopted solution for CO2 '
                    'mitigation. The target FA:OPC ratio is input into the model to define the '
                    'PDS scenario. The model calculates the annual mass of OPC that can be '
                    'avoided, the energy saved, and the CO2 emissions avoided.  There are two '
                    'factors (cement demand and FA supply) that have the potential to limit OPC '
                    'replacement with FA. Model input includes the PDS transition period (e.g. 5 '
                    'years) to implement the new policy for cement production, concrete '
                    'standards, and FA reuse infrastructure. The model allows an addtional '
                    'policy option: to utilise FA in landfill when the 100% of FA waste stream '
                    'is utilised in cement production and other uses. For this scenario, '
                    'reduction of coal demand for electricity generation in the PDS3 affects the '
                    'total amount of fly ash available. '
                    ),
                'dataframe': ds3_df},
            {'name': 'Drawdown Book Edition 1 PDS 1, 2 and 3', 'include': True,
                'description': (
                    'Fly Ash (FA) is a waste product of coal fired power stations. FA that is '
                    'not reused, is disposed in dry landfills or wet ponds. FA is valuable '
                    'because it can be used to replace Ordinary Portland Cement (OPC) in the '
                    'cement mix (up to a certain percentage) and hence it can be used to reduce '
                    'the CO2 footprint of concrete. The separate HVFAC model evaluates the total '
                    'amount of FA available in a market based on projected coal demand and '
                    "coal's fly ash concentration. The model divides the total FA supply into "
                    "three streams (i) landfill; (ii)  'other uses' (i.e. reuse but not cement); "
                    'and (iii) cement mixes. The total addressable market for cement '
                    'production/demand is initially defined as the total cement demand (assumed '
                    'OPC) plus that portion of FA that is reused for cement. A higher ratio of '
                    'FA:OPC (e.g. 45%:55%) for the cement mix is the adopted solution for CO2 '
                    'mitigation. The target FA:OPC ratio is input into the model to define the '
                    'PDS scenario. The model calculates the annual mass of OPC that can be '
                    'avoided, the energy saved, and the CO2 emissions avoided.  There are two '
                    'factors (cement demand and FA supply) that have the potential to limit OPC '
                    'replacement with FA. Model input includes the PDS transition period (e.g. 5 '
                    'years) to implement the new policy for cement production, concrete '
                    'standards, and FA reuse infrastructure. The model allows an addtional '
                    'policy option: to utilise FA in landfill when the 100% of FA waste stream '
                    'is utilised in cement production and other uses. This scenario uses inputs '
                    'calculated for the Drawdown book edition 1, some of which have been updated '
                    'with newer data. '
                    ),
                'dataframe': ds4_df},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=self.ac.soln_pds_adoption_custom_high_sd_mult,
            low_sd_mult=self.ac.soln_pds_adoption_custom_low_sd_mult,
            total_adoption_limit=pds_tam_per_region)

        # Custom REF Data
        # Data Source 1
        hvfac_mmt_ref = pd.read_excel(io=wb, sheet_name='HVFAC Links', header=0, index_col=0,
                usecols='B:L', dtype='float', engine='openpyxl', skiprows=113, nrows=46
                ).rename(mapper=demangle, axis='columns').rename(columns={
                    'Asia (sans Japan)': 'Asia (Sans Japan)',
                    'Middle East & Africa': 'Middle East and Africa',
                    })
        hvfac_mmt_ref.index.name = 'Year'
        hvfac_mmt_ref.loc[2014] = 0.0
        ref1_df = hvfac_mmt_ref.sort_index() / clinker_pct

        # Data Source 2
        filename_ref2 = THISDIR.joinpath('ca_ref_data', 'ref_adoption_scenario_2.csv')
        book_ref_mmt = pd.read_csv(filename_ref2, header=0, index_col=0, skipinitialspace=True,
                         skip_blank_lines=True, comment='#', dtype=np.float64)
        book_ref_mmt.index = book_ref_mmt.index.astype(int)
        ref2_df = book_ref_mmt / clinker_pct

        ca_ref_data_sources = [
            {'name': 'REF Custom Adoption Based on Fly Ash Availability Analysis', 'include': True,
                'description': (
                    'Fly Ash (FA) is a waste product of coal fired power stations. FA that is '
                    'not reused, is disposed in dry landfills or wet ponds. FA is valuable '
                    'because it can be used to replace Ordinary Portland Cement (OPC) in the '
                    'cement mix (up to a certain percentage) and hence it can be used to reduce '
                    'the CO2 footprint of concrete. The separate HVFAC model evaluates the total '
                    'amount of FA available in a market based on projected coal demand and '
                    "coal's fly ash concentration. The model divides the total FA supply into "
                    "three streams (i) landfill; (ii)  'other uses' (i.e. reuse but not cement); "
                    'and (iii) cement mixes. The total addressable market for cement '
                    'production/demand is initially defined as the total cement demand (assumed '
                    'OPC) plus that portion of FA that is reused for cement. A higher ratio of '
                    'FA:OPC (e.g. 45%:55%) for the cement mix is the adopted solution for CO2 '
                    'mitigation. The target FA:OPC ratio is input into the model to define the '
                    'PDS scenario. The model calculates the annual mass of OPC that can be '
                    'avoided, the energy saved, and the CO2 emissions avoided.  There are two '
                    'factors (cement demand and FA supply) that have the potential to limit OPC '
                    'replacement with FA. Model input includes the PDS transition period (e.g. 5 '
                    'years) to implement the new policy for cement production, concrete '
                    'standards, and FA reuse infrastructure. The model allows an addtional '
                    'policy option: to utilise FA in landfill when the 100% of FA waste stream '
                    'is utilised in cement production and other uses. '
                    ),
                'dataframe': ref1_df},
            {'name': 'Drawdown Book Edition 1 Scenario REF Adoption', 'include': True,
                'description': (
                    'Fly Ash (FA) is a waste product of coal fired power stations. FA that is '
                    'not reused, is disposed in dry landfills or wet ponds. FA is valuable '
                    'because it can be used to replace Ordinary Portland Cement (OPC) in the '
                    'cement mix (up to a certain percentage) and hence it can be used to reduce '
                    'the CO2 footprint of concrete. The separate HVFAC model evaluates the total '
                    'amount of FA available in a market based on projected coal demand and '
                    "coal's fly ash concentration. The model divides the total FA supply into "
                    "three streams (i) landfill; (ii)  'other uses' (i.e. reuse but not cement); "
                    'and (iii) cement mixes. The total addressable market for cement '
                    'production/demand is initially defined as the total cement demand (assumed '
                    'OPC) plus that portion of FA that is reused for cement. A higher ratio of '
                    'FA:OPC (e.g. 45%:55%) for the cement mix is the adopted solution for CO2 '
                    'mitigation. The target FA:OPC ratio is input into the model to define the '
                    'PDS scenario. The model calculates the annual mass of OPC that can be '
                    'avoided, the energy saved, and the CO2 emissions avoided.  There are two '
                    'factors (cement demand and FA supply) that have the potential to limit OPC '
                    'replacement with FA. Model input includes the PDS transition period (e.g. 5 '
                    'years) to implement the new policy for cement production, concrete '
                    'standards, and FA reuse infrastructure. The model allows an addtional '
                    'policy option: to utilise FA in landfill when the 100% of FA waste stream '
                    'is utilised in cement production and other uses. This scenario uses inputs '
                    'calculated for the Drawdown book edition 1, some of which have been updated '
                    'with newer data. '
                    ),
                'dataframe': ref2_df},
        ]
        self.ref_ca = customadoption.CustomAdoption(data_sources=ca_ref_data_sources,
            soln_adoption_custom_name=self.ac.soln_ref_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=ref_tam_per_region)

        if self.ac.soln_ref_adoption_basis == 'Custom':
            ref_adoption_data_per_region = self.ref_ca.adoption_data_per_region()
        else:
            ref_adoption_data_per_region = None

        if False:
            # One may wonder why this is here. This file was code generated.
            # This 'if False' allows subsequent conditions to all be elif.
            pass
        elif self.ac.soln_pds_adoption_basis == 'Fully Customized PDS':
            pds_adoption_data_per_region = self.pds_ca.adoption_data_per_region()
            pds_adoption_trend_per_region = self.pds_ca.adoption_trend_per_region()
            pds_adoption_is_single_source = None
        elif self.ac.soln_pds_adoption_basis == 'Existing Adoption Prognostications':
            pds_adoption_data_per_region = self.ad.adoption_data_per_region()
            pds_adoption_trend_per_region = self.ad.adoption_trend_per_region()
            pds_adoption_is_single_source = self.ad.adoption_is_single_source()
        elif self.ac.soln_pds_adoption_basis == 'Linear':
            pds_adoption_data_per_region = None
            pds_adoption_trend_per_region = None
            pds_adoption_is_single_source = None

        ht_ref_adoption_initial = pd.Series(
            list(self.ac.ref_base_adoption.values()), index=dd.REGIONS)
        ht_ref_adoption_final = ref_tam_per_region.loc[2050] * (ht_ref_adoption_initial /
            ref_tam_per_region.loc[2018])
        ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_ref_datapoints.loc[2018] = ht_ref_adoption_initial
        ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
        ht_pds_adoption_initial = ht_ref_adoption_initial
        ht_pds_adoption_final_percentage = pd.Series(
            list(self.ac.pds_adoption_final_percentage.values()),
            index=list(self.ac.pds_adoption_final_percentage.keys()))
        ht_pds_adoption_final = ht_pds_adoption_final_percentage * pds_tam_per_region.loc[2050]
        ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_pds_datapoints.loc[2018] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
        self.ht = helpertables.HelperTables(ac=self.ac,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=ref_tam_per_region, pds_adoption_limits=pds_tam_per_region,
            ref_adoption_data_per_region=ref_adoption_data_per_region,
            use_first_pds_datapoint_main=False,
            copy_pds_to_ref=False, copy_ref_datapoint=False, copy_pds_datapoint=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=4)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=ref_tam_per_region,
            pds_total_adoption_units=pds_tam_per_region,
            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
            repeated_cost_for_iunits=True,
            bug_cfunits_double_count=False)
        soln_pds_tot_iunits_reqd = self.ua.soln_pds_tot_iunits_reqd()
        soln_ref_tot_iunits_reqd = self.ua.soln_ref_tot_iunits_reqd()
        conv_ref_tot_iunits = self.ua.conv_ref_tot_iunits()
        soln_net_annual_funits_adopted=self.ua.soln_net_annual_funits_adopted()

        self.fc = firstcost.FirstCost(ac=self.ac, pds_learning_increase_mult=2,
            ref_learning_increase_mult=2, conv_learning_increase_mult=2,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_tot_iunits=conv_ref_tot_iunits,
            soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
            soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
            conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
            fc_convert_iunit_factor=1.0)

        self.oc = operatingcost.OperatingCost(ac=self.ac,
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
            soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
            conv_ref_annual_tot_iunits=self.ua.conv_ref_annual_tot_iunits(),
            soln_pds_annual_world_first_cost=self.fc.soln_pds_annual_world_first_cost(),
            soln_ref_annual_world_first_cost=self.fc.soln_ref_annual_world_first_cost(),
            conv_ref_annual_world_first_cost=self.fc.conv_ref_annual_world_first_cost(),
            single_iunit_purchase_year=2017,
            soln_pds_install_cost_per_iunit=self.fc.soln_pds_install_cost_per_iunit(),
            conv_ref_install_cost_per_iunit=self.fc.conv_ref_install_cost_per_iunit(),
            conversion_factor=1.0)

        self.c4 = ch4calcs.CH4Calcs(ac=self.ac,
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

        self.c2 = co2calcs.CO2Calcs(ac=self.ac,
            ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
            soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),
            soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),
            soln_pds_direct_co2_emissions_saved=self.ua.soln_pds_direct_co2_emissions_saved(),
            soln_pds_direct_ch4_co2_emissions_saved=self.ua.soln_pds_direct_ch4_co2_emissions_saved(),
            soln_pds_direct_n2o_co2_emissions_saved=self.ua.soln_pds_direct_n2o_co2_emissions_saved(),
            soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
            soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
            conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
            conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
            conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            fuel_in_liters=False)

        self.r2s = rrs.RRS(total_energy_demand=ref_tam_per_region.loc[2014, 'World'],
            soln_avg_annual_use=self.ac.soln_avg_annual_use,
            conv_avg_annual_use=self.ac.conv_avg_annual_use)

