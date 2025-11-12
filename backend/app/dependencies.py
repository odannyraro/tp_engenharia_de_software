from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.models import db
from sqlalchemy.orm import sessionmaker, Session
from app.models import Usuario
from jose import jwt, JWTError

# Create a local OAuth2 schema here to avoid circular imports with app.main
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")


def pegar_sessao():
    try:
        SessionLocal = sessionmaker(bind=db)
        session = SessionLocal()
        yield session
    finally:
        session.close()


def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    # import SECRET_KEY/ALGORITHM lazily to avoid circular import with app.main
    from app.main import SECRET_KEY, ALGORITHM

    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token")
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    return usuario