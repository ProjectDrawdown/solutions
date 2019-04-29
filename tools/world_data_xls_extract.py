""" Reads 'WORLD Land Data' or 'WORLD Ocean Data' sheet """

import xlrd
import pathlib
import pandas as pd
import os
from model.dd import THERMAL_DYNAMICAL_REGIMES, THERMAL_MOISTURE_REGIMES
from tools.util import cell_to_offsets, convert_float, to_filename

LAND_XLS_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land', 'WORLD Land Data.xlsx')
LAND_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land', 'world')
OCEAN_XLS_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'ocean', 'WORLD Ocean Data.xlsx')
OCEAN_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'ocean', 'world')

pd.set_option('display.expand_frame_repr', False)


class WorldDataReader:

    def __init__(self, key='land'):
        """
        Class to read in data.
        Args:
            key: 'land' or 'ocean'
        """
        wb = xlrd.open_workbook(filename=LAND_XLS_PATH) if key == 'land' else xlrd.open_workbook(
            filename=OCEAN_XLS_PATH)
        self.key = key
        self.sheet = wb.sheet_by_name('WORLD Land Data') if key == 'land' else wb.sheet_by_name('WORLD_Ocean_Data')

        self.first_cell = cell_to_offsets('D4') if key == 'Land' else cell_to_offsets('D10')
        self.regimes = THERMAL_MOISTURE_REGIMES if key == 'land' else THERMAL_DYNAMICAL_REGIMES
        self.df_dict = None
        self._make_df_template()

    def read_world_data_xls(self):
        """
        Reads the world * data xls and returns a dict of DataFrames. The keys are Regimes.
        e.g. self.df_dict['Tropical-Humid']
        """

        self.df_dict = {}
        row, col = self.first_cell
        for i, regime in enumerate(self.regimes):
            row_offset = i * 16 if self.key == 'land' else i * 17
            df = self.get_single_table_df(row + row_offset, col)
            df.name = regime
            self.df_dict[regime] = df
        return self.df_dict

    def get_single_table_df(self, row1, col1):
        """
        Reads a Regime table from the spreadsheet when given the first cell.
        e.g. get_single_adoption_df(*cell_to_offsets('D4')) would give the table associated
        with cell D4 (Tropical-Humid).
        """

        assert 'OECD90' in self.sheet.cell_value(row1, col1 - 1)

        df = self.df_template.copy(deep=True)
        for i in range(self.num_zones):
            col = []
            for j in self.row_nums:  # skip blank row
                col.append(convert_float(self.sheet.cell_value(row1 + j, col1 + i)))
            df[self.columns[i]] = col
        return df.fillna(0.)

    def make_csvs(self):
        """ Makes csv versions of tables and stores in data/land/world """
        path = LAND_CSV_PATH if self.key == 'land' else OCEAN_CSV_PATH

        # Sanity check
        if os.listdir(path):
            ans = input('Overwrite existing csv files? y or n')
            if ans == 'n':
                return
            elif ans != 'y':
                print('Not a valid answer')
                return

        # check the DataFrames are loaded
        if self.df_dict is None:
            self.read_world_data_xls()

        # write CSVs
        for regime in self.regimes:
            df = self.df_dict[regime]
            df.to_csv(path.joinpath(to_filename(regime) + '.csv'))

    def _make_df_template(self):
        """ Makes template of adoption table to feed data into """
        index = []
        row, col = self.first_cell
        if self.key == 'land':
            self.row_nums = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10]  # skip blank row
            self.num_zones = 29
            row_offset = 3
            self.columns = ['Total Area (km2)']
        else:
            self.row_nums = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11]  # skip blank row
            self.num_zones = 6
            row_offset = 9
            self.columns = ['Total Area (Mha)']
        for i in self.row_nums:
            index.append(self.sheet.cell_value(row + i, col - 1))
        for i in range(self.num_zones):
            self.columns.append(self.sheet.cell_value(row - row_offset, col + 1 + i))
        self.df_template = pd.DataFrame(columns=self.columns, index=index)


if __name__ == '__main__':
    r = WorldDataReader(key='ocean')
    r.read_world_data_xls()
    r.make_csvs()
