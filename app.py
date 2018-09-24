"""Flask App for http://codeearth.net."""

import io
import os

import advanced_controls
from flask import Flask, request, render_template, jsonify
import pandas as pd
from model import firstcost
from model import unitadoption
import werkzeug.exceptions

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
    js = request.get_json(force=True)
    pprint.pprint(js)
    ref_sol_funits = to_csv(js, 'ref_sol_funits', app.logger)
    pds_sol_funits = to_csv(js, 'pds_sol_funits', app.logger)
    aau_sol_funits = js['aau_sol_funits']
    life_cap_sol_funits = js['life_cap_sol_funits']
    aau_conv_funits = js['aau_conv_funits']
    life_cap_conv_funits = js['life_cap_conv_funits']
    ref_tam_funits = to_csv(js, 'ref_tam_funits', app.logger)
    pds_tam_funits = to_csv(js, 'pds_tam_funits', app.logger)

    ua = unitadoption.UnitAdoption()
    results = dict()
    results['na_funits'] = ua.na_funits(
        ref_sol_funits, pds_sol_funits).to_csv()
    results['pds_sol_cum_iunits'] = ua.sol_cum_iunits(
        pds_sol_funits, aau_sol_funits).to_csv()
    results['ref_sol_cum_iunits'] = ua.sol_cum_iunits(
        ref_sol_funits, aau_sol_funits).to_csv()
    results['life_rep_sol_years'] = ua.life_rep_years(
        life_cap_sol_funits, aau_sol_funits)
    results['life_rep_conv_years'] = ua.life_rep_years(
        life_cap_conv_funits, aau_conv_funits)
    return jsonify(results)


def pdSeriesYears(js, name):
  arr = js.get(name, [])
  year_var_name = name + '_year'
  start = js.get(year_var_name, 0)
  stop = start + len(arr)
  return pd.Series(arr, index=pd.RangeIndex(start=start, stop=stop))


@app.route("/firstcost", methods=['POST'])
def firstCost():
    '''Implements First Cost tab from Excel model implementation.'''
    js = request.get_json(force=True)
    ac_rq = to_advanced_controls(js, app.logger)
    fc_rq = js.get('first_cost', {})
    ua_rq = js.get('unit_adoption', {})
    fc = firstcost.FirstCost(
        ac=ac_rq,
        pds_learning_increase_mult=fc_rq.get('pds_learning_increase_mult', 0),
        ref_learning_increase_mult=fc_rq.get('ref_learning_increase_mult', 0),
        conv_learning_increase_mult=fc_rq.get('conv_learning_increase_mult', 0))

    soln_pds_tot_iunits_req = pdSeriesYears(ua_rq, 'soln_pds_tot_iunits_req')
    conv_ref_tot_iunits_req = pdSeriesYears(ua_rq, 'conv_ref_tot_iunits_req')
    soln_ref_tot_iunits_req = pdSeriesYears(ua_rq, 'soln_ref_tot_iunits_req')
    soln_pds_new_iunits_req = pdSeriesYears(ua_rq, 'soln_pds_new_iunits_req')
    soln_ref_new_iunits_req = pdSeriesYears(ua_rq, 'soln_ref_new_iunits_req')
    conv_ref_new_iunits_req = pdSeriesYears(ua_rq, 'conv_ref_new_iunits_req')

    results = dict()
    soln_pds_install_cost_per_iunit = fc.soln_pds_install_cost_per_iunit(
        soln_pds_tot_iunits_req=soln_pds_tot_iunits_req,
        conv_ref_tot_iunits_req=conv_ref_tot_iunits_req)
    results['soln_pds_install_cost_per_iunit'] = soln_pds_install_cost_per_iunit.tolist()
    conv_ref_install_cost_per_iunit = fc.conv_ref_install_cost_per_iunit(
        conv_ref_tot_iunits_req=conv_ref_tot_iunits_req)
    results['conv_ref_install_cost_per_iunit'] = conv_ref_install_cost_per_iunit.tolist()
    soln_ref_install_cost_per_iunit = fc.soln_ref_install_cost_per_iunit(
        soln_ref_tot_iunits_req, conv_ref_tot_iunits_req)
    results['soln_ref_install_cost_per_iunit'] = soln_ref_install_cost_per_iunit.tolist()
    soln_pds_annual_world_first_cost = fc.soln_pds_annual_world_first_cost(
        soln_pds_new_iunits_req=soln_pds_new_iunits_req,
        soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit)
    results['soln_pds_annual_world_first_cost'] = fc.soln_pds_annual_world_first_cost(
        soln_pds_new_iunits_req, soln_pds_install_cost_per_iunit).tolist()
    results['soln_pds_cumulative_install'] = fc.soln_pds_cumulative_install(
        soln_pds_annual_world_first_cost).tolist()
    soln_ref_annual_world_first_cost = fc.soln_ref_annual_world_first_cost(
        soln_ref_new_iunits_req, soln_ref_install_cost_per_iunit)
    results['soln_ref_annual_world_first_cost'] = soln_ref_annual_world_first_cost.tolist()
    conv_ref_annual_world_first_cost = fc.conv_ref_annual_world_first_cost(
        conv_ref_new_iunits_req, conv_ref_install_cost_per_iunit)
    results['conv_ref_annual_world_first_cost'] = conv_ref_annual_world_first_cost.tolist()
    results['ref_cumulative_install'] = fc.ref_cumulative_install(
        conv_ref_annual_world_first_cost, soln_ref_annual_world_first_cost).tolist()

    return jsonify(results)


def to_csv(data, key, logger):
    '''
    Helper function to load CSV from input data dictionary.
    '''
    csvstr = data[key]
    csvio = io.StringIO(csvstr)
    csv = pd.read_csv(csvio)
    logger.info("%s parsed as:\n%s", key, csv)
    return csv


def to_advanced_controls(data, logger):
    '''Helper function to extract advanced controls fields.'''
    if not data.get('advanced_controls'):
        raise werkzeug.exceptions.BadRequest('advanced_controls missing')
    ac = data['advanced_controls']
    return advanced_controls.AdvancedControls(**ac)


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
