from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao
from models import Evento, EdicaoEvento, Artigo

edition_router = APIRouter(prefix="/edicao", tags=["edicao"])

@edition_router.get("/{nome_evento}/{ano}")
async def get_edicao_por_evento_e_ano(nome_evento: str, ano: int, session: Session = Depends(pegar_sessao)):
    """
    Retorna uma edição específica de um evento, incluindo seus artigos.
    """
    evento = session.query(Evento).filter(Evento.nome.ilike(f"{nome_evento}")).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    edicao = session.query(EdicaoEvento).filter(
        EdicaoEvento.id_evento == evento.id,
        EdicaoEvento.ano == ano
    ).first()

    if not edicao:
        raise HTTPException(status_code=404, detail="Edição não encontrada")

    artigos = session.query(Artigo).filter(Artigo.id_edicao == edicao.id).all()

    edicao_data = {
        "id": edicao.id,
        "ano": edicao.ano,
        "local": edicao.local,
        "id_evento": edicao.id_evento,
        "evento_nome": evento.nome,
        "artigos": [
            {
                "id": artigo.id,
                "titulo": artigo.titulo,
                "autores": [autor.strip() for autor in artigo.autores.split(' and ')] if artigo.autores else [],
                "resumo": "Resumo não disponível.",
                "nome_evento": artigo.nome_evento,
                "ano": artigo.ano,
                "pagina_inicial": artigo.pagina_inicial,
                "pagina_final": artigo.pagina_final,
                "caminho_pdf": artigo.caminho_pdf,
                "booktitle": artigo.booktitle,
                "publisher": artigo.publisher,
                "location": artigo.location,
                "id_edicao": artigo.id_edicao
            } for artigo in artigos
        ]
    }
    return edicao_data