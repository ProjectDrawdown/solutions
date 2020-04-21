"""Reads Variable Meta Analysis tab

   The code in this file is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE
   version 3.0.

   Outputs of this utility are considered to be data and do not automatically
   carry the license used for the code in this utility. It is up to the user and
   copyright holder of the inputs to determine what copyright applies to the
   output.
"""

import collections
import os
import pathlib

import numpy as np
import pandas as pd
import tools.util

CSV_TEMPLATE_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'VMA', 'vma_template.csv')
DATA_DIR_PATH = pathlib.Path(__file__).parents[1].joinpath('data')
pd.set_option('display.expand_frame_repr', False)

# A few VMA columns are only present in some solutions, for example specific to Land or Ocean solns.
OPTIONAL_COLUMNS = [
    'Thermal-Moisture Regime',
    'Crop',
    'Closest Matching Standard Crop (by Revenue/ha)',
]

def convert_year(x):
    if pd.isna(x):
        return np.nan
    try:
        return int(x)
    except ValueError:
        # a few VMAs use a range like '1990-2000'
        return str(x)


def convert_conversion_calculation(x):
    if x == 'Removed due to Copyright':
        return np.nan
    if not pd.isna(x):
        return float(x)
    return x


# dtype conversion map
COLUMN_DTYPE_MAP = {
    'SOURCE ID: Author/Org, Date, Info': lambda x: x,
    'Link': lambda x: x,
    'World / Drawdown Region': lambda x: x,
    'Specific Geographic Location': lambda x: x,
    'Thermal-Moisture Regime': lambda x: x,
    'Source Validation Code': lambda x: x,
    'Year / Date': lambda x: convert_year(x),
    'License Code': lambda x: x,
    'Raw Data Input': lambda x: float(x) if x is not np.nan else x,
    'Original Units': lambda x: x,
    'Conversion calculation': lambda x: convert_conversion_calculation(x),
    'Common Units': lambda x: x,
    'Weight': lambda x: x,
    'Assumptions': lambda x: x,
    'Closest Matching Standard Crop (by Revenue/ha)': lambda x: x,
    'Crop': lambda x: x,
    'Exclude Data?': lambda x: tools.util.convert_bool(x) if x is not np.nan else x,
}


def make_vma_df_template():
    """
    Helper function that generates a DataFrame with the same columns as the tables in
    the xls solution Variable Meta Analysis. This is the correct DataFrame format to
    input to the VMA python class. A researcher can thus use this function to create
    a new VMA table in python to populate with data if they want.
    """
    df = pd.read_csv(CSV_TEMPLATE_PATH, index_col=False, skipinitialspace=True,
            skip_blank_lines=True, comment='#', dtype="object")
    return df


def df_approx(df1, df2):
    try:
        pd.testing.assert_frame_equal(df1.astype(str), df2.astype(str), check_exact=False)
        return True
    except:
        return False


class VMAReader:
    def __init__(self, wb):
        """
        wb: Workbook from an Excel file, as from xlrd.open_workbook
        """
        self.wb = wb
        self.df_template = make_vma_df_template()
        # Give a starter value for this, it will get populated later if
        # necessary (don't populate now for speed reasons)
        self._data_csvs = None

    def _read_data_csvs(self):
        data_csvs = {}
        for filename in DATA_DIR_PATH.rglob('*.csv'):
            relpath = filename.relative_to(DATA_DIR_PATH).parts
            data_csvs[relpath] = pd.read_csv(filename, skipinitialspace=True,
                    skip_blank_lines=True, comment='#', dtype="object")
        return data_csvs

    def find_data_csv(self, df):
        # Poplate self._data_csvs if it hasn't been done yet. Do this
        # just-in-time to support use cases where we don't need to call
        # find_data_csv, like xls_df_dict().
        if self._data_csvs is None:
            self._data_csvs = self._read_data_csvs()

        for filename, data_df in self._data_csvs.items():
            if df_approx(df, data_df):
                return filename
        return None

    def xls_df_dict(self, alt_vma=False, title=None):
        """
        Finds tables in self.wb, reads them into dataframes, then returns a
        dictionary keyed by the table title. If a title is given, return a
        dictionary with just that title and dataframe.

        Raises KeyError if the title is not available.

        Arguments:
            alt_vma: False = process the primary VMA sheet 'Variable Meta-analysis',
                     True = process the alternate VMA sheet 'Variable Meta-analysis-DD' with fixed
                        values for Average, High, and Low.

        Returns:
            Returns a dictionary of tuples, of the form: {
                "title of the VMA, found by _find_tables": (
                    VMA dataframe,
                    Boolean value from the table on whether to "Use weight?" 
                    Float tuple, fixed summary values: (mean, high, low)
                )
            }
        """
        if alt_vma:
            sheetname = 'Variable Meta-analysis-DD'
            fixed_summary = True
        else:
            sheetname = 'Variable Meta-analysis'
            fixed_summary = False

        # Extract VMA table locations
        self._find_tables(sheetname=sheetname)

        # Either extract all titles or the desired one
        if title is None:
            locations_to_process = self.table_locations.items()
        else:
            locations_to_process = [(title, self.table_locations[title])]

        df_dict = collections.OrderedDict()
        for title, location in locations_to_process:
            df, use_weight, summary = self.read_single_table(source_id_cell=location,
                                                             sheetname=sheetname,
                                                             fixed_summary=fixed_summary)
            if df.empty:
                # in line with our policy of setting empty tables to None
                df_dict[title] = (None, False, (np.nan, np.nan, np.nan))
            else:
                # Process optional columns, drop if they are totally empty
                for col in OPTIONAL_COLUMNS:
                    if df.loc[:, col].isnull().all():
                        df.drop(labels=col, axis='columns', inplace=True)
                # Then save the table dataframe in an ordered dict by title
                df_dict[title] = (df, use_weight, summary)

        return df_dict

    def read_xls(self, csv_path=None, alt_vma=False):
        """
        Reads the whole Variable Meta-analysis xls sheet. If a CSV path is
        given, writes out a series of CSVs, of the form <table title>.csv and
        VMA_info.csv (contains summary data for each VMA).
        Note this currently only works for LAND solutions.

        Arguments:
            csv_path: (pathlib path object or str) If specified, will write
                CSVs to path for each table
            alt_vma: See docstring for xls_df_dict

        Returns a sort of "directory dataframe", pointing to each created CSV,
        noting the VMA title for that CSV, along with a couple of boolean
        values.
        """

        df_dict = self.xls_df_dict(alt_vma)

        vma_df = pd.DataFrame(
            columns=['Filename', 'Title on xls', 'Has data?', 'Use weight?'],
            index=pd.Index(data=list(range(1, len(df_dict) + 1)), name='VMA number')
        )
        info_df = pd.DataFrame(columns=['Title on xls', 'Fixed Mean', 'Fixed High', 'Fixed Low'])
        info_df.index.name = 'VMA number'

        i = 1
        for title, (table_df, use_weight, (average, high, low)) in df_dict.items():
            path_friendly_title = ''
            if table_df is not None:
                existing = self.find_data_csv(table_df)
                if existing is None:
                    path_friendly_title = tools.util.to_filename(title) + '.csv'
                    if csv_path is not None:
                        table_df.to_csv(os.path.join(csv_path, path_friendly_title), index=False)
                else:
                    # This CSV already exists in the data directory because multiple solutions
                    # use it. Reference the common file in all of those solutions.
                    path_friendly_title = existing

            row = {'Filename': path_friendly_title,
                   'Title on xls': title,
                   'Has data?': False if table_df is None else True,
                   'Use weight?': use_weight}
            vma_df.loc[i, :] = row

            if not pd.isna(average) or not pd.isna(high) or not pd.isna(low):
                row = {'Title on xls': title,
                       'Fixed Mean': average,
                       'Fixed High': high,
                       'Fixed Low': low}
                info_df.loc[i, :] = row

            # Bookkeep to track our position in vma_df, info_df
            i += 1

        if csv_path is not None:
            info_df.to_csv(os.path.join(csv_path, 'VMA_info.csv'))

        return vma_df


    def normalize_col_name(self, name):
        """Substitute well-known names for variants seen in some solutions."""
        known_aliases = {
            'Manually Exclude Data?': 'Exclude Data?',
            'Manually Excluded?': 'Exclude Data?',
            'Weight by: Production': 'Weight',
            # someone did a global replace of 'version' with 'edition' in Conservation Ag.
            'Conedition calculation': 'Conversion calculation',
            # Airplanes removed Geographic Location from one of the VMAs.
            'Specific': 'Specific Geographic Location',
            'Closest Matching Crop (by Revenue/ha)':
                'Closest Matching Standard Crop (by Revenue/ha)',
        }
        return known_aliases.get(name, name)


    def read_single_table(self, source_id_cell, sheetname, fixed_summary):
        """
        Reads a single Variable Meta-analysis table (e.g. Current Adoption).
        source_id_cell: xls location or offsets of SOURCE ID cell of table
        (e.g. 'C48' or cell_to_offsets('C48'), where C48 is the cell that starts 'SOURCE ID...')

        sheetname: typically 'Variable Meta-analysis' or 'Variable Meta-analysis-DD'
        fixed_summary: whether Average, High, and Low are fixed values to be extracted from Excel.
        """
        sheet = self.wb.sheet_by_name(sheetname)
        df = self.df_template.copy(deep=True)
        if isinstance(source_id_cell, str):  # for convenience + testing
            row1, col1 = tools.util.cell_to_offsets(source_id_cell)
        else:  # for use with read_xls
            row1, col1 = source_id_cell

        # Check column names before proceeding
        col_names = list(df.columns)
        idx = 0
        skipcols = []
        for c in range(16):
            val = str(sheet.cell_value(row1, col1 + c))
            if not val or idx >= len(col_names) or val == 'Battery Size':
                # Electric Bikes added 'Battery Size' in the empty column
                skipcols.append(c)
                continue    # skip blank columns
            name_to_check = self.normalize_col_name(val.strip().replace('*', ''))

            col_name = col_names[idx]
            while col_name in OPTIONAL_COLUMNS and name_to_check != col_name:
                col_names.remove(col_name)
                col_name = col_names[idx]

            assert col_name == name_to_check, f'unknown VMA column: {name_to_check} on row {row1}'
            idx += 1
        assert idx == len(col_names), f'columns not present: {idx} != {len(col_names)}'

        max_sources = 120
        done = False
        for r in range(max_sources):
            new_row = {}
            idx = 0
            for c in range(16):
                if c in skipcols:
                    continue
                col_name = col_names[idx]
                cell_val = sheet.cell_value(row1 + 1 + r, col1 + c)  # get raw val
                if cell_val == '**Add calc above':
                    done = True  # edge case where the table is filled with no extra rows
                    break
                cell_val = COLUMN_DTYPE_MAP[col_name](tools.util.empty_to_nan(cell_val))  # conversions
                new_row[col_name] = cell_val
                idx += 1
            if done or all(
                pd.isna(v) for k, v in new_row.items() if k not in ['Common Units', 'Weight']):
                last_row = r
                break  # assume an empty row (except for Common Units) indicates no more sources
            else:
                df = df.append(new_row, ignore_index=True)
        else:
            raise Exception(f"No blank row detected in table. Either there are {max_sources} " +
                    f"VMAs in table, the table is overfull, or there is some error in the code. "
                    f"Cell: {source_id_cell}")
        if (df['Weight'] == 0).all():
            # Sometimes all weights are set to 0 instead of blank. Change them to be NaN.
            df['Weight'] = df['Weight'].replace(0, np.nan)

        for r in range(last_row, last_row + 50):  # look past last row
            if sheet.cell_value(row1 + r, 17) == 'Use weight?':
                use_weight = tools.util.convert_bool(sheet.cell_value(row1 + r + 1, 17))
                break
            if sheet.cell_value(row1 + r, 18) == 'Use weight?':
                use_weight = tools.util.convert_bool(sheet.cell_value(row1 + r + 1, 18))
                break
        else:
            raise ValueError("No 'Use weight?' cell found")

        if fixed_summary:
            # Find the Average, High, Low cells.
            for r in range(last_row, last_row + 50):
                col = 0
                label = str(sheet.cell_value(row1 + r, 17)).lower()
                if label.startswith('average') or 'sum' in label:
                    col = 20 if use_weight else 19
                label = str(sheet.cell_value(row1 + r, 16)).lower()
                if label.startswith('average') or 'sum' in label:
                    col = 19 if use_weight else 18
                if col:
                    average = float(sheet.cell_value(row1 + r, col))
                    high = float(sheet.cell_value(row1 + r + 1, col))
                    low = float(sheet.cell_value(row1 + r + 2, col))
                    break
            else:
                raise ValueError(f"No 'Average' cell found for {source_id_cell}")
        else:
            average = high = low = np.nan

        return df, use_weight, (average, high, low)


    def _find_tables(self, sheetname):
        """
        Finds locations of all tables from the Variable Meta-analysis tab. They are not
        evenly spaced due to missing or extra rows, so to be safe we comb the following
        N rows from each table title. We also comb 10 rows ahead of each title to find
        the SOURCE ID cell, as this is also a varying spacing.

        Arguments:
            sheetname: name of the Excel Sheet. Internal solution files use
                'Variable Meta-analysis', public files use 'Variable Meta-analysis-DD'.
        """

        normalize_vma_names = {
            'SOLUTION First Cost per Implementation Unit of the solution':
                'SOLUTION First Cost per Implementation Unit',
            'CONVENTIONAL First Cost per Implementation Unit for replaced practices/technologies':
                'CONVENTIONAL First Cost per Implementation Unit',
            'Yield  from CONVENTIONAL Practice': 'Yield from CONVENTIONAL Practice',
            'Indirect CO2 Emissions per CONVENTIONAL Implementation OR functional Unit -- CHOOSE ONLY ONE on Advanced Controls':
                'CONVENTIONAL Indirect CO2 Emissions per Unit',
            'Indirect CO2 Emissions per SOLUTION Implementation Unit (Select on Advanced Controls)':
                'SOLUTION Indirect CO2 Emissions per Unit',
            'ALTERNATIVE APPROACH      Annual Energy Used UNDEGRADED LAND':
                'ALTERNATIVE APPROACH Annual Energy Used UNDEGRADED LAND',
            'SOLUTION VARIABLE Operating Cost per Functional Unit':
                'SOLUTION Variable Operating Cost (VOM) per Functional Unit',
            'SOLUTION FIXED Operating Cost per Implementation Unit':
                'SOLUTION Fixed Operating Cost (FOM)',
            'CONVENTIONAL VARIABLE Operating Cost per Functional Unit':
                'CONVENTIONAL Variable Operating Cost (VOM) per Functional Unit',
            'CONVENTIONAL FIXED Operating Cost per Implementation Unit':
                'CONVENTIONAL Fixed Operating Cost (FOM)',
            'Fuel Consumed per Functional Unit - CONVENTIONAL':
                'CONVENTIONAL Fuel Consumed per Functional Unit',
            'Total Energy Used per functional unit - SOLUTION':
                'SOLUTION Total Energy Used per Functional Unit',
            'Electricity Consumed per Functional Unit - CONVENTIONAL':
                'CONVENTIONAL Total Energy Used per Functional Unit',
            'Electricty Consumed per Functional Unit - CONVENTIONAL':
                'CONVENTIONAL Total Energy Used per Functional Unit',
            'Fuel Efficiency Factor - SOLUTION': 'SOLUTION Fuel Efficiency Factor',
            'Energy Efficiency Factor - SOLUTION': 'SOLUTION Energy Efficiency Factor',
            'Direct Emissions per CONVENTIONAL Functional Unit':
                'CONVENTIONAL Direct Emissions per Functional Unit',
            'Direct Emissions per SOLUTION Functional Unit':
                'SOLUTION Direct Emissions per Functional Unit',
            'Lifetime Capacity - SOLUTION': 'SOLUTION Lifetime Capacity',
            'Lifetime Capacity - CONVENTIONAL': 'CONVENTIONAL Lifetime Capacity',
            'Average Annual Use - SOLUTION': 'SOLUTION Average Annual Use',
            'Average Annual Use - CONVENTIONAL': 'CONVENTIONAL Average Annual Use',
        }

        table_locations = collections.OrderedDict()
        sheet = self.wb.sheet_by_name(sheetname)
        row, col = 40, 2
        for table_num in range(1, 36):
            found = False
            for rows_to_next_table in range(200):
                title_from_cell = str(sheet.cell_value(row + rows_to_next_table, col)).strip()
                title_from_cell = normalize_vma_names.get(title_from_cell, title_from_cell)
                if title_from_cell.startswith('VARIABLE'):
                    # if the table has a generic VARIABLE title assume no more variables to record
                    self.table_locations = table_locations
                    return  # search for tables ends here
                elif not title_from_cell:
                    continue

                # Rather than recording titles we will check for vma number. We need to validate
                # that this really is a Title, as VMAs are also numbered. We check that two rows
                # down is "Number", the heading for the numbered VMAs.
                table_num_on_sheet = sheet.cell_value(row + rows_to_next_table, col - 2)
                VMA_heading_check = False
                for offset in [1, 2, 3]:
                    cell_value = str(sheet.cell_value(row + rows_to_next_table + offset, col - 2))
                    if cell_value == 'Number':
                        VMA_heading_check = True
                if table_num_on_sheet == table_num and VMA_heading_check:  # if title cell of table
                    for space_after_title in range(10):
                        offset = rows_to_next_table + space_after_title
                        if sheet.cell_value(row + offset,
                                            col) == 'SOURCE ID: Author/Org, Date, Info':
                            table_locations[title_from_cell] = (row + offset, col)
                            row += offset
                            found = True
                            break
                    else:
                        raise Exception('Cannot find SOURCE ID cell for {}'.format(title_from_cell))
                if found:
                    break
            else:
                print(table_locations)
                raise Exception('Cannot find table number {}'.format(table_num))
        self.table_locations = table_locations
