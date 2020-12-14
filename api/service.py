import json
import glob
import pathlib
import uvicorn

from typing import Optional
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from functools import lru_cache

import solution.factory
from model.data_handler import DataHandler
from api.routers import account, user


app = FastAPI()
app.include_router(account.router)
app.include_router(user.router)
DATADIR = pathlib.Path(__file__).parents[0].joinpath('data')

@app.get('/solutions/{name}')
def get_scenario(name: str, scenario: Optional[str]=None):
  sol = solution.factory.one_solution_scenarios(name)
  if sol:
    constructor = sol[0]
    obj = constructor(scenario=scenario)
    return {name: to_json(obj)}
  else:
    return {}

def to_json(scenario):
    json_data = dict()
    instance_vars = vars(scenario).keys()
    for iv in instance_vars:
        try:
            obj = getattr(scenario, iv)
            if issubclass(type(obj), DataHandler):
                json_data[iv] = obj.to_json()
        except BaseException as e:
            json_data[iv] = None
    return {scenario.scenario: json_data}

@app.get('/scenarios/{cannonical}')
def scenario_group(cannonical: str):
    directory = DATADIR
    for filename in glob.glob(str(directory.joinpath('*.json'))):
        with open(filename, 'r') as fid:
            j = json.loads(fid.read())
            js = j.copy()
    return {cannonical: js[cannonical]}

# For Debugging
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
