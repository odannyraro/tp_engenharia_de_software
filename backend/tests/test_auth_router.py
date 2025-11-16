import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.models import db, Usuario, EdicaoEvento, Artigo
from sqlalchemy.orm import sessionmaker
from app.router.auth_router import criar_token

# 50% IA

SessionLocal = sessionmaker(bind=db)

class TestAuthRouter(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.session = SessionLocal()
    
    def tearDown(self):
        self.session.close()

    def test_usuario_info(self):
        self.session.query(Usuario).filter(Usuario.email == "adm@example.com").delete()
        admin = Usuario("Admin", "adm@example.com", "unused-password", True)
        self.session.add(admin)
        self.session.commit()
        self.session.refresh(admin)
        token = criar_token(admin.id)
        self.assertIsNotNone(token, msg="criar_token did not return a token")

        headers = {"Authorization": f"Bearer {token}"}

        with self.subTest("Pegar info usuario"):
            res = self.client.get("/auth/me", headers=headers)
            self.assertEqual(res.status_code, 200)
            body = res.json()
            self.assertIn("Admin", body.get('nome'))

        with self.subTest("Refresh token"):
            res = self.client.get("/auth/refresh", headers=headers)
            self.assertEqual(res.status_code, 200)
            body = res.json()
            self.assertIn("access_token", body)
            self.assertIn("token_type", body)

    def test_criar_conta_login(self):
        # Monkeypatch the bcrypt_context used by the app to avoid system bcrypt dependency
        import app.main as app_main

        original_bcrypt = getattr(app_main, "bcrypt_context", None)

        class DummyBcrypt:
            def hash(self, value: str) -> str:
                return value

            def verify(self, plain: str, hashed: str) -> bool:
                return plain == hashed

        app_main.bcrypt_context = DummyBcrypt()

        test_email = "testuser@example.com"
        try:
            payload = {
                "nome": "Test User",
                "email": test_email,
                "senha": "secret-password",
                "admin": False,
            }

            # Create account
            res = self.client.post("/auth/criar_conta", json=payload)
            self.assertEqual(res.status_code, 200, msg=res.text)
            body = res.json()
            self.assertIn("mensagem", body)

            # Login with created account
            login_payload = {"email": test_email, "senha": "secret-password"}
            res2 = self.client.post("/auth/login", json=login_payload)
            self.assertEqual(res2.status_code, 200, msg=res2.text)
            body2 = res2.json()
            self.assertIn("access_token", body2)
            self.assertIn("refresh_token", body2)
            self.assertIn("user", body2)
        finally:
            # cleanup created user and restore bcrypt_context
            try:
                self.session.query(Usuario).filter(Usuario.email == test_email).delete()
                self.session.commit()
            except Exception:
                self.session.rollback()
            if original_bcrypt is not None:
                app_main.bcrypt_context = original_bcrypt
            else:
                delattr(app_main, "bcrypt_context")