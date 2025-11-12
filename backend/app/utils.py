import bibtexparser
from bibtexparser.customization import convert_to_unicode
from app.schemas import ArtigoSchema  # Assumindo que schemas é importável
from typing import List # Novo import necessário para o tipo de retorno

# A função agora retorna uma lista de ArtigoSchema
def parse_bibtex_to_artigo_schema(bibtex_text: str):
    from bibtexparser import loads
    bib_database = loads(bibtex_text)
    
    artigos = []
    for entry in bib_database.entries:
        chave = entry.get("ID") or entry.get("key")  # "sbes-paper3"
        
        artigo = ArtigoSchema(
            titulo=entry.get("title"),
            autores=entry.get("author"),
            nome_evento=entry.get("booktitle"),
            ano=int(entry["year"]) if "year" in entry else None,
            pagina_inicial=int(entry["pages"].split("--")[0]) if "pages" in entry and "--" in entry["pages"] else None,
            pagina_final=int(entry["pages"].split("--")[1]) if "pages" in entry and "--" in entry["pages"] else None,
            caminho_pdf=None,
            booktitle=entry.get("booktitle"),
            publisher=entry.get("publisher"),
            location=entry.get("location"),
        )

        artigos.append((artigo, chave))  # ✅ retorna a chave junto

    return artigos