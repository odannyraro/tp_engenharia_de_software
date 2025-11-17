// cypress/e2e/article_tests.cy.js

describe('E2E: Gerenciamento de Artigos', () => {
  // --- Configuração ---
  const adminEmail = 'teste@example.com'; // Admin email de 'addArticle.cy.js'
  const adminPassword = '123456'; // Admin password de 'addArticle.cy.js'
  const baseUrl = 'http://localhost:5173'; // Base URL de 'addArticle.cy.js'
  const now = Date.now();

  // Garante que o arquivo dummy existe na pasta fixtures
  before(() => {
    cy.writeFile('cypress/fixtures/dummy.pdf', 'Conteúdo de teste PDF');
  });

  // Realiza o login antes de CADA teste
  beforeEach(() => {
    cy.visit(`${baseUrl}/admin`);
    cy.get('input[placeholder="Email"]').type(adminEmail);
    cy.get('input[placeholder="Senha"]').type(adminPassword);
    cy.get('button[type="submit"]').click();
    // Confirma que o login foi feito e a página de admin carregou
    cy.contains('Gerenciador de Artigos').should('be.visible'); //
  });

  // ====================================================================
  //  TESTE 1: Criação de Artigo com Sucesso (Happy Path)
  // ====================================================================

  it('Deve criar um artigo com sucesso (criando seus pré-requisitos)', () => {
    // Dados para este teste
    const eventName = `Evento (Sucesso) ${now}`;
    const editionYear = new Date().getFullYear() + 1;
    const articleTitle = `Artigo (Sucesso) ${now}`;
    const articleAuthors = 'Autor de Sucesso';

    // --- 1. Criar Evento (Pré-requisito) ---
    cy.log('Passo 1: Criar Evento');
    cy.contains('button', 'Novo Evento').click();
    cy.get('h2').contains('Criar Novo Evento').should('be.visible'); //
    cy.get('label').contains('Nome:').next('input').type(eventName);
    cy.get('label').contains('Sigla:').next('input').type('SUC');
    cy.contains('button', 'Salvar').click();
    cy.contains('h2', 'Criar Novo Evento').should('not.exist');
    cy.wait(500); // Espera a lista de eventos recarregar
    cy.contains('div', eventName).should('be.visible');

    // --- 2. Criar Edição (Pré-requisito) ---
    cy.log('Passo 2: Criar Edição');
    cy.contains('div', eventName)
      .parents('div[style*="grid-template-columns"]')
      .find('button')
      .contains('Criar Edição')
      .click(); //
    cy.get('h2').contains(`Criar Nova Edição para ${eventName}`).should('be.visible'); //
    cy.get('label').contains('Ano:').next('input[type="number"]').type(editionYear);
    cy.contains('button', 'Salvar').click();
    cy.contains('Edição criada com sucesso!').should('be.visible');
    cy.contains('button', 'Fechar').click();
    cy.contains('h2', `Criar Nova Edição para ${eventName}`).should('not.exist');

    // --- 3. Criar Artigo (O Teste Principal) ---
    cy.log('Passo 3: Criar Artigo');
    cy.contains('button', 'Adicionar Artigo').click(); //
    cy.get('h2').contains('Criar Novo Artigo').should('be.visible'); //

    // Preenche o formulário do artigo
    cy.get('label').contains('Título:').next('input').type(articleTitle);
    cy.get('label').contains('Autores').next('input').type(articleAuthors);
    cy.get('label').contains('Nome do Evento:').next('input').type(eventName); // Usa o evento criado no Passo 1
    cy.get('label').contains('Ano:').next('input[type="number"]').type(editionYear); // Usa a edição criada no Passo 2
    cy.get('input[type="file"]').selectFile('cypress/fixtures/dummy.pdf'); //
    cy.contains('button', 'Salvar').click();

    // --- 4. Verificação ---
    cy.log('Passo 4: Verificar sucesso');
    cy.contains('h2', 'Criar Novo Artigo').should('not.exist');
    
    // Verifica se o artigo aparece na "Lista de Artigos" na AdminPage
    const articleListContainer = cy.contains('h2', 'Lista de Artigos').parent(); 
    articleListContainer.contains(articleTitle).should('be.visible');
  });

  // ====================================================================
  //  TESTE 2: Criação de Artigo com Erro (Evento Inexistente)
  // ====================================================================

  it('Deve exibir um erro ao tentar criar um artigo para um evento inexistente', () => {
    // Dados para este teste
    const eventName_Error = `Evento Inexistente ${now}`;
    const articleTitle_Error = `Artigo (Erro) ${now}`;

    cy.log('Passo 1: Abrir formulário de artigo');
    cy.contains('button', 'Adicionar Artigo').click(); //
    cy.get('h2').contains('Criar Novo Artigo').should('be.visible'); //

    // --- 2. Preencher formulário com dados inválidos ---
    cy.log('Passo 2: Preencher com evento inexistente');
    cy.get('label').contains('Título:').next('input').type(articleTitle_Error);
    cy.get('label').contains('Autores').next('input').type('Autor Erro');
    cy.get('label').contains('Nome do Evento:').next('input').type(eventName_Error); // Evento que não existe
    cy.get('label').contains('Ano:').next('input[type="number"]').type('2025');
    cy.get('input[type="file"]').selectFile('cypress/fixtures/dummy.pdf');
    
    // --- 3. Salvar e esperar o erro ---
    cy.log('Passo 3: Salvar e verificar erro');
    cy.contains('button', 'Salvar').click();

    // --- 4. Verificação do Erro ---
    // Esta mensagem de erro vem do backend
    const errorMessage = `Evento '${eventName_Error}' não encontrado`;
    
    // O AdminPage.jsx exibe o erro capturado
    cy.contains(errorMessage).should('be.visible');

    // O modal NÃO deve fechar
cy.get('h2').contains('Criar Novo Artigo').scrollIntoView().should('be.visible');
  });
});