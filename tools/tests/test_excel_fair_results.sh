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

topdir=$1
toolsdir=${topdir}/tools

tmpdir=$(mktemp -d -t excel_fair.XXXXXX)
cd ${tmpdir}
PYTHONPATH=${topdir}:${PYTHONPATH} python ${toolsdir}/excel_fair_results.py --excelfile=${toolsdir}/tests/excel_fair_results_test.xlsx
outputPDS1=$(cat excel_fair_results_test_Temperature_PDS1.csv)
outputPDS2=$(cat excel_fair_results_test_Temperature_PDS2.csv)
outputPDS3=$(cat excel_fair_results_test_Temperature_PDS3.csv)

require "$outputPDS1" "Baseline,Total" && \
require "$outputPDS2" "Baseline,Total" && \
require "$outputPDS3" "Baseline,Total" && \
require "$outputPDS1" "2015," && \
require "$outputPDS2" "2015," && \
require "$outputPDS3" "2015," && \
require "$outputPDS1" "2060," && \
require "$outputPDS2" "2060," && \
require "$outputPDS3" "2060," && \
true

if [ $? -ne 0 ]; then
    rc=1
fi

if [[ ! -f excel_fair_results_test_PDS1.mp4 || \
      ! -f excel_fair_results_test_PDS2.mp4 || \
      ! -f excel_fair_results_test_PDS3.mp4 ]]; then
    rc=1
fi

rm -rf ${tmpdir}

trap 'kill $(jobs -pr) >/dev/null 2>&1' SIGINT SIGTERM EXIT

exit $rc
