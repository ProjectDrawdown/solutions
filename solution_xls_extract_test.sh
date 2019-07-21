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

tmpdir=$(mktemp -d soln_xls.XXXXXX)
PYTHONPATH=.:${PYTHONPATH} ./tools/solution_xls_extract.py --excelfile=./tools/tests/solution_xls_extract_RRS_test_A.xlsm --outputdir=${tmpdir}
output=$(cat ${tmpdir}/__init__.py)
ad_data=$(cat ${tmpdir}/ad/ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv)
ac_files=$(cat ${tmpdir}/ac/*)

# Check infer class name
require "$output" "class Scenario" && \
# Check scenario parsing
require "${output}${ac_files}" "PDS-16p2050- Optimum (Book Ed.1)" && \
# Check Solution name extraction
require "$output" "name = 'Utility Scale Solar PV'" && \
# Check Helper Tables extraction
require "$output" "helpertables.HelperTables" && \
# Check First Cost extraction
require "$output" "ref_learning_increase_mult=2, conv_learning_increase_mult=2," && \
# Check Adoption Data extraction
require "$output" "'Based on: IEA ETP 2016 6DS'" && \
# Check TAM Data extraction
require "$output" "'3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly'," && \
# Adoption Data CSV files
require "$ad_data" 3598.7298966826534 && \
# Check that 0.0 is converted to NaN (i.e. empty)
require "$ad_data" "2012,58.199999999999996,,,,,,,,," && \
true

if [ $? -ne 0 ]; then
    rc=1
fi

rm -rf ${tmpdir}
trap 'kill $(jobs -pr) >/dev/null 2>&1' SIGINT SIGTERM EXIT

exit $rc
