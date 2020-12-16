import json
import glob
import uvicorn

from typing import Optional
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from functools import lru_cache

import solution.factory
from model.data_handler import DataHandler
from api.routers import account, user, workbook, scenerios

app = FastAPI()
app.include_router(account.router)
app.include_router(user.router)
app.include_router(workbook.router)
app.include_router(scenerios.router)

# For Debugging
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
