from flask import Flask, request
import csv
import io
import pprint
import pandas as pd
from model import unitadoption

app = Flask(__name__)


def to_csv(csvstr):
    csvio = io.StringIO(csvstr)
    return pd.read_csv(csvio)


@app.route("/unitadoption", methods=['POST'])
def unitAdoption():
    ref_sol_funits = to_csv(request.form['ref'])
    pds_sol_funits = to_csv(request.form['pds'])
    app.logger.info("ref parsed as:\n%s", ref_sol_funits)
    app.logger.info("pds parsed as:\n%s", pds_sol_funits)

    ua = unitadoption.UnitAdoption()
    return ua.na_funits(ref_sol_funits, pds_sol_funits).to_csv()
