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

solndir = pathlib.Path(__file__).parents[0].joinpath('solution', 'solarpvutil')
datadir = pathlib.Path(__file__).parents[0].joinpath('data')


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


@app.route("/firstcost", methods=['POST'])
def firstCost():
    '''Implements First Cost tab from Excel model implementation.'''
    js = request.get_json(force=True)
    ac_rq = to_advanced_controls(js, app.logger)
    fc_rq = js.get('first_cost', {})
    ua_rq = js.get('unit_adoption', {})

    funits = ua_rq.get('soln_pds_tot_iunits_reqd', [])
    soln_pds_tot_iunits_reqd = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    funits = ua_rq.get('conv_ref_tot_iunits_reqd', [])
    conv_ref_tot_iunits_reqd = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    funits = ua_rq.get('soln_ref_tot_iunits_reqd', [])
    soln_ref_tot_iunits_reqd = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    iunits = ua_rq.get('soln_pds_new_iunits_reqd', [])
    soln_pds_new_iunits_reqd = pd.DataFrame(iunits[1:], columns=iunits[0]).set_index('Year')
    iunits = ua_rq.get('soln_ref_new_iunits_reqd', [])
    soln_ref_new_iunits_reqd = pd.DataFrame(iunits[1:], columns=iunits[0]).set_index('Year')
    iunits = ua_rq.get('conv_ref_new_iunits_reqd', [])
    iunits = [x for x in iunits if x[0] != 'Lifetime']
    conv_ref_new_iunits_reqd = pd.DataFrame(iunits[1:], columns=iunits[0]).set_index('Year')

    fc = firstcost.FirstCost(ac=ac_rq,
        pds_learning_increase_mult=fc_rq.get('pds_learning_increase_mult', 0),
        ref_learning_increase_mult=fc_rq.get('ref_learning_increase_mult', 0),
        conv_learning_increase_mult=fc_rq.get('conv_learning_increase_mult', 0),
        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
        conv_ref_tot_iunits_reqd=conv_ref_tot_iunits_reqd,
        soln_pds_new_iunits_reqd=soln_pds_new_iunits_reqd,
        soln_ref_new_iunits_reqd=soln_ref_new_iunits_reqd,
        conv_ref_new_iunits_reqd=conv_ref_new_iunits_reqd)
    results_str = json.dumps(fc.to_dict(), separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/unitadoption.v3", methods=['POST'])
def unitAdoption3():
    """Third version of the API, switches to JSON with no CSV."""
    js = request.get_json(force=True)
    ac_rq = to_advanced_controls(js, app.logger)
    ua_rq = js.get('unit_adoption', {})
    tpr = ua_rq.get('ref_tam_per_region', [])
    ref_tam_per_region = pd.DataFrame(tpr[1:], columns=tpr[0]).set_index('Year')
    tpr = ua_rq.get('pds_tam_per_region', [])
    pds_tam_per_region = pd.DataFrame(tpr[1:], columns=tpr[0]).set_index('Year')
    funits = ua_rq.get('soln_pds_funits_adopted', [])
    soln_pds_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')
    funits = ua_rq.get('soln_ref_funits_adopted', [])
    soln_ref_funits_adopted = pd.DataFrame(funits[1:], columns=funits[0]).set_index('Year')

    ua = unitadoption.UnitAdoption(ac=ac_rq, datadir=datadir,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        soln_ref_funits_adopted=soln_ref_funits_adopted,
        soln_pds_funits_adopted=soln_pds_funits_adopted)
    results_str = json.dumps(ua.to_dict(), separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/operatingcost", methods=['POST'])
def operatingCost():
    """Operating Cost module."""
    js = request.get_json(force=True)
    ac_rq = to_advanced_controls(js, app.logger)
    ua_rq = js.get('unit_adoption', {})
    fc_rq = js.get('first_cost', {})
    oc_rq = js.get('operating_cost', {})

    p = ua_rq.get('soln_net_annual_funits_adopted', [])
    soln_net_annual_funits_adopted = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    p = ua_rq.get('soln_pds_tot_iunits_reqd', [])
    soln_pds_tot_iunits_reqd = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    p = ua_rq.get('soln_ref_tot_iunits_reqd', [])
    soln_ref_tot_iunits_reqd = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    p = ua_rq.get('conv_ref_annual_tot_iunits', [])
    conv_ref_annual_tot_iunits = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')

    p = fc_rq.get('annual_world_first_cost', [])
    annual_world_first_cost = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    soln_pds_annual_world_first_cost = annual_world_first_cost['soln_pds_annual_world_first_cost']
    soln_ref_annual_world_first_cost = annual_world_first_cost['soln_ref_annual_world_first_cost']
    conv_ref_annual_world_first_cost = annual_world_first_cost['conv_ref_annual_world_first_cost']
    soln_pds_install_cost_per_iunit = annual_world_first_cost['soln_pds_install_cost_per_iunit']
    conv_ref_install_cost_per_iunit = annual_world_first_cost['conv_ref_install_cost_per_iunit']

    single_iunit_purchase_year = oc_rq.get('single_iunit_purchase_year', 0)

    oc = operatingcost.OperatingCost(ac=ac_rq,
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
        soln_ref_tot_iunits_reqd=soln_ref_tot_iunits_reqd,
        conv_ref_annual_tot_iunits=conv_ref_annual_tot_iunits,
        soln_pds_annual_world_first_cost=soln_pds_annual_world_first_cost,
        soln_ref_annual_world_first_cost=soln_ref_annual_world_first_cost,
        conv_ref_annual_world_first_cost=conv_ref_annual_world_first_cost,
        single_iunit_purchase_year=single_iunit_purchase_year,
        soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit,
        conv_ref_install_cost_per_iunit=conv_ref_install_cost_per_iunit)
    results_str = json.dumps(oc.to_dict(), separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/emissionsfactors", methods=['POST'])
def emissionsFactors():
    """Emissions Factors module."""
    js = request.get_json(force=True)
    ac_rq = to_advanced_controls(js, app.logger)

    ef = emissionsfactors.ElectricityGenOnGrid(ac=ac_rq)
    results_str = json.dumps(ef.to_dict(), separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/adoptiondata", methods=['POST'])
def adoptionData():
    """Adoption Data module."""
    js = request.get_json(force=True)
    ac_rq = to_advanced_controls(js, app.logger)
    ad_rq = js.get('adoption_data', {})

    p = ad_rq.get('adconfig', [])
    adconfig = pd.DataFrame(p[1:], columns=p[0]).set_index('param')

    data_sources = {
      'Baseline Cases': {
        'Based on: IEA ETP 2016 6DS': pathlib.PurePath(solndir, 'ad_based_on_IEA_ETP_2016_6DS.csv'),
        'Based on: AMPERE (2014) IMAGE Refpol': pathlib.PurePath(solndir,
          'ad_based_on_AMPERE_2014_IMAGE_TIMER_Reference.csv'),
        'Based on: AMPERE (2014) MESSAGE REFPol': pathlib.PurePath(solndir,
          'ad_based_on_AMPERE_2014_MESSAGE_MACRO_Reference.csv'),
        'Based on: AMPERE (2014) GEM E3 REFpol': pathlib.PurePath(solndir,
          'ad_based_on_AMPERE_2014_GEM_E3_Reference.csv'),
      },
      'Conservative Cases': {
        'Based on: IEA ETP 2016 4DS': pathlib.PurePath(solndir, 'ad_based_on_IEA_ETP_2016_4DS.csv'),
        'Based on: AMPERE (2014) IMAGE 550': pathlib.PurePath(solndir,
          'ad_based_on_AMPERE_2014_IMAGE_TIMER_550.csv'),
        'Based on: AMPERE (2014) MESSAGE 550': pathlib.PurePath(solndir,
          'ad_based_on_AMPERE_2014_MESSAGE_MACRO_550.csv'),
        'Based on: AMPERE (2014) GEM E3 550': pathlib.PurePath(solndir,
          'ad_based_on_AMPERE_2014_GEM_E3_550.csv'),
        'Based on: Greenpeace (2015) Reference': pathlib.PurePath(solndir,
          'ad_based_on_Greenpeace_2015_Reference.csv'),
      },
      'Ambitious Cases': {
        'Based on: IEA ETP 2016 2DS': pathlib.PurePath(solndir, 'ad_based_on_IEA_ETP_2016_2DS.csv'),
        'Based on: AMPERE (2014) IMAGE 450': pathlib.PurePath(solndir,
          'ad_based_on_AMPERE_2014_IMAGE_TIMER_450.csv'),
        'Based on: AMPERE (2014) MESSAGE 450': pathlib.PurePath(solndir,
          'ad_based_on_AMPERE_2014_MESSAGE_MACRO_450.csv'),
        'Based on: AMPERE (2014) GEM E3 450': pathlib.PurePath(solndir,
          'ad_based_on_AMPERE_2014_GEM_E3_450.csv'),
        'Based on: Greenpeace (2015) Energy Revolution': pathlib.PurePath(solndir,
          'ad_based_on_Greenpeace_2015_Energy_Revolution.csv'),
      },
      '100% RES2050 Case': {
        'Based on: Greenpeace (2015) Advanced Energy Revolution': pathlib.PurePath(solndir,
          'ad_based_on_Greenpeace_2015_Advanced_Revolution.csv'),
      },
    }

    ad = adoptiondata.AdoptionData(ac=ac_rq, data_sources=data_sources, adconfig=adconfig)
    results_str = json.dumps(ad.to_dict(), separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/helpertables", methods=['POST'])
def helperTables():
    """Helper Tables module."""
    js = request.get_json(force=True)
    ac_rq = to_advanced_controls(js, app.logger)
    ht_rq = js.get('helper_tables', {})
    ua_rq = js.get('unit_adoption', {})
    ad_rq = js.get('adoption_data', {})

    dps = ht_rq.get('ref_datapoints', [])
    ref_datapoints = pd.DataFrame(dps[1:], columns=dps[0]).set_index('Year')
    dps = ht_rq.get('pds_datapoints', [])
    pds_datapoints = pd.DataFrame(dps[1:], columns=dps[0]).set_index('Year')

    tpr = ua_rq.get('ref_tam_per_region', [])
    ref_tam_per_region = pd.DataFrame(tpr[1:], columns=tpr[0]).set_index('Year')
    tpr = ua_rq.get('pds_tam_per_region', [])
    pds_tam_per_region = pd.DataFrame(tpr[1:], columns=tpr[0]).set_index('Year')

    lmh = ad_rq.get('adoption_low_med_high', [])
    adoption_low_med_high = pd.DataFrame(lmh[1:], columns=lmh[0]).set_index('Year')

    ht = helpertables.HelperTables(ac=ac_rq,
        ref_datapoints=ref_datapoints, pds_datapoints=pds_datapoints,
        ref_tam_per_region=ref_tam_per_region, pds_tam_per_region=pds_tam_per_region,
        adoption_low_med_high_global=adoption_low_med_high,
        adoption_is_single_source=False)
    results_str = json.dumps(ht.to_dict(), separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/co2calcs", methods=['POST'])
def co2Calcs():
    """CO2 Calcs module."""
    js = request.get_json(force=True)
    ac_rq = to_advanced_controls(js, app.logger)
    ef_rq = js.get('emissions_factors', {})
    ua_rq = js.get('unit_adoption', {})

    fuel_in_liters = ef_rq.get('fuel_in_liters', False)
    p = ef_rq.get('conv_ref_grid_CO2_per_KWh', [])
    conv_ref_grid_CO2_per_KWh = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    p = ef_rq.get('conv_ref_grid_CO2eq_per_KWh', [])
    conv_ref_grid_CO2eq_per_KWh = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')

    p = ua_rq.get('soln_net_annual_funits_adopted', [])
    soln_net_annual_funits_adopted = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    p = ua_rq.get('soln_pds_new_iunits_reqd', [])
    soln_pds_new_iunits_reqd = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    p = ua_rq.get('soln_ref_new_iunits_reqd', [])
    soln_ref_new_iunits_reqd = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    p = ua_rq.get('conv_ref_new_iunits_reqd', [])
    conv_ref_new_iunits_reqd = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    p = ua_rq.get('soln_pds_direct_co2_emissions_saved', [])
    soln_pds_direct_co2_emissions_saved = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    p = ua_rq.get('soln_pds_direct_ch4_co2_emissions_saved', [])
    soln_pds_direct_ch4_co2_emissions_saved = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    p = ua_rq.get('soln_pds_direct_n2o_co2_emissions_saved', [])
    soln_pds_direct_n2o_co2_emissions_saved = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    p = ua_rq.get('soln_pds_net_grid_electricity_units_used', [])
    soln_pds_net_grid_electricity_units_used = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    p = ua_rq.get('soln_pds_net_grid_electricity_units_saved', [])
    soln_pds_net_grid_electricity_units_saved = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')

    ch4_ppb_calculator = pd.DataFrame(0, columns=["PPB", "notused"], index=list(range(2015, 2061)))

    c2 = co2calcs.CO2Calcs(ac=ac_rq,
        ch4_ppb_calculator=ch4_ppb_calculator,
        soln_pds_net_grid_electricity_units_saved=soln_pds_net_grid_electricity_units_saved,
        soln_pds_net_grid_electricity_units_used=soln_pds_net_grid_electricity_units_used,
        soln_pds_direct_co2_emissions_saved=soln_pds_direct_co2_emissions_saved,
        soln_pds_direct_ch4_co2_emissions_saved=soln_pds_direct_ch4_co2_emissions_saved,
        soln_pds_direct_n2o_co2_emissions_saved=soln_pds_direct_n2o_co2_emissions_saved,
        soln_pds_new_iunits_reqd=soln_pds_new_iunits_reqd,
        soln_ref_new_iunits_reqd=soln_ref_new_iunits_reqd,
        conv_ref_new_iunits_reqd=conv_ref_new_iunits_reqd,
        conv_ref_grid_CO2_per_KWh=conv_ref_grid_CO2_per_KWh,
        conv_ref_grid_CO2eq_per_KWh=conv_ref_grid_CO2eq_per_KWh,
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
        fuel_in_liters=fuel_in_liters)
    ch4 = ch4calcs.CH4Calcs(ac=ac_rq, soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)
    results = c2.to_dict()
    results.update(ch4.to_dict())
    results_str = json.dumps(results, separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/tamdata", methods=['POST'])
def tamData():
    """TAM Data module."""
    js = request.get_json(force=True)
    td_rq = js.get('tam_data', {})

    p = td_rq.get('tamconfig', [])
    tamconfig = pd.DataFrame(p[1:], columns=p[0]).set_index('param')

    td = tam.TAM(tamconfig=tamconfig, tam_ref_data_sources=rrs.tam_ref_data_sources,
        tam_pds_data_sources=rrs.tam_pds_data_sources)
    results_str = json.dumps(td.to_dict(), separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/solarpvutil", methods=['POST'])
def solarPVUtil():
    """SolarPVUtil solution."""
    pv = solarpvutil.SolarPVUtil()

    results_str = json.dumps(pv.to_dict(), separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/solarpvroof", methods=['POST'])
def solarPVRoof():
    """SolarPVRoof solution."""
    pv = solarpvroof.SolarPVRoof()

    results_str = json.dumps(pv.to_dict(), separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


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
