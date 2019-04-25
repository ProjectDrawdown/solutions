"""Generate graphics for Jupyter notebook."""

import os.path
import sys

import altair as alt
import IPython.display
import ipywidgets
import pandas as pd

from model.advanced_controls import SOLUTION_CATEGORY

import solution.factory
import ui.modelmap
import ui.vega

pd.set_option('display.max_columns', 200)
pd.set_option('display.max_rows', 200)


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



def fullname(s):
    return type(s).__name__ + ':' + s.scenario


def get_overview():
    """Returns (overview, checkboxes).

       Where:
         overview is an ipywidget to be displayed in Jupyter showing an overview
           of available solutions, information about the solutions, and contains checkboxes
           allowing specific solutions to be examined in more details.
         checkboxes is a dict of solution names to ipywidget.checkbox objects.
    """
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

    solution_chart = ipywidgets.Output()
    with solution_chart:
        IPython.display.display({'application/vnd.vega.v4+json': ui.vega.solution_donut_chart(
            solutions=all_solutions, width=400, height=400)}, raw=True)

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
    for row in all_solutions.sort_values(['SectorCO2eq', 'CO2eq'],
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
            solutions=all_solutions, width=400, height=800)}, raw=True)

    chrt_layout = ipywidgets.Layout(flex='3 1 0%', width='auto')
    charts = ipywidgets.VBox(children=[solution_chart, solution_treemap], layout=chrt_layout)
    overview = ipywidgets.HBox(children=[solution_list, charts], layout=cntr_layout)

    return (overview, checkboxes)


def _get_summary_ua(solutions):
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
                             'Functional/Land Adoption Increase in 2050 (PDS vs REF)']
    details_ua = ipywidgets.Output()
    with details_ua:
        df = pd.DataFrame(unit_adoption_text, columns=unit_adoption_columns)
        IPython.display.display(IPython.display.HTML(
            df.style.set_table_styles(dataframe_css_styles).hide_index().render()))
    return details_ua


def _get_summary_ad(solutions):
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
                        'Global Solution Functional/Land Units in 2050',
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
                color=alt.Color('solution', legend=alt.Legend(orient='top-left')),
                tooltip=['solution', 'iunits', 'Year'],
            ).properties(
                title='World Adoption - Implementation Units'
            ).interactive()
            IPython.display.display(iunit_chart)

    adoption_funit_chart = ipywidgets.Output()
    with adoption_funit_chart:
        df = pd.DataFrame()
        for s in solutions:
            if s.ac.solution_category == SOLUTION_CATEGORY.LAND:
                df['Total Land Area:'+fullname(s)] = s.tla_per_region.loc[2020:2050, 'World']
            else:
                ref_tam = s.tm.ref_tam_per_region().loc[2020:2050, 'World']
                pds_tam = s.tm.pds_tam_per_region().loc[2020:2050, 'World']
                df['Total Market-REF:' + fullname(s)] = ref_tam
                df['Total Market-PDS:' + fullname(s)] = pds_tam
            ref_funits = s.ht.soln_ref_funits_adopted().loc[2020:2050, 'World']
            pds_funits = s.ht.soln_pds_funits_adopted().loc[2020:2050, 'World']
            df['Solution-REF:' + fullname(s)] = ref_funits
            df['Solution-PDS:' + fullname(s)] = pds_funits
        funit_df = df.reset_index().melt('Year', value_name='units', var_name='solution')
        funit_chart = alt.Chart(funit_df, width=400).mark_line().encode(
                y='units:Q',
                x=alt.X('Year', type='ordinal', scale=alt.Scale(domain=list(range(2015, 2056)))),
                color=alt.Color('solution', legend=alt.Legend(orient='top-right')),
                tooltip=['solution', 'units:O', 'Year']
            ).properties(
                title='World Adoption - Functional/Land Units'
            ).interactive()
        IPython.display.display(funit_chart)

    if has_iunit_chart:
        children = [adoption_iunit_chart, adoption_funit_chart]
    else:
        children = [adoption_funit_chart]
    adoption_graphs = ipywidgets.HBox(children=children)

    return (adoption_heading, adoption_graphs)

def _get_summary_financial(solutions):
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
            cref_oc = s.oc.conv_ref_annual_operating_cost().loc[2020:2050] / 1000000000
            df['Conventional Operating Costs/Savings:' + fullname(s)] = cref_oc
        cost_df = df.reset_index().melt('Year', value_name='costs', var_name='solution')
        cost_chart = alt.Chart(cost_df, width=350).mark_line().encode(
            y=alt.Y('costs', title='US$B'),
            x=alt.X('Year', type='ordinal', scale=alt.Scale(domain=list(range(2015, 2056)))),
            color=alt.Color('solution', legend=alt.Legend(orient='top-left')),
            tooltip=['solution', 'costs', 'Year'],
        ).properties(
            title='World Operating Cost Difference'
        ).interactive()
        IPython.display.display(cost_chart)

    return (financial_heading, financial_graphs)


def _get_summary_climate(solutions):
    """Return Summary panel for climate results.

       Arguments:
       solutions: a list of solution objects to be processed.
    """
    climate_text = []
    for s in solutions:
        if s.ac.solution_category == SOLUTION_CATEGORY.LAND:
            # Note the sequestration table in co2calcs doesn't set values to zero outside
            # the study years. In the xls there is a separate table which does this. Here,
            # we select the years directly.
            # The xls implemntation also excludes the year 2020, almost certainly by mistake.
            # Thus, this value will differ slightly from the one given in the Detailed Results
            # xls sheet.
            # https://docs.google.com/document/d/19sq88J_PXY-y_EnqbSJDl0v9CdJArOdFLatNNUFhjEA/edit
            g_tons = s.c2.co2_sequestered_global().loc[2020:2050, 'All'].sum() / 1000
        else:
            g_tons = s.c2.co2eq_mmt_reduced().loc[2020:2050, 'World'].sum() / 1000
        climate_text.append([fullname(s), f"{g_tons:.2f} Gt"])

    climate_heading = ipywidgets.Output()
    with climate_heading:
        df = pd.DataFrame(climate_text, columns=['Scenario', 'Total CO2-eq Reduced/Sequestered'])
        IPython.display.display(IPython.display.HTML(df.style.set_table_styles(
            dataframe_css_styles).hide_index().render()))

    # Reduction
    df = pd.DataFrame()
    for s in solutions:
        if s.ac.solution_category == SOLUTION_CATEGORY.LAND:
            df[fullname(s)] = s.c2.co2_sequestered_global(
                    ).loc[2020:2050, 'All'].cumsum().mul(0.001)
        else:
            df[fullname(s)] = s.c2.co2eq_mmt_reduced().loc[2020:2050, 'World'].cumsum().mul(0.001)
    reduction_df = df.reset_index().melt('Year', value_name='Gt CO2-eq', var_name='solution')
    reduction_graph = ipywidgets.Output()
    with reduction_graph:
        chart = alt.Chart(reduction_df, width=300).mark_line().encode(
            y='Gt CO2-eq',
            x=alt.X('Year', type='ordinal'),
            color=alt.Color('solution', legend=alt.Legend(orient='top-left')),
            tooltip=['solution', 'Gt CO2-eq', 'Year'],
        ).properties(
            title='World Cumulative CO2-eq Reduced/Sequestered'
        ).interactive()
        IPython.display.display(chart)

    # Concentration
    df = pd.DataFrame()
    for s in solutions:
        df[fullname(s)] = s.c2.co2eq_ppm_calculator().loc[2020:2050, 'CO2-eq PPM']
    concentration_df = df.reset_index().melt('Year', value_name='concentration', var_name='solution')
    concentration_graph = ipywidgets.Output()
    with concentration_graph:
        chart = alt.Chart(concentration_df, width=300).mark_line().encode(
            y='concentration',
            x=alt.X('Year', type='ordinal'),
            color=alt.Color('solution', legend=alt.Legend(orient='top-left')),
            tooltip=['solution', 'concentration', 'Year'],
        ).properties(
            title='World Cumulative GHG Concentration Reduction'
        ).interactive()
        IPython.display.display(chart)

    climate_graphs = ipywidgets.HBox(children=[reduction_graph, concentration_graph])

    return (climate_heading, climate_graphs)

def _get_summary_productivity(solutions):
    """Return Summary panel for land productivity.

       Arguments:
       solutions: a list of solution objects to be processed.
    """
    has_prod_results = False
    prod_text = []
    for s in solutions:
        if s.ac.solution_category == SOLUTION_CATEGORY.LAND:
            has_prod_results = True
            pot_yield_incr = s.ua.soln_net_annual_funits_adopted(
                    ).loc[2020:2050, 'World'].sum() * s.ac.yield_coeff
            prod_text.append([fullname(s), f"{pot_yield_incr:.2f} MMt"])
    prod_columns = ['Scenario', 'Potential yield increase over report years']

    if not has_prod_results:
        return (None, None)

    prod_heading = ipywidgets.Output()
    with prod_heading:
        df = pd.DataFrame(prod_text, columns=prod_columns)
        IPython.display.display(IPython.display.HTML(df.style.set_table_styles(
            dataframe_css_styles).hide_index().render()))

    prod_graph = ipywidgets.Output()
    with prod_graph:
        df = pd.DataFrame()
        for s in solutions:
            if s.ac.solution_category == SOLUTION_CATEGORY.LAND:
                funits = s.ua.soln_net_annual_funits_adopted().loc[2020:2050, 'World']
                yield_df = (funits * s.ac.yield_coeff).cumsum()
                df[fullname(s)] = yield_df
        prod_df = df.reset_index().melt('Year', value_name='metric tons', var_name='solution')
        chart = alt.Chart(prod_df, width=300).mark_line().encode(
            y='metric tons',
            x=alt.X('Year', type='ordinal'),
            color=alt.Color('solution', legend=alt.Legend(orient='top-left')),
            tooltip=['solution', 'metric tons', 'Year'],
        ).properties(
            title='Cumulative Potential Yield Increase'
        ).interactive()
        IPython.display.display(chart)

    return (prod_heading, prod_graph)


def blue_label(text):
    div = '<div style="background-color:LightSkyBlue;border:1px solid black;'
    div += 'font-weight:bold;text-align:center;font-size:0.875em;">'
    return ipywidgets.HTML(value=div + text + '</div>')


def get_summary_tab(solutions):
    """Return Summary panel.

       Arguments:
       solutions: a list of solution objects to be processed.
    """
    key_results_label = blue_label('The Key Adoption Results')
    unit_adoption_heading = _get_summary_ua(solutions)
    (adoption_heading, adoption_graphs) = _get_summary_ad(solutions)

    financial_results_label = blue_label('The Key Financial Results')
    (financial_heading, cost_graphs) = _get_summary_financial(solutions)

    climate_results_label = blue_label('The Key Climate Results')
    (climate_heading, climate_graphs) = _get_summary_climate(solutions)

    prod_results_label = blue_label('The Key Productivity Results')
    (prod_heading, prod_graph) = _get_summary_productivity(solutions)
    has_prod_results = True if (prod_heading and prod_graph) else False

    detailed_results = ipywidgets.Output()
    with detailed_results:
        to_disp = [key_results_label, unit_adoption_heading, adoption_heading, adoption_graphs,
                financial_results_label, financial_heading, cost_graphs, climate_results_label,
                climate_heading, climate_graphs]
        if has_prod_results:
            to_disp.extend([prod_results_label, prod_heading, prod_graph])
        IPython.display.display(ipywidgets.VBox(to_disp))

    return detailed_results


def get_model_tab(solutions):
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
        d = ipywidgets.Output()
        with d:
            IPython.display.display(IPython.display.SVG(
                data=ui.modelmap.get_model_overview_svg(model=c)))
        children.append(d)
        titles.append(c.__name__)
    model_overview = ipywidgets.Accordion(children=children, layout=ipywidgets.Layout(width='90%'))
    for idx, name in enumerate(titles):
        model_overview.set_title(idx, name)

    return model_overview


def get_VMA_tab(solutions):
    """Return VMA panel.

       Arguments:
       solutions: a list of solution objects to be processed.
    """
    variable_meta_analysis = ipywidgets.Output()
    with variable_meta_analysis:
        children = []
        for s in solutions:
            for (name, v) in s.VMAs:
                vma_widget = ipywidgets.Output()
                with vma_widget:
                    IPython.display.display(IPython.display.HTML(v.source_data.drop(['Link',
                        'Source Validation Code', 'License Code'], axis=1).fillna('').to_html()))
                summary_table = ipywidgets.Output()
                with summary_table:
                    (mean, high, low) = v.avg_high_low()
                    df = pd.DataFrame([[mean, high, low]], columns=['Mean', 'High', 'Low'])
                    IPython.display.display(IPython.display.HTML(df.style.format("{:.01f}"
                        ).set_properties(**{'width': '10em'}).set_table_styles(
                            dataframe_css_styles).hide_index().render()))

                accordion = ipywidgets.Accordion(children=[vma_widget],
                        layout=ipywidgets.Layout(width='90%'))
                accordion.set_title(0, name)
                vma_widget = ipywidgets.Output()
                with vma_widget:
                    IPython.display.display(ipywidgets.HBox(children=[summary_table, accordion]))
                children.append(vma_widget)
        IPython.display.display(ipywidgets.VBox(children=children))
    return variable_meta_analysis


def get_first_cost_tab(solutions):
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


def get_operating_cost_tab(solutions):
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


def get_adoption_data_tab(solutions):
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
                title='Adoption'
            ).interactive()
            IPython.display.display(chart)

        geo_source = alt.topo_feature(os.path.join('data',
            'world_topo_sans_antartica_with_dd_regions.json'), 'regions')

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

        if s.ac.solution_category == SOLUTION_CATEGORY.LAND:
            # The chart by geo region isn't really sensible for LAND solutions, which are much
            # more driven by Agro-ecological zones than by political boundaries.
            children.append(ipywidgets.HBox([ad_table, ipywidgets.VBox([ad_model, ad_chart])]))
        else:
            children.append(ipywidgets.HBox([ad_table, ipywidgets.VBox([ad_model, ad_chart,
                ad_abs_geo, ad_pct_geo])]))

    adoption_data = ipywidgets.Accordion(children=children)
    for i, s in enumerate(solutions):
        adoption_data.set_title(i, fullname(s))

    return adoption_data


def get_tam_data_tab(solutions):
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
                'world_topo_sans_antartica_with_dd_regions.json'), 'regions')
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
                'world_topo_sans_antartica_with_dd_regions.json'), 'regions')
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

        children.append(ipywidgets.VBox(
            [ipywidgets.HBox([tm_table_pds, ipywidgets.VBox([tm_model, tm_geo_pds])]),
             ipywidgets.HBox([tm_table_ref, ipywidgets.VBox([tm_geo_ref])])]))
        titles.append(fullname(s))

    if children:
        tam_data = ipywidgets.Accordion(children=children)
        for idx, title in enumerate(titles):
            tam_data.set_title(idx, title)
    else:
        tam_data = None
    return (tam_data)


def get_co2_calcs_tab(solutions):
    """Return CO2 Calcs panel.

       Arguments:
       solutions: a list of solution objects to be processed.
    """
    children = []
    for s in solutions:
        if s.ac.solution_category == SOLUTION_CATEGORY.LAND:
            df = pd.DataFrame(s.c2.co2_sequestered_global().loc[2020:2050, 'All'])
            df.columns = ['CO2']
        else:
            df = pd.concat([s.c2.co2_mmt_reduced().loc[2020:2050, 'World'],
                            s.c2.co2eq_mmt_reduced().loc[2020:2050, 'World']], axis=1)
            df.columns = ['CO2', 'CO2eq']
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
                title='CO2 MMt'
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


def get_aez_data_tab(solutions):
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
    return(aez_data)


def get_detailed_results_tabs(solutions):
    """Return tab bar of detailed results for a set of solutions."""
    summary = get_summary_tab(solutions)
    model_overview = get_model_tab(solutions)
    variable_meta_analysis = get_VMA_tab(solutions)
    first_cost = get_first_cost_tab(solutions)
    operating_cost = get_operating_cost_tab(solutions)
    adoption_data = get_adoption_data_tab(solutions)
    tam_data = get_tam_data_tab(solutions)
    co2_calcs = get_co2_calcs_tab(solutions)
    aez_data = get_aez_data_tab(solutions)

    # ------------------ Create tabs -----------------
    children = [summary, model_overview, variable_meta_analysis, adoption_data]
    titles = ["Summary", "Model", "Variable Meta-Analysis", "Adoption Data"]
    if tam_data:
        children.append(tam_data)
        titles.append('TAM Data')
    if aez_data:
        children.append(aez_data)
        titles.append('AEZ Data')
    children.extend([first_cost, operating_cost, co2_calcs])
    titles.extend(["First Cost", "Operating Cost", "CO2"])

    tabs = ipywidgets.Tab(children=children)
    for (idx, title) in enumerate(titles):
        tabs.set_title(idx, title)
    return tabs


def get_solutions_from_checkboxes(checkboxes):
    """Iterate through a dict of checkboxes, return objects for all selected solutions."""
    all_solutions_scenarios = solution.factory.all_solutions_scenarios()
    solutions = []
    for soln, cbox in checkboxes.items():
        if cbox.value:
            constructor, scenarios = all_solutions_scenarios[soln]
            for scenario in scenarios:
                solutions.append(constructor(scenario))

    if not solutions:
        soln = 'silvopasture'
        constructor, scenarios = all_solutions_scenarios[soln]
        for scenario in scenarios:
            solutions.append(constructor(scenario))

    return solutions
