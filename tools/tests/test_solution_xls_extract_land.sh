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
PYTHONPATH=.:${PYTHONPATH} ${toolsdir}/solution_xls_extract.py --excelfile=${toolsdir}/tests/solution_xls_extract_LAND_test_A.xlsm --outputdir=${tmpdir}
output=$(cat ${tmpdir}/__init__.py)
ac_files=$(cat ${tmpdir}/ac/*)

# Check infer class name
require "$output" "class Scenario" && \
# Check scenario parsing
require "${output}${ac_files}" "PDS-84p2050-Plausible-PDScustom-low-Bookedition1" && \
# Check Solution name extraction
require "$output" "name = 'Afforestation'" && \
# Check Helper Tables extraction
require "$output" "helpertables.HelperTables" && \
# Check First Cost extraction
require "$output" "ref_learning_increase_mult=2, conv_learning_increase_mult=2," && \
require "$output" "fc_convert_iunit_factor=land.MHA_TO_HA" && \
# Check Adoption Data extraction
require "$output" "Fully Customized PDS" && \
require "$output" "ca_pds_data_sources = [" && \
# Check TLA extraction
require "$output" "tla.tla_per_region(self.ae.get_land_distribution())" && \
true

rm -rf ${tmpdir}


tmpdir=$(mktemp -d soln_xls.XXXXXX)
PYTHONPATH=.:${PYTHONPATH} ${toolsdir}/solution_xls_extract.py --excelfile=${toolsdir}/tests/solution_xls_extract_LAND_test_B.xlsm --outputdir=${tmpdir}
output=$(cat ${tmpdir}/__init__.py)
ac_files=$(cat ${tmpdir}/ac/*)

# Check infer class name
require "$output" "class Scenario" && \
# Check Custom TLA is handled
require "${output}" "tla.CustomTLA" && \
true

rm -rf ${tmpdir}


trap 'kill $(jobs -pr) >/dev/null 2>&1' SIGINT SIGTERM EXIT

exit $rc
