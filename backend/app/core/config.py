from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Classe para gerenciar as configurações da aplicação.
    O Pydantic lê automaticamente as variáveis de um arquivo .env ou do ambiente.
    Ex: Para sobrescrever o nome do projeto, defina a variável de ambiente:
    export PROJECT_NAME="Minha Biblioteca Incrível"
    """

    # --- Configurações do Projeto ---
    PROJECT_NAME: str = "API Biblioteca Digital"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "Projeto para a disciplina de Engenharia de Software."

    # --- Configurações do Banco de Dados ---
    # A URL de conexão será lida da variável de ambiente `DATABASE_URL`.
    # Se não for encontrada, usará o valor padrão para um banco SQLite local.
    DATABASE_URL: str = "sqlite:///./biblioteca.db"
    
    class Config:
        # Nome do arquivo .env para carregar as variáveis de ambiente (opcional)
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Instância única das configurações que será importada em outros módulos
settings = Settings()