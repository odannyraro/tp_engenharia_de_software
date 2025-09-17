from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import ArtigoSchema, ResponseArtigoSchema
from dependencies import pegar_sessao, verificar_token
from models import Artigo, Usuario, EdicaoEvento, Evento
from typing import List

artigo_router = APIRouter(prefix="/artigo", tags=["artigo"])

@artigo_router.get("/")
async def home():
    """
    Rota padrão para artigos
    """
    return {"mensagem": "Você acessou a rota padrão para artigos"}

@artigo_router.post("/artigo")
async def criar_artigo(artigo_schema: ArtigoSchema, session: Session = Depends(pegar_sessao),
                       usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    edicao = session.query(EdicaoEvento).filter(EdicaoEvento.id == artigo_schema.id_edicao).first()
    if not edicao:
        raise HTTPException(status_code=400, detail=f"Não existe essa edicao ({artigo_schema.id_edicao}) no artigo que está tentado registrar")
    
    artigo = session.query(Artigo).filter((Artigo.titulo == artigo_schema.titulo) & (Artigo.id_edicao == artigo_schema.id_edicao)).first()
    if artigo:
        raise HTTPException(status_code=400, detail=f"Já existe artigo com esse título {artigo_schema.titulo} na edição {artigo_schema.id_edicao}")

    evento = session.query(Evento).filter(Evento.id == edicao.id_evento).first()
    novo_artigo = Artigo(**artigo_schema.model_dump())
    session.add(novo_artigo)
    session.commit()
    return {"mensagem": f"Artigo {artigo_schema.titulo} incluido na edição {artigo_schema.id_edicao} em {evento.nome}"}

@artigo_router.post("/artigo/remover/{id_artigo}")
async def remover_artigo(id_artigo: int, session: Session = Depends(pegar_sessao),
                       usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    artigo = session.query(Artigo).filter(Artigo.id == id_artigo).first()
    if not artigo:
        raise HTTPException(status_code=400, detail="Não existe artigo com esse ID")
    
    session.delete(artigo)
    session.commit()
    return {"mensagem": f"artigo '{id_artigo}' removido com sucesso",
            "Artigo": artigo}

@artigo_router.post("/artigo/editar/{id_artigo}")
async def editar_artigo(id_artigo: int, artigo_schema: ArtigoSchema, session: Session = Depends(pegar_sessao),
                       usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    artigo = session.query(Artigo).filter(Artigo.id == id_artigo).first()
    if not artigo:
        raise HTTPException(status_code=400, detail="Não existe artigo com esse ID")
    
    evento = session.query(EdicaoEvento).filter(EdicaoEvento.id == artigo_schema.id_edicao).first()
    if not evento:
        raise HTTPException(status_code=400, detail="Não existe essa edicao no artigo que esta tentando editar")
    
    for key, value in artigo_schema.model_dump().items():
        setattr(artigo, key, value)
    session.commit()
    return {"mensagem": f"Artigo '{id_artigo}' editado com sucesso"}

@artigo_router.get("/artigo/pesquisa-titulo", response_model=List[ResponseArtigoSchema])
async def pesquisa_titulo(titulo: str, session: Session = Depends(pegar_sessao)):
    result_artigos = session.query(Artigo).filter(Artigo.titulo.contains(titulo)).all()
    if not result_artigos:
        raise HTTPException(status_code=400, detail="Não existe artigo com esse título")
    return result_artigos

@artigo_router.get("/artigo/pesquisa-evento", response_model=List[ResponseArtigoSchema])
async def pesquisa_evento(evento_nome: str, session: Session = Depends(pegar_sessao)):
    evento_pesquisado = session.query(Evento).filter(Evento.nome == evento_nome).first()
    if not evento_pesquisado:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    edicoes = session.query(EdicaoEvento).filter(EdicaoEvento.id_evento == evento_pesquisado.id).all()
    edicoes_ids = [e.id for e in edicoes]
    result_artigos = session.query(Artigo).filter(Artigo.id_edicao.in_(edicoes_ids)).all()
    return result_artigos

@artigo_router.get("/artigo/pesquisa-autor", response_model=List[ResponseArtigoSchema])
async def pesquisa_autor(Nome: str, Sobrenome: str, session: Session = Depends(pegar_sessao)):
    result_artigos = session.query(Artigo).filter(Artigo.autor.contains(f"{Sobrenome}, {Nome}")).all()
    if not result_artigos:
        raise HTTPException(status_code=400, detail="Não existe artigo com esse autor")
    return result_artigos