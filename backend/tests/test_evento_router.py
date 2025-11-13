import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.models import db, Subscriber, Usuario
from sqlalchemy.orm import sessionmaker
from app.router.auth_router import criar_token

SessionLocal = sessionmaker(bind=db)

class TestEventoRouter(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.session = SessionLocal()

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