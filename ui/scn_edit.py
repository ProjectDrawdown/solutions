"""Scenario / Advanced Controls editor."""

import dataclasses
import sys

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


def _dropdown_observe(change):
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


def _value_entry_observe(change):
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


def _on_vma_button_click(b):
    """Called when the Mean/High/Low buttons are clicked."""
    b.state['value_entry'].value = b.value_name


def scn_edit_vma_var(scenarios, varname, vma, title, tooltip, subtitle):
    """Render an editor box for a single VMA.
       Arguments:
         scenarios: a dict where the keys are scenario names, values are AdvancedControls objects
         varname: variable name in AdvancedControls to edit, like 'conv_2014_cost'
         vma: model.VMA object being edited
         title: name of the VMA being edited
         tooltip: tooltip to display with the title
         subtitle: line to print under the title, typically includes the units of the value
           being allocated like "MHa" or "US$2014/TWh"
    """
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
    dd_styles += ".dd_txt_center {text-align:center;}"
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
    value_entry.observe(_value_entry_observe, names='value')

    options = [ALL_SCENARIOS] + list(scenarios.keys())
    dropdown = ipywidgets.Dropdown(options=options, indent=False, layout=ly_drop)
    dropdown.observe(_dropdown_observe, names='value')

    element_state = { 'scenarios': scenarios, 'vma': vma, 'varname': varname,
            'value_entry': value_entry, 'dropdown': dropdown, 'values': values, }
    value_entry.state = element_state
    dropdown.state = element_state
    _set_value_entry_shadows(state=element_state)

    mean_button = ipywidgets.Button(description=f'{mean:.3f}', layout=ly_butn)
    mean_button.value_name = MEAN_MAGIC
    mean_button.state = element_state
    mean_button.on_click(_on_vma_button_click)
    high_button = ipywidgets.Button(description=f'{high:.3f}', layout=ly_butn)
    high_button.value_name = HIGH_MAGIC
    high_button.state = element_state
    high_button.on_click(_on_vma_button_click)
    low_button = ipywidgets.Button(description=f'{low:.3f}', layout=ly_butn)
    low_button.value_name = LOW_MAGIC
    low_button.state = element_state
    low_button.on_click(_on_vma_button_click)
    if not vma:
        mean_button.disabled = high_button.disabled = low_button.disabled = True
    varname_text = ipywidgets.Text(value=varname, disabled=True, indent=False, layout=ly_full)
    varname_text.add_class('dd_txt_center')

    children = [
        ipywidgets.HTML(dd_styles),
        ipywidgets.Button(description=title, disabled=True, tooltip=tooltip, layout=ly_full),
        ipywidgets.Button(description=subtitle, disabled=True, tooltip=tooltip, layout=ly_full),
        varname_text,
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


def _get_editor_for_var(c, varname):
    fields = dataclasses.fields(list(c.scenarios.values())[0])

    for field in fields:
        if field.name != varname:
            continue
        vma = None
        for vma_name in field.metadata.get('vma_titles', []):
            if vma_name in c.VMAs:
                vma = c.VMAs[vma_name]
        return scn_edit_vma_var(scenarios=c.scenarios, vma=vma, varname=varname, title=vma_name,
                tooltip=field.metadata.get('tooltip', ''),
                subtitle=field.metadata.get('subtitle', ''))
    return None


edit_ui_layout_land = [
    ('separator', 'Financial'),
    ('editor', ['conv_2014_cost', 'conv_fixed_oper_cost_per_iunit',
        'yield_from_conv_practice', ]),
    ('editor', ['pds_2014_cost', 'soln_fixed_oper_cost_per_iunit',
        'yield_gain_from_conv_to_soln', ]),
    ('separator', 'Electricity Grid based Emissions'),
    ('editor', ['conv_annual_energy_used', 'soln_energy_efficiency_factor',
        'soln_annual_energy_used', ]),
    ('separator', 'Non-Electricity Fuel Combustion-based Emissions'),
    ('editor', ['conv_fuel_consumed_per_funit', 'soln_fuel_efficiency_factor',]),
    ('separator', 'Direct Emissions (excl. electricity- or fuel-based)'),
    ('editor', ['tco2eq_reduced_per_land_unit', 'tco2_reduced_per_land_unit',
        'tn2o_co2_reduced_per_land_unit', 'tch4_co2_reduced_per_land_unit']),
    ('separator', 'CARBON SEQUESTRATION AND LAND INPUTS'),
    ('editor', ['seq_rate_global', 'carbon_not_emitted_after_harvesting', 'disturbance_rate', ]),
]

edit_ui_layout_ocean = [
    ('separator', 'Financial'),
    ('editor', ['conv_2014_cost', 'conv_fixed_oper_cost_per_iunit', ]),
    ('editor', ['pds_2014_cost', 'soln_fixed_oper_cost_per_iunit', ]),
]

edit_ui_layout_rrs = [
    ('separator', 'Financial'),
    ('editor', ['conv_2014_cost', 'conv_lifetime_capacity', 'conv_avg_annual_use',
        'conv_var_oper_cost_per_funit', 'conv_fixed_oper_cost_per_iunit', ]),
    ('editor', ['pds_2014_cost', 'soln_lifetime_capacity', 'soln_avg_annual_use',
        'soln_var_oper_cost_per_funit', 'soln_fixed_oper_cost_per_iunit', ]),
    ('separator', 'Emissions'),
    ('editor', ['conv_annual_energy_used', 'soln_energy_efficiency_factor',
        'soln_annual_energy_used', 'conv_fuel_consumed_per_funit',
        'soln_fuel_efficiency_factor',]),
    ('separator', 'Annual Direct Emissions (excl. electricity- or fuel-based)'),
    ('editor', ['conv_emissions_per_funit', 'soln_emissions_per_funit',]),
    ('separator', 'Indirect Emissions (CO2-eq)'),
    ('editor', ['conv_indirect_co2_per_unit', 'soln_indirect_co2_per_iunit',]),
    ('separator', 'Optional Emissions Factors'),
    ('editor', ['ch4_co2_per_funit', 'n2o_co2_per_funit',]),
]


def get_scenario_editor_for_solution(soln_mod):
    """Return Scenario Editor for a given solution.

       Arguments:
          soln_mod: a module for a particular solution, like solution.solarpvutil
    """
    first_scenario = list(soln_mod.scenarios.keys())[0]
    solution_category = soln_mod.scenarios[first_scenario].solution_category
    edit_ui_layout = []
    if solution_category == ac.SOLUTION_CATEGORY.LAND:
        edit_ui_layout = edit_ui_layout_land
    elif solution_category == ac.SOLUTION_CATEGORY.OCEAN:
        edit_ui_layout = edit_ui_layout_ocean
    else:
        edit_ui_layout = edit_ui_layout_rrs

    children = []
    for (row_type, row) in edit_ui_layout:
        if row_type == 'separator':
            div = '<div style="background-color:LightSkyBlue;border:1px solid black;'
            div += 'font-weight:bold;text-align:center;font-size:0.875em;">'
            label = ipywidgets.HTML(value=f"{div}{row}</div>")
            children.append(label)
        elif row_type == 'editor':
            row_children = []
            for varname in row:
                row_children.append(_get_editor_for_var(soln_mod, varname))
            children.append(ipywidgets.HBox(row_children))
            children.append(ipywidgets.HTML(value='<div>&nbsp;</div>'))

    return ipywidgets.VBox(children=children)
