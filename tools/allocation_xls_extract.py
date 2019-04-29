""" Reads 'Land Allocation - Max TLA' or 'Ocean Allocation - Max TLA'  sheet """

import xlrd
import pathlib
import pandas as pd
import os
from model.dd import THERMAL_DYNAMICAL_REGIMES, THERMAL_MOISTURE_REGIMES
from tools.util import cell_to_offsets, convert_float, to_filename

LAND_XLS_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land', 'Land Allocation - Max TLA.xlsx')
LAND_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land', 'allocation')
OCEAN_XLS_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'ocean', 'Ocean Allocation - Max TOA.xlsx')
OCEAN_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'ocean', 'allocation')
pd.set_option('display.expand_frame_repr', False)


class AllocationReader:

    def __init__(self, key='land'):
        f = LAND_XLS_PATH if key == 'land' else OCEAN_XLS_PATH
        wb = xlrd.open_workbook(filename=f)
        sheetname = 'Land Allocation - Max TLA' if key == 'land' else 'Ocean Allocation - Max TOA'
        self.sheet = wb.sheet_by_name(sheetname)
        self.key = key
        if key == 'land':
            self.first_cells = [
                cell_to_offsets('D18'),  # forests
                cell_to_offsets('AU18'),  # grasslands
                cell_to_offsets('CL18'),  # irrigated croplands
                cell_to_offsets('EC18')  # rainfed croplands
            ]
        else:
            self.first_cells = [cell_to_offsets('D18')]
        self.regimes = THERMAL_MOISTURE_REGIMES if key == 'land' else THERMAL_DYNAMICAL_REGIMES
        self.df_dict = None
        self._make_df_template()

    def read_allocation_xls(self):
        """
        Reads the allocation xls and returns a nested dict of DataFrames. The structure of the dict
        is Regime -> AEZ number.
        e.g. self.df_dict['Tropical-Humid']['AEZ1']
        """

        self.df_dict = {}
        for i, regime in enumerate(self.regimes):
            tmr_dict = {}
            for cell in self.first_cells:
                title_row_offset = 3 if self.key == 'land' else 5
                assert 'EZ' in self.sheet.cell_value(cell[0] - title_row_offset, cell[1] - 1)
                assert 'EZ' in self.sheet.cell_value(cell[0] - 2, cell[1] - 1)
                row, col = cell
                num_cols = 7 if self.key == 'land' else 6
                for j in range(num_cols):
                    row_offset = i * 27
                    col_offset = j * 6
                    df = self.get_single_adoption_df(row + row_offset, col + col_offset)
                    df.name = aez = self.sheet.cell_value(row - title_row_offset, col - 1 + col_offset).strip()
                    tmr_dict[aez] = df
            self.df_dict[regime] = tmr_dict
        return self.df_dict

    def get_single_adoption_df(self, row1, col1):
        """
        Reads an adoption table from the spreadsheet when given the first cell.
        e.g. get_single_adoption_df(*cell_to_offsets('D18')) would give the
        table associated with cell D18 (Tropical-Humid, AEZ1).
        """

        assert self.sheet.cell_value(row1, col1 - 1).endswith('Protection')

        df = self.df_template.copy(deep=True)
        for i in range(5):
            col = []
            for j in range(25):
                col.append(convert_float(self.sheet.cell_value(row1 + j, col1 + i)))
            df[self.columns[i]] = col
        return df

    def make_csvs(self):
        """ Makes csv versions of tables and stores in data/land/allocation """

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
            self.read_allocation_xls()

        # write CSVs
        for regime in self.regimes:
            filename = to_filename(regime)
            os.mkdir(path.joinpath(filename))
            for zone, df in self.df_dict[regime].items():
                df.to_csv(path.joinpath(filename, to_filename(zone) + '.csv'))

    def _make_df_template(self):
        """ Makes template of adoption table to feed data into """
        self.columns = []
        index = []
        row, col = self.first_cells[0]
        for i in range(25):
            index.append(self.sheet.cell_value(row + i, col - 1))
        for i in range(5):
            self.columns.append(self.sheet.cell_value(row - 1, col + i))
        self.df_template = pd.DataFrame(columns=self.columns, index=index)


if __name__ == '__main__':
    r = AllocationReader(key='ocean')
    r.read_allocation_xls()
    r.make_csvs()
