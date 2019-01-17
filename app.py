"""Flask App for http://codeearth.net."""

import io
import json
import os
import pathlib

from flask import Flask, request, render_template, jsonify, Response
import numpy as np
import pandas as pd
from model import adoptiondata
from model import advanced_controls
from model import co2calcs
from model import ch4calcs
from model import emissionsfactors
from model import firstcost
from model import helpertables
from model import interpolation
from model import operatingcost
from model import tam
from model import unitadoption
from solution import rrs
from solution import solarpvroof
from solution import solarpvutil
import werkzeug.exceptions


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # minify JSON


def json_dumps_default(obj):
  """Default function for json.dumps."""
  if isinstance(obj, np.integer):
    return int(obj)
  elif isinstance(obj, np.floating):
    return float(obj)
  elif isinstance(obj, np.ndarray):
    return obj.tolist()
  elif isinstance(obj, pd.DataFrame):
    return [[obj.index.name, *obj.columns.tolist()]] + obj.reset_index().values.tolist()
  elif isinstance(obj, pd.Series):
    return [[obj.index.name, obj.name]] + obj.reset_index().values.tolist()
  else:
    raise TypeError('Unable to JSON encode: ' + repr(obj))


@app.route("/", methods=['GET'])
def home():
    '''Simple home page with links to documentation, license and source code'''
    # Allow overriding of repo URL in environment for people hosting a fork etc.
    repo = os.getenv('DRAWDOWN_REPO', "https://gitlab.com/codeearth/drawdown")
    return render_template('home.html', repo=repo)


@app.route("/solarpvutil", methods=['POST'])
def solarPVUtil():
    """SolarPVUtil solution."""
    scenario = request.args.get('scenario', default=None)
    pv = solarpvutil.SolarPVUtil(scenario=scenario)

    results_str = json.dumps(pv.to_dict(), separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/solarpvroof", methods=['POST'])
def solarPVRoof():
    """SolarPVRoof solution."""
    scenario = request.args.get('scenario', default=None)
    pv = solarpvroof.SolarPVRoof(scenario=scenario)

    results_str = json.dumps(pv.to_dict(), separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


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
