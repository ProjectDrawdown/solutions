""" Reads Variable Meta Analysis tab """

import os
import pathlib
import pandas as pd
from numpy import nan
from collections import OrderedDict
import warnings
from tools.util import cell_to_offsets, empty_to_nan, to_filename, convert_bool

CSV_TEMPLATE_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'VMA', 'vma_template.csv')
pd.set_option('display.expand_frame_repr', False)

# dtype conversion map
COLUMN_DTYPE_MAP = {
    'SOURCE ID: Author/Org, Date, Info': lambda x: x,
    'Link': lambda x: x,
    'World / Drawdown Region': lambda x: x,
    'Specific Geographic Location': lambda x: x,
    'Thermal-Moisture Regime': lambda x: x,
    'Source Validation Code': lambda x: x,
    'Year / Date': lambda x: int(x) if x is not nan else x,
    'License Code': lambda x: x,
    'Raw Data Input': lambda x: float(x) if x is not nan else x,
    'Original Units': lambda x: x,
    'Conversion calculation': lambda x: float(x) if x is not nan else x,
    'Common Units': lambda x: x,
    'Weight': lambda x: x,
    'Assumptions': lambda x: x,
    'Exclude Data?': lambda x: convert_bool(x) if x is not nan else x,
}

ADOPTION_VARIABLES = [
    'Current Adoption', 'CONVENTIONAL First Cost per Implementation Unit for replaced practices/technologies',
    'SOLUTION First Cost per Implementation Unit of the solution',
    'CONVENTIONAL Operating Cost per Functional Unit per Annum',
    'SOLUTION Operating Cost per Functional Unit per Annum',
    'CONVENTIONAL Net Profit Margin per Functional Unit per Annum',
    'SOLUTION Net Profit Margin per Functional Unit per Annum', 'Yield  from CONVENTIONAL Practice',
    'Yield Gain (% Increase from CONVENTIONAL to SOLUTION)'
]

EMISSIONS_REDUCTION_VARIABLES = [
    'Electricty Consumed per CONVENTIONAL Functional Unit', 'Energy Efficiency Factor - SOLUTION',
    'Total Energy Used per SOLUTION functional unit', 'Fuel Consumed per CONVENTIONAL Functional Unit',
    'Fuel Reduction Factor SOLUTION', 't CO2-eq (Aggregate emissions) Reduced per Land Unit',
    't CO2 Reduced per Land Unit', 't N2O-CO2-eq Reduced per Land Unit', 't CH4-CO2-eq Reduced per Land Unit',
    'Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit -- CHOOSE ONLY ONE',
    'Indirect CO2 Emissions per SOLUTION Implementation Unit'
]

SEQUESTRATION_AND_LAND_INPUTS = [
    'Sequestration Rates', 'Sequestered Carbon NOT Emitted after Cyclical Harvesting/Clearing', 'Disturbance Rate']


def make_vma_df_template():
    """
    Helper function that generates a DataFrame with the same columns as the tables in
    the xls solution Variable Meta Analysis. This is the correct DataFrame format to
    input to the VMA python class. A researcher can thus use this function to create
    a new VMA table in python to populate with data if they want.
    """
    df = pd.read_csv(CSV_TEMPLATE_PATH, index_col=False, skipinitialspace=True, skip_blank_lines=True, comment='#')
    return df


class VMAReader:
    def __init__(self, wb):
        """
        xls_path: path to solution xls file
        """
        self.sheet = wb.sheet_by_name('Variable Meta-analysis')
        self.df_template = make_vma_df_template()

    def read_xls(self, csv_path=None):
        """
        Reads the whole Variable Meta-analysis xls sheet.
        Note this currently only works for LAND solutions.
        csv_path: (pathlib path object or str) If specified, will write CSVs to path for each table
        """
        self._find_tables()
        df_dict = OrderedDict()
        for title, location in self.table_locations.items():
            df = self.read_single_table(location)
            if df.empty:  # in line with our policy of setting empty tables to None
                df_dict[title] = None
            else:
                df_dict[title] = df

        if csv_path is not None:
            idx = pd.Index(data=list(range(1, len(df_dict) + 1)), name='VMA number')
            info_df = pd.DataFrame(columns=['Filename', 'Title on xls', 'Has data?'], index=idx)
            i = 1
            for title, df in df_dict.items():
                path_friendly_title = to_filename(title)
                row = {'Filename': path_friendly_title, 'Title on xls': title,
                       'Has data?': False if df is None else True}
                info_df.loc[i, :] = row
                i += 1
                if df is not None:
                    df.to_csv(os.path.join(csv_path, path_friendly_title + '.csv'), index=False)
            info_df.to_csv(os.path.join(csv_path, 'VMA_info.csv'))
        return df_dict

    def read_single_table(self, source_id_cell):
        """
        Reads a single Variable Meta-analysis table (e.g. Current Adoption).
        source_id_cell: xls location or offsets of SOURCE ID cell of table
        (e.g. 'C48' or cell_to_offsets('C48'), where C48 is the cell that starts 'SOURCE ID...')
        """
        df = self.df_template.copy(deep=True)
        if isinstance(source_id_cell, str):  # for convenience + testing
            row1, col1 = cell_to_offsets(source_id_cell)
        else:  # for use with read_xls
            row1, col1 = source_id_cell
        for r in range(30):
            new_row = {}
            for c in range(15):
                if c == 14:
                    c += 1  # There is a blank column before the "Exclude Data?" column
                col_name = df.columns[c] if c != 15 else df.columns[-1]
                if r == 0:  # check col name before proceeding
                    first_cell = self.sheet.cell_value(row1, col1 + c)
                    name_to_check = first_cell.strip().replace('*', '')
                    assert name_to_check == col_name, 'cell value: {} is not {}'.format(first_cell, col_name)
                cell_val = self.sheet.cell_value(row1 + 1 + r, col1 + c)  # get raw val
                cell_val = COLUMN_DTYPE_MAP[col_name](empty_to_nan(cell_val))  # conversions
                new_row[col_name] = cell_val
            if all(pd.isna(v) for k, v in new_row.items() if k != 'Common Units'):
                break  # assume an empty row (except for Common Units) indicates no more sources to copy
            else:
                df = df.append(new_row, ignore_index=True)
        else:
            warnings.warn(
                'No blank row detected in table. Either there are 30+ VMAs in table, the table has been misused'
                'or there is some error in the code.')
        if (df['Weight'] == 0).all():
            # Sometimes all weights are set to 0 instead of blank. In this case we want them to be NaN.
            df['Weight'] = df['Weight'].replace(0, nan)
        return df

    def _find_first_cells(self):
        section_titles = ['ADOPTION VARIABLES', 'FINANCIAL VARIABLES', 'EMISSIONS REDUCTION VARIABLES',
                          'SEQUESTRATION AND LAND INPUTS', 'ADDITIONAL VARIABLES']
        first_cells = {}
        for r in range(30, 1000):
            if self.sheet.cell_value(r, 0) == section_titles[0]:
                # first cell may be the row below but _find_tables will deal with that
                first_cells[section_titles.pop(0)] = (r + 1, 2)
            if not section_titles:
                break
        else:
            print('Could not find section titles: {}'.format(section_titles))
        self.first_cells = first_cells

    def _find_tables(self):
        """
        Finds locations of all tables from the Variable Meta-analysis tab. They are not
        evenly spaced due to missing or extra rows, so to be safe we comb the following
        100 rows from each table title. We also comb 10 rows ahead of each title to find
        the SOURCE ID cell, as this is also a varying spacing.
        """
        self._find_first_cells()
        all_vars = OrderedDict([
            ('ADOPTION VARIABLES', ADOPTION_VARIABLES),
            ('EMISSIONS REDUCTION VARIABLES', EMISSIONS_REDUCTION_VARIABLES),
            ('SEQUESTRATION AND LAND INPUTS', SEQUESTRATION_AND_LAND_INPUTS),
            # additional variables go up to Variable 37 in accordance with the xls
            ('ADDITIONAL VARIABLES', ['var' + str(i) for i in range(24, 38)])
        ])
        table_locations = OrderedDict()
        for key, table_titles in all_vars.items():
            row, col = self.first_cells[key]
            for table_i, title in enumerate(table_titles):
                found = False
                for rows_to_next_table in range(100):
                    if self.sheet.cell_value(row + rows_to_next_table, col) == title:
                        for space_after_title in range(10):
                            offset = rows_to_next_table + space_after_title
                            if self.sheet.cell_value(row + offset, col) == 'SOURCE ID: Author/Org, Date, Info':
                                table_locations[title] = (row + offset, col)
                                row += offset
                                found = True
                                break
                        else:
                            raise Exception('Cannot find SOURCE ID cell for ' + title)
                    elif title.startswith('var'):  # additional variables
                        table_num = self.sheet.cell_value(row + rows_to_next_table, col - 2)
                        # as we cannot do a name check for solution specific names, we check the table number one
                        # cell to the left of the name to verify we have the title cell. This should start at 24.
                        if table_num == table_i + 24:
                            # we must also check the table has been named or we assume there are no additional vars
                            title_from_cell = self.sheet.cell_value(row + rows_to_next_table, col)
                            if title_from_cell.startswith('VARIABLE'):
                                self.table_locations = table_locations
                                return  # search for tables ends here
                            else:
                                for space_after_title in range(10):
                                    offset = rows_to_next_table + space_after_title
                                    if self.sheet.cell_value(row + offset, col) == 'SOURCE ID: Author/Org, Date, Info':
                                        table_locations[title_from_cell] = (row + offset, col)
                                        row += offset
                                        found = True
                                        break
                                else:
                                    raise Exception('Cannot find SOURCE ID cell for ' + title)

                    if found:
                        break
                else:
                    print(table_locations)
                    raise Exception('Cannot find: ' + title)
        self.table_locations = table_locations

