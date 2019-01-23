"""Tests for solution_xls_extract.py"""

import pytest
from tools import solution_xls_extract as sx

def test_convert_sr_float():
  s = "Val:(0.182810601365724) Formula:='Variable Meta-analysis'!G1411"
  assert sx.convert_sr_float(s) == pytest.approx(0.182810601365724)
  assert sx.convert_sr_float('0.1987') == pytest.approx(0.1987)
  assert sx.convert_sr_float('') == pytest.approx(0.0)
  assert sx.convert_sr_float('12') == pytest.approx(12.0)

def test_infer_classname():
  ic = sx.infer_classname
  assert ic('BiomassELC_RRS_ELECGEN_v1.1b_24Oct18.xlsm') == 'Biomass'
  assert ic('CHP_A_RRS_ELECGEN_v1.1b_12Oct18.xlsm') == 'CoGenElectricity'
  assert ic('CHP_B_RRS_ELECGEN_v1.1b_12Oct18.xlsm') == 'CoGenHeat'
  assert ic('CSP_RRS_ELECGEN_v1.1b_24Oct18.xlsm') == 'ConcentratedSolar'
  assert ic('Geothermal_RRS_ELECGEN_v1.1b_24Oct18.xlsm') == 'Geothermal'
  assert ic('InstreamHydro_RRS_ELECGEN_v1.1b_24Oct18.xlsm') == 'InstreamHydro'
  assert ic('Insulation_RRSModel_v1.1d_27Aug18.xlsm') == 'Insulation'
  assert ic('LandfillMethane_RRS_ELECGEN_v1.1c_24Oct18.xlsm') == 'LandfillMethane'
  assert ic('LargeMethaneDigesters_RRS_ELECGEN_v1.1b_24Oct18.xlsm') == 'LargeMethaneDigesters'
  assert ic('MicroWind_RRS_ELECGEN_v1.1b_24Oct18.xlsm') == 'MicroWind'
  assert ic('Nuclear_RRS_ELECGEN_v1.1b_24Oct18.xlsm') == 'Nuclear'
  assert ic('Regenerative_Agriculture_L-UseAgri_v1.1b_02Aug18.xlsm') == 'RegenerativeAgriculture'
  assert ic('SmartThermostats-RRSv1.1b-24Apr18.xlsm') == 'SmartThermostats'
  assert ic('SolarPVRooftop_RRS_ELECGEN_v1.1b_24Oct18.xlsm') == 'SolarPVRoof'
  assert ic('Tropical_Forest_Restoration_L-Use_v1.1b_3Aug18.xlsm') == 'TropicalForests'
  assert ic('WastetoEnergy_RRS_ELECGEN_v1.1b_24Oct18.xlsm') == 'WasteToEnergy'
  assert ic('Wave&Tidal_RRS_ELECGEN_v1.1b_24Oct18.xlsm') == 'WaveAndTidal'
  assert ic('WindOffshore_RRS_ELECGEN_v1.1b_24Oct18.xlsm') == 'WindOffshore'
  assert ic('WindOnshore_RRS_ELECGEN_v1.1b_24Oct18.xlsm') == 'WindOnshore'
  assert ic('Drawdown-Utility Scale Solar PV_RRS.ES_v1.1_13Jan2019_PUBLIC') == 'SolarPVUtil'
