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

tmpdir=$(mktemp -t -d excel_fair.XXXXXX)
cd ${tmpdir}
PYTHONPATH=${topdir}:${PYTHONPATH} python ${toolsdir}/excel_fair_results.py --excelfile=${toolsdir}/tests/excel_fair_results_test.xlsx
outputTPDS1=$(cat excel_fair_results_test_Totals_PDS1.csv)
outputTPDS2=$(cat excel_fair_results_test_Totals_PDS2.csv)
outputTPDS3=$(cat excel_fair_results_test_Totals_PDS3.csv)
outputFPDS1=$(cat excel_fair_results_test_FaIR_PDS1.csv)
outputFPDS2=$(cat excel_fair_results_test_FaIR_PDS2.csv)
outputFPDS3=$(cat excel_fair_results_test_FaIR_PDS3.csv)

require "$outputTPDS1" "Year,Baseline,Total" && \
require "$outputTPDS2" "Year,Baseline,Total" && \
require "$outputTPDS3" "Year,Baseline,Total" && \
require "$outputTPDS1" "2015," && \
require "$outputTPDS2" "2015," && \
require "$outputTPDS3" "2015," && \
require "$outputTPDS1" "2060," && \
require "$outputTPDS2" "2060," && \
require "$outputTPDS3" "2060," && \
require "$outputFPDS1" "Year,Baseline,Total" && \
require "$outputFPDS2" "Year,Baseline,Total" && \
require "$outputFPDS3" "Year,Baseline,Total" && \
require "$outputFPDS1" "2015," && \
require "$outputFPDS2" "2015," && \
require "$outputFPDS3" "2015," && \
require "$outputFPDS1" "2060," && \
require "$outputFPDS2" "2060," && \
require "$outputFPDS3" "2060," && \
true

if [ $? -ne 0 ]; then
    rc=1
fi
rm -rf ${tmpdir}

trap 'kill $(jobs -pr) >/dev/null 2>&1' SIGINT SIGTERM EXIT

exit $rc
