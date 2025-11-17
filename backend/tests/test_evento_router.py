import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.models import db, Evento, Usuario, EdicaoEvento, Artigo
from sqlalchemy.orm import sessionmaker
from app.router.auth_router import criar_token

SessionLocal = sessionmaker(bind=db)

class TestEventoRouter(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.session = SessionLocal()

    def tearDown(self):
        self.session.close()

    def test_listar_eventos(self):
        res = self.client.get("/evento/recentes")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIsInstance(body, list)
        self.assertLessEqual(len(list(body)), 5)
        for item in body:
            self.assertIn("id", item)
            self.assertIn("nome", item)
            self.assertIn("sigla", item)

    def test_search_evento(self):
        res = self.client.get("/evento/search", params={"q": "Evento teste"})
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIsInstance(body, list)
        if body:
            nomes = [item.get('nome') for item in body if isinstance(item, dict)]
            self.assertIn("Evento teste", nomes)
    
    def test_search_evento_especifico(self):
        str = "Evento teste"
        res = self.client.get(f"/evento/{str}")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIsInstance(body, dict)
        if body:
            self.assertIn("Evento teste", body.get('nome'))

    def test_criar_remover_editar_evento(self):
        self.session.query(Usuario).filter(Usuario.email == "adm@example.com").delete()
        admin = Usuario("Admin", "adm@example.com", "unused-password", True)
        self.session.add(admin)
        self.session.commit()
        self.session.refresh(admin)
        token = criar_token(admin.id)
        self.assertIsNotNone(token, msg="criar_token did not return a token")

        headers = {"Authorization": f"Bearer {token}"}
        payload = {"nome": "Teste", "sigla": "ST", "entidade_promotora": "SBS"}
        payload1 = {"nome": "Teste", "sigla": "ST", "entidade_promotora": "UFF"}

        with self.subTest("criar_evento"):
            res = self.client.post("/evento/", headers=headers, json=payload)
            self.assertEqual(res.status_code, 200)
            body = res.json()
            self.assertIn("mensagem", body)
        
        with self.subTest("editar evento"):
            res = self.client.post(f"/evento/editar/{4}", headers=headers, json=payload1)
            self.assertEqual(res.status_code, 200)
            body = res.json()
            self.assertIn("mensagem", body)

        with self.subTest("remover_evento"):
            res = self.client.post(f"/evento/remover/{payload['nome']}", headers=headers)
            self.assertEqual(res.status_code, 200)
            body = res.json()
            self.assertIn("mensagem", body)

class TestEdicaoRouter(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.session = SessionLocal()

    def tearDown(self):
        self.session.close()

    def test_criar_editar_remove_edicao(self):
        self.session.query(Usuario).filter(Usuario.email == "adm@example.com").delete()
        admin = Usuario("Admin", "adm@example.com", "unused-password", True)
        self.session.add(admin)
        self.session.commit()
        self.session.refresh(admin)
        token = criar_token(admin.id)
        self.assertIsNotNone(token, msg="criar_token did not return a token")

        headers = {"Authorization": f"Bearer {token}"}

        temp_event = Evento("Evento Teste Temp", "ETT", entidade_promotora="SBS")
        self.session.add(temp_event)
        self.session.commit()
        self.session.refresh(temp_event)

        payload = {"ano": 2023, "local": "UFMG", "id_evento": temp_event.id}
        payload1 = {"ano": 2025, "local": "UFMG", "id_evento": temp_event.id}

        # criar edicao via API
        with self.subTest("criar_edicao"):
            res = self.client.post("/evento/edicao/", headers=headers, json=payload)
            self.assertEqual(res.status_code, 200)
            body = res.json()
            self.assertIn("mensagem", body)

        ed = self.session.query(EdicaoEvento).filter(EdicaoEvento.id_evento == temp_event.id, EdicaoEvento.ano == payload['ano']).first()
        self.assertIsNotNone(ed, msg="Edicao not created in DB")

        with self.subTest("editar_edicao"):
            res = self.client.post(f"/evento/edicao/editar/{ed.id}", headers=headers, json=payload1)
            self.assertEqual(res.status_code, 200)
            body = res.json()
            self.assertIn("mensagem", body)

        with self.subTest("remover_edicao"):
            res = self.client.post(f"/evento/edicao/remover/{ed.id}", headers=headers)
            self.assertEqual(res.status_code, 200)
            body = res.json()
            self.assertIn("mensagem", body)

        self.session.delete(temp_event)
        self.session.commit()

    def test_get_edicao(self):
        temp_event = Evento("Evento Teste Get", "ETG", entidade_promotora="SBS")
        self.session.add(temp_event)
        self.session.commit()
        self.session.refresh(temp_event)

        ed = EdicaoEvento(ano=2024, id_evento=temp_event.id, local="UFMG")
        self.session.add(ed)
        self.session.commit()
        self.session.refresh(ed)

        artigo = Artigo(titulo="Artigo Teste", autores="Autor A and Autor B", nome_evento=temp_event.nome, ano=2024, pagina_inicial=1, pagina_final=5, caminho_pdf=None, id_edicao=ed.id)
        self.session.add(artigo)
        self.session.commit()
        self.session.refresh(artigo)

        res = self.client.get(f"/edicao/{temp_event.nome}/{ed.ano}")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIsInstance(body, dict)
        self.assertEqual(body.get("ano"), 2024)
        self.assertEqual(body.get("evento_nome"), temp_event.nome)
        self.assertIn("artigos", body)
        self.assertIsInstance(body["artigos"], list)

        titles = [a.get("titulo") for a in body["artigos"]]
        self.assertIn("Artigo Teste", titles)
        
        self.session.delete(artigo)
        self.session.delete(ed)
        self.session.delete(temp_event)
        self.session.commit()
