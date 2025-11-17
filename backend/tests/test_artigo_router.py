import unittest
import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import db, Usuario, Evento, EdicaoEvento, Artigo
from app.router.auth_router import criar_token


SessionLocal = sessionmaker(bind=db)


class TestArtigoRouter(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.session = SessionLocal()

    def tearDown(self):
        self.session.close()

    def test_criar_listar_get_search_artigo(self):
        titulo = "Teste Artigo Unidade"
        nome_evento = "Evento Teste"
        self.session.query(Artigo).filter(Artigo.titulo == titulo).delete()
        self.session.query(EdicaoEvento).filter(EdicaoEvento.ano == 2021).delete()
        self.session.query(Evento).filter(Evento.nome == nome_evento).delete()
        self.session.query(Usuario).filter(Usuario.email == "admin_artigo@example.com").delete()
        self.session.commit()

        evento = Evento(nome_evento)
        self.session.add(evento)
        self.session.commit()
        self.session.refresh(evento)

        ed = EdicaoEvento(2021, evento.id, local="LocalTeste")
        self.session.add(ed)
        self.session.commit()
        self.session.refresh(ed)

        admin = Usuario("Admin Artigo", "admin_artigo@example.com", "plainpw", True)
        self.session.add(admin)
        self.session.commit()
        self.session.refresh(admin)

        token = criar_token(admin.id)
        headers = {"Authorization": f"Bearer {token}"}

        # Prepare a fake PDF file for upload
        pdf_bytes = b"%PDF-1.4 test pdf content\n%%EOF"
        files = {"pdf_file": ("teste.pdf", pdf_bytes, "application/pdf")}

        data = {
            "titulo": titulo,
            "autores": "Fulano da Silva and Beltrano de Souza",
            "nome_evento": nome_evento,
            "ano": "2021",
            "pagina_inicial": "1",
            "pagina_final": "10",
        }

        # Call create article endpoint
        res = self.client.post("/artigo/artigo", headers=headers, data=data, files=files)
        self.assertEqual(res.status_code, 200, msg=res.text)
        body = res.json()
        self.assertIn("mensagem", body)
        caminho_pdf = body.get("caminho_pdf")

        # Ensure the file was saved (response gives path)
        if caminho_pdf:
            self.assertTrue(os.path.exists(caminho_pdf))

        # listar_artigos_recentes
        res_recent = self.client.get("/artigo/recentes")
        self.assertEqual(res_recent.status_code, 200)
        recent_list = res_recent.json()
        self.assertIsInstance(recent_list, list)
        titles = [a.get("titulo") for a in recent_list]
        self.assertIn(titulo, titles)

        # teste integração
        artigo_obj = self.session.query(Artigo).filter(Artigo.titulo == titulo).first()
        self.assertIsNotNone(artigo_obj)
        artigo_id = artigo_obj.id

        # get_artigo
        res_get = self.client.get(f"/artigo/{artigo_id}")
        self.assertEqual(res_get.status_code, 200)
        body_get = res_get.json()
        self.assertEqual(body_get.get('titulo'), titulo)

        # search by title
        res_search = self.client.get("/artigo/artigo/search", params={"field": "titulo", "q": "Unidade"})
        self.assertEqual(res_search.status_code, 200)
        results = res_search.json()
        self.assertTrue(any(r.get('titulo') == titulo for r in results))

        # cleanup: remove created article, event, edition, user and file
        try:
            # remove file if exists
            if caminho_pdf and os.path.exists(caminho_pdf):
                os.remove(caminho_pdf)
        except Exception:
            pass

        try:
            self.session.delete(artigo_obj)
        except Exception:
            self.session.rollback()
        try:
            self.session.query(EdicaoEvento).filter(EdicaoEvento.id == ed.id).delete()
            self.session.query(Evento).filter(Evento.id == evento.id).delete()
            self.session.query(Usuario).filter(Usuario.id == admin.id).delete()
            self.session.commit()
        except Exception:
            self.session.rollback()