# pylint: skip-file

"""
This module converts Natural Earth's ne_10m_admin_0_countries.zip shapefile to
GeoJSON. Individual countries are mapped to Drawdown regions according to
https://github.com/ProjectDrawdown/spatial-aez/blob/master/admin_names.py
"""

import sys
import os
import admin_names
import geopandas

help_message = """
Usage:
python ne_countries_to_drawdown_regions_geojson.py /path/to/shapefile.zip [/path/to/output.json]
    produces GeoJSON file from shapefile ZIP. If output path is not provided,
    it will use name of .zip file to create JSON output file in the python working dir.
"""

# List of countries and territories which should NOT be mapped to regions
SPECIAL_COUNTRIES = [
    'China',
    'India',
    'EU',
    'United States of America'
]


def map_ne_admin_to_drawdown_regions(row):
    """
    Maps Natural Earth's ADMIN name to a list of Drawdown regions
    """
    ne_name = row['ADMIN']
    dd_name = admin_names.lookup(ne_name)

    if dd_name in SPECIAL_COUNTRIES:
        return [dd_name]
    else:
        dd_region = admin_names.region_mapping.get(dd_name)
        if dd_region is None:
            return None
        elif isinstance(dd_region, list):
            return dd_region
        else:
            raise ValueError(f"List expected, but got {dd_region}")


def map_ne_admin_counties_to_drawdown_regions(shapefile_zip_path):
    """
    This function takes ne_10m_admin_0_countries.zip shapefile, maps individual
    countries to Drawdown regions and outputs GeoJSON which only includes
    Drawdown regions. Individual countries' information is removed.
    """
    dd_col_name = 'DRAWDOWN_REGION'
    esri = geopandas.read_file(f"zip://{shapefile_zip_path}")
    esri[dd_col_name] = esri.apply(
        lambda row: map_ne_admin_to_drawdown_regions(row), axis=1)

    # Expanding list of Drawdown regions into separate rows
    expanded_rows = []
    def list_to_rows(row):
        values = row[dd_col_name]
        if isinstance(values, list):  # Can be None
            for v in values:
                new_row = row.to_dict()
                new_row[dd_col_name] = v
                expanded_rows.append(new_row)

    esri.apply(list_to_rows, axis=1)
    expanded_esri = geopandas.GeoDataFrame(expanded_rows)

    all_rows_region_only = expanded_esri[[dd_col_name, 'geometry']]
    region_only = all_rows_region_only.dissolve(dd_col_name)
    return region_only


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(help_message)
        sys.exit(1)

    shapefile_zip_path = sys.argv[1]
    if not os.path.exists(shapefile_zip_path):
        print(f"File not found: {shapefile_zip_path}")
        sys.exit(1)
    else:
        if len(sys.argv) == 3:
            output_json_path = sys.argv[2]
        else:
            shapefile_zip_name = shapefile_zip_path.rsplit("/", 1)[1]
            shapefile_base_name = shapefile_zip_name.rsplit(".", 1)[0]
            output_json_path = f"./{shapefile_base_name}.json"

        region_only = map_ne_admin_counties_to_drawdown_regions(shapefile_zip_path)

        region_only.to_file(output_json_path, driver='GeoJSON')

        print(f"GeoJSON saved to {output_json_path}")
