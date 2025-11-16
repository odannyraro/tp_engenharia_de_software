import unittest
from app.dependencies import pegar_sessao, verificar_token
from app.models import Usuario, db
from sqlalchemy.orm import sessionmaker, Session
from app.router.auth_router import criar_token
from fastapi import HTTPException

# GERADO IA

SessionLocal = sessionmaker(bind=db)


class TestDependencies(unittest.TestCase):
    def test_pegar_sessao_returns_session(self):
        gen = pegar_sessao()
        session = next(gen)
        # session should be a SQLAlchemy Session
        self.assertIsInstance(session, Session)
        # close the generator to ensure cleanup path runs
        try:
            gen.close()
        except Exception:
            pass

    def test_verificar_token_valid(self):
        session = SessionLocal()
        session.query(Usuario).filter(Usuario.email == 'dep-test@example.com').delete()
        session.commit()

        user = Usuario('Dep Test', 'dep-test@example.com', 'pwd', True)
        session.add(user)
        session.commit()
        session.refresh(user)

        token = criar_token(user.id)
        returned = verificar_token(token, session)
        self.assertEqual(returned.id, user.id)

        session.delete(user)
        session.commit()
        session.close()

    def test_verificar_token_invalid(self):
        session = SessionLocal()
        with self.assertRaises(HTTPException) as cm:
            verificar_token('this-is-not-a-token', session)
        self.assertEqual(cm.exception.status_code, 401)
        session.close()


if __name__ == '__main__':
    unittest.main()