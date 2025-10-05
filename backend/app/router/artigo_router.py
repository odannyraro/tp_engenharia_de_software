from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from schemas import ArtigoSchema, ResponseArtigoSchema
from dependencies import pegar_sessao, verificar_token
from models import Artigo, Usuario, Subscriber, Evento, EdicaoEvento
from typing import List
from fastapi import Query
from typing import Dict, Any
import smtplib
import os
from email.message import EmailMessage
from starlette.concurrency import run_in_threadpool # Import necessário para assincronicidade
from utils import parse_bibtex_to_artigo_schema # Ajustado o import

artigo_router = APIRouter(prefix="/artigo", tags=["artigo"])

# FUNÇÃO AUXILIAR: Lógica de Notificação
def _notificar_subscribers(session: Session, artigo_schema: ArtigoSchema):
    """
    Notifica subscribers cujo nome case exatamente com algum autor do artigo.
    Mantida síncrona, deve ser chamada via threadpool se for muito lenta.
    """
    try:
        subscribers = session.query(Subscriber).all()
        artigo_autores = artigo_schema.autores

        def normalize(name: str):
            return ' '.join(name.strip().split())

        autores_list = [p.strip() for p in artigo_autores.split(' and ') if p.strip()]

        matched = []
        for sub in subscribers:
            sub_name = normalize(sub.nome)
            for a in autores_list:
                a_norm = normalize(a)
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
        # Esta função não deve levantar exceção para não quebrar a transação de BD

# FUNÇÃO CORE: Lógica de Validação e Inserção
def _cadastrar_artigo_core(session: Session, artigo_schema: ArtigoSchema) -> str:
    """
    Realiza a validação de evento/edição, verifica duplicidade e adiciona 
    um ArtigoSchema à sessão do banco de dados (sem commit).
    Retorna o título do artigo cadastrado.
    """
    # 1. Verifica se o evento existe
    evento = session.query(Evento).filter(Evento.nome == artigo_schema.nome_evento).first()
    if not evento:
        raise HTTPException(status_code=400, detail=f"Evento '{artigo_schema.nome_evento}' não encontrado")

    edicao = None
    
    if artigo_schema.ano:
        # Se o ANO for fornecido no ArtigoSchema, compara o ID do Evento E o Ano.
        edicao = session.query(EdicaoEvento).filter(
            (EdicaoEvento.id_evento == evento.id) & (EdicaoEvento.ano == artigo_schema.ano)
        ).first()
        
        # Se o ano é fornecido, mas a edição específica não existe, levanta erro.
        if not edicao:
            raise HTTPException(status_code=400, detail=f"Não existe edição do evento '{evento.nome}' no ano {artigo_schema.ano}")
            
    else:
        # Se o ANO NÃO for fornecido, compara APENAS o ID do Evento.
        # Isto retornará a primeira edição encontrada (geralmente a mais antiga ou a primeira a ser inserida no BD).
        # ATENÇÃO: Se houver várias edições sem ano, o resultado é arbitrário (o primeiro encontrado).
        edicao = session.query(EdicaoEvento).filter(
            EdicaoEvento.id_evento == evento.id
        ).first()

        # Se não houver ANO e nenhuma edição for encontrada para o evento, levanta erro.
        if not edicao:
            raise HTTPException(status_code=400, detail=f"Não existe edição cadastrada para o evento '{evento.nome}' (ano não especificado).")
            
    
    # Verifica duplicidade pelo par (titulo, id_edicao)
    artigo = session.query(Artigo).filter((Artigo.titulo == artigo_schema.titulo) & (Artigo.id_edicao == edicao.id)).first()
    if artigo:
        raise HTTPException(status_code=400, detail=f"Artigo com título '{artigo_schema.titulo}' já cadastrado na edição {edicao.id}.")

    # 4. Criação do novo artigo e add à session
    # Obtém o dicionário de dados do ArtigoSchema
    artigo_data = artigo_schema.model_dump()
    
    # Adiciona o campo validado 'id_edicao' ao dicionário de dados
    artigo_data['id_edicao'] = edicao.id
    
    # A maneira mais limpa de instanciar o modelo Artigo.
    # Isso garante que todos os campos do schema Pydantic sejam mapeados.
    novo_artigo = Artigo(**artigo_data) # <--- MUDANÇA PRINCIPAL AQUI
    
    session.add(novo_artigo)
    
    # 5. Notificação
    _notificar_subscribers(session, artigo_schema)
    
    return novo_artigo.titulo

# =========================================================================
# ENDPOINTS (ASSÍNCRONOS)
# =========================================================================

@artigo_router.get("/")
async def home():
    """
    Rota padrão para artigos
    """
    return {"mensagem": "Você acessou a rota padrão para artigos"}

# ENDPOINT: Criar artigo
@artigo_router.post("/artigo")
async def criar_artigo(artigo_schema: ArtigoSchema, session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)):
    """
    Cria um único artigo após validações de evento, edição e duplicidade.
    """
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    try:
        # Executa a lógica core em uma thread separada para evitar bloqueio do asyncio
        titulo_cadastrado = await run_in_threadpool(_cadastrar_artigo_core, session, artigo_schema)
        
        # O commit é feito APÓS a lógica core ser bem-sucedida
        session.commit()
        
    except HTTPException:
        # Em caso de erro de validação (HTTPException), faz o rollback e relança o erro.
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno ao cadastrar artigo: {e}")

    return {"mensagem": f"Artigo {titulo_cadastrado} incluído com sucesso no evento {artigo_schema.nome_evento}"}

# ENDPOINT: Importar múltiplos artigos via BibTeX
@artigo_router.post("/artigo/importar-bibtex")
async def importar_bibtex(
    bibtex_file: UploadFile = File(..., description="Arquivo de texto contendo dados BibTeX"),
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):
    """
    Importa múltiplos artigos a partir de um arquivo .bib ou .txt, reutilizando a lógica de criação.
    """
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    # 1. Leitura e Parsing do BibTeX (Assíncrono via threadpool)
    try:
        contents = await bibtex_file.read()
        bibtex_data = contents.decode('utf-8') 
        
        # O parser é chamado na threadpool, retornando uma LISTA de ArtigoSchema
        artigos_data_list = await run_in_threadpool(parse_bibtex_to_artigo_schema, bibtex_data)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Erro de validação ou formato do BibTeX: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar o arquivo BibTeX: {e}")
        
    # 2. Cadastramento de TODOS os Artigos (Transação Atômica)
    titulos_cadastrados = []
    
    try:
        for artigo_schema in artigos_data_list:
            # Chama a lógica central de cadastro para CADA artigo na lista
            titulo_cadastrado = _cadastrar_artigo_core(session, artigo_schema)
            titulos_cadastrados.append(titulo_cadastrado)
        
        # 3. Commit Único no Final
        # Se TUDO deu certo (nenhuma HTTPException), salva todos no BD
        session.commit()
        
    except HTTPException as e:
        # Se QUALQUER artigo falhar na validação, faz o rollback de todos os adds
        session.rollback()
        raise e 
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno ao cadastrar múltiplos artigos: {e}")

    # 4. Mensagem de Sucesso
    mensagem_final = f"Sucesso! Foram importados {len(titulos_cadastrados)} artigos do arquivo '{bibtex_file.filename}'."
    
    return {"mensagem": mensagem_final, "total_importados": len(titulos_cadastrados), "titulos": titulos_cadastrados}

# ENDPOINT: Remover artigo
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

# ENDPOINT: Editar artigo
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

# ENDPOINT: Listar artigos mais recentes
@artigo_router.get("/recentes", response_model=List[ResponseArtigoSchema])
async def listar_artigos_recentes(session: Session = Depends(pegar_sessao)):
    """
    Lista os 5 artigos mais recentes adicionados ao banco de dados.
    """
    artigos = session.query(Artigo).order_by(Artigo.id.desc()).limit(5).all()
    return artigos


# ENDPOINT: Pesquisa unificada
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


@artigo_router.get('/authors/{author_slug}')
async def author_home(author_slug: str, session: Session = Depends(pegar_sessao)) -> Dict[str, Any]:
    """
    Página do autor: lista os artigos daquele autor organizados por ano (sem paginação).
    URL exemplo: /authors/marco-tulio-valente
    Observação: não fazemos aliasing — o slug é convertido em nome simples (troca '-' por ' ').
    """
    def normalize_name(s: str) -> str:
        return ' '.join(s.replace('-', ' ').strip().split()).lower()

    search_name = normalize_name(author_slug)

    # Busca candidatos por ilike para reduzir o conjunto e depois filtra por igualdade normalizada
    candidates = session.query(Artigo).filter(Artigo.autores.ilike(f"%{search_name}%")).all()

    matched = []
    for art in candidates:
        autores_list = [a.strip() for a in (art.autores or '').split(' and ') if a.strip()]
        for a in autores_list:
            if normalize_name(a) == search_name:
                matched.append(art)
                break

    # Agrupa por ano
    grouped: Dict[Any, list] = {}
    for art in matched:
        year = art.ano if getattr(art, 'ano', None) is not None else 'Unknown'
        grouped.setdefault(year, []).append(art)

    # Ordena anos desc (Unknown por último)
    years = [y for y in grouped.keys() if y != 'Unknown']
    years.sort(reverse=True)
    if 'Unknown' in grouped:
        years.append('Unknown')

    result = {
        'author': author_slug.replace('-', ' '),
        'articles_by_year': []
    }

    for y in years:
        arts = grouped[y]
        arts_sorted = sorted(arts, key=lambda x: (x.ano if x.ano is not None else -1, (x.titulo or '').lower()), reverse=True)
        serialized = [
            {
                'titulo': a.titulo,
                'autores': a.autores,
                'nome_evento': a.nome_evento,
                'ano': a.ano,
                'pagina_inicial': a.pagina_inicial,
                'pagina_final': a.pagina_final,
                'caminho_pdf': a.caminho_pdf,
                'booktitle': getattr(a, 'booktitle', None),
                'publisher': getattr(a, 'publisher', None),
                'location': getattr(a, 'location', None),
                'id_edicao': getattr(a, 'id_edicao', None)
            }
            for a in arts_sorted
        ]
        result['articles_by_year'].append({'year': y, 'articles': serialized})

    return result