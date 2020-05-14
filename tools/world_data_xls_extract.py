""" Reads 'WORLD Land Data' or 'WORLD Ocean Data' sheet """

import argparse
import pathlib
import sys

import model.dd
import pandas as pd
import tools.util
import xlrd

LAND_XLS_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land', 'WORLD Land Data.xlsx')
LAND_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land', 'world', '2020')
OCEAN_XLS_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'ocean', 'WORLD Ocean Data.xlsx')
OCEAN_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'ocean', 'world')

pd.set_option('display.expand_frame_repr', False)


class WorldDataReader:

    def __init__(self, key='land', outputdir=None):
        """
        Class to read in data.
        Args:
            key: 'land' or 'ocean'
        """
        if key == 'land':
            filename = LAND_XLS_PATH
            self.regimes = model.dd.THERMAL_MOISTURE_REGIMES8
            sheetname = '2020'
            self.first_cell = tools.util.cell_to_offsets('D4')
            self.valid_zones = model.dd.AEZS
        else:
            filename = OCEAN_XLS_PATH
            self.regimes = model.dd.THERMAL_DYNAMICAL_REGIMES
            sheetname = 'WORLD_Ocean_Data'
            self.first_cell = tools.util.cell_to_offsets('D10')
            self.valid_zones = None
        self.key = key

        wb = xlrd.open_workbook(filename=filename)
        self.sheet = wb.sheet_by_name(sheetname)
        self.df_dict = None
        self._make_df_template()

        if outputdir is None:
            outputdir = LAND_CSV_PATH if key == 'land' else OCEAN_CSV_PATH
        self.outputdir = pathlib.Path(outputdir)


    def read_world_data_xls(self):
        """
        Reads the world * data xls and returns a dict of DataFrames. The keys are Regimes.
        e.g. self.df_dict['Tropical-Humid']
        """

        self.df_dict = {}
        row, col = self.first_cell
        num_regimes = len(self.regimes)
        regimes = list(self.regimes)  # make a copy
        for i in range(0, num_regimes):
            row_offset = i * 16 if self.key == 'land' else i * 17
            df = self.get_single_table_df(row + row_offset, col)
            xls_regime = str(self.sheet.cell_value(row + row_offset - 2, 2))
            for regime in regimes:
                if regime in xls_regime:
                    regimes.remove(regime)
                    break
            assert regime in str(self.sheet.cell_value(row + row_offset - 2, 2))
            df.name = regime
            self.df_dict[regime] = df
        return self.df_dict

    def get_single_table_df(self, row1, col1):
        """
        Reads a Regime table from the spreadsheet when given the first cell.
        e.g. get_single_adoption_df(*tools.util.cell_to_offsets('D4')) would give the table associated
        with cell D4 (Tropical-Humid).
        """

        assert 'OECD90' in self.sheet.cell_value(row1, col1 - 1)

        df = self.df_template.copy(deep=True)
        for i in range(self.num_zones):
            col = []
            for j in self.row_nums:  # skip blank row
                col.append(tools.util.convert_float(self.sheet.cell_value(row1 + j, col1 + i)))
            df[self.columns[i]] = col
        return df.fillna(0.)

    def make_csvs(self):
        """ Makes csv versions of tables and stores in data/land/world """
        # check the DataFrames are loaded
        if self.df_dict is None:
            self.read_world_data_xls()

        # write CSVs
        for regime in self.regimes:
            df = self.df_dict[regime]
            df.to_csv(self.outputdir.joinpath(tools.util.to_filename(regime) + '.csv'))

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
            zone = str(self.sheet.cell_value(row - row_offset, col + 1 + i)).strip()
            zone = " ".join(zone.split())  # collapse multiple spaces into one.
            if self.valid_zones:
                assert zone in self.valid_zones
            self.columns.append(zone)
        self.df_template = pd.DataFrame(columns=self.columns, index=index)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extract Land/Ocean data from Excel.')
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

    r = WorldDataReader(key=args.key, outputdir=args.outputdir)
    r.read_world_data_xls()
    r.make_csvs()
