from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import SubscriberSchema, ResponseSubscriberSchema
from dependencies import pegar_sessao, verificar_token
from models import Subscriber, Usuario
from typing import List

subscriber_router = APIRouter(prefix="/subscriber", tags=["subscriber"])


@subscriber_router.post("/inscrever", response_model=ResponseSubscriberSchema)
async def inscrever(subscriber: SubscriberSchema, session: Session = Depends(pegar_sessao)):
    # cria um assinante público
    novo = Subscriber(nome=subscriber.nome, email=subscriber.email)
    session.add(novo)
    session.commit()
    return novo


@subscriber_router.get("/list", response_model=List[ResponseSubscriberSchema])
async def listar(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    # somente admin pode listar
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Acesso negado")
    return session.query(Subscriber).all()
