import unittest
import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import db, Usuario, Evento, EdicaoEvento, Artigo
from app.router.auth_router import criar_token
from app.router import artigo_router
from app.schemas import ArtigoSchema
from app.models import Subscriber


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
        # Edit the article via endpoint
        new_title = "Teste Artigo Unidade - Editado"
        edit_data = {
            "titulo": new_title,
            "autores": "Fulano da Silva and Beltrano de Souza",
            "nome_evento": nome_evento,
            "ano": "2021",
            "pagina_inicial": "2",
            "pagina_final": "12",
        }
        res_edit = self.client.post(f"/artigo/artigo/editar/{artigo_id}", headers=headers, data=edit_data)
        self.assertEqual(res_edit.status_code, 200, msg=res_edit.text)

        # verify edited
        res_get2 = self.client.get(f"/artigo/{artigo_id}")
        self.assertEqual(res_get2.status_code, 200)
        body_get2 = res_get2.json()
        self.assertEqual(body_get2.get('titulo'), new_title)

        # Remove the article via endpoint
        res_remove = self.client.post(f"/artigo/artigo/remover/{artigo_id}", headers=headers)
        self.assertEqual(res_remove.status_code, 200, msg=res_remove.text)

        # Ensure article no longer exists
        removed = self.session.query(Artigo).filter(Artigo.id == artigo_id).first()
        self.assertIsNone(removed)

        # cleanup: remove event, edition, user and any leftover file
        try:
            if caminho_pdf and os.path.exists(caminho_pdf):
                os.remove(caminho_pdf)
        except Exception:
            pass

        try:
            self.session.query(EdicaoEvento).filter(EdicaoEvento.id == ed.id).delete()
            self.session.query(Evento).filter(Evento.id == evento.id).delete()
            self.session.query(Usuario).filter(Usuario.id == admin.id).delete()
            self.session.commit()
        except Exception:
            self.session.rollback()

    def test_helper_functions_and_import_bibtex(self):
        # Test internal helpers: salvar path, extrair zip, notificar_subscribers
        tmp_src = "tmp_test_source.pdf"
        with open(tmp_src, "wb") as f:
            f.write(b"dummy pdf content")

        try:
            # test _salvar_pdf_sincrono_path
            dest_name = "copied_test.pdf"
            saved = artigo_router._salvar_pdf_sincrono_path(tmp_src, dest_name)
            self.assertTrue(os.path.exists(saved))

            # test _salvar_pdf_sincrono_file via the endpoint is covered elsewhere

            # test _extrair_zip_e_mapear_pdfs: create an in-memory zip
            import io, zipfile
            zip_bytes_io = io.BytesIO()
            with zipfile.ZipFile(zip_bytes_io, mode="w") as zf:
                zf.writestr("paper1.pdf", b"pdf1")
                zf.writestr("nested/paper2.pdf", b"pdf2")
            zip_content = zip_bytes_io.getvalue()

            mapping, temp_dir = artigo_router._extrair_zip_e_mapear_pdfs(zip_content)
            try:
                self.assertIn("paper1.pdf", mapping)
                self.assertIn("paper2.pdf", mapping)
                self.assertTrue(os.path.exists(temp_dir))
            finally:
                if os.path.exists(temp_dir):
                    import shutil as _sh
                    _sh.rmtree(temp_dir)

            # test _notificar_subscribers: create a subscriber that matches an author
            self.session.query(Subscriber).filter(Subscriber.email == "sub_notify@example.com").delete()
            sub = Subscriber("Fulano da Silva", "sub_notify@example.com")
            self.session.add(sub)
            self.session.commit()

            artigo_schema = ArtigoSchema(
                titulo="Titulo Notify",
                autores="Fulano da Silva and Outro",
                nome_evento="Evento Notify",
                ano=2020,
            )

            msgs = artigo_router._notificar_subscribers(self.session, artigo_schema)
            # should return at least one message (printed fallback)
            self.assertIsInstance(msgs, list)

        finally:
            # cleanup
            if os.path.exists(tmp_src):
                os.remove(tmp_src)
            try:
                if os.path.exists(saved):
                    os.remove(saved)
            except Exception:
                pass
            try:
                self.session.query(Subscriber).filter(Subscriber.email == "sub_notify@example.com").delete()
                self.session.commit()
            except Exception:
                self.session.rollback()

        # Integration test for importar_bibtex endpoint
        # create event and edition
        ev_name = "Evento Bibtex Teste"
        self.session.query(Artigo).filter(Artigo.nome_evento == ev_name).delete()
        self.session.query(EdicaoEvento).filter(EdicaoEvento.ano == 2018).delete()
        self.session.query(Evento).filter(Evento.nome == ev_name).delete()
        self.session.commit()

        evento = Evento(ev_name)
        self.session.add(evento)
        self.session.commit()
        self.session.refresh(evento)
        ed = EdicaoEvento(2018, evento.id)
        self.session.add(ed)
        self.session.commit()

        # admin
        admin = Usuario("Admin Bibtex", "admin_bibtex@example.com", "pw", True)
        self.session.add(admin)
        self.session.commit()
        self.session.refresh(admin)
        token = criar_token(admin.id)
        headers = {"Authorization": f"Bearer {token}"}

        # create bibtex text with a single entry key 'paperkey'
        bibtex = """@inproceedings{paperkey,
  title={Paper Title},
  author={Author One and Author Two},
  booktitle={%s},
  year={2018},
  pages={1--4}
}""" % ev_name

        # create zip with paperkey.pdf
        import io, zipfile
        zip_io = io.BytesIO()
        with zipfile.ZipFile(zip_io, mode="w") as zf:
            zf.writestr("paperkey.pdf", b"pdfcontent")
        zip_io.seek(0)

        files = {
            "bibtex_file": ("import.bib", bibtex, "text/plain"),
            "pdf_zip_file": ("pdfs.zip", zip_io.read(), "application/zip")
        }

        res = self.client.post("/artigo/artigo/importar-bibtex", headers=headers, files=files)
        self.assertEqual(res.status_code, 200, msg=res.text)
        body = res.json()
        self.assertIn("total_cadastrados", body)

        # cleanup created rows and files
        try:
            # remove any pdfs listed in response
            for t in body.get('titulos_cadastrados', []):
                pass
        finally:
            try:
                self.session.query(Artigo).filter(Artigo.nome_evento == ev_name).delete()
                self.session.query(EdicaoEvento).filter(EdicaoEvento.id == ed.id).delete()
                self.session.query(Evento).filter(Evento.id == evento.id).delete()
                self.session.query(Usuario).filter(Usuario.id == admin.id).delete()
                self.session.commit()
            except Exception:
                self.session.rollback()

    def test_authors_endpoint(self):
        # Test the /artigo/authors/{author_slug} endpoint
        author_name = "Marco Tulio Valente"
        author_slug = author_name.lower().replace(' ', '-')

        # cleanup any previous
        self.session.query(Artigo).filter(Artigo.autores.ilike(f"%{author_name}%")).delete()
        self.session.query(EdicaoEvento).filter(EdicaoEvento.ano.in_([2019, 2022])).delete()
        self.session.query(Evento).filter(Evento.nome == "Evento Authors Teste").delete()
        self.session.query(Usuario).filter(Usuario.email == "admin_authors@example.com").delete()
        self.session.commit()

        evento = Evento("Evento Authors Teste")
        self.session.add(evento)
        self.session.commit()
        self.session.refresh(evento)

        ed1 = EdicaoEvento(2019, evento.id)
        ed2 = EdicaoEvento(2022, evento.id)
        self.session.add_all([ed1, ed2])
        self.session.commit()
        self.session.refresh(ed1)
        self.session.refresh(ed2)

        admin = Usuario("Admin Authors", "admin_authors@example.com", "pw", True)
        self.session.add(admin)
        self.session.commit()
        self.session.refresh(admin)

        token = criar_token(admin.id)
        headers = {"Authorization": f"Bearer {token}"}

        pdf_bytes = b"%PDF-1.4 fake pdf\n%%EOF"
        files = {"pdf_file": ("a.pdf", pdf_bytes, "application/pdf")}

        data1 = {
            "titulo": "Artigo Autor A",
            "autores": f"{author_name} and Outro Autor",
            "nome_evento": evento.nome,
            "ano": "2019",
            "pagina_inicial": "1",
            "pagina_final": "5",
        }

        data2 = {
            "titulo": "Artigo Autor B",
            "autores": f"Outro Autor and {author_name}",
            "nome_evento": evento.nome,
            "ano": "2022",
            "pagina_inicial": "10",
            "pagina_final": "20",
        }

        res1 = self.client.post("/artigo/artigo", headers=headers, data=data1, files=files)
        self.assertEqual(res1.status_code, 200, msg=res1.text)
        res2 = self.client.post("/artigo/artigo", headers=headers, data=data2, files=files)
        self.assertEqual(res2.status_code, 200, msg=res2.text)

        # Call authors endpoint
        res_auth = self.client.get(f"/artigo/authors/{author_slug}")
        self.assertEqual(res_auth.status_code, 200)
        body = res_auth.json()
        self.assertIn('author', body)
        self.assertIn('articles_by_year', body)
        self.assertEqual(body.get('author'), author_slug.replace('-', ' '))

        years = {entry['year']: entry['articles'] for entry in body.get('articles_by_year', [])}
        self.assertIn(2019, years)
        self.assertIn(2022, years)
        titles = [a['titulo'] for lst in years.values() for a in lst]
        self.assertIn('Artigo Autor A', titles)
        self.assertIn('Artigo Autor B', titles)

        # cleanup created rows and files
        try:
            for res in (res1, res2):
                try:
                    caminho = res.json().get('caminho_pdf')
                    if caminho and os.path.exists(caminho):
                        os.remove(caminho)
                except Exception:
                    pass
        except Exception:
            pass

        try:
            self.session.query(Artigo).filter(Artigo.autores.ilike(f"%{author_name}%")).delete()
            self.session.query(EdicaoEvento).filter(EdicaoEvento.id.in_([ed1.id, ed2.id])).delete()
            self.session.query(Evento).filter(Evento.id == evento.id).delete()
            self.session.query(Usuario).filter(Usuario.id == admin.id).delete()
            self.session.commit()
        except Exception:
            self.session.rollback()