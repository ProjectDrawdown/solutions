from flask import Flask, request
import csv
import io
import pprint
import pandas as pd
app = Flask(__name__)


def fromCSV(rawcsv):
    data = []
    lines = rawcsv.split("@")
    reader = csv.reader(lines, delimiter=',')
    for row in reader:
        data.append(row)
    return data


@app.route("/unitadoption")
def unitAdoption():
    pds = fromCSV(request.args.get('pds'))
    pprint.pprint(pds)
    ref = fromCSV(request.args.get('ref'))
    pprint.pprint(ref)
    output = io.StringIO()

    writer = csv.writer(output, delimiter=",")
    if len(pds) != len(ref):
        return "PDS and REF CSV length does not match", 400
    for row in range(len(pds)):
        outrow = []
        if len(pds[row]) != len(ref[row]):
            return "PDS and REF CSV row length does not match", 400
        for field in range(len(pds[row])):
            outrow.append(float(pds[row][field]) - float(ref[row][field]))
        writer.writerow(outrow)
    return output.getvalue()


@app.route("/unitadoptionjson", methods=['POST'])
def unitAdoptionJson():
    content = request.json
    pds = pd.DataFrame.from_records(content['pds'])
    ref = pd.DataFrame.from_records(content['ref'])
    return pprint.pformat(pds - ref)
