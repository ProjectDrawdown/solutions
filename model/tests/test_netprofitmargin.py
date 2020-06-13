from solution.conservationagriculture import scenarios, Scenario
from model.netprofitmargin import NetProfitMargin
import pandas as pd
import pytest

MILLION = 1000000

def plausible_conservationagriculture_ac():
    return Scenario('PDS-39p2050-Plausible-PDScustom-high-Bookedition1')

def graft_extra_fields_into_obj(obj : Scenario):
    obj.ac.soln_net_profit_margin_per_iunit = 530.393529225332
    return obj

@pytest.fixture(scope='session')
def some_netprofitmargin():
    obj = plausible_conservationagriculture_ac()
    obj = graft_extra_fields_into_obj(obj)
    return NetProfitMargin(
        ac=obj.ac,
        ua=obj.ua,
        sol_trans_pd_len=4,
        sol_trans_pd_type=NetProfitMargin.TransitionPeriodType.FIXED_PERCENT,
        sol_trans_pd_pct=.25,
        conv_trans_pd_len=0,
        conv_trans_pd_type=NetProfitMargin.TransitionPeriodType.LINEAR,
        converting_factor=1 * MILLION
    )


def test_duh(some_netprofitmargin):
    npm = some_netprofitmargin
    assert isinstance(npm, NetProfitMargin)
    assert len(npm.index) == npm.LAST_YEAR + 1 - npm.FIRST_YEAR


# def test_pds_npm_calc(some_netprofitmargin : NetProfitMargin):
#     pds_npm_calc = some_netprofitmargin.pds_npm_calc()
#     assert isinstance(pds_npm_calc, pd.DataFrame)

def test_lifetime_cost(some_netprofitmargin : NetProfitMargin):
    annual_npm = some_netprofitmargin.lifetime_cost()
    assert isinstance(annual_npm, pd.DataFrame)
