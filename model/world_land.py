from pathlib import Path
import pandas as pd
from model import dd

AEZS = dd.AEZS

# Two standard reductions of the 28 AEZs into smaller subsets
AEZ_LAND_COVER_MAP = {'Forest': AEZS[:7], 'Grassland': AEZS[7:14], 'Irrigated Cropland': AEZS[14:21],
                      'Rainfed Cropland': AEZS[21:28]}

AEZ_ALLOCATION_MAP = {
    'Non-Degraded Forest':    AEZS[:3],
    'Degraded Forest':        AEZS[3:7],
    'Non-Degraded Grassland': AEZS[7:10],
    'Degraded Grassland':     AEZS[10:14],
    'Non-Degraded Cropland':  AEZS[14:17] + AEZS[21:24],
    'Degraded Cropland':      AEZS[17:21] + AEZS[24:28],
}
"""The AEZ Allocation Map is the division of AEZs used during land allocation integration"""

datadir = Path(__file__).parents[1] / "data" / "land" / "world"

class World_TMR_AEZ_Map:
    def __init__(self, series_name="2020", map_data = None):
        """Construct the world map that maps Regions, Thermal Moisture Regimes and AEZ Regions onto land area (km^2).
        By default will read from the 2020 series.
        If map_data is provided, set to that data instead of reading from saved data.
        """ 
        self.series_name = series_name
        if map_data:
            self._map = map_data
        else:
            rootdir = datadir / self.series_name
            if not rootdir.is_dir():
                raise ValueError(f"World Map series {series_name} not found")
            dict_set = {}
            for filename in rootdir.glob('*.csv'):
                # We don't check here whether or not it is a 'legal' name
                # this may make it easier to expand/modify later, or it may lead to confusing errors...
                tmrname = filename.stem.replace('_','-')
                df = pd.read_csv(filename, encoding='utf-8')
                df = df.rename(columns={df.columns[0]: "Region"})
                df.set_index("Region", inplace=True)
                dict_set[tmrname] = df
                # in the stored files, the column header for "region" is sometimes missing

            self._map = pd.concat(dict_set.values(), keys=dict_set.keys())
            self._map.index.names = ["TMR", "Region"]

    def map(self):
        """Return the data.  Note the data is not protected; it is possible to update the map by altering it.
        The dataframe has a nested TMR, World region index and AEZ columns."""
        return self._map
    
    def store_map(self, series_name):
        """Store the current value. Will overwrite an existing series_name or add a new one."""
        raise NotImplemented()

    def reduce_columns(self, column_mapping):
        """Create a reduced map by summing columns in column mapping.  The column mapping should be like
        `AEZ_LAND_COVER_MAP`"""
        newcols = {}
        for (newcol, arange) in enumerate(column_mapping):
            newcols[newcol] = self._map[arange].sum(axis=1)
        return pd.concat(newcols.values(), axis=1, keys=newcols.keys())
