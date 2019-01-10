#!/bin/sh

FLASK_APP=app.py FLASK_ENV=development flask run >/dev/null 2>&1 &

# wait until flask is ready to serve requests
sleep 0.25
for i in {1..5}
do
    url='http://127.0.0.1:5000/'
    json='Content-Type: application/json'
    curl --silent -H "$json" "$url" >/dev/null 2>&1 && break
    sleep 1
done

rc=0

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

input='{}'
url='http://127.0.0.1:5000/solarpvutil'
output=$(curl --silent -H 'Content-Type: application/json' --data "$input" "$url") 

require "$output" '"tam_data":{' && \
require "$output" '"adoption_data":{' && \
require "$output" '"helper_tables":{' && \
require "$output" '"emissions_factors":{' && \
require "$output" '"unit_adoption":{' && \
require "$output" '"first_cost":{' && \
require "$output" '"operating_cost":{' && \
require "$output" '"ch4_calcs":{' && \
require "$output" '"co2_calcs":{' && \
true

if [ $? -ne 0 ]; then
    rc=1
fi


trap 'kill $(jobs -pr) >/dev/null 2>&1' SIGINT SIGTERM EXIT

exit $rc
