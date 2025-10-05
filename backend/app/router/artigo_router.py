from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from schemas import ArtigoSchema, ResponseArtigoSchema
from dependencies import pegar_sessao, verificar_token
from models import Artigo, Usuario, Subscriber, Evento, EdicaoEvento
from typing import List, Dict, Any, Tuple, Optional 
import smtplib
import os
from email.message import EmailMessage
from starlette.concurrency import run_in_threadpool # Import necessário para assincronicidade
from utils import parse_bibtex_to_artigo_schema
import shutil # Necessário para operações de arquivo
import zipfile 
import tempfile

artigo_router = APIRouter(prefix="/artigo", tags=["artigo"])

# Diretório base onde os PDFs serão salvos
# ATENÇÃO: É recomendável usar variáveis de ambiente para o caminho em uma aplicação real.
PDF_UPLOAD_DIR = "pdfs"
os.makedirs(PDF_UPLOAD_DIR, exist_ok=True)


# FUNÇÃO AUXILIAR: Lógica de Salvamento de PDF (Síncrona)
def _salvar_pdf_sincrono_path(source_path: str, filename: str) -> str:
    """
    Salva ou move um arquivo do source_path para o diretório de uploads.
    Retorna o caminho completo do arquivo salvo.
    """
    final_path = os.path.join(PDF_UPLOAD_DIR, filename)
    try:
        # Copia o arquivo para a pasta de uploads
        shutil.copy(source_path, final_path)
        return final_path
    except Exception as e:
        raise RuntimeError(f"Falha ao salvar o arquivo no disco: {e}")

# FUNÇÃO AUXILIAR: Lógica de Salvamento de PDF (Síncrona)
def _salvar_pdf_sincrono_file(upload_file: UploadFile, filename: str) -> str:
    """
    Salva o conteúdo de UploadFile em disco de forma síncrona.
    Retorna o caminho completo do arquivo salvo.
    """
    file_path = os.path.join(PDF_UPLOAD_DIR, filename)
    try:
        # Usa 'shutil.copyfileobj' para lidar com uploads grandes de forma eficiente
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return file_path
    except Exception as e:
        # Garante que o buffer do arquivo seja 'rewind' ou tratado se necessário
        # Mas para o salvamento, o erro é mais importante
        print(f"Erro ao salvar PDF: {e}")
        # Levantar exceção aqui fará o run_in_threadpool propagá-la
        raise RuntimeError(f"Falha ao salvar o arquivo no disco: {e}")

# FUNÇÃO AUXILIAR (ADICIONADA): Descompacta e Mapeia PDFs
# FUNÇÃO AUXILIAR (ATUALIZADA): Descompacta e Mapeia PDFs
def _extrair_zip_e_mapear_pdfs(zip_file_content: bytes) -> Tuple[Dict[str, str], str]:
    """
    Descompacta o conteúdo do ZIP em um diretório temporário.
    Retorna uma tupla: (dicionário {nome_pdf: caminho_temporario}, caminho_diretório_temporário)
    O chamador é responsável por limpar o diretório temporário.
    """
    file_map: Dict[str, str] = {}
    temp_dir = tempfile.mkdtemp() # <--- O diretório temporário é criado aqui
    
    # Salva o arquivo ZIP em um local temporário para poder abri-lo
    zip_temp_path = os.path.join(temp_dir, "temp.zip")
    with open(zip_temp_path, "wb") as f:
        f.write(zip_file_content)
        
    try:
        with zipfile.ZipFile(zip_temp_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.lower().endswith('.pdf'):
                    base_filename = os.path.basename(member)
                    zip_ref.extract(member, temp_dir)
                    
                    # Garantimos o caminho completo dentro da extração
                    extracted_path = os.path.join(temp_dir, member)
                    
                    file_map[base_filename] = extracted_path
                    
        return file_map, temp_dir # <--- RETORNA O CAMINHO TEMP
    except Exception as e:
        # Se falhar durante a extração, tentamos limpar e propagamos o erro
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise RuntimeError(f"Erro ao processar arquivo ZIP: {e}")
    finally:
        # Remove o arquivo ZIP temporário, mas mantém a pasta temp_dir
        if os.path.exists(zip_temp_path):
            os.remove(zip_temp_path)

# FUNÇÃO AUXILIAR: Lógica de Notificação (mantida)
def _notificar_subscribers(session: Session, artigo_schema: ArtigoSchema):
    # ... (Lógica de notificação permanece a mesma)
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

# FUNÇÃO CORE: Lógica de Validação e Inserção (mantida)
def _cadastrar_artigo_core(session: Session, artigo_schema: ArtigoSchema) -> str:
    # ... (Lógica core de cadastro permanece a mesma)
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
    artigo_data = artigo_schema.model_dump()
    artigo_data['id_edicao'] = edicao.id
    
    # Instancia o modelo Artigo
    novo_artigo = Artigo(**artigo_data) 
    
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

# ENDPOINT: Criar artigo (ATUALIZADO PARA RECEBER PDF)
@artigo_router.post("/artigo")
async def criar_artigo(
    artigo_schema: ArtigoSchema = Depends(), # Usamos Depends() para receber o JSON do corpo
    pdf_file: UploadFile = File(..., description="Arquivo PDF do artigo"), # Recebe o arquivo
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):
    """
    Cria um único artigo, salva o PDF e faz validações de evento, edição e duplicidade.
    """
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    if pdf_file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF (application/pdf).")
        
    # Gera um nome de arquivo único/seguro (ex: ID do artigo depois do commit, mas aqui usamos o título)
    # ATENÇÃO: Em produção, um UUID ou nome seguro é preferível.
    # Por simplicidade, usamos o título.
    filename = f"{artigo_schema.titulo.lower().replace(' ', '_')}_{pdf_file.filename}"
    
    # 1. Salvar o PDF no disco (em uma thread separada)
    caminho_pdf_salvo = None
    try:
        # Salva o arquivo em disco ANTES de tentar o commit no BD
        caminho_pdf_salvo = await run_in_threadpool(_salvar_pdf_sincrono_file, pdf_file, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo PDF: {e}")
    finally:
        # Garante que o arquivo temporário do upload seja fechado
        await pdf_file.close()

    # 2. Atualiza o schema com o caminho do PDF salvo
    # Isso garante que o caminho correto seja persistido no BD
    artigo_schema.caminho_pdf = caminho_pdf_salvo
    
    # 3. Executa a lógica core de validação e adição ao BD
    try:
        # Executa a lógica core em uma thread separada para evitar bloqueio do asyncio
        titulo_cadastrado = await run_in_threadpool(_cadastrar_artigo_core, session, artigo_schema)
        
        # O commit é feito APÓS a lógica core ser bem-sucedida
        session.commit()
        
    except HTTPException:
        # Se houve erro de validação (HTTPException) no core, faz o rollback do BD e...
        session.rollback()
        # DEVE-SE TAMBÉM remover o arquivo salvo, se for o caso!
        if caminho_pdf_salvo and os.path.exists(caminho_pdf_salvo):
             os.remove(caminho_pdf_salvo)
        raise
    except Exception as e:
        session.rollback()
        if caminho_pdf_salvo and os.path.exists(caminho_pdf_salvo):
             os.remove(caminho_pdf_salvo)
        raise HTTPException(status_code=500, detail=f"Erro interno ao cadastrar artigo: {e}")

    return {"mensagem": f"Artigo {titulo_cadastrado} incluído com sucesso no evento {artigo_schema.nome_evento}",
            "caminho_pdf": caminho_pdf_salvo}

# ENDPOINT: Importar múltiplos artigos via BibTeX
@artigo_router.post("/artigo/importar-bibtex")
async def importar_bibtex(
    bibtex_file: UploadFile = File(..., description="Arquivo de texto contendo dados BibTeX"),
    pdf_zip_file: UploadFile = File(..., description="Arquivo ZIP contendo os PDFs (nomes devem corresponder à chave BibTeX)"),
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token)
):
    """
    Importa múltiplos artigos a partir de um arquivo BibTeX e um ZIP de PDFs.
    Requer que o nome do PDF no ZIP corresponda à chave BibTeX.
    """
    ALLOWED_MIME_TYPES = [
        'application/zip', 
        'application/x-zip-compressed', 
        'application/octet-stream' # Inclui o genérico para maior compatibilidade
    ]

    if pdf_zip_file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"O arquivo de PDFs deve ser um ZIP (MIME type recebido: {pdf_zip_file.content_type})."
        )
    
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    titulos_cadastrados = []
    artigos_pulados: List[Dict[str, str]] = []
    
    pdf_file_map: Dict[str, str] = {}
    # Inicializa a variável que será limpa no final
    temp_dir_to_clean: Optional[str] = None 
    
    try:
        # 1. Leitura e Parsing do BibTeX (Assíncrono)
        contents_bibtex = await bibtex_file.read()
        bibtex_data = contents_bibtex.decode('utf-8')
        
        artigos_com_meta = await run_in_threadpool(parse_bibtex_to_artigo_schema, bibtex_data)
        print("DEBUG artigos_com_meta:", artigos_com_meta)
        
        # 2. Descompactação e Mapeamento dos PDFs (Assíncrono)
        contents_zip = await pdf_zip_file.read()
        
        # CORREÇÃO DO ERRO DE DESEMPACOTAMENTO:
        # Captura o resultado como uma única tupla e depois desempacota.
        resultado_extracao = await run_in_threadpool(_extrair_zip_e_mapear_pdfs, contents_zip)
        pdf_file_map, temp_dir_to_clean = resultado_extracao
        
        # 3. Processamento de CADA Artigo
        for artigo_schema, chave_bibtex in artigos_com_meta:
            pdf_filename_esperado = f"{chave_bibtex}.pdf"  # ✅ usa o nome BibTeX
            erro_parsing = None
            identificador = chave_bibtex

            # Checagem de falha de parsing ou schema base (existente)
            if erro_parsing or artigo_schema is None:
                artigos_pulados.append({
                    "identificador": identificador, 
                    "motivo": f"Falha de validação/parsing do BibTeX: {erro_parsing or 'Schema incompleto/inválido'}."
                })
                continue
                
            # NOVO: Regra de Negócio: Ignorar artigos sem ano (se exigido)
            # A função core faz essa checagem, mas é bom dar um feedback mais específico aqui
            # se o campo está vazio, prevenindo a chamada desnecessária ao BD.
            if not artigo_schema.ano:
                artigos_pulados.append({
                    "titulo": artigo_schema.titulo,
                    "motivo": f"Artigo ignorado. O campo 'ano' está faltando ou é inválido no BibTeX."
                })
                continue

            # --- 3.2. Mapeamento e Salvamento do PDF ---
            if pdf_filename_esperado not in pdf_file_map:
                artigos_pulados.append({
                    "titulo": artigo_schema.titulo,
                    "motivo": f"Arquivo PDF '{pdf_filename_esperado}' não encontrado no ZIP."
                })
                continue
            
            source_pdf_path = pdf_file_map[pdf_filename_esperado]
            final_pdf_filename = f"{artigo_schema.nome_evento.lower()}_{pdf_filename_esperado}"
            caminho_pdf_salvo = None
            
            # Salva o arquivo permanentemente
            try:
                # CORREÇÃO LÓGICA: Deve usar _salvar_pdf_sincrono_path, pois a origem é um PATH
                caminho_pdf_salvo = await run_in_threadpool(_salvar_pdf_sincrono_path, source_pdf_path, final_pdf_filename)
                artigo_schema.caminho_pdf = caminho_pdf_salvo
            except Exception as e:
                artigos_pulados.append({
                    "titulo": artigo_schema.titulo,
                    "motivo": f"Falha ao salvar PDF no disco: {e}"
                })
                continue
                
            # --- 3.3. Cadastro no BD (em memória) ---
            try:
                # O _cadastrar_artigo_core já chama a notificação
                titulo_cadastrado = await run_in_threadpool(_cadastrar_artigo_core, session, artigo_schema)
                titulos_cadastrados.append(titulo_cadastrado)
                
            except HTTPException as e:
                artigos_pulados.append({
                    "titulo": artigo_schema.titulo,
                    "motivo": f"Erro de cadastro no BD: {e.detail}"
                })
                if caminho_pdf_salvo and os.path.exists(caminho_pdf_salvo):
                    os.remove(caminho_pdf_salvo)
                continue 
        
        # 4. Commit Único no Final
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno ou falha na transação: {e}")
    finally:
        # 5. Limpeza (CORRIGIDA)
        if temp_dir_to_clean and os.path.exists(temp_dir_to_clean):
            # Remove recursivamente o diretório temporário e todo o seu conteúdo
            shutil.rmtree(temp_dir_to_clean)
        
    # 6. Mensagem de Sucesso e Relatório
    mensagem_final = f"Importação finalizada. Total de artigos cadastrados: {len(titulos_cadastrados)}."
    
    if artigos_pulados:
        mensagem_final += f" {len(artigos_pulados)} artigo(s) foram pulados. Veja o relatório."

    return {
        "mensagem": mensagem_final, 
        "total_cadastrados": len(titulos_cadastrados), 
        "titulos_cadastrados": titulos_cadastrados,
        "total_pulados": len(artigos_pulados),
        "relatorio_erros": artigos_pulados
    }

# ... (Endpoints listar, remover, editar, pesquisar e author_home permanecem iguais)
# ENDPOINT: Remover artigo
@artigo_router.post("/artigo/remover/{id_artigo}")
async def remover_artigo(id_artigo: int, session: Session = Depends(pegar_sessao),
                       usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Você não tem autorização para fazer essa modificação")
    
    artigo = session.query(Artigo).filter(Artigo.id == id_artigo).first()
    if not artigo:
        raise HTTPException(status_code=400, detail="Não existe artigo com esse ID")
    
    # Removendo arquivo físico se existir
    if artigo.caminho_pdf and os.path.exists(artigo.caminho_pdf):
        try:
            os.remove(artigo.caminho_pdf)
        except Exception as e:
            print(f"AVISO: Falha ao remover arquivo PDF {artigo.caminho_pdf}: {e}")
    
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