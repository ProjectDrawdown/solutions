import pandas as pd
import pathlib

LAND_CSV_PATH = pathlib.Path(__file__).parents[1].joinpath('data', 'land')
pd.set_option('display.expand_frame_repr', False)


class AEZ:
    """ AEZ Data module """
    def __init__(self, solution):
        self.solution = solution
        self._populate_solution_la()

    def _populate_solution_la(self):
        df = pd.read_csv(LAND_CSV_PATH.joinpath('aez', 'solution_la_template.csv'), index_col='Thermal Moisture Regime')
        df = df.fillna(0)
        for tmr in df.index:
            tmr_path = LAND_CSV_PATH.joinpath('allocation', tmr.replace('/', '_'))
            for col in df:
                if col.startswith('AEZ29'):  # this zone is not included in land allocation
                    continue
                aez_path = tmr_path.joinpath(col +'.csv')
                la_df = pd.read_csv(aez_path, index_col=0)
                total_perc_allocated = la_df.loc[self.solution]['Total % allocated']
                if total_perc_allocated > 0:
                    df.at[tmr, col] = total_perc_allocated
        self.perc_la_df = df


if __name__ == '__main__':
    aez = AEZ('Tropical Forest Restoration')
