from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import solution.factory
app = FastAPI()
class Item(BaseModel):
  name: str
  price: float
  is_offer: Optional[bool] = None
@app.get('/')
def read_root():
  return { 'message': 'Hello World !!'}
@app.get('/items/{item_id}')
def read_item(item_id: int, q: Optional[str]=None):
  return { 'item_id': item_id, 'q': q }
@app.put('/items/{item_id}')
def update_item(item_id: int, item: Item):
  return { 'item_price': item.price, 'item_id': item_id, 'item': item }
@app.get('/solutions/{name}')
def get_scenario(name: str, q: Optional[str]=None):
  solutions = solution.factory.all_solutions_scenarios()
  if solutions[name]:
    constructor = solutions[name][0]
    obj = constructor(scenario=None)
    rs = dict()
    rs['c2'] = obj.c2.to_json()
    rs['fc'] = obj.fc.to_json()
    rs_final = dict({name: rs})
    return rs_final
  else:
    return {}
