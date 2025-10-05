from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path

load_dotenv()

env_path = Path('.') / 'app' / '.env'
load_dotenv(dotenv_path=env_path)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI(title = os.getenv("PROJECT_NAME"), description= os.getenv("PROJECT_DESCRIPITION"), version= os.getenv("PROJECT_VERSION"))

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

from router.auth_router import auth_router
from router.evento_routher import evento_router
from router.artigo_router import artigo_router
from router.subscriber_router import subscriber_router

app.include_router(auth_router)
app.include_router(evento_router)
app.include_router(artigo_router)
app.include_router(subscriber_router)