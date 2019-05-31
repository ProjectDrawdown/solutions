#!/bin/bash

# To be able to process the source GeoJSON files, you must:
# npm install -g topojson


# ==============================================
# world_topo_sans_antartica_with_dd_regions.json
# ==============================================

# https://medium.com/@mbostock/command-line-cartography-part-3-1158e4c55a1e
# was very helpful in developing this series of steps.
#
# source file from
# https://raw.githubusercontent.com/deldersveld/topojson/master/world-countries.json
#
# toposimplify -s command reduces the level of detail of the topology,
# to reduce the file size for the small view we're going to use.
# The -f argument tells it to remove small, detached rings (like small islands).
# We do this in the lowres file to save space, though we leave the islands in place
# in the higher res file.
#
# region_annotate.py annotates each country with its Drawdown region.
#
# topomerge d.dd_region combines countries according to the Drawdown region
#
# topomerge -f 'false' removes the original country boundaries, leaving only
# the drawdown regions.
#
# the second toposimplify removes the now unreferenced arcs which had
# been part of the country boundaries.

toposimplify -s 0.0005 -f world-countries.json |\
	python region_annotate.py |\
	topomerge areas=countries1 -k "d.dd_region" |\
	topomerge -f 'false' countries1=countries1 |\
	toposimplify -f > world_topo_lowres.json

toposimplify -s 0.000001 world-countries-sans-antarctica.json |\
	python region_annotate.py |\
	topomerge areas=countries1 -k "d.dd_region" |\
	topomerge -f 'false' countries1=countries1 |\
	toposimplify > world_topo_sans_antartica_highres.json


# ==============================================
# world_topo_with_aez.json
# ==============================================

# source file from
# https://github.com/JRLamontagne/Factorial_SSP-SPA_Exploration/blob/8f9277398e7419cc97a28cd69e45b2c5c6250c68/data/aez-w-greenland.geojson
#
# Converted to TopoJSON using https://mapshaper.org, in aez-w-greenland.json

toposimplify -p 0.75 -f aez-w-greenland.json |\
	topomerge aez=aez-w-greenland -k "d.properties.AEZ" |\
	python3 -m json.tool > world_topo_with_aez.json
