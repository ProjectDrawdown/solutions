"""Scenario / Advanced Controls editor."""

import ipywidgets
import IPython.core.display
import numpy as np
from model import advanced_controls as ac


MEAN_MAGIC = '📎 Mean'
HIGH_MAGIC = '📎 High'
LOW_MAGIC = '📎 Low'
ALL_SCENARIOS = 'All Scenarios'
VALUE_DIFFERS = '(differs between scenarios)'


def _set_value_entry_shadows(state):
    value_entry = state['value_entry']
    values = list(state['values'].values())
    all_scenarios_equal = (values.count(values[0]) == len(values))

    if all_scenarios_equal:
        value_entry.remove_class('dd_vma_shadow')
    else:
        value_entry.add_class('dd_vma_shadow')

    return all_scenarios_equal


def dropdown_observe(change):
    """Observer callback for dropdown selection changes.

       When the selected scenario changes we need to:
          1. update the value displayed in the value_entry text input.
          2. Determine if all scenarios have the same value or not, and if not then
             add the drop-shadow decoration to this editing box to show the user there
             are multiple values.

       Arguments:
         change: the observer callback information.
    """
    scenario = change['new']
    dropdown = change['owner']
    state = dropdown.state
    values = state['values']

    all_scenarios_equal = _set_value_entry_shadows(state)
    if scenario == ALL_SCENARIOS:
        if all_scenarios_equal:
            new_value = list(values.values())[0]
        else:
            new_value = VALUE_DIFFERS
    else:
        new_value = values[scenario]

    value_entry = state['value_entry']
    state['value_entry'].value = str(new_value)


def value_entry_observe(change):
    """Observer callback for when text is added to value_entry widget.

       Arguments:
         change: the observer callback information.
    """

    widget = change['owner']
    value = change['new']
    if value == VALUE_DIFFERS:
        return
    values = widget.state['values']
    selection = widget.state['dropdown'].value
    if selection == ALL_SCENARIOS:
        for scenario in values.keys():
            values[scenario] = value
    else:
        values[selection] = value
    _set_value_entry_shadows(widget.state)


def on_vma_button_click(b):
    """Called when the Mean/High/Low buttons are clicked."""
    b.state['value_entry'].value = b.value_name


def scn_edit_vma_var(scenarios, vma, title, tooltip, subtitle):
    """Render an editor box for a single VMA.
       Arguments:
         scenarios: a dict where the keys are scenario names, values are AdvancedControls objects
         vma: model.VMA object being edited
         title: name of the VMA being edited
         tooltip: tooltip to display with the title
         subtitle: line to print under the title, typically includes the units of the value
           being allocated like "MHa" or "US$2014/TWh"
    """
    varname = ac.get_param_for_vma_name(title)
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
    ly_drop = ipywidgets.Layout(width='95%', grid_area='full_row')

    dd_styles = "<style>"
    dd_styles += ".dd_vma_val input {background-color:#D0F0D0 !important;text-align:center;}"
    dd_styles += ".dd_vma_shadow {box-shadow:4px 4px 0px #20A020,8px 8px 0px #20A020;}"
    dd_styles += "</style>"

    values = {}
    for sc in scenarios.values():
        values[sc.name] = getattr(sc, varname)
    value_list = list(values.values())
    all_scenarios_equal = (value_list.count(value_list[0]) == len(value_list))
    if all_scenarios_equal:
        value = value_list[0]
    else:
        value = VALUE_DIFFERS

    value_entry = ipywidgets.Text(value=f'{value}', continuous_update=False, layout=ly_butn)
    value_entry.add_class('dd_vma_val')
    value_entry.observe(value_entry_observe, names='value')

    options = [ALL_SCENARIOS] + list(scenarios.keys())
    dropdown = ipywidgets.Dropdown(options=options, indent=False, layout=ly_drop)
    dropdown.observe(dropdown_observe, names='value')

    element_state = { 'scenarios': scenarios, 'vma': vma, 'varname': varname,
            'value_entry': value_entry, 'dropdown': dropdown, 'values': values, }
    value_entry.state = element_state
    dropdown.state = element_state
    _set_value_entry_shadows(state=element_state)

    mean_button = ipywidgets.Button(description=f'{mean:.3f}', layout=ly_butn)
    mean_button.value_name = MEAN_MAGIC
    mean_button.state = element_state
    mean_button.on_click(on_vma_button_click)
    high_button = ipywidgets.Button(description=f'{high:.3f}', layout=ly_butn)
    high_button.value_name = HIGH_MAGIC
    high_button.state = element_state
    high_button.on_click(on_vma_button_click)
    low_button = ipywidgets.Button(description=f'{low:.3f}', layout=ly_butn)
    low_button.value_name = LOW_MAGIC
    low_button.state = element_state
    low_button.on_click(on_vma_button_click)
    if not vma:
        mean_button.disabled = high_button.disabled = low_button.disabled = True

    children = [
        ipywidgets.HTML(dd_styles),
        ipywidgets.Button(description=title, disabled=True, tooltip=tooltip, layout=ly_full),
        ipywidgets.Button(description=subtitle, disabled=True, tooltip=tooltip, layout=ly_full),
        dropdown,
        ipywidgets.HBox([ipywidgets.Label('Value', layout=ly_labl), value_entry], layout=ly_full),
        ipywidgets.HBox([ipywidgets.Label('Mean', layout=ly_labl), mean_button], layout=ly_full),
        ipywidgets.HBox([ipywidgets.Label('High', layout=ly_labl), high_button], layout=ly_full),
        ipywidgets.HBox([ipywidgets.Label('Low', layout=ly_labl), low_button], layout=ly_full),
        ipywidgets.HBox([ipywidgets.Label('Weighted Average?',
            layout=ipywidgets.Layout(width='auto')),
            ipywidgets.Checkbox(value=use_weight, indent=False,
                layout=ipywidgets.Layout(width='auto'))], layout=ly_full),
        ipywidgets.Label(f'Total Sources: {total_sources}',layout=ly_full),
    ]
    box = ipywidgets.VBox(children=children, layout=ipywidgets.Layout(width='250px',
            grid_template_rows='auto auto auto auto', grid_template_columns='100%',
            grid_template_areas='"full_row"'))
    dropdown.box = box
    return box


def conv_first_cost(scenarios, vmas):
    """Conventional First Cost column for scenario editor.
       Arguments:
          scenarios: dict of {scenario_name: AdvancedControls_object}
          vmas: dict of {vma_name: VMA_object}
    """
    title = 'CONVENTIONAL First Cost per Implementation Unit for replaced practices'
    tooltip = ("CONVENTIONAL First Cost per Implementation Unit for replaced practices\n\n"
               "NOTE: This is the cost of acquisition and the cost of installation "
               "(sometimes one and the same) or the cost of initiating a program/practice "
               "(for solutions where there is no direct artifact to acquire and install) "
               "per Unit of Implementation of the CONVENTIONAL mix of practices (those "
               "practices that do not include the technology in question.\n\n"
               "E.g. What is the cost to purchase an internal combustion engine (ICE) "
               "vehicle?")
    subtitle = '(implementation units)'
    return scn_edit_vma_var(scenarios=scenarios, vma=vmas.get(title, None),
            title=title, tooltip=tooltip, subtitle=subtitle)


def conv_oper_cost_total(scenarios, vmas):
    """Conventional Operating Cost, including Fixed and Variable. Typically used for Land solutions.
       Arguments:
          scenarios: dict of {scenario_name: AdvancedControls_object}
          vmas: dict of {vma_name: VMA_object}
    """
    title = 'CONVENTIONAL Operating Cost per Functional Unit per Annum'
    tooltip = ("CONVENTIONAL Operating Cost per Functional Unit per Annum\n\n"
               "NOTE: This is the Operating Cost per functional unit, derived "
               "from the CONVENTIONAL mix of technologies/practices.  In most "
               "cases this will be expressed as a cost per 'hectare of land'.\n\n"
               "This annualized value should capture the variable costs for "
               "maintaining the CONVENTIONAL practice, as well as  fixed costs. "
               "The value should reflect the average over the reasonable lifetime "
               "of the practice.\n\n"
               "Note: If the Operating Cost changes significantly across years, "
               "you can use a customized calculation at bottom of 'Operating Cost' sheet.")
    subtitle = '(per ha per annum)'
    return scn_edit_vma_var(scenarios=scenarios, vma=vmas.get(title, None),
            title=title, tooltip=tooltip, subtitle=subtitle)


def conv_lifetime_capacity(scenarios, vmas):
    """Conventional lifetime capacity column for scenario editor.
       Arguments:
          scenarios: dict of {scenario_name: AdvancedControls_object}
          vmas: dict of {vma_name: VMA_object}
    """
    title = 'Lifetime Capacity - CONVENTIONAL'
    tooltip = ("Lifetime Capacity - CONVENTIONAL\n\n"
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
    subtitle = 'use until replacement is required'
    return scn_edit_vma_var(scenarios=scenarios, vma=vmas.get(title, None),
            title=title, tooltip=tooltip, subtitle=subtitle)


def soln_first_cost(scenarios, vmas):
    """Solution First Cost column for scenario editor.
       Arguments:
          scenarios: dict of {scenario_name: AdvancedControls_object}
          vmas: dict of {vma_name: VMA_object}
    """
    title = 'SOLUTION First Cost per Implementation Unit'
    tooltip = ("SOLUTION First Cost per Implementation Unit\n\n"
               "NOTE: This is the cost of acquisition and the cost of installation "
               "(sometimes one and the same) or the cost of initiating a program/practice "
               "(for solutions where there is no direct artifact to acquire and install) "
               "per Implementation unit of the SOLUTION.\n\n"
               "E.g. What is the cost to acquire and install rooftop solar PV?")
    if list(scenarios.values())[0].solution_category == ac.SOLUTION_CATEGORY.LAND:
        subtitle = '(per ha)'
    else:
        subtitle = '(implementation units)'
    return scn_edit_vma_var(scenarios=scenarios, vma=vmas.get(title, None),
            title=title, tooltip=tooltip, subtitle=subtitle)


def soln_oper_cost_total(scenarios, vmas):
    """Solution Operating Cost, including Fixed and Variable. Typically used for Land solutions.
       Arguments:
          scenarios: dict of {scenario_name: AdvancedControls_object}
          vmas: dict of {vma_name: VMA_object}
    """
    title = 'SOLUTION Operating Cost per Functional Unit per Annum'
    tooltip = ("SOLUTION Operating Cost per Functional Unit per Annum\n\n"
               "NOTE: This is the Operating Cost per functional unit, derived from the SOLUTION. "
               "In most cases this will be expressed as a cost per 'hectare of land'.\n\n"
               "This annualized value should capture both the variable costs for maintaining the "
               "SOLUTION practice as well as the fixed costs. The value should reflect the average "
               "over the reasonable lifetime of the practice.")
    subtitle = '(per ha per annum)'
    return scn_edit_vma_var(scenarios=scenarios, vma=vmas.get(title, None),
            title=title, tooltip=tooltip, subtitle=subtitle)


def soln_oper_cost_fixed(scenarios, vmas):
    """Solution Fixed Operating Cost. Typically used for RRS solutions.
       Arguments:
          scenarios: dict of {scenario_name: AdvancedControls_object}
          vmas: dict of {vma_name: VMA_object}
    """
    title = 'SOLUTION Fixed Operating Cost (FOM)'
    tooltip = ("SOLUTION Fixed Operating Cost (FOM)\n\n"
               "NOTE: This is the annual operating cost per implementation unit, derived from "
               "the SOLUTION.  In most cases this will be expressed as a cost per 'some unit "
               "of installation size'\n\n"
               "E.g., $10,000 per kw. In terms of transportation, this can be considered the "
               "total insurance, and maintenance cost per car.\n\n"
               "Purchase costs can be amortized here or included as a first cost, but not both.")
    subtitle = '(implementation units)'
    return scn_edit_vma_var(scenarios=scenarios, vma=vmas.get(title, None),
            title=title, tooltip=tooltip, subtitle=subtitle)


def soln_net_profit_margin(scenarios, vmas):
    """Solution net profit margin.
       Arguments:
          scenarios: dict of {scenario_name: AdvancedControls_object}
          vmas: dict of {vma_name: VMA_object}
    """
    title = 'SOLUTION Net Profit Margin per Functional Unit per Annum'
    tooltip = ("SOLUTION Net Profit Margin per Functional Unit per Annum\n\n"
               "NOTE: This is the net annual profit margin per functional unit, derived from "
               "the SOLUTION mix of technologies/practices.  In most cases this will be expressed "
               "as a profit per 'hectare of land'.\n\n"
               "This annualized value should capture net margin, not gross margin that result "
               "from the practice, whether sales of plant or animal products. The value should "
               "reflect the average over the reasonable lifetime of the practice.\n\n"
               "Note: If the net profit margin changes significantly across years, you can use a "
               "customized calculation at bottom of 'Net Profit Margin' sheet.")
    subtitle = 'years'
    return scn_edit_vma_var(scenarios=scenarios, vma=vmas.get(title, None),
            title=title, tooltip=tooltip, subtitle=subtitle)
