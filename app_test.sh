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

input='{"advanced_controls":{"pds_2014_cost":1444.93954421485,"conv_2014_cost":2010.03170851964,"pds_first_cost_efficiency_rate":0.196222222222222,"pds_first_cost_below_conv":true,"conv_first_cost_efficiency_rate":0.02},"first_cost":{"pds_learning_increase_mult":2,"conv_learning_increase_mult":2},"unit_adoption":{"pds_tot_soln_iunits_req":[0.061158144891382,0.0956963287565992,0.147709178675075,0.208131559430844,0.276585853638905],"ref_tot_conv_iunits_req":[4.53535289538464,4.8796378165883,5.05302431141252,5.2263750432106,5.39969647677689]}}'
url='http://127.0.0.1:5000/firstcost'
output=$(curl --silent -H 'Content-Type: application/json' --data $input $url | tr -d '[:space:]') 
expected=$(echo '{"conv_install_cost_per_iunit":[0.0,2005749716919.2083,2003709559856.4333,2001740610594.36,1999838071911.3604],"pds_install_cost_per_iunit":[1663888168616.1255,1444939544214.8499,1260211854559.479,1131125771261.7144,1034176540754.2719]}' | tr -d '[:space:]')

if [ "${output}" != "${expected}" ]; then
    echo "${output} != ${expected}"
    rc=1
fi


trap 'kill $(jobs -pr)' SIGINT SIGTERM EXIT
