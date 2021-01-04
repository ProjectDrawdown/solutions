from starlette.testclient import TestClient

from api.service import app

client = TestClient(app)

def test_get_all_workbooks():
  response = client.get("/workbooks/")
  assert response.status_code == 200
  json_data = response.json()
  assert len(json_data) > 0

# def test_solutions():
#     response = client.get("/solutions/solarpvutil?scenario=PDS-25p2050-Optimum2020")
#     assert response.status_code == 200
#     json_data = response.json()
#     assert 'solarpvutil' in json_data
#     assert 'PDS-25p2050-Optimum2020' in json_data['solarpvutil']
#     scenario = json_data['solarpvutil']['PDS-25p2050-Optimum2020']
#     assert 'tm' in scenario
#     assert 'ad' in scenario
#     assert 'ef' in scenario
#     assert 'ua' in scenario
#     assert 'fc' in scenario
#     assert 'oc' in scenario
#     assert 'c4' in scenario
#     assert 'c2' in scenario
