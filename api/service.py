from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import solution.factory
app = FastAPI()

@app.get('/solutions/{name}')
def get_scenario(name: str, q: Optional[str]=None):
  solutions = solution.factory.all_solutions_scenarios()
  if solutions[name]:
    constructor = solutions[name][0]
    obj = constructor(scenario=None)
    # rs = dict()
    # rs['c2'] = obj.c2.to_json()
    # rs['fc'] = obj.fc.to_json()
    # rs_final = dict({name: rs})
    # return rs_final
    return obj.to_json()
  else:
    return {}
