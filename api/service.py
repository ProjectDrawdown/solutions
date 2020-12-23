import json
import glob
import uvicorn

from typing import Optional
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

import solution.factory
from api.routers.routes import account, user, workbook, resource

app = FastAPI()
app.include_router(account.router)
app.include_router(user.router)
app.include_router(workbook.router)
app.include_router(resource.router)

# For Debugging
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
