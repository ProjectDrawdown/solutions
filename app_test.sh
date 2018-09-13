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


trap 'kill $(jobs -pr)' SIGINT SIGTERM EXIT
