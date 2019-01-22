""" Reads 'Land Allocation - Max TLA'  sheet """

import xlrd
import re
import pathlib
import pandas as pd
from tools.xls_extract import cell_to_offsets, convert_float

LAND_ALLOCATION_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land', 'Land Allocation - Max TLA.xlsx')
pd.set_option('display.expand_frame_repr', False)


def convert(val):
    """ Allows passing non-empty strings through the convert_float function """
    try:
        return convert_float(val)
    except ValueError:
        return val


class LandAllocationReader:

    def __init__(self):
        wb = xlrd.open_workbook(filename=LAND_ALLOCATION_PATH)
        self.sheet = wb.sheet_by_name('Land Allocation - Max TLA')

        self.first_cells = [
            cell_to_offsets('D18'),  # forests
            cell_to_offsets('AU18'),  # grasslands
            cell_to_offsets('CL18'),  # irrigated croplands
            cell_to_offsets('EC18')  # rainfed croplands
        ]
        self.thermal_moisture_regimes = ['Tropical-Humid', 'Temperate/Boreal-Humid', 'Tropical-Semi-Arid',
                                    'Temperate/Boreal-Semi-Arid', 'Global Arid', 'Global Arctic']

        self._make_df_template()

    def read_land_allocation_xls(self):
        """
        Reads the land allocation xls and returns a nested dict of DataFrames. The structure of the dict
        is Thermal Moisure Regime -> AEZ number.
        e.g. self.df_dict['Tropical-Humid']['AEZ1']
        """

        self.df_dict = {}
        for i, tmr in enumerate(self.thermal_moisture_regimes):
            tmr_dict = {}
            for cell in self.first_cells:
                assert 'AEZ' in self.sheet.cell_value(cell[0] - 3, cell[1] - 1)
                assert 'AEZ' in self.sheet.cell_value(cell[0] - 2, cell[1] - 1)
                row, col = cell
                for j in range(7):
                    row_offset = i * 27
                    col_offset = j * 6
                    df = self.get_single_adoption_df(row + row_offset, col + col_offset)
                    tmr_dict[self.sheet.cell_value(row - 2, col - 1 + col_offset)] = df
            self.df_dict[tmr] = tmr_dict
        return self.df_dict

    def get_single_adoption_df(self, row1, col1):
        """
        Reads an adoption table from the spreadsheet when given the first cell.
        e.g. get_single_adoption_df(*cell_to_offsets('D18')) would give the
        table associated with cell D18 (Tropical-Humid, AEZ1).
        :return: DataFrame of table
        """

        assert 'Forest Protection' in self.sheet.cell_value(row1, col1 - 1)

        df = self.df_template.copy(deep=True)
        for i in range(5):
            col = []
            for j in range(25):
                col.append(convert(self.sheet.cell_value(row1 + j, col1 + i)))
            df[self.columns[i]] = col
        return df

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
    r = LandAllocationReader()
    r.read_land_allocation_xls()