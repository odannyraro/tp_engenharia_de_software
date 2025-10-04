from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import ArtigoSchema, ResponseArtigoSchema
from dependencies import pegar_sessao, verificar_token
from models import Artigo, Usuario, Subscriber, Evento, EdicaoEvento
from typing import List
from fastapi import Query
import smtplib
import os
from email.message import EmailMessage

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
    
    # Verifica se o evento existe
    evento = session.query(Evento).filter(Evento.nome == artigo_schema.nome_evento).first()
    if not evento:
        raise HTTPException(status_code=400, detail=f"Evento '{artigo_schema.nome_evento}' não encontrado")

    # Verifica se existe uma edição desse evento com o mesmo ano do artigo
    if not artigo_schema.ano:
        raise HTTPException(status_code=400, detail="O campo 'ano' é obrigatório para verificar a edição correspondente")
    edicao = session.query(EdicaoEvento).filter((EdicaoEvento.id_evento == evento.id) & (EdicaoEvento.ano == artigo_schema.ano)).first()
    if not edicao:
        raise HTTPException(status_code=400, detail=f"Não existe edição do evento '{evento.nome}' no ano {artigo_schema.ano}")

    # Verifica duplicidade pelo par (titulo, id_edicao)
    artigo = session.query(Artigo).filter((Artigo.titulo == artigo_schema.titulo) & (Artigo.id_edicao == edicao.id)).first()
    if artigo:
        raise HTTPException(status_code=400, detail=f"Já existe artigo com esse título {artigo_schema.titulo} na edição {edicao.id}")
    # Map fields explicitly to avoid accepting unexpected legacy keys
    artigo_data = artigo_schema.model_dump()
    novo_artigo = Artigo(
        titulo=artigo_data.get('titulo'),
        autores=artigo_data.get('autores'),
        nome_evento=artigo_data.get('nome_evento'),
        ano=artigo_data.get('ano'),
        pagina_inicial=artigo_data.get('pagina_inicial'),
        pagina_final=artigo_data.get('pagina_final'),
        caminho_pdf=artigo_data.get('caminho_pdf'),
        booktitle=artigo_data.get('booktitle'),
        publisher=artigo_data.get('publisher'),
        location=artigo_data.get('location'),
        id_edicao=edicao.id
    )
    session.add(novo_artigo)
    session.commit()
    # Notificar usuários inscritos
    try:
        # Notifica subscribers públicos cujo nome case exatamente com algum autor do artigo
        subscribers = session.query(Subscriber).all()
        # autores no formato armazenado: Artigo.autores é uma string com 'Nome Sobrenome and Outro Autor'
        artigo_autores = artigo_schema.autores

        # Normalize: cria variantes para comparação
        def normalize(name: str):
            return ' '.join(name.strip().split())

        autores_list = [p.strip() for p in artigo_autores.split(' and ') if p.strip()]

        matched = []
        for sub in subscribers:
            sub_name = normalize(sub.nome)
            for a in autores_list:
                a_norm = normalize(a)
                # comparação direta (formato atual: 'Nome Sobrenome')
                if a_norm.lower() == sub_name.lower():
                    matched.append(sub)
                    break

        if matched:
            smtp_host = os.getenv('SMTP_HOST')
            smtp_port = int(os.getenv('SMTP_PORT')) if os.getenv('SMTP_PORT') else None
            smtp_user = os.getenv('SMTP_USER')
            smtp_pass = os.getenv('SMTP_PASS')
            subject = f"Novo artigo: {artigo_schema.titulo}"
            body = (
                f"Foi publicado um novo artigo '{artigo_schema.titulo}' no evento {artigo_schema.nome_evento}.\n\n"
                f"Autores: {artigo_schema.autores}\n"
                f"Ano: {artigo_schema.ano or 'N/A'}\n"
                f"Local: {artigo_schema.location or 'N/A'}\n"
                f"Páginas: {artigo_schema.pagina_inicial or 'N/A'}-{artigo_schema.pagina_final or 'N/A'}\n"
                f"PDF: {artigo_schema.caminho_pdf or 'N/A'}"
            )
            if smtp_host and smtp_port:
                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From'] = smtp_user or 'no-reply@example.com'
                msg.set_content(body)
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    if smtp_user and smtp_pass:
                        server.starttls()
                        server.login(smtp_user, smtp_pass)
                    for u in matched:
                        msg['To'] = u.email
                        server.send_message(msg)
            else:
                for u in matched:
                    print(f"[NOTIFY] Enviar email para {u.email}: {subject} - {body}")
    except Exception as e:
        print(f"Erro ao notificar subscribers: {e}")
    return {"mensagem": f"Artigo {artigo_schema.titulo} incluido no evento {artigo_schema.nome_evento}"}

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
    
    # Atualiza somente os campos definidos no novo esquema
    for key, value in artigo_schema.model_dump().items():
        setattr(artigo, key, value)
    session.commit()
    return {"mensagem": f"Artigo '{id_artigo}' editado com sucesso"}

# Removed per-field search endpoints in favor of the unified /artigo/search endpoint


@artigo_router.get("/artigo/search", response_model=List[ResponseArtigoSchema])
async def pesquisa_unificada(field: str = Query(..., description="Campo a pesquisar: titulo, autor, evento"),
                              q: str = Query(..., description="Substring a procurar"),
                              session: Session = Depends(pegar_sessao)):
    """
    Pesquisa unificada por artigo. `field` deve ser um de: 'titulo', 'autor', 'evento'.
    Retorna todos os artigos cujo campo contém a substring `q` (case-insensitive).
    """
    field = field.lower()
    q = q.strip()
    if field not in ("titulo", "autor", "evento"):
        raise HTTPException(status_code=400, detail="Campo inválido. Use 'titulo', 'autor' ou 'evento'.")

    if field == "titulo":
        resultados = session.query(Artigo).filter(Artigo.titulo.ilike(f"%{q}%")).all()
    elif field == "autor":
        resultados = session.query(Artigo).filter(Artigo.autores.ilike(f"%{q}%")).all()
    else:  # evento
        resultados = session.query(Artigo).filter(Artigo.nome_evento.ilike(f"%{q}%")).all()

    return resultados