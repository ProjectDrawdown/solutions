#!/bin/sh

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

output=$(PYTHONPATH=.:${PYTHONPATH} ./tools/solution_xls_extract.py --excelfile=./tools/tests/solution_xls_extract_RRS_test_A.xlsm --classname=SolarPVUtil) 

require "$output" "PDS-16p2050- Optimum (Book Ed.1)" && \
# Check Solution name extraction
require "$output" "name = 'Utility Scale Solar PV'" && \
# Check Helper Tables extraction
require "$output" "[2050, 272.41409799108703, 97.40188603589483, 0.5231196255288569, 60.19814198613077," && \
# Check First Cost extraction
require "$output" "ref_learning_increase_mult=2, conv_learning_increase_mult=2," && \
# Check Adoption Data extraction
require "$output" "'Based on: IEA ETP 2016 6DS'" && \
# Check TAM Data extraction
require "$output" "'3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly', '3rd Poly'," && \
true

if [ $? -ne 0 ]; then
    rc=1
fi


trap 'kill $(jobs -pr) >/dev/null 2>&1' SIGINT SIGTERM EXIT

exit $rc
