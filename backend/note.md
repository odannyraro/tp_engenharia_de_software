- para rodar o local host: na pasta backend/app rodar uvicorn main:app --reload
- Para ver a documentação é http://127.0.0.1:8000/docs#/

- Criar db ou criar a migração (atualizar modificação de tabela, coluna, etc): na pasta backend/app rodar alembic revision --autogenerate -m "mensagem" e logo dps alembic upgrade head