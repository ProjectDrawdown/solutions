#!/bin/bash

# source file from
# https://raw.githubusercontent.com/deldersveld/topojson/master/world-countries-sans-antarctica.json
#
# toposimplify command reduces the level of detail of the topology,
# to reduce the file size for the small view we're going to use.
#
# drawdown_region_annotate.py annotates each country with its Drawdown region.
#
# topomerge combines countries according to the Drawdown region

toposimplify -p 1 -f world-countries-sans-antarctica.json |\
	python region_annotate.py |\
	topomerge regions=countries1 -k "d.dd_region" |\
	python3 -m json.tool > world_topo_sans_antartica_with_dd_regions.json

# This topomerge would drop some of the internal details and leave the
# external border. See
# https://medium.com/@mbostock/command-line-cartography-part-3-1158e4c55a1e
# for more details.
# topomerge --mesh -f 'a == b' regions=regions |\
# However doing this results in a bad artifact across Asia and Africa
# when rendered in Altair charts, presumably points are being combined
# erroneously.
