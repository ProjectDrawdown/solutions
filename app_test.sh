#!/bin/sh

FLASK_APP=app.py FLASK_ENV=development flask run >/dev/null 2>&1 &

# wait until flask is ready to serve requests
sleep 0.25
for i in {1..5}
do
    url='http://127.0.0.1:5000/'
    json='Content-Type: application/json'
    curl --silent -H $json $url >/dev/null 2>&1 && break
    sleep 1
done

rc=0

input='{"pds":"a,b,c,d\n2,2,5,4\n2,3,4,10","ref":"a,b,c,d\n1,2,3,4\n2,2,4,4"}'
url='http://127.0.0.1:5000/unitadoption'
output=$(curl --silent -H 'Content-Type: application/json' --data $input $url | tr -d '[:space:]') 
expected=$(echo "a,b,c,d\r\n1,0,2,0\r\n0,1,0,6\r\n" | tr -d '[:space:]')

if [ "${output}" != "${expected}" ]; then
    echo "${output} != ${expected}"
    rc=1
fi

input='{"pds":"e,f,g,h\n0,0,0,0\n1,2,3,4","ref":"e,f,g,h\n1,2,3,4\n0,0,0,0"}'
url='http://127.0.0.1:5000/unitadoption'
output=$(curl --silent -H 'Content-Type: application/json' --data $input $url | tr -d '[:space:]') 
expected=$(echo "e,f,g,h\r\n-1,-2,-3,-4\r\n1,2,3,4\r\n" | tr -d '[:space:]')

if [ "${output}" != "${expected}" ]; then
    echo "${output} != ${expected}"
    rc=1
fi

input='{"advanced_controls":{"pds_2014_cost":1444.93954421485,"ref_2014_cost":1444.93954421485,"conv_2014_cost":2010.03170851964,"soln_first_cost_efficiency_rate":0.196222222222222,"soln_first_cost_below_conv":true,"conv_first_cost_efficiency_rate":0.02},"first_cost":{"pds_learning_increase_mult":2,"ref_learning_increase_mult":2,"conv_learning_increase_mult":2},"unit_adoption":{"soln_pds_tot_iunits_req":[0.061158144891382,0.0956963287565992,0.147709178675075,0.208131559430844,0.276585853638905],"soln_pds_tot_iunits_req_year":2014,"conv_ref_tot_iunits_req":[4.53535289538464,4.8796378165883,5.05302431141252,5.2263750432106,5.39969647677689],"conv_ref_tot_iunits_req_year":2014,"soln_ref_tot_iunits_req":[0.061158144891382,0.0635681132081653,0.0659780815249495,0.0683880498417336,0.0707980181585176],"soln_ref_tot_iunits_req_year":2014,"soln_pds_new_iunits_req":[0.0345381838652173,0.0520128499184754,0.0604223807557696,0.0684542942080606],"soln_pds_new_iunits_req_year":2015,"soln_ref_new_iunits_req":[0.00240996831678339,0.00240996831678411,0.0024099683167841,0.0024099683167841],"soln_ref_new_iunits_req_year":2015,"conv_ref_new_iunits_req":[0.0119610746639919,0.0184667514288979,0.0215975517088693,0.0245877680921211],"conv_ref_new_iunits_req_year":2015}}'
url='http://127.0.0.1:5000/firstcost'
output=$(curl --silent -H 'Content-Type: application/json' --data $input $url) 
formatted_output=$(echo "$output" | tr -d '[:space:]')
expected=$(echo '{"conv_ref_annual_world_first_cost":[0.0,23990922121.35127,37002006377.57517,43232696345.0553,49171554733.951126],"conv_ref_install_cost_per_iunit":[2010031708519.6401,2005749716919.2083,2003709559856.4333,2001740610594.36,1999838071911.3604],"ref_cumulative_install":[0.0,27473180642.57649,67916850252.30461,114552519226.14102,167090108762.41345],"soln_pds_annual_world_first_cost":[0.0,49905587652.21577,65547210056.68573,68345312033.83885,70793825183.8673],"soln_pds_cumulative_install":[0.0,49905587652.21577,115452797708.90149,183798109742.74036,254591934926.60767],"soln_pds_install_cost_per_iunit":[1663888168616.1255,1444939544214.8499,1260211854559.479,1131125771261.7144,1034176540754.2719],"soln_ref_annual_world_first_cost":[0.0,3482258521.2252207,3441663232.1529527,3402972628.781113,3366034802.32131],"soln_ref_install_cost_per_iunit":[1462645781446.203,1444939544214.8499,1428094804476.7446,1412040401146.059,1396713300701.397]}' | tr -d '[:space:]')

if [ "${formatted_output}" != "${expected}" ]; then
    echo "${output} != ${expected}"
    rc=1
fi


trap 'kill $(jobs -pr)' SIGINT SIGTERM EXIT
