from flask import Flask, request, render_template
import csv
import io
import os
import pprint
import pandas as pd
from model import unitadoption

app = Flask(__name__)


@app.route("/", methods=['GET'])
def home():
    '''Simple home page with links to documentation, license and source code'''
    # Allow overriding of repo URL in environment for people hosting a fork etc.
    repo = os.getenv('DRAWDOWN_REPO', "https://gitlab.com/codeearth/drawdown")
    return render_template('home.html', repo=repo)


@app.route("/unitadoption", methods=['POST'])
def unitAdoption():
    '''Initial version of the API - only implements the na_funits calculation.'''
    ref_sol_funits = to_csv(request.json, 'ref', app.logger)
    pds_sol_funits = to_csv(request.json, 'pds', app.logger)

    ua = unitadoption.UnitAdoption()
    return ua.na_funits(ref_sol_funits, pds_sol_funits).to_csv(index=False)


@app.route("/unitadoption.v2", methods=['POST'])
def unitAdoption2():
    '''Second version of the API - implements most of the unit adoption tab.'''
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


def to_csv(data, key, logger):
    '''
    Helper function to load CSV from input data dictionary.
    '''
    csvstr = data[key]
    csvio = io.StringIO(csvstr)
    csv = pd.read_csv(csvio)
    logger.info("%s parsed as:\n%s", key, csv)
    return csv


def shutdown():
    '''
    Shut down the server and exit.

    By default, no route to this function is installed. The production server does not
    have a URL exposed which will cause it to exit. Unit tests will add a route to
    the instance they are running within the test, allowing the server to be stopped.
    '''
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return 'Server shutting down...'


def get_app_for_tests():
    '''
    Return the app object for tests to use.
    '''
    return app
