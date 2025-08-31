from fastapi import FastAPI
from app.adapters.api import artigo_router
from app.core.config import settings # <-- IMPORTAR

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION
)

app.include_router(artigo_router.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": f"Bem-vindo à {settings.PROJECT_NAME}!"}