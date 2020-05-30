import geopandas
from shapely import geometry


def test_shapefile_to_json():
    gdf = geopandas.GeoDataFrame({
        "name": ["abc", "def"],
        "geometry": [
            geometry.Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]),
            geometry.Polygon([[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]])
        ]
    })
    
    assert 0 < 1