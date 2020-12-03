from fastapi import Depends, FastAPI, Header, HTTPException
from .routers import account, user

app = FastAPI()
app.include_router(account.router)
app.include_router(user.router)
