import json
import glob
import uvicorn

from typing import Optional
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from fastapi_plugins import redis_plugin

import solution.factory
from api.config import get_settings, RedisSettings

from api.routers.routes import (
    account, 
    user, 
    workbook, 
    resource,
    vma,
    projection
)

app = FastAPI()
app.include_router(account.router)
app.include_router(user.router)
app.include_router(workbook.router)
app.include_router(resource.router)
app.include_router(vma.router)
app.include_router(projection.router)

redis_config = RedisSettings()

@app.on_event('startup')
async def on_startup() -> None:
    await redis_plugin.init_app(app, config=redis_config)
    await redis_plugin.init()

@app.on_event('shutdown')
async def on_shutdown() -> None:
    await redis_plugin.terminate()

# For Debugging
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
