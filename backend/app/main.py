from fastapi import FastAPI
from app.adapters.api import artigo_router

app = FastAPI(
    title="API da Biblioteca Digital",
    description="Projeto para a disciplina de Engenharia de Software.",
    version="1.0.0"
)

# Inclui as rotas definidas no router
app.include_router(artigo_router.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API da Biblioteca Digital!"}