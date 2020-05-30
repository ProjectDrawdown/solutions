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
    os.chdir(tmp_dir)
    gdf = geopandas.GeoDataFrame({
        "name": ["abc", "def"],
        "geometry": [
            geometry.Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]),
            geometry.Polygon([[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]])
        ]
    })

    # basename = os.path.join(tmp_dir, "shapefile_to_json_test")
    basename = "shapefile_to_json_test"
    gdf.to_file(f"{basename}.shp")

    with ZipFile(f"{basename}.zip", "w") as testzip:
        testzip.write(f"{basename}.shp")
        testzip.write(f"{basename}.cpg")
        testzip.write(f"{basename}.dbf")
        testzip.write(f"{basename}.shx")

    topojson = convert_to_json(os.path.join(tmp_dir, f"{basename}.zip"))

    assert json.loads(topojson_str) == json.loads(topojson)
