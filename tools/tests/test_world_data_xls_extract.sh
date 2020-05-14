#!/bin/bash

require() {
  output="$1"
  expected="$2"
  formatted_output=$(echo "$output" | tr -d '[:space:]' | tr -d '"' )
  formatted_expected=$(echo "$expected" | tr -d '[:space:]' | tr -d '"' )
  if [[ "${formatted_output}" =~ "${formatted_expected}" ]]; then
      return 0
  fi
  echo "$(echo "$output" | cut -c1-40) does not contain $(echo "$expected" | cut -c1-40)"
  return 1
}

toolsdir=$1

tmpdir=$(mktemp -d soln_xls.XXXXXX)
PYTHONPATH=.:${PYTHONPATH} python ${toolsdir}/world_data_xls_extract.py --outputdir=${tmpdir}

test -f ${tmpdir}/Boreal_Humid.csv || exit 1
test -f ${tmpdir}/Global_Arctic.csv || exit 1
test -f ${tmpdir}/Temperate_Humid.csv || exit 1
test -f ${tmpdir}/Tropical_Humid.csv || exit 1
test -f ${tmpdir}/Boreal_Semi_Arid.csv || exit 1
test -f ${tmpdir}/Global_Arid.csv || exit 1
test -f ${tmpdir}/Temperate_Semi_Arid.csv || exit 1
test -f ${tmpdir}/Tropical_Semi_Arid.csv || exit 1

require "$(cat ${tmpdir}/Boreal_Humid.csv)" "AEZ1: Forest, prime, minimal" && \
require "$(cat ${tmpdir}/Global_Arctic.csv)" "AEZ2: Forest, good, minimal" && \
require "$(cat ${tmpdir}/Temperate_Humid.csv)" "AEZ3: Forest, good, moderate" && \
require "$(cat ${tmpdir}/Tropical_Humid.csv)" "AEZ4: Forest, good, steep" && \
require "$(cat ${tmpdir}/Boreal_Semi_Arid.csv)" "AEZ5: Forest, marginal, minimal" && \
require "$(cat ${tmpdir}/Global_Arid.csv)" "AEZ6: Forest, marginal, moderate" && \
require "$(cat ${tmpdir}/Temperate_Semi_Arid.csv)" "AEZ7: Forest, marginal, steep" && \
require "$(cat ${tmpdir}/Tropical_Semi_Arid.csv)" "AEZ8: Grassland, prime, minimal" && \
true

if [ $? -ne 0 ]; then
    rc=1
fi
rm -rf ${tmpdir}

trap 'kill $(jobs -pr) >/dev/null 2>&1' SIGINT SIGTERM EXIT

exit $rc
