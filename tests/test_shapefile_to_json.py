import os
import json
from shapefile_to_topojson import convert_to_json
from zipfile import ZipFile
from shapely import geometry
import geopandas


topojson_str = """
{
  "type": "Topology",
  "objects": {
    "data": {
      "geometries": [
        {
          "id": "0",
          "type": "Polygon",
          "properties": {
            "name": "abc"
          },
          "bbox": [
            0.0,
            0.0,
            1.0,
            1.0
          ],
          "arcs": [
            [
              -2,
              0
            ]
          ]
        },
        {
          "id": "1",
          "type": "Polygon",
          "properties": {
            "name": "def"
          },
          "bbox": [
            1.0,
            0.0,
            2.0,
            1.0
          ],
          "arcs": [
            [
              1,
              2
            ]
          ]
        }
      ],
      "type": "GeometryCollection"
    }
  },
  "bbox": [
    0.0,
    0.0,
    2.0,
    1.0
  ],
  "arcs": [
    [
      [
        1.0,
        0.0
      ],
      [
        0.0,
        0.0
      ],
      [
        0.0,
        1.0
      ],
      [
        1.0,
        1.0
      ]
    ],
    [
      [
        1.0,
        0.0
      ],
      [
        1.0,
        1.0
      ]
    ],
    [
      [
        1.0,
        1.0
      ],
      [
        2.0,
        1.0
      ],
      [
        2.0,
        0.0
      ],
      [
        1.0,
        0.0
      ]
    ]
  ]
}
"""


def test_shapefile_to_json():
    tmp_dir = os.getenv("TEMP_DIR")
    gdf = geopandas.GeoDataFrame({
        "name": ["abc", "def"],
        "geometry": [
            geometry.Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]),
            geometry.Polygon([[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]])
        ]
    })

    basename = "shapefile_to_json_test"
    tmp_basename = os.path.join(tmp_dir, basename)
    gdf.to_file(f"{tmp_basename}.shp")

    with ZipFile(f"{tmp_basename}.zip", "w") as testzip:
        testzip.write(f"{tmp_basename}.shp", arcname=f"{basename}.shp")
        testzip.write(f"{tmp_basename}.cpg", arcname=f"{basename}.cpg")
        testzip.write(f"{tmp_basename}.dbf", arcname=f"{basename}.dbf")
        testzip.write(f"{tmp_basename}.shx", arcname=f"{basename}.shx")

    topojson = convert_to_json(f"{tmp_basename}.zip")

    assert json.loads(topojson_str) == json.loads(topojson)
