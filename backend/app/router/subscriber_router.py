from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from schemas import SubscriberSchema, ResponseSubscriberSchema
from dependencies import pegar_sessao, verificar_token
from models import Subscriber, Usuario

subscriber_router = APIRouter(prefix="/subscriber", tags=["subscriber"])

@subscriber_router.post("/", response_model=ResponseSubscriberSchema)
async def subscribe(subscriber: SubscriberSchema, session: Session = Depends(pegar_sessao)):
    existing = session.query(Subscriber).filter(Subscriber.email == subscriber.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Já existe um assinante com esse email")
    novo = Subscriber(subscriber.nome, subscriber.email)
    session.add(novo)
    session.commit()
    session.refresh(novo)
    return {"id": novo.id, "nome": novo.nome, "email": novo.email}

@subscriber_router.get("/", response_model=List[ResponseSubscriberSchema])
async def list_subscribers(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para acessar esta rota")
    subs = session.query(Subscriber).all()
    return [{"id": s.id, "nome": s.nome, "email": s.email} for s in subs]

@subscriber_router.delete("/{subscriber_id}")
async def unsubscribe(subscriber_id: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para executar esta ação")
    s = session.query(Subscriber).filter(Subscriber.id == subscriber_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Assinante não encontrado")
    session.delete(s)
    session.commit()
    return {"mensagem": "Assinante removido"}
