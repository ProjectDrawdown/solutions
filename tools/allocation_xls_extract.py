""" Reads 'Land Allocation - Max TLA' or 'Ocean Allocation - Max TLA'  sheet """

import argparse
import pathlib
import sys

import model.dd
import pandas as pd
import tools.util
import xlrd

LAND_XLS_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land', 'Land Allocation - Max TLA.xlsx')
LAND_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land', 'allocation')
OCEAN_XLS_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'ocean', 'Ocean Allocation - Max TOA.xlsx')
OCEAN_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'ocean', 'allocation')
pd.set_option('display.expand_frame_repr', False)


class AllocationReader:

    def __init__(self, key='land', outputdir=None):
        if key == 'land':
            f = LAND_XLS_PATH
            self.regimes = model.dd.THERMAL_MOISTURE_REGIMES
            sheetname = '2019'
        else:
            f = OCEAN_XLS_PATH
            self.regimes = model.dd.THERMAL_DYNAMICAL_REGIMES
            sheetname = 'Ocean Allocation - Max TOA'
        self.key = key

        wb = xlrd.open_workbook(filename=f)
        self.sheet = wb.sheet_by_name(sheetname)
        if key == 'land':
            self.first_cells = [
                tools.util.cell_to_offsets('D18'),  # forests
                tools.util.cell_to_offsets('AU18'),  # grasslands
                tools.util.cell_to_offsets('CL18'),  # irrigated croplands
                tools.util.cell_to_offsets('EC18')  # rainfed croplands
            ]
        else:
            self.first_cells = [tools.util.cell_to_offsets('D18')]
        self.df_dict = None
        self._make_df_template()

        if outputdir is None:
            outputdir = LAND_CSV_PATH if key == 'land' else OCEAN_CSV_PATH
        self.outputdir = pathlib.Path(outputdir)


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
                if self.key == 'land':
                    row_mult = 31
                    num_cols = 7
                else:
                    row_mult = 27
                    num_cols = 6
                for j in range(num_cols):
                    row_offset = i * row_mult
                    col_offset = j * 6
                    df = self.get_single_adoption_df(row + row_offset, col + col_offset)
                    df.name = aez = self.sheet.cell_value(row - title_row_offset, col - 1 + col_offset).strip()
                    tmr_dict[aez] = df
            self.df_dict[regime] = tmr_dict
        return self.df_dict

    def get_single_adoption_df(self, row1, col1):
        """
        Reads an adoption table from the spreadsheet when given the first cell.
        e.g. get_single_adoption_df(*tools.util.cell_to_offsets('D18')) would give the
        table associated with cell D18 (Tropical-Humid, AEZ1).
        """

        df = self.df_template.copy(deep=True)
        for i in range(5):
            col = []
            for j in range(25):
                col.append(tools.util.convert_float(self.sheet.cell_value(row1 + j, col1 + i)))
            df[self.columns[i]] = col
        return df

    def make_csvs(self):
        """ Makes csv versions of tables and stores in data/land/allocation """
        # Sanity check
        if list(self.outputdir.glob('*')):
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
            filename = tools.util.to_filename(regime)
            self.outputdir.joinpath(filename).mkdir(parents=True, exist_ok=True)
            for zone, df in self.df_dict[regime].items():
                df.to_csv(self.outputdir.joinpath(filename, tools.util.to_filename(zone) + '.csv'))

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
    parser = argparse.ArgumentParser(
        description='Extract Land/Ocean allocation from Excel..')
    parser.add_argument('--key', default='land', help='"land" or "ocean"')
    parser.add_argument('--outputdir', help='Directory to write generated CSV files to')
    args = parser.parse_args(sys.argv[1:])

    if args.outputdir is None:
        if args.key == 'land':
            args.outputdir = LAND_CSV_PATH
        else:
            args.outputdir = OCEAN_CSV_PATH
    else:
        args.outputdir = pathlib.Path(args.outputdir)

    r = AllocationReader(key=args.key, outputdir=args.outputdir)
    r.read_allocation_xls()
    r.make_csvs()
