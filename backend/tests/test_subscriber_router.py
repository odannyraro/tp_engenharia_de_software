import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.models import db, Subscriber, Usuario
from sqlalchemy.orm import sessionmaker
from app.router.auth_router import criar_token

# GERADOR POR IA

SessionLocal = sessionmaker(bind=db)


class TestSubscriberRouter(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.session = SessionLocal()
        self.test_email = "tester-sub@example.com"
        self.session.query(Subscriber).filter(Subscriber.email == self.test_email).delete()
        self.session.commit()

    def tearDown(self):
        try:
            self.session.query(Subscriber).filter(Subscriber.email == self.test_email).delete()
            self.session.query(Usuario).filter(Usuario.email == self.test_email).delete()
            self.session.commit()
        finally:
            self.session.close()

    def test_subscribe_public(self):
        payload = {"nome": "Teste Subscriber", "email": self.test_email}
        res = self.client.post("/subscriber/", json=payload)

        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIn("id", body)
        self.assertEqual(body["email"], self.test_email)

        sub = self.session.query(Subscriber).filter(Subscriber.email == self.test_email).first()
        self.assertIsNotNone(sub)

    def test_unsubscribe_admin(self):
        # create a subscriber to remove
        novo = Subscriber("ToRemove", self.test_email)
        self.session.add(novo)
        self.session.commit()
        self.session.refresh(novo)

        self.session.query(Usuario).filter(Usuario.email == "adm@example.com").delete()
        admin = Usuario("Admin", "adm@example.com", "unused-password", True)
        self.session.add(admin)
        self.session.commit()
        self.session.refresh(admin)

        # create a token directly for the admin user (no login request)
        token = criar_token(admin.id)
        self.assertIsNotNone(token, msg="criar_token did not return a token")

        # call delete endpoint
        headers = {"Authorization": f"Bearer {token}"}
        res = self.client.delete(f"/subscriber/{novo.id}", headers=headers)
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIn("mensagem", body)

        # ensure removed
        s = self.session.query(Subscriber).filter(Subscriber.email == self.test_email).first()
        self.assertIsNone(s)


if __name__ == "__main__":
    unittest.main()