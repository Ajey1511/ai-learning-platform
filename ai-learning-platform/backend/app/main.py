from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.core.config import settings
from app.db import Base, engine
from app import models  # noqa: F401
from app.seed import seed

app = FastAPI(title=settings.app_name, version="1.0.0", description="Competency gap analysis and explainable personalized learning recommendations")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix=settings.api_v1_prefix)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed()

@app.get("/health")
def health(): return {"status":"ok"}
