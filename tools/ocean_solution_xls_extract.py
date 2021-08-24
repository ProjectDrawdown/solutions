#!/usr/bin/env python
"""Extract parameters from a Drawdown excel model to help create
   the Python implementation of the solution and its scenarios.

   The code in this file is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE
   version 3.0.

   Outputs of this utility are considered to be data and do not automatically
   carry the license used for the code in this utility. It is up to the user and
   copyright holder of the inputs to determine what copyright applies to the
   output.
"""
import yaml
import json
import os.path
import pathlib
import re
import sys
import datetime


import numpy as np
import pandas as pd
import os

# add a path entry one level up the directory tree at solutions/
# this allows the following import statements to work.
path = str(pathlib.Path(__file__).parents[1])
sys.path.append(path)

import tools.excel_tools as xl_tools

from model import advanced_controls as ac

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def convert_sr_float(val):
    """Return floating point value from Excel ScenarioRecord tab.

       There are three main formats:
       + simple: 0.182810601365724
       + percentage: 20%
       + annotated: Val:(0.182810601365724) Formula:='Variable Meta-analysis'!G1411
    """
    m = re.match(r'Val:\(([-+]?(\d+(\.\d*)?|\d+(\,\d*)?|\.\d+)([eE][-+]?\d+)?)\) Formula:=',
                 str(val))
    if m:
        s = str(m.group(1)).replace(',', '.')
        return float(s)
    if str(val).startswith('Val:() Formula:='):
        return float(0.0)
    if str(val).endswith('%'):
        (num, _) = str(val).split('%', maxsplit=1)
        return float(num) / 100.0
    if val == '':
        return 0.0
    return float(val)


def get_scenario_data(cfg):
    """Extract scenarios from an Ocean solutions Excel file.
       Arguments:
         cfg: Config values read in from config file
    """
    
    process_results = False

    df = xl_tools.get_from_excel(cfg["excelFile"], sheet='ScenarioRecord', excel_range='A:K', column_names = list("ABCDEFGHIJK"))
    
    filterForScenarioNames  = df["D"] == 'Name of Scenario:'
    filterOutTemplate = ~df["E"].str.contains('TEMPLATE', na=False)
    filter = filterForScenarioNames & filterOutTemplate 

    scen_rows = df[filter].index.to_list() # will get something like [301, 592, 883, 1174, 1465, 1756, 2047]

    # remove the template section
    df = df.iloc[scen_rows[0]:]

    # Now we only have non-template data in df
    # Next get rid of empty rows. Exclude column A for this, which contains a row index.
    filterOutBlankRows = df[list("BCDEFGHIJK")].any(axis='columns')
    df = df[filterOutBlankRows]

    # Append the last row or we'll miss out the last scenario:
    last_row = df.index.to_list().pop()
    scen_rows.append(last_row)

    scen_info = {}
    scen_results = {}
    scen_inputs = {}
    for i in range(0, len(scen_rows)-1): # iterate through the list of start/end row boundaries

        # Scenario data forms a series of "blocks" (both inputs and results)
        # Note: using loc here, not iloc, so we're using the index, which tracks the original Excel row id.
        scen_block = df.loc[scen_rows[i]:scen_rows[i+1]-1]

        # Assumption 1: first two lines form a scenario info section 
        scenario_time_stamp, scenario_name = scen_block[["B","E"]].iloc[0]
        scenario_description = scen_block["E"].iloc[1]

        # Find first instance of a section name containing the string "RESULTS"
        results_start = scen_block["B"].str.contains("RESULTS", case=False, regex=False, na=False).argmax()

        # Find first instance of a section name containing the string "INPUTS"
        inputs_start = scen_block["B"].str.contains("INPUTS", case=False, regex=False, na=False).argmax()

        # Now we know the boundaries of the results section and the inputs section
        start_position = results_start
        end_position = inputs_start-1
        results_block = scen_block.iloc[start_position:end_position]
        
        start_position = inputs_start
        end_position = scen_rows[i+1]-1
        inputs_block = scen_block.iloc[start_position:end_position]

        # Assumption 2: Column B contains the section names
        # Assumption 3: Column D contains the data keys
        # Assumption 4: Column E contains the data values
        # Assumption 5: Column F contains the data units
        
        scen_info = {'scenario_timestamp': scenario_time_stamp, 'scenario_description': scenario_description}

        if process_results == True:    
            results = process_block(results_block, scenario_name, scenario_outputs_spec)
            scen_results[scenario_name] = results
            scen_results[scenario_name].update(scen_info)
        
        # Now process the scenario inputs
        # Copy the Info section from the scen_results dict:
        
        results = process_block(inputs_block, scenario_inputs_spec)
        scen_inputs[scenario_name] = results
        scen_inputs[scenario_name].update(scen_info)
                
    return [scen_inputs, scen_results]


def process_block(scenario_block : pd.DataFrame, import_spec):
    data_dict = {}
    scenario_block = scenario_block.loc[:,['D','E']].dropna(how='all')
    import_spec_copy = import_spec.copy()
    
    skipping_row = False
    for row in scenario_block.itertuples(index=False):

        if (len(import_spec_copy) == 0) and (spec_item is None):
            break
        
        if not skipping_row:
            spec_item = import_spec_copy.pop(0)

        skipping_row = False

        row_D, row_E = row.D, row.E

        if not isinstance(row_D, str):
            skipping_row = True
            continue

        if row_D.casefold() not in [k.casefold() for k in spec_item.keys()]:
            skipping_row = True
            continue

        row_D = (row.D).strip()
    
        if isinstance(row_E, str):
            row_E = (row.E).strip()
    
        # Now read the individual statistics.
        stat_name, stat_value = row_D, row_E

        if stat_value == 'nan':
            stat_value = ''
        if pd.isna(stat_value):
            stat_value = 0.0

        # If it's in ('yes','y','n','no'), set it to a boolean.
        if isinstance(stat_value, str):
            if (stat_value.casefold() ==  'n'.casefold()) or (stat_value.casefold() ==  'no'.casefold()):
                stat_value = False
            elif (stat_value.casefold() == 'y'.casefold()) or (stat_value.casefold() ==  'yes'.casefold()):
                stat_value = True
            
        if not pd.isna(stat_name): # if not empty.
            
            spec_vals_dict = list(spec_item.values())[0]
            if len(spec_vals_dict) > 0:
                
                # Is there a rename_to specified?
                if 'rename_to' in spec_vals_dict:
                    stat_name = spec_vals_dict['rename_to']

                # Is there a regex substitution string specified?
                
                if stat_value and 'value_regex_match' in spec_vals_dict:
                    value_regex_match = spec_vals_dict['value_regex_match']
                else:
                    value_regex_match = ''

                if value_regex_match and isinstance(stat_value,str):
                    p = re.compile(value_regex_match)
                    m = p.match(stat_value)
                    # It's okay if we don't find a match, so no error if false.
                    regex_match = m.group(1)
                    regex_match = re.sub(r',','.',regex_match)
                    stat_value = float(regex_match)

                    # raise ValueError(f'Inconsistent import spec for {major_section_name}, {minor_section_name}, {spec_key}. \
                    #             Found value_regex_match of {value_regex_match}, but no associated value_regex_replace key')

            if pd.isna(stat_value):
                stat_value = None

            data_dict[stat_name] = stat_value
            spec_item = None

    return data_dict


def json_dumps_default(obj):
    """Default function for json.dumps."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return [[obj.index.name, *obj.columns.tolist()]] + obj.reset_index().values.tolist()
    elif isinstance(obj, pd.Series):
        return [[obj.index.name, obj.name]] + obj.reset_index().values.tolist()
    elif isinstance(obj, ac.SOLUTION_CATEGORY):
        return ac.solution_category_to_string(obj)
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        raise TypeError('Unable to JSON encode: ' + repr(obj))


def main():
    # Usually run this from inside the VS Code IDE.

    soln_name = 'Seafloor Protection' # Should match top-level key in ocean_solution_xls_extract_config.yaml

    path_to_here = pathlib.Path(__file__).parent.parent
    config_file = os.path.join(path_to_here,'solution/seafloorprotection/ocean_solution_xls_extract_config.yaml')
    #config_file = 'ocean_solution_xls_extract_config.yaml'
    print('Using config file:', config_file)
    stream = open(config_file, 'r')
    all_configs = yaml.load(stream, Loader=yaml.FullLoader)

    cfg = all_configs[soln_name]
    outputDir = cfg['outputDir']
    excelFile = cfg['excelFile']

    import_spec_path = os.path.join(path_to_here,'solution/seafloorprotection/ocean_solution_xls_extract_spec.yaml')
    #import_spec_path = 'solution/macroalgaerestoration/ocean_solution_xls_extract_spec.yaml'
    print('Using import spec:', import_spec_path)
    import_specs = open(import_spec_path, 'r')

    global scenario_outputs_spec
    global scenario_inputs_spec

    scenario_outputs_spec, scenario_inputs_spec = list(yaml.load_all(import_specs, Loader=yaml.FullLoader))
    
    print('Processing solution: ', soln_name, '\nUsing excelfile:', excelFile, '\nOutputting to: ', outputDir)
   
    inputs, outputs = get_scenario_data(cfg)   

    # remove minor section names from inputs:
    # new_inputs = {}
    # for scen in inputs.keys():
    #     new_inputs[scen] = {}
    #     new_inputs[scen]['Info'] = inputs[scen]['Info']
    #     del(inputs[scen]['Info'])
    #     for major_section in inputs[scen].keys():
    #         new_inputs[scen][major_section] = {}
    #         for minor_section in inputs[scen][major_section].keys():
    #             for k in inputs[scen][major_section][minor_section].keys():
    #                 new_inputs[scen][major_section][k] = inputs[scen][major_section][minor_section][k][0] # Use first element of list to only get value (subsequent entries have units)

    if len(inputs)>0:
        json_file_inputs = os.path.join(outputDir,'scenario_inputs.json')
        with open(json_file_inputs, mode='w') as f:
            json.dump(obj=inputs, fp=f, indent=4, default=json_dumps_default)
        
    if len(outputs)>0:
        json_file_outputs = os.path.join(outputDir,'scenario_outputs.json')
        with open(json_file_outputs, mode='w') as f:
            json.dump(obj=outputs, fp=f, indent=4, default=json_dumps_default)

    
    # for k in inputs.keys():
    #     json_file_inputs = os.path.join(outputDir,k + '_scenario_inputs.json')
    #     with open(json_file_inputs, mode='w') as f:
    #         json.dump(obj=inputs[k], fp=f, indent=4, default=json_dumps_default)
    #         f.close()


    # for k in outputs.keys():
    #     json_file_outputs = os.path.join(outputDir,k + '_scenario_results.json')
    #     with open(json_file_outputs, mode='w') as f:
    #         json.dump(obj=outputs[k], fp=f, indent=4, default=json_dumps_default)
    #         f.close()

if __name__ == "__main__":
    main()
