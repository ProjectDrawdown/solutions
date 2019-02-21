import xlrd
from collections import OrderedDict
import pandas as pd
from tools.util import cell_to_offsets, convert_float
from model.customadoption import generate_df_template, YEARS, REGIONS


class CustomAdoptionReader:
    def __init__(self, xls_path, ref_or_pds):
        """
        xls_path: path to solution xls file
        """
        wb = xlrd.open_workbook(filename=str(xls_path))
        if ref_or_pds.lower() == 'ref':
            self.sheet = wb.sheet_by_name('Custom REF Adoption')
        elif ref_or_pds.lower() == 'pds':
            self.sheet = wb.sheet_by_name('Custom PDS Adoption')
        else:
            raise ValueError('specify PDS or REF')
        self.df_template = generate_df_template()

    def read_xls(self, csv_path=None):
        """
        Reads the whole Custom Adoption xls sheet.
        csv_path: (pathlib path object) If specified, will write CSVs to path for each table
        """
        self._find_tables()
        df_dict = OrderedDict()
        for title, location in self.table_locations.items():
            df = self.read_single_scenario(location)
            if df.empty:  # in line with our policy of setting empty tables to None
                df_dict[title] = None
            else:
                df_dict[title] = df
                if csv_path is not None:
                    path_friendly_title = title.replace('/', '_')
                    df.to_csv(csv_path.joinpath(path_friendly_title + '.csv'), index=['Year'])
        return df_dict

    def read_single_scenario(self, scenario_num_cell):
        """
        Reads a single Scenario table.
        source_id_cell: xls location or offsets of 'Scenario' cell of table
        (e.g. 'A77' or cell_to_offsets('A77'), where A77 is the cell that contains 'Scenario 1')
        """
        df = self.df_template.copy(deep=True)
        if isinstance(scenario_num_cell, str):  # for convenience + testing
            row1, col1 = cell_to_offsets(scenario_num_cell)
        else:  # for use with read_xls
            row1, col1 = scenario_num_cell
        for c, region in enumerate(REGIONS):
            col_name = self.sheet.cell_value(row1 + 1, col1 + 1 + c)
            assert col_name == region, 'column mismatch (xls: {}, python: {})'.format(col_name, region)
            col = pd.Series(index=df.index)
            for r, year in enumerate(YEARS):
                if c == 0:
                    # check once that years are correct
                    assert int(self.sheet.cell_value(row1 + 2 + r, col1)) == year, 'row mismatch'
                col[year] = convert_float(self.sheet.cell_value(row1 + 2 + r, col1 + 1 + c), return_nan=True)
            df[region] = col
        return df

    def _find_tables(self):
        """ Find locations and titles of scenario tables """
        locations = OrderedDict()
        row, col = cell_to_offsets('A77')
        for i in range(1, 11):
            scen_num = self.sheet.cell_value(row, col)
            expected = 'Scenario ' + str(i)
            assert scen_num == expected, 'xls: {}, expected: {}'.format(scen_num, expected)
            title = self.sheet.cell_value(row, col + 1)
            if title.startswith('[Type Scenario'):
                break  # assume blank from here on
            locations[title] = row, col
            row += 54  # tables are evenly spaced 54 rows apart
        self.table_locations = locations
