"""Generate graphics for Jupyter notebook."""

import os.path
import sys

# we don't want FutureWarning messages appearing in the Jupyter notebook. The person running
# the notebook is likely not the person who could address the warning.
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import altair as alt
import IPython.display
import ipywidgets
import numpy as np
import pandas as pd
import qgrid

from model.advanced_controls import SOLUTION_CATEGORY
from model.co2calcs import C_TO_CO2EQ

import solution.factory
import ui.color
import ui.frizz
import ui.geo
import ui.modelmap
import ui.scn_edit
import ui.vega


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


def solnname(s):
    return type(s).__name__


def fullname(s):
    return type(s).__name__ + ':' + s.scenario


def vma_button_clicked(button):
    """on_click() handler for Jupyter UI buttons."""
    uiobj = button.d['uiobj']
    uiobj._vma_button_clicked(button.d['button_name'])


class JupyterUI:
    """Jupyter notebook UI for Drawdown solutions."""
    def __init__(self):
        pd.set_option('display.max_columns', 200)
        pd.set_option('display.max_rows', 200)
        all_solutions = pd.read_csv(os.path.join('data', 'overview', 'solutions.csv'),
                                            index_col=False, skipinitialspace=True, header=0,
                                            skip_blank_lines=True, comment='#')
        soln_results = pd.read_csv(os.path.join('data', 'overview', 'soln_results.csv'),
                                            index_col=False, skipinitialspace=True, header=0,
                                            skip_blank_lines=True, comment='#')
        all_solutions = all_solutions.merge(soln_results, on='Solution', how='left')
        sectors = all_solutions.pivot_table(index='Sector', aggfunc=sum)
        all_solutions['SectorCO2eq'] = all_solutions.apply(
                lambda row: sectors.loc[row['Sector'], 'CO2eq'], axis=1)

        # all_solutions is a list of all solutions the system knows about, solutions is the list
        # of solution objects currently being analyzed with detailed results tabs.
        self.all_solutions = all_solutions
        self.solutions = []

        # checkboxes is a dict of solution names to ipywidget.checkbox objects.
        self.checkboxes = None

        # ui_elements holds state for different parts of the UI which the user can manipulate
        self.ui_elements = {}


    def _get_sector_for_solution(self, module_name):
        row = self.all_solutions.loc[self.all_solutions['DirName'] == module_name]
        if row.empty:
            # remove prepended 'solution.solarpvutil'
            mn = module_name.split('.')[-1]
            row = self.all_solutions.loc[self.all_solutions['DirName'] == mn]
        if row.empty:
            return ''
        return row.iloc[0]['Sector']


    def get_overview(self):
        """Returns overview

           Where:
             overview is an ipywidget to be displayed in Jupyter showing an overview
               of available solutions, information about the solutions, and contains checkboxes
               allowing specific solutions to be examined in more details.
        """
        solution_chart = ipywidgets.Output()
        with solution_chart:
            IPython.display.display({'application/vnd.vega.v4+json': ui.vega.solution_donut_chart(
                solutions=self.all_solutions, width=400, height=400)}, raw=True)

        soln_layout = ipywidgets.Layout(flex='12 1 0%', width='auto')
        sctr_layout = ipywidgets.Layout(flex='8 1 0%', width='auto')
        c2eq_layout = ipywidgets.Layout(flex='2 1 0%', width='auto')
        cbox_layout = ipywidgets.Layout(flex='1 1 0%', width='auto')
        cntr_layout = ipywidgets.Layout(display="flex", flex_flow="row",
                justify_items="stretch", width="100%")
        white_row = '<div style="font-size:medium; background-color:white;padding-left:2px;">'
        grey_row = '<div style="font-size:medium; background-color:#ececec;padding-left:2px;">'
        hdr_row = '<div style="font-size:large;background-color:white;'
        hdr_row += 'padding-left:2px;font-weight:bold;">'

        checkboxes = {}
        children = [ipywidgets.HBox([ipywidgets.HTML(f'{hdr_row}Solution</div>', layout=soln_layout),
                                     ipywidgets.HTML(f'{hdr_row}Sector</div>', layout=sctr_layout),
                                     ipywidgets.HTML(f'{hdr_row}CO2eq</div>', layout=c2eq_layout),
                                     ipywidgets.HTML('<div></div>', layout=cbox_layout)],
                                     layout=cntr_layout)]
        style = white_row
        for row in self.all_solutions.sort_values(['SectorCO2eq', 'CO2eq'],
                ascending=False).fillna('').itertuples():
            soln = ipywidgets.HTML(f'{style}{row.Solution}</div>', layout=soln_layout)
            sctr = ipywidgets.HTML(f'{style}{row.Sector}</div>', layout=sctr_layout)
            c2eq = ipywidgets.HTML(f'{style}{row.CO2eq:.02f}</div>', layout=c2eq_layout)
            if row.DirName:
                cbox = ipywidgets.Checkbox(layout=cbox_layout)
                checkboxes[row.DirName] = cbox
            else:
                cbox = ipywidgets.HTML('<div></div>', layout=cbox_layout)
            cbox.style.description_width = '0px'
            children.append(ipywidgets.HBox([soln, sctr, c2eq, cbox], layout=cntr_layout))
            style = grey_row if style == white_row else white_row
        list_layout = ipywidgets.Layout(flex='5 1 0%', width='auto')
        solution_list = ipywidgets.VBox(children=children, layout=list_layout)

        solution_treemap = ipywidgets.Output()
        with solution_treemap:
            IPython.display.display({'application/vnd.vega.v4+json': ui.vega.solution_treemap(
                solutions=self.all_solutions, width=400, height=800)}, raw=True)

        chrt_layout = ipywidgets.Layout(flex='3 1 0%', width='auto')
        charts = ipywidgets.VBox(children=[solution_chart, solution_treemap], layout=chrt_layout)
        details_progressbar = ipywidgets.FloatProgress(value=0.0, min=0.0, max=1.0,
                step=0.01, orientation='horizontal', layout=ipywidgets.Layout(width='99%'))
        self.ui_elements['details_progressbar'] = details_progressbar
        overview = ipywidgets.VBox(children=[
            ipywidgets.HBox(children=[solution_list, charts], layout=cntr_layout),
            details_progressbar])

        self.checkboxes = checkboxes
        return overview


    def _get_summary_ua(self, solutions):
        """Return Summary panel for Unit Adoption.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        unit_adoption_text = []
        for s in solutions:
            ilabel = s.units['implementation unit']
            flabel = s.units['functional unit']
            if ilabel:
                pds_vs_ref = (s.ua.soln_pds_tot_iunits_reqd().loc[2050, 'World'] -
                        s.ua.soln_ref_tot_iunits_reqd().loc[2050, 'World'])
                iunits = f"{pds_vs_ref:.2f} {ilabel}"
                funits = f"{s.ua.soln_net_annual_funits_adopted().loc[2050, 'World']:.2f} {flabel}"
            else:
                iunits = ''
                funits = f"{s.ua.soln_net_annual_funits_adopted().loc[2050, 'World']:.2f} {flabel}"
            unit_adoption_text.append([fullname(s), iunits, funits])

        unit_adoption_columns = ['Scenario', 'Implementation Adoption Increase in 2050 (PDS vs REF)',
                                 'Functional Units/Area Adoption Increase in 2050 (PDS vs REF)']
        details_ua = ipywidgets.Output()
        with details_ua:
            df = pd.DataFrame(unit_adoption_text, columns=unit_adoption_columns)
            IPython.display.display(IPython.display.HTML(
                df.style.set_table_styles(dataframe_css_styles).hide_index().render()))
        return details_ua


    def _get_summary_ad(self, solutions):
        """Return Summary panel for Adoption Data.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        adoption_text = []
        for s in solutions:
            ilabel = s.units['implementation unit']
            flabel = s.units['functional unit']
            if ilabel:
                iunits = f'{s.ua.soln_pds_tot_iunits_reqd().loc[2050, "World"]:.2f} {ilabel}'
            else:
                iunits = ''
            funits = f'{s.ht.soln_pds_funits_adopted().loc[2050, "World"]:.2f} {flabel}'
            adoption_text.append([fullname(s), iunits, funits, '%', '%', '%'])
        adoption_columns = ['Scenario', 'Global Solution Implementation Units in 2050',
                            'Global Solution Functional Units/Area in 2050',
                            'Global Solution Adoption Share - 2014',
                            'Global Solution Adoption Share - 2020',
                            'Global Solution Adoption Share - 2050']
        adoption_heading = ipywidgets.Output()
        with adoption_heading:
            df = pd.DataFrame(adoption_text, columns=adoption_columns)
            IPython.display.display(IPython.display.HTML(df.style.set_table_styles(
                dataframe_css_styles).hide_index().render()))

        has_iunit_chart = False
        adoption_iunit_chart = ipywidgets.Output()
        with adoption_iunit_chart:
            df = pd.DataFrame()
            for s in solutions:
                if s.units['implementation unit'] is None:
                    continue
                df[fullname(s)] = s.ua.soln_pds_tot_iunits_reqd().loc[2020:2050, 'World']
            if not df.empty:
                has_iunit_chart = True
                iunit_df = df.reset_index().melt('Year', value_name='iunits', var_name='solution')
                iunit_chart = alt.Chart(iunit_df, width=400).mark_line().encode(
                    y='iunits',
                    x='Year:O',
                    color=alt.Color('solution', legend=alt.Legend(orient='top-left', title=None)),
                    tooltip=['solution', alt.Tooltip('iunits:Q', format='.2f'), 'Year'],
                ).properties(
                    title='World Adoption - Implementation Units'
                ).interactive()
                IPython.display.display(iunit_chart)

        adoption_funit_chart = ipywidgets.Output()
        with adoption_funit_chart:
            df = pd.DataFrame()
            for s in self.solutions:
                # tla/toa is constant between scenarios in the same solution so we only plot it once
                if s.ac.solution_category == SOLUTION_CATEGORY.LAND:
                    df['Total Land Area:' + solnname(s)] = s.tla_per_region.loc[2020:2050, 'World']
                elif s.ac.solution_category == SOLUTION_CATEGORY.OCEAN:
                    df['Total Ocean Area:' + solnname(s)] = s.toa_per_region.loc[2020:2050, 'World']
                else:
                    ref_tam = s.tm.ref_tam_per_region().loc[2020:2050, 'World']
                    pds_tam = s.tm.pds_tam_per_region().loc[2020:2050, 'World']
                    df['Total Market-REF:' + fullname(s)] = ref_tam
                    df['Total Market-PDS:' + fullname(s)] = pds_tam
            funit_df = df.reset_index().melt('Year', value_name='units', var_name='fullname')
            funit_df[['variable','solution']] = funit_df.fullname.str.split(':', n=1, expand=True)
            chart1 = alt.Chart(funit_df, width=400).mark_line().encode(
                    y='units:Q',
                    x=alt.X('Year', type='ordinal', scale=alt.Scale(domain=list(range(2015, 2056)))),
                    color=alt.Color('solution', legend=alt.Legend(orient='top-left', title=None)),
                    detail='fullname',
                    tooltip=['variable', 'solution', alt.Tooltip('units:Q', format='.2f'), 'Year']
                ).properties(
                    title='World Adoption - Functional Units/Area'
                ).interactive()
            df = pd.DataFrame()
            for s in self.solutions:
                ref_funits = s.ht.soln_ref_funits_adopted().loc[2020:2050, 'World']
                df['Solution-REF:' + fullname(s)] = ref_funits
            funit_df = df.reset_index().melt('Year', value_name='units', var_name='fullname')
            funit_df[['variable','solution']] = funit_df.fullname.str.split(':', n=1, expand=True)
            chart2 = alt.Chart(funit_df, width=400).mark_line(strokeDash=[1,1]).encode(
                    y='units:Q',
                    x=alt.X('Year', type='ordinal', scale=alt.Scale(domain=list(range(2015, 2056)))),
                    color=alt.Color('solution', legend=alt.Legend(orient='top-left', title=None)),
                    detail='fullname',
                    tooltip=['variable', 'solution', alt.Tooltip('units:Q', format='.2f'), 'Year']
                ).properties(
                    title='World Adoption - Functional Units/Area'
                ).interactive()
            df = pd.DataFrame()
            for s in self.solutions:
                pds_funits = s.ht.soln_pds_funits_adopted().loc[2020:2050, 'World']
                df['Solution-PDS:' + fullname(s)] = pds_funits
            funit_df = df.reset_index().melt('Year', value_name='units', var_name='fullname')
            funit_df[['variable','solution']] = funit_df.fullname.str.split(':', n=1, expand=True)
            chart3 = alt.Chart(funit_df, width=400).mark_line(strokeDash=[3,2]).encode(
                    y='units:Q',
                    x=alt.X('Year', type='ordinal', scale=alt.Scale(domain=list(range(2015, 2056)))),
                    color=alt.Color('solution', legend=alt.Legend(orient='top-left', title=None)),
                    detail='fullname',
                    tooltip=['variable', 'solution', alt.Tooltip('units:Q', format='.2f'), 'Year']
                ).properties(
                    title='World Adoption - Functional Units/Area'
                ).interactive()
            IPython.display.display(chart1 + chart2 + chart3)

        if has_iunit_chart:
            children = [adoption_iunit_chart, adoption_funit_chart]
        else:
            children = [adoption_funit_chart]
        adoption_graphs = ipywidgets.HBox(children=children)

        return (adoption_heading, adoption_graphs)


    def _get_summary_financial(self, solutions):
        """Return Summary panel for financial results.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        financial_text = []
        for s in solutions:
            fc_label = s.units['first cost']
            oc_label = s.units['operating cost']

            marginal_first_cost = (s.fc.soln_pds_annual_world_first_cost().loc[:2050].sum() -
                s.fc.soln_ref_annual_world_first_cost().loc[:2050].sum() -
                s.fc.conv_ref_annual_world_first_cost().loc[:2050].sum()) / 10**9
            net_operating_savings = ((s.oc.conv_ref_cumulative_operating_cost().loc[2050] -
                                     s.oc.conv_ref_cumulative_operating_cost().loc[2020]) -
                                    (s.oc.soln_pds_cumulative_operating_cost().loc[2050] -
                                     s.oc.soln_pds_cumulative_operating_cost().loc[2020])) / 10**9
            lifetime_operating_savings = s.oc.soln_marginal_operating_cost_savings().sum() / 10**9
            financial_text.append([fullname(s),
                                   f'{marginal_first_cost:.2f} {fc_label}',
                                   f'{net_operating_savings:.2f} {oc_label}',
                                   f'{lifetime_operating_savings:.2f} {oc_label}'])
        financial_columns = ['Scenario', 'Marginal First Cost 2020-2050',
                             'Net Operating Savings 2020-2050', 'Lifetime Operating Savings 2020-2050']

        financial_heading = ipywidgets.Output()
        with financial_heading:
            df = pd.DataFrame(financial_text, columns=financial_columns)
            IPython.display.display(IPython.display.HTML(df.style.set_table_styles(
                dataframe_css_styles).hide_index().render()))

        financial_graphs = ipywidgets.Output()
        with financial_graphs:
            df = pd.DataFrame()
            for s in solutions:
                pds_oc = s.oc.soln_pds_annual_operating_cost().loc[2020:2050] / 1000000000
                df['Solution Operating Costs/Savings:' + fullname(s)] = pds_oc
            cost_df = df.reset_index().melt('Year', value_name='costs', var_name='fullname')
            cost_df[['variable','solution']] = cost_df.fullname.str.split(':', n=1, expand=True)
            chart1 = alt.Chart(cost_df, width=350).mark_line().encode(
                y=alt.Y('costs', title='US$B'),
                x=alt.X('Year', type='ordinal', scale=alt.Scale(domain=list(range(2015, 2056)))),
                color=alt.Color('solution', legend=alt.Legend(orient='top-left', title=None)),
                detail='fullname',
                tooltip=['variable', 'solution', alt.Tooltip('costs:Q', format='.2f'), 'Year']
            ).properties(
                title='World Operating Cost Difference'
            ).interactive()

            df = pd.DataFrame()
            for s in solutions:
                cref_oc = s.oc.conv_ref_annual_operating_cost().loc[2020:2050] / 1000000000
                df['Conventional Operating Costs/Savings:' + fullname(s)] = cref_oc
            cost_df = df.reset_index().melt('Year', value_name='costs', var_name='fullname')
            cost_df[['variable','solution']] = cost_df.fullname.str.split(':', n=1, expand=True)
            chart2 = alt.Chart(cost_df, width=350).mark_line(strokeDash=[3,2]).encode(
                y=alt.Y('costs', title='US$B'),
                x=alt.X('Year', type='ordinal', scale=alt.Scale(domain=list(range(2015, 2056)))),
                color=alt.Color('solution', legend=alt.Legend(orient='top-left', title=None)),
                detail='fullname',
                tooltip=['variable', 'solution', alt.Tooltip('costs:Q', format='.2f'), 'Year']
            ).properties(
                title='World Operating Cost Difference'
            ).interactive()
            IPython.display.display(chart1 + chart2)

        return (financial_heading, financial_graphs)


    def _get_summary_climate(self, solutions):
        """Return Summary panel for climate results.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        climate_text = []
        for s in solutions:
            g_tons = s.c2.co2eq_mmt_reduced().loc[2020:2050, 'World'].sum() / 1000
            if s.ac.solution_category == SOLUTION_CATEGORY.LAND or s.ac.solution_category == SOLUTION_CATEGORY.OCEAN:
                # Note the sequestration table in co2calcs doesn't set values to zero outside
                # the study years. In the xls there is a separate table which does this. Here,
                # we select the years directly.
                # The xls implemntation also excludes the year 2020, almost certainly by mistake.
                # Thus, this value will differ slightly from the one given in the Detailed Results
                # xls sheet.
                # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit
                g_tons += s.c2.co2_sequestered_global().loc[2020:2050, 'All'].sum() / 1000
            climate_text.append([fullname(s), f"{g_tons:.2f} Gt"])

        climate_heading = ipywidgets.Output()
        with climate_heading:
            df = pd.DataFrame(climate_text, columns=['Scenario', 'Total Atmospheric CO2-eq Reduction'])
            IPython.display.display(IPython.display.HTML(df.style.set_table_styles(
                dataframe_css_styles).hide_index().render()))

        # Reduction/sequestration/TAR data
        red_df, seq_df, tar_df = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        ymin = ymax = 0
        for s in solutions:
            reduction = s.c2.co2eq_mmt_reduced().loc[2020:2050, 'World'].cumsum().mul(0.001)
            red_df[fullname(s)] = reduction
            if s.ac.solution_category == SOLUTION_CATEGORY.LAND or s.ac.solution_category == SOLUTION_CATEGORY.OCEAN:
                sequestration = s.c2.co2_sequestered_global().loc[2020:2050, 'All'].cumsum().mul(0.001)
                seq_df[fullname(s)] = sequestration
                tar_df[fullname(s)] = reduction + sequestration
                ymax = max(seq_df.max().max(), red_df.max().max(), ymax)
                ymin = min(seq_df.min().min(), red_df.min().min(), ymin)
            else:
                tar_df[fullname(s)] = reduction
                ymax = max(red_df.max().max(), ymax)
                ymin = min(0, ymin)

        # Sequestration graph
        if not seq_df.empty:
            sequestration_df = seq_df.reset_index().melt('Year', value_name='Gt CO2', var_name='solution')
            sequestration_graph = ipywidgets.Output()
            with sequestration_graph:
                chart = alt.Chart(sequestration_df, width=300).mark_line().encode(
                    y=alt.Y('Gt CO2', scale=alt.Scale(domain=[ymin, ymax])),  # use same scale
                    x=alt.X('Year', type='ordinal'),
                    color=alt.Color('solution', legend=alt.Legend(orient='top-left', title=None)),
                    tooltip=['solution', 'Gt CO2', 'Year'],
                ).properties(
                    title='World Cumulative CO2 Sequestered'
                ).interactive()
                IPython.display.display(chart)

            # Reduction graph
            reduction_df = red_df.reset_index().melt('Year', value_name='Gt CO2-eq', var_name='solution')
            reduction_graph = ipywidgets.Output()
            with reduction_graph:
                chart = alt.Chart(reduction_df, width=300).mark_line().encode(
                    y=alt.Y('Gt CO2-eq', scale=alt.Scale(domain=[ymin, ymax])),  # use same scale
                    x=alt.X('Year', type='ordinal'),
                    color=alt.Color('solution', legend=alt.Legend(orient='top-left', title=None)),
                    tooltip=['solution', 'Gt CO2-eq', 'Year'],
                ).properties(
                    title='World Cumulative CO2-eq Reduced'
                ).interactive()
                IPython.display.display(chart)

            tar_graph_width = 300
        else:
            # resize total atmospheric reduction graph to fill display
            tar_graph_width = 700

        # Total atmospheric reduction graph
        total_reduction_df = tar_df.reset_index().melt('Year', value_name='Gt CO2-eq', var_name='solution')
        total_reduction_graph = ipywidgets.Output()
        with total_reduction_graph:
            chart = alt.Chart(total_reduction_df, width=tar_graph_width).mark_line().encode(
                y=alt.Y('Gt CO2-eq', scale=alt.Scale(domain=[ymin, ymax])),  # use same scale
                x=alt.X('Year', type='ordinal'),
                color=alt.Color('solution', legend=alt.Legend(orient='top-left', title=None)),
                tooltip=['solution', 'Gt CO2-eq', 'Year'],
            ).properties(
                title='World Cumulative Total Atmospheric CO2-eq Reduction'
            ).interactive()
            IPython.display.display(chart)

        # Concentration data/graph
        df = pd.DataFrame()
        for s in solutions:
            df[fullname(s)] = s.c2.co2eq_ppm_calculator().loc[2020:2050, 'CO2-eq PPM']
        concentration_df = df.reset_index().melt('Year', value_name='concentration', var_name='solution')
        concentration_graph = ipywidgets.Output()
        with concentration_graph:
            chart = alt.Chart(concentration_df, width=700).mark_line().encode(
                y='concentration',
                x=alt.X('Year', type='ordinal'),
                color=alt.Color('solution', legend=alt.Legend(orient='top-left', title=None)),
                tooltip=['solution', 'concentration', 'Year'],
            ).properties(
                title='World Cumulative GHG Concentration Reduction'
            ).interactive()
            IPython.display.display(chart)

        climate_graph_list = [total_reduction_graph]
        if not seq_df.empty:
            climate_graph_list += [reduction_graph, sequestration_graph]

        mmt_graphs = ipywidgets.HBox(children=climate_graph_list)
        concentration_graphs = ipywidgets.HBox(children=[concentration_graph])

        return climate_heading, mmt_graphs, concentration_graphs



    def _get_summary_productivity(self, solutions):
        """Return Summary panel for land/ocean productivity.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        prod_text = []
        yield_df = pd.DataFrame()
        for s in solutions:
            if s.ac.solution_category == SOLUTION_CATEGORY.LAND or s.ac.solution_category == SOLUTION_CATEGORY.OCEAN:
                funits = s.ua.soln_net_annual_funits_adopted().loc[2020:2050, 'World']
                pot_yield_incr = funits.sum() * s.ac.yield_coeff
                if pot_yield_incr > 0:
                    yield_df[fullname(s)] = (funits * s.ac.yield_coeff).cumsum()
                    prod_text.append([fullname(s), f"{pot_yield_incr:.2f} MMt"])
        prod_columns = ['Scenario', 'Potential yield increase over report years']

        if not prod_text:
            return (None, None)

        prod_heading = ipywidgets.Output()
        with prod_heading:
            df = pd.DataFrame(prod_text, columns=prod_columns)
            IPython.display.display(IPython.display.HTML(df.style.set_table_styles(
                dataframe_css_styles).hide_index().render()))

        prod_graph = ipywidgets.Output()
        with prod_graph:
            prod_df = yield_df.reset_index().melt('Year', value_name='metric tons', var_name='solution')
            chart = alt.Chart(prod_df, width=300).mark_line().encode(
                y='metric tons',
                x=alt.X('Year', type='ordinal'),
                color=alt.Color('solution', legend=alt.Legend(orient='top-left', title=None)),
                tooltip=['solution', 'metric tons', 'Year'],
            ).properties(
                title='Cumulative Potential Yield Increase'
            ).interactive()
            IPython.display.display(chart)

        return (prod_heading, prod_graph)


    def _get_summary_protection(self, solutions):
        """Return Summary panel for land/ocean protection results.

           Arguments:
                solutions: a list of solution objects to be processed.
        """
        protect_text = []
        cridl_df, protected_co2_df, protected_c_df = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        for s in solutions:
            if s.ac.solution_category == SOLUTION_CATEGORY.LAND or s.ac.solution_category == SOLUTION_CATEGORY.OCEAN:
                cumulative_land_deg = s.ua.cumulative_reduction_in_total_degraded_land()['World']
                red_land_deg = cumulative_land_deg[2050] - cumulative_land_deg[2019]
                if red_land_deg > 0:
                    cridl_df[fullname(s)] = cumulative_land_deg.loc[2020:2050]
                    protected_c = (s.ua.soln_pds_funits_adopted.loc[2020:2050, 'World'] -
                            s.ua.pds_cumulative_degraded_land_protected().loc[2020:2050, 'World'])
                    if s.ac.tC_storage_in_protected_land_type is not None:
                        protected_c *= s.ac.tC_storage_in_protected_land_type / 1000
                    else:
                        protected_c *= 0.0
                    protected_c_df[fullname(s)] = protected_c
                    protected_co2 = protected_c * C_TO_CO2EQ
                    protected_co2_df[fullname(s)] = protected_c
                    protect_text.append([fullname(s),
                                         f"{red_land_deg:.2f} MHa",
                                         f"{protected_co2[2050]:.2f} Gt CO2",
                                         f"{protected_c[2050]:.2f} Gt Carbon"])
        protect_columns = ['Scenario', 'Reduced Land Degradation from 2020-2050', 'Total CO2 Under Protection by 2050',
                                'Total Carbon Under Protection by 2050']

        if not protect_text:
            return (None, None)

        protect_heading = ipywidgets.Output()
        with protect_heading:
            df = pd.DataFrame(protect_text, columns=protect_columns)
            IPython.display.display(IPython.display.HTML(df.style.set_table_styles(
                dataframe_css_styles).hide_index().render()))

        cridl_graph = ipywidgets.Output()
        with cridl_graph:
            cridl_df = cridl_df.reset_index().melt('Year', value_name='million hectare', var_name='solution')
            chart = alt.Chart(cridl_df, width=300).mark_line().encode(
                y='million hectare',
                x=alt.X('Year', type='ordinal'),
                color=alt.Color('solution', legend=alt.Legend(orient='top-left', title=None)),
                tooltip=['solution', 'million hectare', 'Year'],
            ).properties(
                title='Cumulative Reduced Land Degradation'
            ).interactive()
            IPython.display.display(chart)

        protected_co2_graph = ipywidgets.Output()
        with protected_co2_graph:
            protected_co2_df = protected_co2_df.reset_index().melt('Year', value_name='Gt CO2', var_name='solution')
            chart = alt.Chart(protected_co2_df, width=300).mark_line().encode(
                y='Gt CO2',
                x=alt.X('Year', type='ordinal'),
                color=alt.Color('solution', legend=alt.Legend(orient='bottom-right', title=None)),
                tooltip=['solution', 'Gt CO2', 'Year'],
            ).properties(
                title='Total CO2 Under Protection'
            ).interactive()
            IPython.display.display(chart)
            
        protected_c_graph = ipywidgets.Output()
        with protected_c_graph:
            protected_c_df = protected_c_df.reset_index().melt('Year', value_name='Gt carbon', var_name='solution')
            chart = alt.Chart(protected_c_df, width=300).mark_line().encode(
                y='Gt carbon',
                x=alt.X('Year', type='ordinal'),
                color=alt.Color('solution', legend=alt.Legend(orient='bottom-right', title=None)),
                tooltip=['solution', 'Gt carbon', 'Year'],
            ).properties(
                title='Total Carbon Under Protection'
            ).interactive()
            IPython.display.display(chart)

        protect_graphs = ipywidgets.HBox(children=[cridl_graph, protected_co2_graph, protected_c_graph])

        return (protect_heading, protect_graphs)


    def blue_label(self, text):
        div = '<div style="background-color:LightSkyBlue;border:1px solid black;'
        div += 'font-weight:bold;text-align:center;font-size:0.875em;">'
        return ipywidgets.HTML(value=div + text + '</div>')


    def get_summary_tab(self, solutions):
        """Return Summary panel.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        key_results_label = self.blue_label('The Key Adoption Results')
        unit_adoption_heading = self._get_summary_ua(solutions)
        (adoption_heading, adoption_graphs) = self._get_summary_ad(solutions)

        financial_results_label = self.blue_label('The Key Financial Results')
        (financial_heading, cost_graphs) = self._get_summary_financial(solutions)

        climate_results_label = self.blue_label('The Key Climate Results')
        (climate_heading, mmt_graphs, concentration_graphs) = self._get_summary_climate(solutions)

        prod_results_label = self.blue_label('The Key Productivity Results')
        (prod_heading, prod_graph) = self._get_summary_productivity(solutions)
        has_prod_results = True if (prod_heading and prod_graph) else False

        protect_results_label = self.blue_label('The Key Protection Results')
        (protect_heading, protect_graphs) = self._get_summary_protection(solutions)
        has_protect_results = True if (protect_heading and protect_graphs) else False

        detailed_results = ipywidgets.Output()
        with detailed_results:
            to_disp = [key_results_label, unit_adoption_heading, adoption_heading, adoption_graphs,
                    financial_results_label, financial_heading, cost_graphs, climate_results_label,
                    climate_heading, mmt_graphs, concentration_graphs]
            if has_prod_results:
                to_disp.extend([prod_results_label, prod_heading, prod_graph])
            if has_protect_results:
                to_disp.extend([protect_results_label, protect_heading, protect_graphs])
            IPython.display.display(ipywidgets.VBox(to_disp))

        return detailed_results


    def get_model_tab(self, solutions):
        """Return Model panel.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        classes = set()
        for s in solutions:
            classes.add(sys.modules[s.__module__])

        children = []
        titles = []
        for c in classes:
            modelmap = ipywidgets.Output()
            with modelmap:
                IPython.display.display(IPython.display.SVG(
                    data=ui.modelmap.get_model_overview_svg(model=c)))
            editor = ui.scn_edit.get_scenario_editor_for_solution(soln_mod=c)
            divider = ipywidgets.HTML(value='<br/><hr/><br/>')
            children.append(ipywidgets.VBox(children=[modelmap, divider, editor]))
            titles.append(c.__name__)
        layout = ipywidgets.Layout(width='90%')
        model_overview = ipywidgets.Accordion(children=children, layout=layout)
        for idx, name in enumerate(titles):
            model_overview.set_title(idx, name)

        return model_overview


    def _vma_button_clicked(self, button_name):
        state = self.ui_elements[button_name]
        button = state['button']
        table = state['table']
        v = state['vmaobj']
        if state['editing'] == True:
            state['editing'] = False
            v.write_to_file(table.children[0].get_changed_df())
            table.children = [self.get_vma_readonly_sources_list(v)]
            button.description = 'Edit'
        else:
            state['editing'] = True
            table.children = [self.get_vma_editable_sources_list(v)]
            button.description = 'Save'


    def get_vma_readonly_sources_list(self, v):
        return qgrid.show_grid(data_frame=v.source_data.fillna(''), precision=2,
                grid_options={'forceFitColumns':False, 'maxVisibleRows':25},
                column_options={'editable':False})


    def get_vma_editable_sources_list(self, v):
        return qgrid.show_grid(data_frame=v.source_data.fillna(''), show_toolbar=True,
                grid_options={'forceFitColumns':False, 'maxVisibleRows':23},
                column_options={'editable':True})


    def get_VMA_tab(self, solutions):
        """Return VMA panel.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        modules = []
        for s in solutions:
            m = sys.modules[s.__module__]
            if m not in modules:
                modules.append(m)
        summary_css_styles = [
            dict(selector="th", props=[
                ('font-size', '1em'), ('text-align', 'center'), ('font-weight', 'bold'),
                ('color', '#6d6d6d'), ('background-color', '#f7f7f9')
            ]),
            dict(selector="td", props=[
                ('font-size', '0.9em'), ('text-align', 'center'), ('font-weight', 'bold')
            ]),
          ]
        variable_meta_analysis = ipywidgets.Output()
        with variable_meta_analysis:
            children = []
            for m in modules:
                if not hasattr(m, 'VMAs') or not m.VMAs:
                    continue
                vmas_for_module = []
                for (name, v) in m.VMAs.items():
                    div = '<div style="background-color:gainsboro;border:1px solid dimgray;'
                    div += 'font-weight:bold;text-align:center;font-size:1.1em;color:dimgray;">'
                    vma_name = ipywidgets.HTML(f'{div}{name}</div>',
                            layout=ipywidgets.Layout(width='auto', grid_area='vma_name'))
                    mean, high, low = v.avg_high_low()
                    hdr_style = ('font-size:1em;text-align:center;font-weight:bold;' +
                            'color:#6d6d6d;background-color:#f7f7f9')
                    num_style = 'font-size:0.9em;text-align:center;font-weight:bold;'
                    summary = ipywidgets.HTML('<table>' +
                                              f'<tr><td style={hdr_style}>Mean</td></tr>' +
                                              f'<tr><td style={num_style}>{mean:.1f}</td></tr>' +
                                              f'<tr><td style={hdr_style}>High</td></tr>' +
                                              f'<tr><td style={num_style}>{high:.1f}</td></tr>' +
                                              f'<tr><td style={hdr_style}>Low</td></tr>' +
                                              f'<tr><td style={num_style}>{low:.1f}</td></tr>' +
                                              '</table>')
                    edit_button = ipywidgets.Button(description='Edit', button_style='',
                            tooltip='Edit VMA Sources', layout=ipywidgets.Layout(width='auto'))
                    button_name = f'{m.__name__}:{name}:edit_button'
                    edit_button.d = {
                            'uiobj': self,
                            'button_name': button_name,
                            }
                    edit_button.on_click(vma_button_clicked)
                    sidebar = ipywidgets.VBox(children=[summary, edit_button],
                            layout=ipywidgets.Layout(width='auto', grid_area='sidebar'))
                    table = ipywidgets.VBox(children=[self.get_vma_readonly_sources_list(v)])
                    vma_widget = ipywidgets.GridBox(children=[vma_name, sidebar, table],
                            layout=ipywidgets.Layout(width='100%', grid_template_rows='auto auto',
                                    grid_template_columns='7% 93%',
                                    grid_template_areas='''
                                    "vma_name vma_name"
                                    "sidebar table"
                                    '''))
                    vmas_for_module.append(vma_widget)
                    self.ui_elements[button_name] = {
                            'button': edit_button,
                            'table': table,
                            'editing': False,
                            'vmaobj': v,
                            }

                accordion = ipywidgets.Accordion(
                        children=[ipywidgets.VBox(children=vmas_for_module)])
                accordion.set_title(0, m.__name__.split('.')[-1])
                children.append(accordion)
            IPython.display.display(ipywidgets.VBox(children=children))
        return variable_meta_analysis


    def get_first_cost_tab(self, solutions):
        """Return First Cost panel.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        children = []
        for s in solutions:
            df = pd.concat([s.fc.soln_pds_install_cost_per_iunit().loc[2020:2050],
                            s.fc.soln_ref_install_cost_per_iunit().loc[2020:2050],
                            s.fc.conv_ref_install_cost_per_iunit().loc[2020:2050]],
                           axis=1)
            df.columns = ['SOLN-PDS', 'SOLN-REF', 'CONV-REF']
            df[['SOLN-PDS', 'SOLN-REF', 'CONV-REF']] /= s.fc.fc_convert_iunit_factor
            fc_table = ipywidgets.Output()
            with fc_table:
                IPython.display.display(IPython.display.HTML(df
                    .style.format({'SOLN-PDS':'{:.02f}', 'SOLN-REF':'{:.02f}', 'CONV-REF':'{:.02f}'})
                    .set_table_styles(dataframe_css_styles)
                    .render()))
            fc_model = ipywidgets.Output()
            with fc_model:
                IPython.display.display(IPython.display.SVG(data=ui.modelmap.get_model_overview_svg(
                    model=sys.modules[s.__module__], highlights=['fc'], width=350)))
            fc_chart = ipywidgets.Output()
            with fc_chart:
                melted_df = df.reset_index().melt('Year', value_name='cost', var_name='column')
                chart = alt.Chart(melted_df, width=350).mark_line().encode(
                    y='cost',
                    x='Year:O',
                    color=alt.Color('column'),
                    tooltip=['column', 'cost', 'Year'],
                ).properties(
                    title='First Cost (US$M)'
                ).interactive()
                IPython.display.display(chart)
            children.append(ipywidgets.HBox([fc_table, ipywidgets.VBox([fc_model, fc_chart])]))

        first_cost = ipywidgets.Accordion(children=children)
        for i, s in enumerate(solutions):
            first_cost.set_title(i, fullname(s))

        return first_cost


    def get_operating_cost_tab(self, solutions):
        """Return Operating Cost panel.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        children = []
        for s in solutions:
            df = pd.concat([s.oc.soln_pds_annual_operating_cost().loc[2020:2050],
                            s.oc.conv_ref_annual_operating_cost().loc[2020:2050],
                            s.oc.marginal_annual_operating_cost().loc[2020:2050]],
                           axis=1)
            df.columns = ['PDS', 'REF', 'Marginal']
            df[['PDS', 'REF', 'Marginal']] /= s.oc.conversion_factor_fom
            oc_table = ipywidgets.Output()
            with oc_table:
                IPython.display.display(IPython.display.HTML(df
                    .style.format({'PDS':'{:.02f}', 'REF':'{:.02f}', 'Marginal':'{:.02f}'})
                    .set_table_styles(dataframe_css_styles).render()))
            oc_model = ipywidgets.Output()
            with oc_model:
                IPython.display.display(IPython.display.SVG(
                    data=ui.modelmap.get_model_overview_svg(
                        model=sys.modules[s.__module__], highlights=['oc'], width=350)))
            oc_chart = ipywidgets.Output()
            with oc_chart:
                melted_df = df.reset_index().melt('Year', value_name='cost', var_name='column')
                chart = alt.Chart(melted_df, width=300).mark_line().encode(
                    y='cost',
                    x='Year:O',
                    color=alt.Color('column'),
                    tooltip=['column', 'cost', 'Year'],
                ).properties(
                    title='Operating Costs (US$M)'
                ).interactive()
                IPython.display.display(chart)
            children.append(ipywidgets.HBox([oc_table, ipywidgets.VBox([oc_model, oc_chart])]))

        operating_cost = ipywidgets.Accordion(children=children)
        for i, s in enumerate(solutions):
            operating_cost.set_title(i, fullname(s))

        return operating_cost


    def get_adoption_data_tab(self, solutions):
        """Return Adoption Data panel.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        children = []
        for s in solutions:
            df = pd.concat([s.ht.soln_pds_funits_adopted().loc[2020:2050, 'World'],
                            s.ht.soln_ref_funits_adopted().loc[2020:2050, 'World']],
                           axis=1)
            df.columns = ['PDS', 'REF']
            ad_table = ipywidgets.Output()
            with ad_table:
                IPython.display.display(IPython.display.HTML(df
                    .style.format({'PDS':'{:.02f}', 'REF':'{:.02f}'})
                    .set_table_styles(dataframe_css_styles).render()))

            ad_model = ipywidgets.Output()
            with ad_model:
                IPython.display.display(IPython.display.SVG(data=ui.modelmap.get_model_overview_svg(
                    model=sys.modules[s.__module__],
                    highlights=['ad', 'capds', 'caref', 'sc', 'ht'], width=350)))

            ad_chart = ipywidgets.Output()
            with ad_chart:
                melted_df = df.reset_index().melt('Year', value_name='adoption', var_name='column')
                chart = alt.Chart(melted_df, width=300).mark_line().encode(
                    y='adoption',
                    x='Year:O',
                    color=alt.Color('column'),
                    tooltip=['column', 'adoption', 'Year'],
                ).properties(
                    title=f'World Adoption ({s.units["functional unit"]})'
                ).interactive()
                IPython.display.display(chart)

            color = ui.color.get_sector_color(self._get_sector_for_solution(s.__module__))
            ad_frizz = ui.frizz.get_frizzle_chart(df=s.ht.soln_pds_funits_adopted().fillna(0.0),
                    ylabel=f'adoption ({s.units["functional unit"]})', size=450,
                    key=fullname(s)+":adoption_data", color=color)

            geo_source = alt.topo_feature(os.path.join('data',
                'world_topo_sans_antartica_highres.json'), 'areas')

            ad_abs_geo = ipywidgets.Output()
            with ad_abs_geo:
                pds_per_region = s.ht.soln_pds_funits_adopted().loc[[2050]]
                pds_per_region_melted = pds_per_region.reset_index().melt(
                        'Year', value_name='adoption', var_name='region')[['region', 'adoption']]
                chart = alt.Chart(geo_source).mark_geoshape(
                    fill='#dddddd',
                    stroke='black',
                ).encode(
                    color=alt.Color('adoption:Q', scale=alt.Scale(scheme='greens')),
                    tooltip=['id:O', alt.Tooltip('adoption:Q', format='.2f')],
                ).transform_lookup(
                    lookup='id',
                    from_=alt.LookupData(data=pds_per_region_melted, key='region', fields=['adoption'])
                # available projections:
                # https://github.com/d3/d3-3.x-api-reference/blob/master/Geo-Projections.md
                ).project('conicEquidistant').properties(
                    width=400,
                    height=300,
                    title='Regional Adoption (total funits in 2050)'
                )
                IPython.display.display(chart)

            ad_abs_globe = ui.geo.get_globe(os.path.join('data', 'world_topo_lowres.json'),
                    df=s.ht.soln_pds_funits_adopted().loc[2020:2050, :], size=450,
                    key=fullname(s)+":adoption_data_globe")

            if hasattr(s, 'tm'):
                ad_pct_geo = ipywidgets.Output()
                with ad_pct_geo:
                    pds_percent_per_region = (s.ht.soln_pds_funits_adopted().loc[[2050]] /
                            s.tm.pds_tam_per_region().loc[[2050]]) * 100.0
                    pds_percent_per_region_melted = pds_percent_per_region.reset_index().melt(
                            'Year', value_name='percent', var_name='region')[['region', 'percent']]
                    chart = alt.Chart(geo_source).mark_geoshape(
                        fill='#dddddd',
                        stroke='black',
                    ).encode(
                        color=alt.Color('percent:Q', scale=alt.Scale(scheme='greens')),
                        tooltip=['id:O', alt.Tooltip('percent:Q', format='.2f')],
                    ).transform_lookup(
                        lookup='id',
                        from_=alt.LookupData(data=pds_percent_per_region_melted,
                            key='region', fields=['percent'])
                    ).project('conicEquidistant').properties(
                        width=400,
                        height=300,
                        title='Regional Adoption (% of TAM in 2050)'
                    )
                    IPython.display.display(chart)
            else:
                ad_pct_geo = None

            if s.ac.solution_category == SOLUTION_CATEGORY.LAND or s.ac.solution_category == SOLUTION_CATEGORY.OCEAN:
                # The chart by geo region isn't really sensible for LAND/OCEAN solutions, which are much
                # more driven by AEZ/DEZs than by political boundaries.
                children.append(ipywidgets.HBox([ad_table, ipywidgets.VBox([ad_model, ad_chart,
                    ad_frizz])]))
            else:
                children.append(ipywidgets.HBox([ad_table, ipywidgets.VBox([ad_model, ad_chart,
                    ad_frizz, ad_abs_geo, ad_abs_globe, ad_pct_geo])]))

        adoption_data = ipywidgets.Accordion(children=children)
        for i, s in enumerate(solutions):
            adoption_data.set_title(i, fullname(s))

        return adoption_data


    def get_tam_data_tab(self, solutions):
        """Return TAM Data panel.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        children = []
        titles = []
        for s in solutions:
            if not hasattr(s, 'tm'):
                continue
            tm_table_pds = ipywidgets.Output()
            with tm_table_pds:
                df = s.tm.pds_tam_per_region()
                header = '<div style="font-size:16px;font-weight:bold;color:#4d4d4d;'
                header += 'background-color:#f7f7f9;width:100%">PDS TAM per region</div>'
                IPython.display.display(IPython.display.HTML(header + df.style.format('{:.02f}')
                    .set_table_styles(dataframe_css_styles).render()))
            tm_table_ref = ipywidgets.Output()
            with tm_table_ref:
                df = s.tm.ref_tam_per_region()
                header = '<div style="font-size:16px;font-weight:bold;color:#4d4d4d;'
                header += 'background-color:#f7f7f9;width:100%">REF TAM per region</div>'
                IPython.display.display(IPython.display.HTML(header + df.style.format('{:.02f}')
                    .set_table_styles(dataframe_css_styles).render()))

            color = ui.color.get_sector_color(self._get_sector_for_solution(s.__module__))
            tm_pds_frizz = ui.frizz.get_frizzle_chart(df=s.tm.pds_tam_per_region().fillna(0.0),
                    ylabel='PDS TAM', size=300, key=fullname(s)+":pds_tam", color=color)
            tm_ref_frizz = ui.frizz.get_frizzle_chart(df=s.tm.ref_tam_per_region().fillna(0.0),
                    ylabel='REF TAM', size=300, key=fullname(s)+":ref_tam", color=color)

            tm_model = ipywidgets.Output()
            with tm_model:
                IPython.display.display(IPython.display.SVG(
                    data=ui.modelmap.get_model_overview_svg(model=sys.modules[s.__module__],
                        highlights=['tm'], width=250)))

            tm_geo_pds = ipywidgets.Output()
            with tm_geo_pds:
                pds_tam_per_region = s.tm.pds_tam_per_region().loc[[2050]]
                pds_tam_per_region_melted = pds_tam_per_region.reset_index().melt(
                        'Year', value_name='adoption', var_name='region')[['region', 'adoption']]
                source = alt.topo_feature(os.path.join('data',
                    'world_topo_sans_antartica_highres.json'), 'areas')
                chart = alt.Chart(source).mark_geoshape(
                    fill='#dddddd',
                    stroke='black',
                ).encode(
                    color=alt.Color('adoption:Q', scale=alt.Scale(scheme='greens'), legend=None),
                    tooltip=['id:O', alt.Tooltip('adoption:Q', format='.2f', title='TAM')],
                ).transform_lookup(
                    lookup='id',
                    from_=alt.LookupData(data=pds_tam_per_region_melted,
                        key='region', fields=['adoption'])
                # available projections:
                # https://github.com/d3/d3-3.x-api-reference/blob/master/Geo-Projections.md
                ).project('conicEquidistant').properties(
                    width=250,
                    height=180,
                    title='Regional PDS TAM in 2050'
                )
                IPython.display.display(chart)
            tm_geo_ref = ipywidgets.Output()
            with tm_geo_ref:
                ref_tam_per_region = s.tm.ref_tam_per_region().loc[[2050]]
                ref_tam_per_region_melted = ref_tam_per_region.reset_index().melt(
                        'Year', value_name='adoption', var_name='region')[['region', 'adoption']]
                source = alt.topo_feature(os.path.join('data',
                    'world_topo_sans_antartica_highres.json'), 'areas')
                chart = alt.Chart(source).mark_geoshape(
                    fill='#dddddd',
                    stroke='black',
                ).encode(
                    color=alt.Color('adoption:Q', scale=alt.Scale(scheme='greens'), legend=None),
                    tooltip=['id:O', alt.Tooltip('adoption:Q', format='.2f', title='TAM')],
                ).transform_lookup(
                    lookup='id',
                    from_=alt.LookupData(data=ref_tam_per_region_melted,
                        key='region', fields=['adoption'])
                ).project('conicEquidistant').properties(
                    width=250,
                    height=180,
                    title='Regional REF TAM in 2050'
                )
                IPython.display.display(chart)

            tm_globe_pds = ui.geo.get_globe(os.path.join('data', 'world_topo_lowres.json'),
                    df=s.tm.pds_tam_per_region().loc[2020:2050, :], size=450,
                    key=fullname(s)+":tam_pds_globe")

            children.append(ipywidgets.VBox(
                [ipywidgets.HBox([tm_table_pds, ipywidgets.VBox([tm_model, tm_pds_frizz,
                    tm_geo_pds, tm_globe_pds])]),
                 ipywidgets.HBox([tm_table_ref, ipywidgets.VBox([tm_ref_frizz, tm_geo_ref])])]))
            titles.append(fullname(s))

        if children:
            tam_data = ipywidgets.Accordion(children=children)
            for idx, title in enumerate(titles):
                tam_data.set_title(idx, title)
        else:
            tam_data = None
        return tam_data


    def get_co2_calcs_tab(self, solutions):
        """Return CO2 Calcs panel.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        children = []
        for s in solutions:
            if s.ac.solution_category == SOLUTION_CATEGORY.LAND or s.ac.solution_category == SOLUTION_CATEGORY.OCEAN:
                co2_red = s.c2.co2eq_mmt_reduced().loc[2020:2050, 'World']
                co2_seq = s.c2.co2_sequestered_global().loc[2020:2050, 'All']
                df = pd.concat([co2_red, co2_seq, co2_red + co2_seq], axis=1)
                df.columns = ['CO2-eq emissions reduced', 'CO2 sequestered', 'Total atmospheric CO2-eq reduction']
            else:
                df = pd.concat([s.c2.co2_mmt_reduced().loc[2020:2050, 'World'],
                                s.c2.co2eq_mmt_reduced().loc[2020:2050, 'World']], axis=1)
                df.columns = ['CO2', 'CO2-eq']
            c2_table = ipywidgets.Output()
            with c2_table:
                IPython.display.display(IPython.display.HTML(df
                    .style.format('{:.02f}').set_table_styles(dataframe_css_styles).render()))
            c2_chart = ipywidgets.Output()
            with c2_chart:
                melted_df = df.reset_index().melt('Year', value_name='mmt', var_name='column')
                chart = alt.Chart(melted_df, width=300).mark_line().encode(
                    y='mmt',
                    x='Year:O',
                    color=alt.Color('column'),
                    tooltip=['column', 'mmt', 'Year'],
                ).properties(
                    title='Cumulative Atmospheric CO2-eq Reduction (MMt)'
                ).interactive()
                IPython.display.display(chart)
            c2_model = ipywidgets.Output()
            with c2_model:
                IPython.display.display(IPython.display.SVG(
                    data=ui.modelmap.get_model_overview_svg(model=sys.modules[s.__module__],
                        highlights=['c2'], width=350)))
            children.append(ipywidgets.HBox([c2_table, ipywidgets.VBox([c2_model, c2_chart])]))

        co2_calcs = ipywidgets.Accordion(children=children)
        for i, s in enumerate(solutions):
            co2_calcs.set_title(i, fullname(s))
        return co2_calcs


    def get_aez_data_tab(self, solutions):
        """Return AEZ Data panel.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        children = []
        for s in solutions:
            if not hasattr(s, 'ae'):
                continue
            df = s.ae.get_land_distribution()
            ae_table = ipywidgets.Output()
            with ae_table:
                IPython.display.display(IPython.display.HTML(df
                    .style.format('{:.02f}').set_table_styles(dataframe_css_styles).render()))
            ae_model = ipywidgets.Output()
            with ae_model:
                IPython.display.display(IPython.display.SVG(
                    data=ui.modelmap.get_model_overview_svg(
                        model=sys.modules[s.__module__], highlights=['ae'], width=350)))
            children.append(ipywidgets.HBox([ae_table, ae_model]))

        if children:
            aez_data = ipywidgets.Accordion(children=children)
            for i, s in enumerate(solutions):
                aez_data.set_title(i, fullname(s))
        else:
            aez_data = None
        return aez_data


    def get_dez_data_tab(self, solutions):
        """Return DEZ Data panel.

           Arguments:
           solutions: a list of solution objects to be processed.
        """
        children = []
        for s in solutions:
            if not hasattr(s, 'de'):
                continue
            df = s.de.get_ocean_distribution()
            de_table = ipywidgets.Output()
            with de_table:
                IPython.display.display(IPython.display.HTML(df
                    .style.format('{:.02f}').set_table_styles(dataframe_css_styles).render()))
            de_model = ipywidgets.Output()
            with de_model:
                IPython.display.display(IPython.display.SVG(
                    data=ui.modelmap.get_model_overview_svg(
                        model=sys.modules[s.__module__], highlights=['de'], width=350)))
            children.append(ipywidgets.HBox([de_table, de_model]))

        if children:
            dez_data = ipywidgets.Accordion(children=children)
            for i, s in enumerate(solutions):
                dez_data.set_title(i, fullname(s))
        else:
            dez_data = None
        return dez_data


    def get_detailed_results_tabs(self):
        """Return tab bar of detailed results for a set of solutions."""
        details_progressbar = self.ui_elements['details_progressbar']
        details_progressbar.value = 0.0
        solutions = self.get_solutions_from_checkboxes()
        self.solutions = solutions

        remaining = 1.0 - details_progressbar.value
        increment = remaining / 10.0
        summary = self.get_summary_tab(solutions)
        details_progressbar.value += increment
        model_overview = self.get_model_tab(solutions)
        details_progressbar.value += increment
        variable_meta_analysis = self.get_VMA_tab(solutions)
        details_progressbar.value += increment
        first_cost = self.get_first_cost_tab(solutions)
        details_progressbar.value += increment
        operating_cost = self.get_operating_cost_tab(solutions)
        details_progressbar.value += increment
        adoption_data = self.get_adoption_data_tab(solutions)
        details_progressbar.value += increment
        tam_data = self.get_tam_data_tab(solutions)
        details_progressbar.value += increment
        co2_calcs = self.get_co2_calcs_tab(solutions)
        details_progressbar.value += increment
        aez_data = self.get_aez_data_tab(solutions)
        details_progressbar.value += increment
        dez_data = self.get_dez_data_tab(solutions)
        details_progressbar.value = 1.0

        # ------------------ Create tabs -----------------
        children = [summary, model_overview, variable_meta_analysis, adoption_data]
        titles = ["Summary", "Model", "Variable Meta-Analysis", "Adoption Data"]
        if tam_data:
            children.append(tam_data)
            titles.append('TAM Data')
        if aez_data:
            children.append(aez_data)
            titles.append('AEZ Data')
        if dez_data:
            children.append(dez_data)
            titles.append('DEZ Data')
        children.extend([first_cost, operating_cost, co2_calcs])
        titles.extend(["First Cost", "Operating Cost", "CO2"])

        tabs = ipywidgets.Tab(children=children)
        for (idx, title) in enumerate(titles):
            tabs.set_title(idx, title)
        details_progressbar.value = 0.0
        return tabs


    def get_solutions_from_checkboxes(self):
        """Iterate through a dict of checkboxes, return objects for all selected solutions."""
        all_solutions_scenarios = solution.factory.all_solutions_scenarios()
        constructors = []
        for soln, cbox in self.checkboxes.items():
            if cbox.value:
                constructor, scenarios = all_solutions_scenarios[soln]
                for scenario in scenarios:
                    constructors.append((constructor, scenario))

        if not constructors:
            soln = 'forestprotection'
            constructor, scenarios = all_solutions_scenarios[soln]
            for scenario in scenarios:
                constructors.append((constructor, scenario))

        total = float(len(constructors) + 2)
        increment = 1.0 / total
        details_progressbar = self.ui_elements['details_progressbar']

        solutions = []
        for (constructor, scenario) in constructors:
            solutions.append(constructor(scenario))
            details_progressbar.value += increment

        return solutions
