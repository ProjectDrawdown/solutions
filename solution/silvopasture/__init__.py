"""Silvopasture solution model.
   Excel filename: Drawdown_RRS-BIOSEQ_Model_v1.1_MASTER_Silvopasture_Mar2020.xlsm
"""

import pathlib

import numpy as np
import pandas as pd

from model import adoptiondata
from model import advanced_controls as ac
from model import aez
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
from model import tla
from model import conversions

DATADIR = pathlib.Path(__file__).parents[2].joinpath('data')
THISDIR = pathlib.Path(__file__).parents[0]
VMAs = vma.VMA.load_vma_directory(THISDIR/'vma_data/vma_sources.json')

units = {
    "implementation unit": None,
    "functional unit": "Mha",
    "first cost": "US$B",
    "operating cost": "US$B",
}

name = 'Silvopasture'
solution_category = ac.SOLUTION_CATEGORY.LAND

scenarios = ac.load_scenarios_from_json(directory=THISDIR.joinpath('ac'), vmas=VMAs)

# These are the "default" scenarios to use for each of the drawdown categories.
# They should be set to the most recent "official" set"
PDS1 = "PDS-88p2050-Plausible-customPDS-low-Jan2020"
PDS2 = "PDS-94p2050-Drawdown-customPDS-avg-Jan2020"
PDS3 = "PDS-100p2050-Optimum-customPDS-high-Jan2020"

class Scenario(scenario.LandScenario):
    name = name
    units = units
    vmas = VMAs
    solution_category = solution_category
    module_name = THISDIR.stem

    def __init__(self, scen=None):
        # AC
        self.initialize_ac(scen, scenarios, PDS2)

        # TLA
        self.ae = aez.AEZ(solution_name=self.name, cohort=2020,
                regimes=dd.THERMAL_MOISTURE_REGIMES8)
        if self.ac.use_custom_tla:
            self.c_tla = tla.CustomTLA(filename=THISDIR.joinpath('custom_tla_data.csv'))
            custom_world_vals = self.c_tla.get_world_values()
        else:
            custom_world_vals = None
        self.tla_per_region = tla.tla_per_region(self.ae.get_land_distribution(),
            custom_world_values=custom_world_vals)


        # ADOPTION
        self._ref_ca_sources = scenario.load_sources(THISDIR/'ca_ref_data'/'ca_ref_sources.json', 'filename')
        self._pds_ad_sources = scenario.load_sources(THISDIR/'ad'/'ad_sources.json', '*')

        ca_pds_columns = ['Year'] + dd.REGIONS
        tla_2050 = self.tla_per_region.loc[2050, 'World']
        adoption_vma = VMAs['Current Adoption']
        adoption_2018 = adoption_vma.avg_high_low(key='mean')

        # SOURCE: den Herder, M., Moreno, G., Mosquera-Losada, R. M., Palma, J. H., Sidiropoulou,
        # A., Freijanes, J. J. S., ... & Papanastasis, V. P. (2017). Current extent and
        # stratification of agroforestry in the European Union. Agriculture, Ecosystems &
        # Environment, 241, 121-132.
        ds4_silvo_of_grassland = 0.35
        ds4_total_grassland = 3621.237045
        ds4_potential_adoption = ds4_silvo_of_grassland * ds4_total_grassland
        ds4_adopt_2050 = 0.6 * ds4_potential_adoption

        # SOURCE: Somarriba, E., Beer, J., Alegre-Orihuela, J., Andrade, H. J., Cerda, R., DeClerck,
        # F., ... & Krishnamurthy, L. (2012). Mainstreaming agroforestry in Latin America. In
        # Agroforestry-The Future of Global Land Use (pp. 429-453). Springer, Dordrecht.
        ds5_adoption_rate = 0.45
        pg_vma = VMAs['Total Pasture/Grazing Area']
        pasture_grassland_area = pg_vma.avg_high_low(key='mean')
        ds5_potential_adoption = ds5_adoption_rate * pasture_grassland_area
        ds5_adopt_2050 = 0.6 * ds5_potential_adoption

        # SOURCE: Holman et al., 2004, http://www.lrrd.org/lrrd16/12/holm16098.htm
        growth_initial = pd.DataFrame([[2018] + list(self.ac.ref_base_adoption.values())],
                columns=ca_pds_columns).set_index('Year')
        ds6_rate = 0.006

        # SOURCE: Holman et al., 2004, http://www.lrrd.org/lrrd16/12/holm16098.htm
        ds7_rate = 0.013

        ca_pds_data_sources = [
            {'name': 'Linear trend based on Zomers  >30% tree cover percent area applied in grassland area', 'include': False,
             # This is a proxy adoption scenario which is created in the absence of any data
             # available either on historical growth rate of silvopasture or any future
             # projections. Thus, the present scenario builds the future adoption using the
             # Zoomer 2014 information available on tree coverage in the agricultural area.
             # Country level data on agricultural area with > 30 percent tree cover was available
             # at Zomer 2014. This data was compiled at the Project Drawdown regions, which is
             # then used to get their percent with respect  to the total agricultural area.
             # Those percentages were then applied on the grassland area to get the regional
             # grassland area under >30 percent tree cover. The future adoption of the silvopasture
             # area under was thus projected based on the regional linear trend applied to the
             # grassland area with >30 percent tree coverage. The projections were based on the
             # regional linear trend. (Refer PD region wise - silvopasture sheet)
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Linear_trend_based_on_Zomers_30_tree_cover_percent_area_applied_in_grassland_area.csv')},
            {'name': 'Linear trend based on Zomers >30% tree cover percent area and conversion of >10% are to 30% tree cover area applied in grassland area', 'include': False,
             #  In this scenario, the future area in silvopasture is projected based on scenario
             # one, in addition it was assumed that there will be some extra area available for
             # silvopasture by the conversion of 0-10 percent/11-20 percent tree coverage
             # grassland area to >30 percent tree coverage areas as required for a silvopasture
             # system.  The projections are based on regional linear trends.
                'filename': THISDIR.joinpath('ca_pds_data', 'custom_pds_ad_Linear_trend_based_on_Zomers_30_tree_cover_percent_area_and_conversion_of_10_are_to_30_t_d419700f.csv')},
            {'name': 'Linear Interpolation for Adoption Data based on Nair 2012 & Lal et al. 2018', 'include': True,
             # In the absence of comprehensive historical data for silvopasture adoption, this
             # scenario uses available global adoption estimates reported in peer-reviewed
             # publications. Data points ffrom 2012 (Nair 2012) and 2018 (Lal et al. 2018) were
             # used for a linear interpolation of future adoption based on historic expansion of
             # silvopasture adoption.
             'datapoints': pd.DataFrame([
                [2018, self.ac.ref_base_adoption['World'], 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                [2050, 1083.33333333333, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Medium interpolation based on current adoption, linear trend (high regional proportion of grazing land under silvopasture)', 'include': True,
             # Future area in silvopasture is projected based on the proportion of current area
             # of grazing or pasture land under silvopasture practice in the EU, which currently
             # has the highest regional proportion of grazing land under silvopasture worldwide
             # (35%), as reported by den Herder et al 2017 (see VMA, Variable 31). This percentage
             # was applied to the total global grazing area to obtain a medium estimate of
             # potential projected area for future silvopasture adoption. This scenario assumes
             # 60 percent of future silvopasture adoption by 2050.
             'datapoints': pd.DataFrame([
                [2018, self.ac.ref_base_adoption['World'], 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                [2050, ds4_adopt_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'High interpolation based on current adoption, linear trend (high national proportion of grazing land under silvopasture)', 'include': True,
             # Future area in silvopasture is projected based on the proportion of current area
             # of grazing or pasture land under silvopasture practice in Nicaragua, which currently
             # has the highest national proportion of grazing land under silvopasture worldwide
             # (45%), as reported by Somarriba et al 2012 (see VMA, Variable 31). This percentage
             # was applied to the total global grazing area to obtain a high estimate of potential
             # projected area for future silvopasture adoption. This scenario assumes 60 percent
             # of future silvopasture adoption by 2050.
             'datapoints': pd.DataFrame([
                [2018, self.ac.ref_base_adoption['World'], 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                [2050, ds5_adopt_2050, 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                ], columns=ca_pds_columns).set_index('Year')},
            {'name': 'Low growth, linear trend (based on improved pasture area)', 'include': True,
             # This is a proxy adoption scenario which is created in the absence of any data
             # available either on historical growth rate of silvopasture or any future projections
             # on silvopasture. In this scenario future adoption of silvopasture area was projected
             # using the Thorton 2010 future adoption rates given for improved pasture. The
             # silvopasture adoption is  projected based on the average annual adoption percent
             # (0.60%) increase in the improved pasture area given for the five countries (Mexico,
             # Honduras, Nicaragua, Costa Rica, and Panama) by Holman et al 2004 and reported by
             # Thorton et al 2010. With the limitation of data at the regional level, the
             # projections are made only at the global scale.
             'growth_rate': ds6_rate, 'growth_initial': growth_initial},
            {'name': 'High growth, linear trend (based on improved pasture area)', 'include': True,
             # This is a proxy adoption scenario which is created in the absence of any data
             # available either on historical growth rate of silvopasture or any future projections
             # on silvopasture. In this scenario future adoption of silvopasture area was projected
             # using the Thorton 2010 future adoption rates given for improved pasture. The
             # silvopasture adoption is  projected based on the maximum annual adoption percent
             # (1.30%) increase in the improved pasture area given for the five countries (Mexico,
             # Honduras, Nicaragua, Costa Rica, and Panama) by Holman et al 2004 and reported by
             # Thorton et al 2010. With the limitation of data at the regional level, the
             # projections are made only at the global scale.
             'growth_rate': ds7_rate, 'growth_initial': growth_initial},
        ]
        self.pds_ca = customadoption.CustomAdoption(data_sources=ca_pds_data_sources,
            soln_adoption_custom_name=self.ac.soln_pds_adoption_custom_name,
            high_sd_mult=1.0, low_sd_mult=1.0,
            total_adoption_limit=self.tla_per_region)
        # Manual adjustment made in spreadsheet for Drawdown 2020.
        for source in ca_pds_data_sources:
            if 'filename' in source:
                # only the interpolated sources are adjusted
                continue
            name = source['name']
            s = self.pds_ca.scenarios[name]
            df = s['df']
            df.loc[2012, 'World'] = 450.0
            df.loc[2013, 'World'] = 466.666666666667
            df.loc[2014, 'World'] = 483.333333333333
            df.loc[2015, 'World'] = 500.0
            df.loc[2016, 'World'] = 516.666666666667
            df.loc[2017, 'World'] = 533.333333333333
            df.loc[2018, 'World'] = 550.0

        self.initialize_adoption_bases()
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

        ht_ref_adoption_initial = pd.Series(
            list(self.ac.ref_base_adoption.values()), index=dd.REGIONS)
        ht_ref_adoption_final = self.tla_per_region.loc[2050] * (ht_ref_adoption_initial /
            self.tla_per_region.loc[2014])
        ht_ref_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_ref_datapoints.loc[2018] = ht_ref_adoption_initial
        ht_ref_datapoints.loc[2050] = ht_ref_adoption_final.fillna(0.0)
        ht_pds_adoption_initial = ht_ref_adoption_initial
        ht_pds_adoption_final_percentage = pd.Series(
            list(self.ac.pds_adoption_final_percentage.values()),
            index=list(self.ac.pds_adoption_final_percentage.keys()))
        ht_pds_adoption_final = ht_pds_adoption_final_percentage * self.tla_per_region.loc[2050]
        ht_pds_datapoints = pd.DataFrame(columns=dd.REGIONS)
        ht_pds_datapoints.loc[2018] = ht_pds_adoption_initial
        ht_pds_datapoints.loc[2050] = ht_pds_adoption_final.fillna(0.0)
        self.ht = helpertables.HelperTables(ac=self.ac,
            ref_datapoints=ht_ref_datapoints, pds_datapoints=ht_pds_datapoints,
            pds_adoption_data_per_region=pds_adoption_data_per_region,
            ref_adoption_limits=self.tla_per_region, pds_adoption_limits=self.tla_per_region,
            ref_adoption_data_per_region=ref_adoption_data_per_region,
            copy_pds_world_too=False,
            copy_through_year=2018,
            copy_pds_to_ref=False,
            pds_adoption_trend_per_region=pds_adoption_trend_per_region,
            pds_adoption_is_single_source=pds_adoption_is_single_source)

        self.ef = emissionsfactors.ElectricityGenOnGrid(ac=self.ac, grid_emissions_version=1)

        self.ua = unitadoption.UnitAdoption(ac=self.ac,
            ref_total_adoption_units=self.tla_per_region,
            pds_total_adoption_units=self.tla_per_region,
            electricity_unit_factor=1000000.0,
            soln_ref_funits_adopted=self.ht.soln_ref_funits_adopted(),
            soln_pds_funits_adopted=self.ht.soln_pds_funits_adopted(),
            bug_cfunits_double_count=True)
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
            conv_ref_first_cost_uses_tot_units=True,
            fc_convert_iunit_factor=conversions.mha_to_ha)

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
            conversion_factor=conversions.mha_to_ha)

        self.c4 = ch4calcs.CH4Calcs(ac=self.ac,
            soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)

        self.c2 = co2calcs.CO2Calcs(ac=self.ac,
            ch4_ppb_calculator=self.c4.ch4_ppb_calculator(),
            ch4_megatons_avoided_or_reduced=self.c4.ch4_megatons_avoided_or_reduced(),
            soln_pds_net_grid_electricity_units_saved=self.ua.soln_pds_net_grid_electricity_units_saved(),
            soln_pds_net_grid_electricity_units_used=self.ua.soln_pds_net_grid_electricity_units_used(),
            soln_pds_direct_co2eq_emissions_saved=self.ua.direct_co2eq_emissions_saved_land(),
            soln_pds_direct_co2_emissions_saved=self.ua.direct_co2_emissions_saved_land(),
            soln_pds_direct_n2o_co2_emissions_saved=self.ua.direct_n2o_co2_emissions_saved_land(),
            soln_pds_direct_ch4_co2_emissions_saved=self.ua.direct_ch4_co2_emissions_saved_land(),
            soln_pds_new_iunits_reqd=self.ua.soln_pds_new_iunits_reqd(),
            soln_ref_new_iunits_reqd=self.ua.soln_ref_new_iunits_reqd(),
            conv_ref_new_iunits=self.ua.conv_ref_new_iunits(),
            conv_ref_grid_CO2_per_KWh=self.ef.conv_ref_grid_CO2_per_KWh(),
            conv_ref_grid_CO2eq_per_KWh=self.ef.conv_ref_grid_CO2eq_per_KWh(),
            soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
            annual_land_area_harvested=self.ua.soln_pds_annual_land_area_harvested(),
            regime_distribution=self.ae.get_land_distribution(),
            regimes=dd.THERMAL_MOISTURE_REGIMES8)