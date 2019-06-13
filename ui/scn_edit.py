"""Scenario / Advanced Controls editor."""

import ipywidgets
import IPython.core.display
import numpy as np
from model.advanced_controls import SOLUTION_CATEGORY

def scn_edit_vma_var(soln, title, title_tt, units, value):
    vma = soln.ac.vmas.get(title, None)
    mean = high = low = np.nan
    total_sources = 0
    use_weight = False
    if vma:
        (mean, high, low) = vma.avg_high_low()
        total_sources = len(vma.df)
        use_weight = vma.use_weight
    ly_full = ipywidgets.Layout(width='auto', grid_area='full_row')
    ly_labl = ipywidgets.Layout(width='20%')
    ly_butn = ipywidgets.Layout(width='80%')
    dd_styles = "<style>"
    dd_styles += ".dd_data_input input { background-color:#D0F0D0 !important;text-align:center; }"
    dd_styles += ".dd_one_scenario { background-color:GhostWhite !important; }"
    dd_styles += "</style>"
    value_entry = ipywidgets.Text(value=f'{value}', layout=ly_butn)
    value_entry.add_class('dd_data_input')
    def on_value_clicked(b):
        value_entry.value = b.value_name
    mean_button = ipywidgets.Button(description=f'{mean:3f}', layout=ly_butn)
    mean_button.value_name = '📎 Mean'
    mean_button.on_click(on_value_clicked)
    high_button = ipywidgets.Button(description=f'{high:3f}', layout=ly_butn)
    high_button.value_name = '📎 High'
    high_button.on_click(on_value_clicked)
    low_button = ipywidgets.Button(description=f'{low:3f}', layout=ly_butn)
    low_button.value_name = '📎 Low'
    low_button.on_click(on_value_clicked)

    children = [
        ipywidgets.HTML(dd_styles),
        ipywidgets.Button(description=title, disabled=True, tooltip=title_tt, layout=ly_full),
        ipywidgets.Button(description=units, disabled=True, layout=ly_full),
        ipywidgets.HBox([ipywidgets.Label('Value', layout=ly_labl), value_entry], layout=ly_full),
        ipywidgets.HBox([ipywidgets.Label('Mean', layout=ly_labl), mean_button], layout=ly_full),
        ipywidgets.HBox([ipywidgets.Label('High', layout=ly_labl), high_button], layout=ly_full),
        ipywidgets.HBox([ipywidgets.Label('Low', layout=ly_labl), low_button], layout=ly_full),
        ipywidgets.HBox([ipywidgets.Label('Weighted Average?', layout=ipywidgets.Layout(width='auto')),
                         ipywidgets.Checkbox(value=use_weight, indent=False,
                                            layout=ipywidgets.Layout(width='auto'))], layout=ly_full),
        ipywidgets.Label(f'Total Sources: {total_sources}',layout=ly_full),
    ]
    return ipywidgets.VBox(children=children, layout=ipywidgets.Layout(width='250px',
            grid_template_rows='auto auto auto auto', grid_template_columns='100%',
            grid_template_areas='"full_row"'))


def conv_first_cost(soln):
    """Conventional First Cost column for scenario editor.
       Arguments:
         s = solution object
    """
    title = 'CONVENTIONAL First Cost per Implementation Unit for replaced practices'
    title_tooltip = ("CONVENTIONAL First Cost per Implementation Unit for replaced practices\n\n"
                     "NOTE: This is the cost of acquisition and the cost of installation "
                     "(sometimes one and the same) or the cost of initiating a program/practice "
                     "(for solutions where there is no direct artifact to acquire and install) "
                     "per Unit of Implementation of the CONVENTIONAL mix of practices (those "
                     "practices that do not include the technology in question.\n\n"
                     "E.g. What is the cost to purchase an internal combustion engine (ICE) "
                     "vehicle?")
    l = soln.units["implementation unit"]
    units = f'(implementation units: {l})' if l else '(implementation units)'
    return scn_edit_vma_var(soln=soln, title=title, title_tt=title_tooltip,
            units=units, value=soln.ac.conv_2014_cost)


def conv_oper_cost_total(soln):
    """Conventional Operating Cost, including Fixed and Variable. Typically used for Land solutions.
       Arguments:
         s = solution object
    """
    title = 'CONVENTIONAL Operating Cost per Functional Unit per Annum'
    title_tooltip = ("CONVENTIONAL Operating Cost per Functional Unit per Annum\n\n"
                     "NOTE: This is the Operating Cost per functional unit, derived "
                     "from the CONVENTIONAL mix of technologies/practices.  In most "
                     "cases this will be expressed as a cost per 'hectare of land'.\n\n"
                     "This annualized value should capture the variable costs for "
                     "maintaining the CONVENTIONAL practice, as well as  fixed costs. "
                     "The value should reflect the average over the reasonable lifetime "
                     "of the practice.\n\n"
                     "Note: If the Operating Cost changes significantly across years, "
                     "you can use a customized calculation at bottom of 'Operating Cost' sheet.")
    units = '(per ha per annum)'
    return scn_edit_vma_var(soln=soln, title=title, title_tt=title_tooltip,
            units=units, value=soln.ac.conv_fixed_oper_cost_per_iunit)


def conv_net_profit_margin(soln):
    """Conventional net profit margin.
       Arguments:
         s = solution object
    """
    title = 'CONVENTIONAL Net Profit Margin per Functional Unit per Annum'
    title_tooltip = ("CONVENTIONAL Net Profit Margin per Functional Unit per Annum\n\n"
                     "NOTE: This is the net annual profit margin per functional unit, "
                     "derived from the CONVENTIONAL mix of technologies/practices.  In "
                     "most cases this will be expressed as a profit per 'hectare of land'.\n\n"
                     "This annualized value should capture the net margin not gross margin "
                     "that result from the practice, whether sales of plant or animal products. "
                     "The value should reflect the average over the reasonable lifetime of the "
                     "practice.\n\n"
                     "Note: If the net profit margin changes significantly across years, you "
                     "can use a customized calculation at bottom of 'Net Profit Margin' sheet.")
    units = 'years'
    return scn_edit_vma_var(soln=soln, title=title, title_tt=title_tooltip,
            units=units, value=143.544)


def conv_lifetime_capacity(soln):
    """Conventional lifetime capacity column for scenario editor.
       Arguments:
         s = solution object
    """
    title = 'Lifetime Capacity - CONVENTIONAL'
    title_tooltip = ("Lifetime Capacity - CONVENTIONAL\n\n"
                     "NOTE: This is the average expected number of functional units "
                     "generated by the CONVENTIONAL mix of technologies/practices "
                     "throughout their lifetime before replacement is required.  "
                     "If no replacement time is discovered or applicable, please "
                     "use 100 years.\n\n"
                     "E.g. a vehicle will have an average number of passenger kilometers "
                     "it can travel until it can no longer be used and a new vehicle is "
                     "required. Another example would be an HVAC system, which can only "
                     "service a certain amount of floor space over a period of time before "
                     "it will require replacement.")
    units = 'use until replacement is required'
    return scn_edit_vma_var(soln=soln, title=title, title_tt=title_tooltip,
            units=units, value=soln.ac.conv_lifetime_capacity)


def soln_first_cost(soln):
    """Solution First Cost column for scenario editor.
       Arguments:
         s = solution object
    """
    title = 'SOLUTION First Cost per Implementation Unit of the solution'
    title_tooltip = ("SOLUTION First Cost per Implementation Unit of the solution\n\n"
                     "NOTE: This is the cost of acquisition and the cost of installation "
                     "(sometimes one and the same) or the cost of initiating a program/practice "
                     "(for solutions where there is no direct artifact to acquire and install) "
                     "per Implementation unit of the SOLUTION.\n\n"
                     "E.g. What is the cost to acquire and install rooftop solar PV?")
    if soln.ac.solution_category == SOLUTION_CATEGORY.LAND:
        units = '(per ha)'
    else:
        l = soln.units["implementation unit"]
        units = f'(implementation units: {l})' if l else '(implementation units)'
    return scn_edit_vma_var(soln=soln, title=title, title_tt=title_tooltip,
            units=units, value=soln.ac.pds_2014_cost)


def soln_oper_cost_total(soln):
    """Solution Operating Cost, including Fixed and Variable. Typically used for Land solutions.
       Arguments:
         s = solution object
    """
    title = 'SOLUTION Operating Cost per Functional Unit per Annum'
    title_tooltip = ("SOLUTION Operating Cost per Functional Unit per Annum\n\n"
                     "NOTE: This is the Operating Cost per functional unit, derived from the SOLUTION. "
                     "In most cases this will be expressed as a cost per 'hectare of land'.\n\n"
                     "This annualized value should capture both the variable costs for maintaining the "
                     "SOLUTION practice as well as the fixed costs. The value should reflect the average "
                     "over the reasonable lifetime of the practice.")
    units = '(per ha per annum)'
    return scn_edit_vma_var(soln=soln, title=title, title_tt=title_tooltip,
            units=units, value=soln.ac.soln_fixed_oper_cost_per_iunit)


def soln_oper_cost_fixed(soln):
    """Solution Fixed Operating Cost. Typically used for RRS solutions.
       Arguments:
         s = solution object
    """
    title = 'SOLUTION Fixed Operating Cost (FOM)'
    title_tooltip = ("SOLUTION Fixed Operating Cost (FOM)\n\n"
                     "NOTE: This is the annual operating cost per implementation unit, derived from "
                     "the SOLUTION.  In most cases this will be expressed as a cost per 'some unit "
                     "of installation size'\n\n"
                     "E.g., $10,000 per kw. In terms of transportation, this can be considered the "
                     "total insurance, and maintenance cost per car.\n\n"
                     "Purchase costs can be amortized here or included as a first cost, but not both.")
    l = soln.units["implementation unit"]
    units = f'(implementation units: {l})' if l else '(implementation units)'
    return scn_edit_vma_var(soln=soln, title=title, title_tt=title_tooltip,
            units=units, value=soln.ac.soln_fixed_oper_cost_per_iunit)


def soln_net_profit_margin(soln):
    """Solution net profit margin.
       Arguments:
         s = solution object
    """
    title = 'SOLUTION Net Profit Margin per Functional Unit per Annum'
    title_tooltip = ("SOLUTION Net Profit Margin per Functional Unit per Annum\n\n"
                     "NOTE: This is the net annual profit margin per functional unit, derived from "
                     "the SOLUTION mix of technologies/practices.  In most cases this will be expressed "
                     "as a profit per 'hectare of land'.\n\n"
                     "This annualized value should capture net margin, not gross margin that result "
                     "from the practice, whether sales of plant or animal products. The value should "
                     "reflect the average over the reasonable lifetime of the practice.\n\n"
                     "Note: If the net profit margin changes significantly across years, you can use a "
                     "customized calculation at bottom of 'Net Profit Margin' sheet.")
    units = 'years'
    return scn_edit_vma_var(soln=soln, title=title, title_tt=title_tooltip,
            units=units, value=460)
