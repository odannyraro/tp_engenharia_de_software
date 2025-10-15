# Biblioteca Digital de Artigos - Eng. de Software

O objetivo de é desenvolver um sistema web para gerenciamento de artigos e eventos científicos.
Neste projeto, será utilizado as seguintes tecnologias:

Front-End = React.js  
Back-End = Python/FastAPI  
Banco de Dados = SQLite

# Ferramentas de IA utilizadas
- Copilot Agent
- Jules

# Integrantes
- Filipe Caldeira - Banco de Dados / Front-End
- Samuel Miranda - Back-End
- Daniel Rodrigues - Front-End
- Arthur Quaresma - Banck-End / Front-End

# Diagrama de Sequencia - Cadastro Evento 

<img width="1047" height="530" alt="diagrama sequencia cadastro evento" src="https://github.com/user-attachments/assets/8731736a-71c1-40bd-8fa1-4311226c4046" />


# Diagrama de Pacotes

<img width="912" height="675" alt="diagrama arquitetura" src="https://github.com/user-attachments/assets/d35710f8-a3eb-4b0a-b90b-6b1462b1b89c" />


# História #1: Como administrador, eu quero cadastrar (editar, deletar) um evento. (Exemplo: Simpósio Brasileiro de Engenharia de Software)
# Tarefas e Responsáveis:
- Entender como será a aplicação do banco de dados [Filipe]
- Instalar FastAPI [Arthur]
- Instalar banco de dados e criar classes e schemas para Usuário e Evento [Arthur]
- Criar API para cadastro de conta e login [Arthur]
- Criar sistema de autenticação [Arthur]
- Criar rotas de criação, edição e remoção de Evento [Arthur]
- Criar interface, design e estrutura do frontend para a tela [Filipe]
- Fazer a ligação do front com as chamadas na API [Filipe]

# Historia #2: Como administrador, eu quero cadastrar (editar, deletar) uma nova edição de um evento (exemplo: edição de 2025 do SBES)
# Tarefas e Responsáveis:
- Crias classes e schemas para Edição [Arthur]
- Criar rotas para criação, edição e remoção de Edições [Arthur]
- Gerar interface de edições por evento [Filipe]

# Hisptória #3: Como administrador, eu quero cadastrar (editar, deletar) um artigo manualmente, incluindo seu pdf:
# Tarefas e Responsáveis:
- Criar classe e API para Artigos [Arthur]
- Incluir no banco de dados [Arthur]
- Criar rotas de cadastro, edição e remoção de artigos [Arthur]
- Fazer conexão com o front [Filipe]
- Baixar e exibir PDF [Filipe]

# História #5: Como usuário, eu quero pesquisar por artigos: por título, por autor e por nome de evento
# Tarefas e Responsáveis:
- Criar rotas para retornar um ou lista de artigos por opção [Arthur / Filipe]
- Criar interface, design e estrutura do frontend para a tela [Filipe]
- Fazer a ligação do front com as chamadas na API [Filipe]

# História #7: Como usuário, eu quero ter uma home page com meus artigos, organizados por ano 
# Tarefas e Responsáveis:
- Criar classes e métodos no backend [Arthur]
- Criar a API, suas rotas e validações [Arthur]
- Criar a estrutura do frontend, componentes, telas e design [Filipe]


# História #8: Como usuário, eu quero me cadastrar para receber um mail sempre que eu tiver um novo artigo disponibilizado
# Tarefas e Responsáveis:
- Rota para usuario autenticado registrar para receber notificacao [Arthur]
- Modificar criação de artigos para notificar usuarios registrados [Daniel]
- Pop notificação na tela indicando quais autores receberam emails [Arthur]
