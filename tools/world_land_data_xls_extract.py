""" Reads 'WORLD Land Data' sheet """

import xlrd
import pathlib
import pandas as pd
import os
from tools.util import cell_to_offsets, convert_float, to_filename

XLS_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land', 'WORLD Land Data.xlsx')
CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land', 'world')
pd.set_option('display.expand_frame_repr', False)


class WorldLandDataReader:

    def __init__(self):
        wb = xlrd.open_workbook(filename=XLS_PATH)
        self.sheet = wb.sheet_by_name('WORLD Land Data')

        self.first_cell = cell_to_offsets('D4')
        self.thermal_moisture_regimes = ['Tropical-Humid', 'Temperate_Boreal-Humid', 'Tropical-Semi-Arid',
                                    'Temperate_Boreal-Semi-Arid', 'Global Arid', 'Global Arctic']
        self.df_dict = None
        self._make_df_template()

    def read_world_land_data_xls(self):
        """
        Reads the world land data xls and returns a dict of DataFrames. The keys are Thermal Moisture Regimes.
        e.g. self.df_dict['Tropical-Humid']
        """

        self.df_dict = {}
        row, col = self.first_cell
        for i, tmr in enumerate(self.thermal_moisture_regimes):
            row_offset = i * 16
            df = self.get_single_tmr_df(row + row_offset, col)
            df.name = tmr
            self.df_dict[tmr] = df
        return self.df_dict

    def get_single_tmr_df(self, row1, col1):
        """
        Reads a Thermal Moisture Regime table from the spreadsheet when given the first cell.
        e.g. get_single_adoption_df(*cell_to_offsets('D4')) would give the table associated
        with cell D4 (Tropical-Humid).
        :return: DataFrame of table
        """

        assert 'OECD90' in self.sheet.cell_value(row1, col1 - 1)

        df = self.df_template.copy(deep=True)
        for i in range(30):
            col = []
            for j in [0, 1, 2, 3, 4, 5, 7, 8, 9, 10]:   # skip blank row
                col.append(convert_float(self.sheet.cell_value(row1 + j, col1 + i)))
            df[self.columns[i]] = col
        return df

    def make_csvs(self):
        """ Makes csv versions of tables and stores in data/land/world """

        # Sanity check
        if os.listdir(CSV_PATH):
            ans = input('Overwrite existing csv files? y or n')
            if ans == 'n':
                return
            elif ans != 'y':
                print('Not a valid answer')
                return

        # check the DataFrames are loaded
        if self.df_dict is None:
            self.read_world_land_data_xls()

        # write CSVs
        for tmr in self.thermal_moisture_regimes:
            df = self.df_dict[tmr]
            df.to_csv(CSV_PATH.joinpath(to_filename(tmr) + '.csv'))

    def _make_df_template(self):
        """ Makes template of adoption table to feed data into """
        self.columns = ['Total Area (km2)']
        index = []
        row, col = self.first_cell
        for i in [0, 1, 2, 3, 4, 5, 7, 8, 9, 10]:   # skip blank row
            index.append(self.sheet.cell_value(row + i, col - 1))
        for i in range(29):
            self.columns.append(self.sheet.cell_value(row - 3, col + 1 + i))
        self.df_template = pd.DataFrame(columns=self.columns, index=index)


if __name__ == '__main__':
    r = WorldLandDataReader()
    r.read_world_land_data_xls()
    r.make_csvs()