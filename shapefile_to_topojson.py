import sys
import os
import geopandas
import topojson

help_message = """
Usage:
python shapefile_to_topojson.py /path/to/shapefile.zip [/path/to/output.json]
    produces TopoJSON file from shapefile ZIP. If output path is not provided,
    it will use name of .zip file to create output file in the python working dir.
"""


def convert_to_json(shapefile_zip_path: str) -> str:
    """
    Reads ESRI files from ZIP archive and converts them into a single TopoJSON file
    @param shapefile_zip_path (str): path to ESRI zip file

    @return str: TopoJSON string
    """
    esri = geopandas.read_file(f"zip://{shapefile_zip_path}")
    tj = topojson.Topology(esri, prequantize=False, topology=True)

    # Note: tj.to_json("path") is not used here because it outputs json file with single quotes.
    return tj.to_json()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(help_message)

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

        topojson = convert_to_json(shapefile_zip_path)
        with open(output_json_path, "w") as f:
            f.write(topojson)

        print(f"TopoJSON saved to {output_json_path}")
