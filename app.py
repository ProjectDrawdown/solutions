from flask import Flask, request
import csv
import io
import pprint
import pandas as pd
from model import unitadoption

app = Flask(__name__)


def to_csv(data, key, logger):
    '''
    Helper function to load CSV from input data dictionary.
    '''
    csvstr = data[key]
    csvio = io.StringIO(csvstr)
    csv = pd.read_csv(csvio)
    logger.info("%s parsed as:\n%s", key, csv)
    return csv


@app.route("/unitadoption", methods=['POST'])
def unitAdoption():
    ref_sol_funits = to_csv(request.json, 'ref', app.logger)
    pds_sol_funits = to_csv(request.json, 'pds', app.logger)

    ua = unitadoption.UnitAdoption()
    return ua.na_funits(ref_sol_funits, pds_sol_funits).to_csv(index=False)


@app.route("/unitadoption.v2", methods=['POST'])
def unitAdoption2():
    json = request.json
    ref_sol_funits = to_csv(json, 'ref', app.logger)
    pds_sol_funits = to_csv(json, 'pds', app.logger)
    aau_sol_funits = to_csv(json, 'aau_sol_funits', app.logger)
    life_cap_sol_funits = to_csv(json, 'life_cap_sol_funits', app.logger)
    aau_conv_funits = to_csv(json, 'aau_conv_funits', app.logger)
    life_cap_conv_funits = to_csv(json, 'life_cap_conv_funits', app.logger)

    ua = unitadoption.UnitAdoption()
    results = dict()
    results['na_funits'] = ua.na_funits(
        ref_sol_funits, pds_sol_funits).to_csv()
    results['life_rep_sol_years'] = ua.life_rep_years(
        life_cap_sol_funits, aau_sol_funits).to_csv()
    results['life_rep_conv_years'] = ua.life_rep_years(
        life_cap_conv_funits, aau_conv_funits).to_csv()
    return results
