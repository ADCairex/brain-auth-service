from fastapi import FastAPI

from .database import Base, engine
from .endpoints.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Brain Auth Service", version="0.1.0")

app.include_router(auth_router)
