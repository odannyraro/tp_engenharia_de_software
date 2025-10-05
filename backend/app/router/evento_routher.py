from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
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
        # Converte AnyUrl para string apenas se existir
        data['site'] = str(data['site']) if data.get('site') else None
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
    evento.entidade_promotora = evento_schema.entidade_promotora
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

@evento_router.get("/recentes")
async def listar_eventos_recentes(session: Session = Depends(pegar_sessao)):
    """
    Lista os 5 eventos mais recentes adicionados ao banco de dados.
    """
    eventos = session.query(Evento).order_by(Evento.id.desc()).limit(5).all()
    return eventos

@evento_router.get("/search")
async def pesquisar_eventos(q: str, session: Session = Depends(pegar_sessao)):
    """
    Pesquisa por eventos cujo nome contém a substring `q`.
    """
    eventos = session.query(Evento).filter(Evento.nome.ilike(f"%{q}%")).all()
    return eventos

@evento_router.get("/{nome_evento}")
async def get_evento_por_nome(nome_evento: str, session: Session = Depends(pegar_sessao)):
    """
    Retorna um evento específico pelo nome, incluindo suas edições.
    """
    evento = session.query(Evento).filter(Evento.nome.ilike(f"{nome_evento}")).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    edicoes = session.query(EdicaoEvento).filter(EdicaoEvento.id_evento == evento.id).order_by(EdicaoEvento.ano.desc()).all()

    evento_data = {
        "id": evento.id,
        "nome": evento.nome,
        "sigla": evento.sigla,
        "descricao": evento.descricao,
        "site": evento.site,
        "entidade_promotora": evento.entidade_promotora,
        "edicoes": [
            {
                "id": edicao.id,
                "ano": edicao.ano,
                "local": edicao.local,
                "id_evento": edicao.id_evento
            } for edicao in edicoes
        ]
    }
    return evento_data
