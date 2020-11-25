from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

import json
import glob
import pathlib

app = FastAPI()
DATADIR = pathlib.Path(__file__).parents[0].joinpath('data')

@app.get('/scenarios/{cannonical}')
def scenario_group(cannonical: str):
    directory = DATADIR
    for filename in glob.glob(str(directory.joinpath('*.json'))):
        with open(filename, 'r') as fid:
            j = json.loads(fid.read())
            js = j.copy()
    return {cannonical: js[cannonical]}
