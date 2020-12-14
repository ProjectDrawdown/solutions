from functools import lru_cache
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from api.routers import account, user

import uvicorn

app = FastAPI()
app.include_router(account.router)
app.include_router(user.router)

# For Debugging
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
