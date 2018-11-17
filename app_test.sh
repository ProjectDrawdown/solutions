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

input=$(cat app_test.firstcost_req)
url='http://127.0.0.1:5000/firstcost'
output=$(curl --silent -H 'Content-Type: application/json' --data "$input" "$url") 

require "$output" '"soln_pds_install_cost_per_iunit": [["Year", "World"],"' && \
require "$output" '"conv_ref_install_cost_per_iunit": [["Year", "World"],' && \
require "$output" '"soln_ref_install_cost_per_iunit": [["Year", "World"],' && \
require "$output" '"soln_pds_annual_world_first_cost": [["Year", "World"],' && \
require "$output" '"soln_pds_cumulative_install": [["Year", "World"],' && \
require "$output" '"soln_ref_annual_world_first_cost": [["Year", "World"],' && \
require "$output" '"conv_ref_annual_world_first_cost": [["Year", "World"],' && \
require "$output" '"ref_cumulative_install": [["Year", "World"],' && \
true

if [ $? -ne 0 ]; then
    rc=1
fi

input=$(cat app_test.unitadoption3_req)
url='http://127.0.0.1:5000/unitadoption.v3'
output=$(curl --silent -H 'Content-Type: application/json' --data "$input" "$url") 

require "$output" '"ref_population": [["Year",' && \
require "$output" '"ref_gdp": [["Year",' && \
require "$output" '"ref_gdp_per_capita": [["Year",' && \
require "$output" '"ref_tam_per_capita": [["Year",' && \
require "$output" '"ref_tam_per_gdp_per_capita": [["Year",' && \
require "$output" '"ref_tam_growth": [["Year",' && \
require "$output" '"pds_population": [["Year",' && \
require "$output" '"pds_gdp": [["Year",' && \
require "$output" '"pds_gdp_per_capita": [["Year",' && \
require "$output" '"pds_tam_per_capita": [["Year",' && \
require "$output" '"pds_tam_per_gdp_per_capita": [["Year",' && \
require "$output" '"pds_tam_growth": [["Year",' && \
require "$output" '"soln_pds_cumulative_funits": [["Year",' && \
require "$output" '"soln_ref_cumulative_funits": [["Year",' && \
require "$output" '"soln_net_annual_funits_adopted": [["Year",' && \
require "$output" '"soln_pds_tot_iunits_reqd": [["Year",' && \
require "$output" '"soln_pds_new_iunits_reqd": [["Year",' && \
require "$output" '"soln_pds_big4_iunits_reqd": [["Year",' && \
require "$output" '"soln_ref_tot_iunits_reqd": [["Year",' && \
require "$output" '"soln_ref_new_iunits_reqd": [["Year",' && \
require "$output" '"conv_ref_tot_iunits_reqd": [["Year",' && \
require "$output" '"conv_ref_annual_tot_iunits": [["Year",' && \
require "$output" '"conv_ref_new_iunits_reqd": [["Year",' && \
require "$output" '"soln_pds_net_grid_electricity_units_saved": [["Year",' && \
require "$output" '"soln_pds_net_grid_electricity_units_used": [["Year",' && \
require "$output" '"soln_pds_fuel_units_avoided": [["Year",' && \
require "$output" '"soln_pds_direct_co2_emissions_saved": [["Year",' && \
require "$output" '"soln_pds_direct_ch4_co2_emissions_saved": [["Year",' && \
require "$output" '"soln_pds_direct_n2o_co2_emissions_saved": [["Year",' && \
true

if [ $? -ne 0 ]; then
    rc=1
fi

input=$(cat app_test.operatingcost_req)
url='http://127.0.0.1:5000/operatingcost'
output=$(curl --silent -H 'Content-Type: application/json' --data "$input" "$url") 

require "$output" '"soln_new_funits_per_year": [["Year",' && \
require "$output" '"soln_new_funits_per_year_world": [["Year",' && \
require "$output" '"soln_pds_net_annual_iunits_reqd": [["Year",' && \
require "$output" '"soln_pds_new_annual_iunits_reqd": [["Year",' && \
require "$output" '"soln_pds_annual_breakout": [["Year",' && \
require "$output" '"conv_ref_new_annual_iunits_reqd": [["Year",' && \
require "$output" '"conv_ref_new_annual_iunits_reqd": [["Year",' && \
require "$output" '"lifetime_cost_forecast": [["Year",' && \
require "$output" '"soln_pds_annual_operating_cost": [["Year",' && \
require "$output" '"soln_pds_cumulative_operating_cost": [["Year",' && \
require "$output" '"soln_vs_conv_single_iunit_cashflow": [["Year",' && \
require "$output" '"soln_vs_conv_single_iunit_npv": [["Year",' && \
require "$output" '"soln_vs_conv_single_iunit_payback": [["Year",' && \
require "$output" '"soln_vs_conv_single_iunit_npv": [["Year",' && \
require "$output" '"soln_only_single_iunit_cashflow": [["Year",' && \
require "$output" '"soln_only_single_iunit_npv": [["Year",' && \
require "$output" '"soln_only_single_iunit_cashflow": [["Year",' && \
require "$output" '"soln_only_single_iunit_cashflow": [["Year",' && \
true

if [ $? -ne 0 ]; then
    rc=1
fi


input='{"advanced_controls":{"emissions_grid_source":"ipcc_only","emissions_grid_range":"high"}}'
url='http://127.0.0.1:5000/emissionsfactors'
output=$(curl --silent -H 'Content-Type: application/json' --data "$input" "$url") 

require "$output" '"conv_ref_grid_CO2eq_per_KWh": [["Year",' && \
require "$output" '"conv_ref_grid_CO2_per_KWh": [["Year",' && \
true


input='{"advanced_controls":{"soln_pds_adoption_prognostication_source":"Based on: Greenpeace (2015) Advanced Energy Revolution"},"adoption_data":{"sourcename":"Based on: Greenpeace (2015) Advanced Energy Revolution","low_sd":1,"high_sd":1,"growth_choice":"Medium"}}'
url='http://127.0.0.1:5000/adoptiondata'
output=$(curl --silent -H 'Content-Type: application/json' --data "$input" "$url") 

require "$output" '"adoption": [["Year",' && \
require "$output" '"adoption_min_max_sd": [["Year",' && \
require "$output" '"adoption_low_med_high": [["Year",' && \
require "$output" '"linear_growth": [["Year",' && \
require "$output" '"poly_degree2_growth": [["Year",' && \
require "$output" '"poly_degree3_growth": [["Year",' && \
require "$output" '"exponential_growth": [["Year",' && \
true

if [ $? -ne 0 ]; then
    rc=1
fi


input=$(cat app_test.co2calcs_req)
url='http://127.0.0.1:5000/co2calcs'
output=$(curl --silent -H 'Content-Type: application/json' --data "$input" "$url") 

require "$output" '"co2_reduced_grid_emissions": [["Year",' && \
require "$output" '"co2_replaced_grid_emissions": [["Year",' && \
require "$output" '"co2_increased_grid_usage_emissions": [["Year",' && \
require "$output" '"co2eq_reduced_grid_emissions": [["Year",' && \
require "$output" '"co2eq_replaced_grid_emissions": [["Year",' && \
require "$output" '"co2eq_increased_grid_usage_emissions": [["Year",' && \
require "$output" '"co2eq_direct_reduced_emissions": [["Year",' && \
require "$output" '"co2eq_reduced_fuel_emissions": [["Year",' && \
require "$output" '"co2eq_net_indirect_emissions": [["Year",' && \
require "$output" '"co2_mmt_reduced": [["Year",' && \
require "$output" '"co2eq_mmt_reduced": [["Year",' && \
require "$output" '"co2_ppm_calculator": [["Year",' && \
require "$output" '"co2eq_ppm_calculator": [["Year",' && \
require "$output" '"ch4_tons_reduced": [["Year",' && \
require "$output" '"ch4_ppb_calculator": [["Year",' && \
true

if [ $? -ne 0 ]; then
    rc=1
fi


trap 'kill $(jobs -pr) >/dev/null 2>&1' SIGINT SIGTERM EXIT

exit $rc
