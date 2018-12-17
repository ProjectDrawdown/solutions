"""Flask App for http://codeearth.net."""

import io
import json
import os
import os.path

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
import werkzeug.exceptions


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # minify JSON

datadir = os.path.join(os.path.dirname(__file__), 'solution', 'solarpvutil')


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
    fc = firstcost.FirstCost(
        ac=ac_rq,
        pds_learning_increase_mult=fc_rq.get('pds_learning_increase_mult', 0),
        ref_learning_increase_mult=fc_rq.get('ref_learning_increase_mult', 0),
        conv_learning_increase_mult=fc_rq.get('conv_learning_increase_mult', 0))

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

    results = dict()
    soln_pds_install_cost_per_iunit = fc.soln_pds_install_cost_per_iunit(
        soln_pds_tot_iunits_reqd=soln_pds_tot_iunits_reqd,
        conv_ref_tot_iunits_reqd=conv_ref_tot_iunits_reqd)
    results['soln_pds_install_cost_per_iunit'] = format_for_response(soln_pds_install_cost_per_iunit)
    conv_ref_install_cost_per_iunit = fc.conv_ref_install_cost_per_iunit(
        conv_ref_tot_iunits_reqd=conv_ref_tot_iunits_reqd)
    results['conv_ref_install_cost_per_iunit'] = format_for_response(
        conv_ref_install_cost_per_iunit)
    soln_ref_install_cost_per_iunit = fc.soln_ref_install_cost_per_iunit(
        soln_ref_tot_iunits_reqd, conv_ref_tot_iunits_reqd)
    results['soln_ref_install_cost_per_iunit'] = format_for_response(
        soln_ref_install_cost_per_iunit)
    soln_pds_annual_world_first_cost = fc.soln_pds_annual_world_first_cost(
        soln_pds_new_iunits_reqd=soln_pds_new_iunits_reqd,
        soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit)
    results['soln_pds_annual_world_first_cost'] = format_for_response(
        soln_pds_annual_world_first_cost)
    results['soln_pds_cumulative_install'] = format_for_response(
        fc.soln_pds_cumulative_install(soln_pds_annual_world_first_cost))
    soln_ref_annual_world_first_cost = fc.soln_ref_annual_world_first_cost(
        soln_ref_new_iunits_reqd, soln_ref_install_cost_per_iunit)
    results['soln_ref_annual_world_first_cost'] = format_for_response(
        soln_ref_annual_world_first_cost)
    conv_ref_annual_world_first_cost = fc.conv_ref_annual_world_first_cost(
        conv_ref_new_iunits_reqd, conv_ref_install_cost_per_iunit)
    results['conv_ref_annual_world_first_cost'] = format_for_response(
        conv_ref_annual_world_first_cost)
    results['ref_cumulative_install'] = format_for_response(fc.ref_cumulative_install(
        conv_ref_annual_world_first_cost, soln_ref_annual_world_first_cost))
    results_str = json.dumps(results, separators=(',', ':'), default=json_dumps_default)
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
    results = dict()
    results['ref_population'] = format_for_response(ua.ref_population())
    results['ref_gdp'] = format_for_response(ua.ref_gdp())
    results['ref_gdp_per_capita'] = format_for_response(ua.ref_gdp_per_capita())
    results['ref_tam_per_capita'] = format_for_response(ua.ref_tam_per_capita())
    results['ref_tam_per_gdp_per_capita'] = format_for_response(ua.ref_tam_per_gdp_per_capita())
    results['ref_tam_growth'] = format_for_response(ua.ref_tam_growth())
    results['pds_population'] = format_for_response(ua.pds_population())
    results['pds_gdp'] = format_for_response(ua.pds_gdp())
    results['pds_gdp_per_capita'] = format_for_response(ua.pds_gdp_per_capita())
    results['pds_tam_per_capita'] = format_for_response(ua.pds_tam_per_capita())
    results['pds_tam_per_gdp_per_capita'] = format_for_response(ua.pds_tam_per_gdp_per_capita())
    results['pds_tam_growth'] = format_for_response(ua.pds_tam_growth())
    results['soln_pds_cumulative_funits'] = format_for_response(ua.soln_pds_cumulative_funits())
    results['soln_ref_cumulative_funits'] = format_for_response(ua.soln_ref_cumulative_funits())
    soln_net_annual_funits_adopted = ua.soln_net_annual_funits_adopted()
    results['soln_net_annual_funits_adopted'] = format_for_response(soln_net_annual_funits_adopted)
    soln_pds_tot_iunits_reqd = ua.soln_pds_tot_iunits_reqd()
    results['soln_pds_tot_iunits_reqd'] = format_for_response(soln_pds_tot_iunits_reqd)
    results['soln_pds_new_iunits_reqd'] = format_for_response(ua.soln_pds_new_iunits_reqd())
    results['soln_pds_big4_iunits_reqd'] = format_for_response(ua.soln_pds_big4_iunits_reqd())
    soln_ref_tot_iunits_reqd = ua.soln_ref_tot_iunits_reqd()
    results['soln_ref_tot_iunits_reqd'] = format_for_response(soln_ref_tot_iunits_reqd)
    results['soln_ref_new_iunits_reqd'] = format_for_response(ua.soln_ref_new_iunits_reqd())
    results['conv_ref_tot_iunits_reqd'] = format_for_response(ua.conv_ref_tot_iunits_reqd())
    conv_ref_annual_tot_iunits = ua.conv_ref_annual_tot_iunits()
    results['conv_ref_annual_tot_iunits'] = format_for_response(conv_ref_annual_tot_iunits)
    results['conv_ref_new_iunits_reqd'] = format_for_response(ua.conv_ref_new_iunits_reqd())
    results['conv_lifetime_replacement'] = format_for_response(round(ac_rq.conv_lifetime_replacement))

    results['soln_pds_net_grid_electricity_units_saved'] = format_for_response(
      ua.soln_pds_net_grid_electricity_units_saved())
    results['soln_pds_net_grid_electricity_units_used'] = format_for_response(
      ua.soln_pds_net_grid_electricity_units_used())
    results['soln_pds_fuel_units_avoided'] = format_for_response(ua.soln_pds_fuel_units_avoided())
    results['soln_pds_direct_co2_emissions_saved'] = format_for_response(
      ua.soln_pds_direct_co2_emissions_saved())
    results['soln_pds_direct_ch4_co2_emissions_saved'] = format_for_response(
      ua.soln_pds_direct_ch4_co2_emissions_saved())
    results['soln_pds_direct_n2o_co2_emissions_saved'] = format_for_response(
      ua.soln_pds_direct_n2o_co2_emissions_saved())

    results_str = json.dumps(results, separators=(',', ':'), default=json_dumps_default)
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
    conv_ref_net_annual_iunits_reqd = conv_ref_annual_tot_iunits['World']

    p = fc_rq.get('annual_world_first_cost', [])
    annual_world_first_cost = pd.DataFrame(p[1:], columns=p[0]).set_index('Year')
    soln_pds_annual_world_first_cost = annual_world_first_cost['soln_pds_annual_world_first_cost']
    soln_ref_annual_world_first_cost = annual_world_first_cost['soln_ref_annual_world_first_cost']
    conv_ref_annual_world_first_cost = annual_world_first_cost['conv_ref_annual_world_first_cost']
    soln_pds_install_cost_per_iunit = annual_world_first_cost['soln_pds_install_cost_per_iunit']
    conv_ref_install_cost_per_iunit = annual_world_first_cost['conv_ref_install_cost_per_iunit']

    single_iunit_purchase_year = oc_rq.get('single_iunit_purchase_year', 0)

    oc = operatingcost.OperatingCost(ac=ac_rq)
    results = dict()
    soln_new_funits_per_year = oc.soln_new_funits_per_year(soln_net_annual_funits_adopted)
    results['soln_new_funits_per_year'] = format_for_response(soln_new_funits_per_year)
    world = soln_new_funits_per_year['World']
    world.name = 'New Functional Units each Year'
    results['soln_new_funits_per_year_world'] = format_for_response(world)
    soln_pds_net_annual_iunits_reqd = oc.soln_pds_net_annual_iunits_reqd(
        soln_pds_tot_iunits_reqd, soln_ref_tot_iunits_reqd)
    results['soln_pds_net_annual_iunits_reqd'] = format_for_response(soln_pds_net_annual_iunits_reqd)
    soln_pds_new_annual_iunits_reqd = oc.soln_pds_new_annual_iunits_reqd(
        soln_pds_net_annual_iunits_reqd)
    results['soln_pds_new_annual_iunits_reqd'] = format_for_response(soln_pds_new_annual_iunits_reqd)
    soln_pds_annual_breakout = oc.soln_pds_annual_breakout(
      soln_new_funits_per_year=soln_new_funits_per_year['World'],
      soln_pds_new_annual_iunits_reqd=soln_pds_new_annual_iunits_reqd['World'])
    results['soln_pds_annual_breakout'] = format_for_response(soln_pds_annual_breakout)
    soln_pds_annual_operating_cost = oc.soln_pds_annual_operating_cost(soln_pds_annual_breakout)
    results['soln_pds_annual_operating_cost'] = format_for_response(soln_pds_annual_operating_cost)
    results['soln_pds_cumulative_operating_cost'] = format_for_response(
        oc.soln_pds_cumulative_operating_cost( soln_pds_annual_operating_cost))
    conv_ref_new_annual_iunits_reqd = oc.conv_ref_new_annual_iunits_reqd(
        conv_ref_net_annual_iunits_reqd)
    results['conv_ref_new_annual_iunits_reqd'] = format_for_response(conv_ref_new_annual_iunits_reqd)

    # Though it looks strange to set conv_new_funits_per_year=soln_new_funits_per_year, that is
    # what the model does. It is calculating additionality of the PDS on top of the SOLN-REF.
    conv_ref_annual_breakout = oc.conv_ref_annual_breakout(
      conv_new_funits_per_year=soln_new_funits_per_year['World'],
      conv_ref_new_annual_iunits_reqd=conv_ref_new_annual_iunits_reqd)
    results['conv_ref_annual_breakout'] = format_for_response(conv_ref_annual_breakout)

    conv_ref_annual_operating_cost = oc.conv_ref_annual_operating_cost(conv_ref_annual_breakout)
    results['conv_ref_annual_operating_cost'] = format_for_response(conv_ref_annual_operating_cost)
    results['conv_ref_cumulative_operating_cost'] = format_for_response(
        oc.conv_ref_cumulative_operating_cost(conv_ref_annual_operating_cost))
    results['marginal_annual_operating_cost'] = format_for_response(
        oc.marginal_annual_operating_cost(
          soln_pds_annual_operating_cost=soln_pds_annual_operating_cost,
          conv_ref_annual_operating_cost=conv_ref_annual_operating_cost))

    results['lifetime_cost_forecast'] = format_for_response(oc.lifetime_cost_forecast(
      soln_ref_annual_world_first_cost=soln_ref_annual_world_first_cost,
      conv_ref_annual_world_first_cost=conv_ref_annual_world_first_cost,
      soln_pds_annual_world_first_cost=soln_pds_annual_world_first_cost,
      conv_ref_annual_breakout=conv_ref_annual_breakout,
      soln_pds_annual_breakout=soln_pds_annual_breakout))

    soln_vs_conv_single_iunit_cashflow = oc.soln_vs_conv_single_iunit_cashflow(
        single_iunit_purchase_year=single_iunit_purchase_year,
        soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit,
        conv_ref_install_cost_per_iunit=conv_ref_install_cost_per_iunit)
    results['soln_vs_conv_single_iunit_cashflow'] = format_for_response(soln_vs_conv_single_iunit_cashflow)
    soln_vs_conv_single_iunit_npv = oc.soln_vs_conv_single_iunit_npv(
        single_iunit_purchase_year=single_iunit_purchase_year,
        soln_vs_conv_single_iunit_cashflow=soln_vs_conv_single_iunit_cashflow)
    results['soln_vs_conv_single_iunit_npv'] = format_for_response(soln_vs_conv_single_iunit_npv)
    soln_vs_conv_single_iunit_payback = oc.soln_vs_conv_single_iunit_payback(
        soln_vs_conv_single_iunit_cashflow=soln_vs_conv_single_iunit_cashflow)
    results['soln_vs_conv_single_iunit_payback'] = format_for_response(soln_vs_conv_single_iunit_payback)
    soln_vs_conv_single_iunit_payback_discounted = oc.soln_vs_conv_single_iunit_payback_discounted(
        soln_vs_conv_single_iunit_npv=soln_vs_conv_single_iunit_npv)
    results['soln_vs_conv_single_iunit_payback_discounted'] = format_for_response(
        soln_vs_conv_single_iunit_payback_discounted)
    soln_only_single_iunit_cashflow = oc.soln_only_single_iunit_cashflow(
        single_iunit_purchase_year=single_iunit_purchase_year,
        soln_pds_install_cost_per_iunit=soln_pds_install_cost_per_iunit)
    results['soln_only_single_iunit_cashflow'] = format_for_response(soln_only_single_iunit_cashflow)
    soln_only_single_iunit_npv = oc.soln_only_single_iunit_npv(
        single_iunit_purchase_year=single_iunit_purchase_year,
        soln_only_single_iunit_cashflow=soln_only_single_iunit_cashflow)
    results['soln_only_single_iunit_npv'] = format_for_response(soln_only_single_iunit_npv)
    soln_only_single_iunit_payback = oc.soln_only_single_iunit_payback(
        soln_only_single_iunit_cashflow=soln_only_single_iunit_cashflow)
    results['soln_only_single_iunit_payback'] = format_for_response(soln_only_single_iunit_payback)
    soln_only_single_iunit_payback_discounted = oc.soln_only_single_iunit_payback_discounted(
        soln_only_single_iunit_npv=soln_only_single_iunit_npv)
    results['soln_only_single_iunit_payback_discounted'] = format_for_response(
        soln_only_single_iunit_payback_discounted)

    results_str = json.dumps(results, separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/emissionsfactors", methods=['POST'])
def emissionsFactors():
    """Emissions Factors module."""
    js = request.get_json(force=True)
    ac_rq = to_advanced_controls(js, app.logger)

    ef = emissionsfactors.ElectricityGenOnGrid(ac=ac_rq)
    results = dict()
    results['conv_ref_grid_CO2eq_per_KWh'] = format_for_response(ef.conv_ref_grid_CO2eq_per_KWh())
    results['conv_ref_grid_CO2_per_KWh'] = format_for_response(ef.conv_ref_grid_CO2_per_KWh())

    results_str = json.dumps(results, separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/adoptiondata", methods=['POST'])
def adoptionData():
    """Adoption Data module."""
    js = request.get_json(force=True)
    ac_rq = to_advanced_controls(js, app.logger)
    ad_rq = js.get('adoption_data', {})

    p = ad_rq.get('adconfig', [])
    adconfig = pd.DataFrame(p[1:], columns=p[0]).set_index('param')

    ad = adoptiondata.AdoptionData(ac=ac_rq, datadir=datadir, adconfig=adconfig)
    results = dict()

    results['adoption_data_global'] = format_for_response(ad.adoption_data_global())
    results['adoption_min_max_sd_global'] = format_for_response(ad.adoption_min_max_sd_global())
    results['adoption_low_med_high_global'] = format_for_response(ad.adoption_low_med_high_global())
    results['adoption_trend_linear_global'] = format_for_response(
        ad.adoption_trend_global(trend='Linear'))
    results['adoption_trend_poly_degree2_global'] = format_for_response(
        ad.adoption_trend_global(trend='Degree2'))
    results['adoption_trend_poly_degree3_global'] = format_for_response(
        ad.adoption_trend_global(trend='Degree3'))
    results['adoption_trend_exponential_global'] = format_for_response(
        ad.adoption_trend_global(trend='Exponential'))

    results_str = json.dumps(results, separators=(',', ':'), default=json_dumps_default)
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

    ht = helpertables.HelperTables(ac=ac_rq, ref_datapoints=ref_datapoints,
        pds_datapoints=pds_datapoints)
    results = dict()

    results['soln_ref_funits_adopted'] = format_for_response(ht.soln_ref_funits_adopted(
      ref_tam_per_region=ref_tam_per_region))
    results['soln_pds_funits_adopted'] = format_for_response(ht.soln_pds_funits_adopted(
      adoption_low_med_high=adoption_low_med_high, pds_tam_per_region=pds_tam_per_region))

    results_str = json.dumps(results, separators=(',', ':'), default=json_dumps_default)
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

    c2 = co2calcs.CO2Calcs(ac=ac_rq)
    results = dict()

    co2_reduced_grid_emissions = c2.co2_reduced_grid_emissions(
        soln_pds_net_grid_electricity_units_saved=soln_pds_net_grid_electricity_units_saved,
        conv_ref_grid_CO2_per_KWh=conv_ref_grid_CO2_per_KWh)
    results['co2_reduced_grid_emissions'] = format_for_response(co2_reduced_grid_emissions)
    co2_replaced_grid_emissions = c2.co2_replaced_grid_emissions(
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
        conv_ref_grid_CO2_per_KWh=conv_ref_grid_CO2_per_KWh)
    results['co2_replaced_grid_emissions'] = format_for_response(co2_replaced_grid_emissions)
    co2_increased_grid_usage_emissions = c2.co2_increased_grid_usage_emissions(
        soln_pds_net_grid_electricity_units_used=soln_pds_net_grid_electricity_units_used,
        conv_ref_grid_CO2_per_KWh=conv_ref_grid_CO2_per_KWh)
    results['co2_increased_grid_usage_emissions'] = format_for_response(
        co2_increased_grid_usage_emissions)
    co2eq_reduced_grid_emissions = c2.co2eq_reduced_grid_emissions(
        soln_pds_net_grid_electricity_units_saved=soln_pds_net_grid_electricity_units_saved,
        conv_ref_grid_CO2eq_per_KWh=conv_ref_grid_CO2eq_per_KWh)
    results['co2eq_reduced_grid_emissions'] = format_for_response(co2eq_reduced_grid_emissions)
    co2eq_replaced_grid_emissions = c2.co2eq_replaced_grid_emissions(
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
        conv_ref_grid_CO2eq_per_KWh=conv_ref_grid_CO2eq_per_KWh)
    results['co2eq_replaced_grid_emissions'] = format_for_response(co2eq_replaced_grid_emissions)
    co2eq_increased_grid_usage_emissions = c2.co2eq_increased_grid_usage_emissions(
        soln_pds_net_grid_electricity_units_used=soln_pds_net_grid_electricity_units_used,
        conv_ref_grid_CO2eq_per_KWh=conv_ref_grid_CO2eq_per_KWh)
    results['co2eq_increased_grid_usage_emissions'] = format_for_response(
        co2eq_increased_grid_usage_emissions)
    co2eq_direct_reduced_emissions = c2.co2eq_direct_reduced_emissions(
        soln_pds_direct_co2_emissions_saved=soln_pds_direct_co2_emissions_saved,
        soln_pds_direct_ch4_co2_emissions_saved=soln_pds_direct_ch4_co2_emissions_saved,
        soln_pds_direct_n2o_co2_emissions_saved=soln_pds_direct_n2o_co2_emissions_saved)
    results['co2eq_direct_reduced_emissions'] = format_for_response(co2eq_direct_reduced_emissions)
    co2eq_reduced_fuel_emissions = c2.co2eq_reduced_fuel_emissions(
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted,
        fuel_in_liters=fuel_in_liters)
    results['co2eq_reduced_fuel_emissions'] = format_for_response(co2eq_reduced_fuel_emissions)
    co2eq_net_indirect_emissions = c2.co2eq_net_indirect_emissions(
        soln_pds_new_iunits_reqd=soln_pds_new_iunits_reqd,
        soln_ref_new_iunits_reqd=soln_ref_new_iunits_reqd,
        conv_ref_new_iunits_reqd=conv_ref_new_iunits_reqd,
        soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)
    results['co2eq_net_indirect_emissions'] = format_for_response(co2eq_net_indirect_emissions)
    co2_mmt_reduced = c2.co2_mmt_reduced(co2_reduced_grid_emissions=co2_reduced_grid_emissions,
        co2_replaced_grid_emissions=co2_replaced_grid_emissions,
        co2eq_direct_reduced_emissions=co2eq_direct_reduced_emissions,
        co2eq_reduced_fuel_emissions=co2eq_reduced_fuel_emissions,
        co2eq_net_indirect_emissions=co2eq_net_indirect_emissions,
        co2_increased_grid_usage_emissions=co2_increased_grid_usage_emissions)
    results['co2_mmt_reduced'] = format_for_response(co2_mmt_reduced)
    co2eq_mmt_reduced = c2.co2eq_mmt_reduced(
        co2eq_reduced_grid_emissions=co2eq_reduced_grid_emissions,
        co2eq_replaced_grid_emissions=co2eq_replaced_grid_emissions,
        co2eq_increased_grid_usage_emissions=co2eq_increased_grid_usage_emissions,
        co2eq_direct_reduced_emissions=co2eq_direct_reduced_emissions,
        co2eq_reduced_fuel_emissions=co2eq_reduced_fuel_emissions,
        co2eq_net_indirect_emissions=co2eq_net_indirect_emissions)
    results['co2eq_mmt_reduced'] = format_for_response(co2eq_mmt_reduced)
    co2_ppm_calculator = c2.co2_ppm_calculator(co2_mmt_reduced=co2_mmt_reduced,
        co2eq_mmt_reduced=co2eq_mmt_reduced)
    results['co2_ppm_calculator'] = format_for_response(co2_ppm_calculator)
    ch4_ppm_calculator = pd.DataFrame(0, columns=["PPB", "notused"], index=list(range(2015, 2061)))
    co2eq_ppm_calculator = c2.co2eq_ppm_calculator(co2_ppm_calculator=co2_ppm_calculator,
        ch4_ppm_calculator=ch4_ppm_calculator)
    results['co2eq_ppm_calculator'] = format_for_response(co2eq_ppm_calculator)

    ch4 = ch4calcs.CH4Calcs(ac=ac_rq)
    ch4_tons_reduced = ch4.ch4_tons_reduced(
      soln_net_annual_funits_adopted=soln_net_annual_funits_adopted)
    results['ch4_tons_reduced'] = format_for_response(ch4_tons_reduced)
    results['ch4_ppb_calculator'] = format_for_response(ch4.ch4_ppb_calculator(
      ch4_tons_reduced=ch4_tons_reduced))

    results_str = json.dumps(results, separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/tamdata", methods=['POST'])
def tamData():
    """TAM Data module."""
    js = request.get_json(force=True)
    td_rq = js.get('tam_data', {})

    p = td_rq.get('tamconfig', [])
    tamconfig = pd.DataFrame(p[1:], columns=p[0]).set_index('param')

    td = tam.TAM(datadir=datadir, tamconfig=tamconfig)
    results = dict()

    results['forecast_data_global'] = format_for_response(td.forecast_data_global())
    results['forecast_min_max_sd_global'] = format_for_response(td.forecast_min_max_sd_global())
    results['forecast_low_med_high_global'] = format_for_response(td.forecast_low_med_high_global())
    results['forecast_trend_linear_global'] = format_for_response(
        td.forecast_trend_global(trend='Linear'))
    results['forecast_trend_degree2_global'] = format_for_response(
        td.forecast_trend_global(trend='Degree2'))
    results['forecast_trend_degree3_global'] = format_for_response(
        td.forecast_trend_global(trend='Degree3'))
    results['forecast_trend_exponential_global'] = format_for_response(
        td.forecast_trend_global(trend='Exponential'))
    results['forecast_data_oecd90'] = format_for_response(td.forecast_data_oecd90())
    results['forecast_min_max_sd_oecd90'] = format_for_response(td.forecast_min_max_sd_oecd90())
    results['forecast_low_med_high_oecd90'] = format_for_response(td.forecast_low_med_high_oecd90())
    results['forecast_trend_linear_oecd90'] = format_for_response(
        td.forecast_trend_oecd90(trend='Linear'))
    results['forecast_trend_degree2_oecd90'] = format_for_response(
        td.forecast_trend_oecd90(trend='Degree2'))
    results['forecast_trend_degree3_oecd90'] = format_for_response(
        td.forecast_trend_oecd90(trend='Degree3'))
    results['forecast_trend_exponential_oecd90'] = format_for_response(
        td.forecast_trend_oecd90(trend='Exponential'))
    results['forecast_data_eastern_europe'] = format_for_response(td.forecast_data_eastern_europe())
    results['forecast_min_max_sd_eastern_europe'] = format_for_response(
        td.forecast_min_max_sd_eastern_europe())
    results['forecast_low_med_high_eastern_europe'] = format_for_response(
        td.forecast_low_med_high_eastern_europe())
    results['forecast_trend_linear_eastern_europe'] = format_for_response(
        td.forecast_trend_eastern_europe(trend='Linear'))
    results['forecast_trend_degree2_eastern_europe'] = format_for_response(
        td.forecast_trend_eastern_europe(trend='Degree2'))
    results['forecast_trend_degree3_eastern_europe'] = format_for_response(
        td.forecast_trend_eastern_europe(trend='Degree3'))
    results['forecast_trend_exponential_eastern_europe'] = format_for_response(
        td.forecast_trend_eastern_europe(trend='Exponential'))
    results['forecast_data_asia_sans_japan'] = format_for_response(
        td.forecast_data_asia_sans_japan())
    results['forecast_min_max_sd_asia_sans_japan'] = format_for_response(
        td.forecast_min_max_sd_asia_sans_japan())
    results['forecast_low_med_high_asia_sans_japan'] = format_for_response(
        td.forecast_low_med_high_asia_sans_japan())
    results['forecast_trend_linear_asia_sans_japan'] = format_for_response(
        td.forecast_trend_asia_sans_japan(trend='Linear'))
    results['forecast_trend_degree2_asia_sans_japan'] = format_for_response(
        td.forecast_trend_asia_sans_japan(trend='Degree2'))
    results['forecast_trend_degree3_asia_sans_japan'] = format_for_response(
        td.forecast_trend_asia_sans_japan(trend='Degree3'))
    results['forecast_trend_exponential_asia_sans_japan'] = format_for_response(
        td.forecast_trend_asia_sans_japan(trend='Exponential'))
    results['forecast_data_middle_east_and_africa'] = format_for_response(
        td.forecast_data_middle_east_and_africa())
    results['forecast_min_max_sd_middle_east_and_africa'] = format_for_response(
        td.forecast_min_max_sd_middle_east_and_africa())
    results['forecast_low_med_high_middle_east_and_africa'] = format_for_response(
        td.forecast_low_med_high_middle_east_and_africa())
    results['forecast_trend_linear_middle_east_and_africa'] = format_for_response(
        td.forecast_trend_middle_east_and_africa(trend='Linear'))
    results['forecast_trend_degree2_middle_east_and_africa'] = format_for_response(
        td.forecast_trend_middle_east_and_africa(trend='Degree2'))
    results['forecast_trend_degree3_middle_east_and_africa'] = format_for_response(
        td.forecast_trend_middle_east_and_africa(trend='Degree3'))
    results['forecast_trend_exponential_middle_east_and_africa'] = format_for_response(
        td.forecast_trend_middle_east_and_africa(trend='Exponential'))
    results['forecast_data_latin_america'] = format_for_response(td.forecast_data_latin_america())
    results['forecast_min_max_sd_latin_america'] = format_for_response(
        td.forecast_min_max_sd_latin_america())
    results['forecast_low_med_high_latin_america'] = format_for_response(
        td.forecast_low_med_high_latin_america())
    results['forecast_trend_linear_latin_america'] = format_for_response(
        td.forecast_trend_latin_america(trend='Linear'))
    results['forecast_trend_degree2_latin_america'] = format_for_response(
        td.forecast_trend_latin_america(trend='Degree2'))
    results['forecast_trend_degree3_latin_america'] = format_for_response(
        td.forecast_trend_latin_america(trend='Degree3'))
    results['forecast_trend_exponential_latin_america'] = format_for_response(
        td.forecast_trend_latin_america(trend='Exponential'))
    results['forecast_data_china'] = format_for_response(td.forecast_data_china())
    results['forecast_min_max_sd_china'] = format_for_response(td.forecast_min_max_sd_china())
    results['forecast_low_med_high_china'] = format_for_response(td.forecast_low_med_high_china())
    results['forecast_trend_linear_china'] = format_for_response(
        td.forecast_trend_china(trend='Linear'))
    results['forecast_trend_degree2_china'] = format_for_response(
        td.forecast_trend_china(trend='Degree2'))
    results['forecast_trend_degree3_china'] = format_for_response(
        td.forecast_trend_china(trend='Degree3'))
    results['forecast_trend_exponential_china'] = format_for_response(
        td.forecast_trend_china(trend='Exponential'))
    results['forecast_data_india'] = format_for_response(td.forecast_data_india())
    results['forecast_min_max_sd_india'] = format_for_response(td.forecast_min_max_sd_india())
    results['forecast_low_med_high_india'] = format_for_response(td.forecast_low_med_high_india())
    results['forecast_trend_linear_india'] = format_for_response(
        td.forecast_trend_india(trend='Linear'))
    results['forecast_trend_degree2_india'] = format_for_response(
        td.forecast_trend_india(trend='Degree2'))
    results['forecast_trend_degree3_india'] = format_for_response(
        td.forecast_trend_india(trend='Degree3'))
    results['forecast_trend_exponential_india'] = format_for_response(
        td.forecast_trend_india(trend='Exponential'))
    results['forecast_data_eu'] = format_for_response(td.forecast_data_eu())
    results['forecast_min_max_sd_eu'] = format_for_response(td.forecast_min_max_sd_eu())
    results['forecast_low_med_high_eu'] = format_for_response(td.forecast_low_med_high_eu())
    results['forecast_trend_linear_eu'] = format_for_response(
        td.forecast_trend_eu(trend='Linear'))
    results['forecast_trend_degree2_eu'] = format_for_response(
        td.forecast_trend_eu(trend='Degree2'))
    results['forecast_trend_degree3_eu'] = format_for_response(
        td.forecast_trend_eu(trend='Degree3'))
    results['forecast_trend_exponential_eu'] = format_for_response(
        td.forecast_trend_eu(trend='Exponential'))
    results['forecast_data_usa'] = format_for_response(td.forecast_data_usa())
    results['forecast_min_max_sd_usa'] = format_for_response(td.forecast_min_max_sd_usa())
    results['forecast_low_med_high_usa'] = format_for_response(td.forecast_low_med_high_usa())
    results['forecast_trend_linear_usa'] = format_for_response(
        td.forecast_trend_usa(trend='Linear'))
    results['forecast_trend_degree2_usa'] = format_for_response(
        td.forecast_trend_usa(trend='Degree2'))
    results['forecast_trend_degree3_usa'] = format_for_response(
        td.forecast_trend_usa(trend='Degree3'))
    results['forecast_trend_exponential_usa'] = format_for_response(
        td.forecast_trend_usa(trend='Exponential'))

    results_str = json.dumps(results, separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


@app.route("/solarpvutil", methods=['POST'])
def solarPVUtil():
    """SolarPVUtil solution."""
    js = request.get_json(force=True)
    td_rq = js.get('tam_data', {})
    ad_rq = js.get('adoption_data', {})

    p = td_rq.get('tamconfig', [])
    tamconfig = pd.DataFrame(p[1:], columns=p[0]).set_index('param')
    p = ad_rq.get('adconfig', [])
    adconfig = pd.DataFrame(p[1:], columns=p[0]).set_index('param')

    results = dict()

    td = tam.TAM(datadir=datadir, tamconfig=tamconfig)
    results['tam_data'] = td.to_dict()

    ad = adoptiondata.AdoptionData(ac=ac_rq, datadir=datadir, adconfig=adconfig)
    rs = dict()
    rs['adoption_data_global'] = format_for_response(ad.adoption_data_global())
    rs['adoption_min_max_sd_global'] = format_for_response(ad.adoption_min_max_sd_global())
    rs['adoption_low_med_high_global'] = format_for_response(ad.adoption_low_med_high_global())
    rs['adoption_trend_linear_global'] = format_for_response(
        ad.adoption_trend_global(trend='Linear'))
    rs['adoption_trend_poly_degree2_global'] = format_for_response(
        ad.adoption_trend_global(trend='Degree2'))
    rs['adoption_trend_poly_degree3_global'] = format_for_response(
        ad.adoption_trend_global(trend='Degree3'))
    rs['adoption_trend_exponential_global'] = format_for_response(
        ad.adoption_trend_global(trend='Exponential'))
    results['adoption_data'] = rs

    results_str = json.dumps(results, separators=(',', ':'), default=json_dumps_default)
    return Response(response=results_str, status=200, mimetype="application/json")


def to_advanced_controls(data, logger):
    '''Helper function to extract advanced controls fields.'''
    if not data.get('advanced_controls'):
        raise werkzeug.exceptions.BadRequest('advanced_controls missing')
    ac = data['advanced_controls']
    return advanced_controls.AdvancedControls(**ac)


def format_for_response(df):
  if isinstance(df, pd.DataFrame):
    return [[df.index.name, *df.columns.tolist()]] + df.reset_index().values.tolist()
  elif isinstance(df, pd.Series):
    return [[df.index.name, df.name]] + df.reset_index().values.tolist()
  else:
    return str(df)


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
