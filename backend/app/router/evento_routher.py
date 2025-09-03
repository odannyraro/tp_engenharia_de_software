from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import EventoSchema, EdicaoEventoSchema
from dependencies import pegar_sessao, verificar_token
from models import Evento, Usuario, EdicaoEvento

evento_router = APIRouter(prefix="/evento", tags=["evento"])

@evento_router.get("/")
async def home():
    """
    Rota padrão para eventos  
    """
    return {"mensagem": "Você acessou a rota padrão para eventos"}

@evento_router.post("/evento")
async def criar_evento(evento_schema: EventoSchema, session: Session = Depends(pegar_sessao),
                       usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    evento = session.query(Evento).filter(Evento.nome == evento_schema.nome).first()
    if evento:
        raise HTTPException(status_code=400, detail="Já existe evento com esse nome")
    else:
        data = evento_schema.model_dump()
        data['site'] = str(data['site'])  # Converte AnyUrl para string
        novo_evento = Evento(**data)
        session.add(novo_evento)
        session.commit()
        return {"mensagem": f"Evento {evento_schema.nome} criado com sucesso"}
    

@evento_router.post("/evento/remover/{nome_evento}")
async def remover_evento(nome_evento: str, session: Session = Depends(pegar_sessao),
                       usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    evento = session.query(Evento).filter(Evento.nome == nome_evento).first()
    if not evento:
        raise HTTPException(status_code=400, detail="Não existe evento com esse nome")
    session.delete(evento)
    session.commit()
    return {"mensagem": f"Evento '{nome_evento}' removido com sucesso"}


@evento_router.post("/evento/editar/{id_evento}")
async def editar_evento(id_evento: int, evento_schema: EventoSchema, session: Session = Depends(pegar_sessao),
                       usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    evento = session.query(Evento).filter(Evento.id == id_evento).first()
    if not evento:
        raise HTTPException(status_code=400, detail="Não existe evento com esse ID")
    
    evento.nome = evento_schema.nome
    evento.sigla = evento_schema.sigla
    evento.descricao = evento_schema.descricao
    evento.site = str(evento_schema.site) if evento_schema.site else None
    session.commit()
    return {"mensagem": f"Evento '{evento_schema.nome}' editado com sucesso"}


@evento_router.post("/evento/edicao/")
async def nova_edicao(edicao_schema: EdicaoEventoSchema, sessao: Session = Depends(pegar_sessao),
                      usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    evento = sessao.query(Evento).filter(Evento.id == edicao_schema.id_evento).first()
    if not evento:
        raise HTTPException(status_code=400, detail="Evento não encontrado")
    
    edicao = EdicaoEvento(**edicao_schema.model_dump())
    sessao.add(edicao)
    sessao.commit()

    return {"mensagem": f"Nova edição do evento {evento.nome} criada"}

@evento_router.post("/evento/edicao/remover/{id_edicao}")
async def remover_edicao(id_edicao: int, sessao: Session = Depends(pegar_sessao),
                      usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    edicao = sessao.query(EdicaoEvento).filter(EdicaoEvento.id == id_edicao).first()
    if not edicao:
        raise HTTPException(status_code=400, detail="Edicao não encontrado")
    
    evento = sessao.query(Evento).filter(Evento.id == edicao .id_evento).first()
    sessao.delete(edicao)
    sessao.commit()
    return {'mensagem': f"Removido edição {id_edicao} do evento {evento.nome}"}


@evento_router.post("/evento/edicao/editar/{id_edicao}")
async def editar_edicao(id_edicao: int, edicao_schema: EdicaoEventoSchema, session: Session = Depends(pegar_sessao),
                       usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    edicao = session.query(EdicaoEvento).filter(EdicaoEvento.id == id_edicao).first()
    if not edicao:
        raise HTTPException(status_code=400, detail="Não existe edicao com esse ID")
    
    evento = session.query(Evento).filter(Evento.id == edicao_schema.id_evento).first()
    if not evento:
        raise HTTPException(status_code=400, detail=f"Não existe evento de ID {edicao_schema.id_evento}")
    
    edicao.ano = edicao_schema.ano
    edicao.local = edicao_schema.local
    edicao.id_evento = edicao_schema.id_evento
    session.commit()
    return {"mensagem": f"Edição {id_edicao} editada com sucesso"}