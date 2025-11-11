import unittest
from fastapi.testclient import TestClient
from app.main import app, bcrypt_context
from app.models import db, Subscriber, Usuario
from sqlalchemy.orm import sessionmaker
from app.router.auth_router import criar_token

SessionLocal = sessionmaker(bind=db)


class TestSubscriberRouter(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.session = SessionLocal()
        self.test_email = "tester-sub@example.com"
        self.session.query(Subscriber).filter(Subscriber.email == self.test_email).delete()
        self.session.commit()

    def tearDown(self):
        # cleanup any created subscriber or admin
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

        # ensure an admin user exists for this test
        hashed = bcrypt_context.hash("123456")
        admin = Usuario("Admin", "adm@example.com", hashed, True)
        # remove any existing admin with that email first
        self.session.query(Usuario).filter(Usuario.email == "adm@example.com").delete()
        self.session.add(admin)
        self.session.commit()

        # login using JSON body as the endpoint expects
        res = self.client.post("/auth/login", json={"email": "adm@example.com", "senha": "123456"})
        body = res.json()
        token = body.get("access_token")
        self.assertIsNotNone(token, msg=f"Login failed, response: {body}")

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