// Arquivo: cypress/e2e/admin_flow.cy.js

describe('E2E: Fluxo Admin - Criação de Evento -> Edição -> Artigo', () => {
    // ⚠️ ATENÇÃO: Substitua 'SENHA_DO_ADMIN' pela senha real do seu usuário 'adm@example.com'
    const adminEmail = 'teste@example.com';
    const adminPassword = '123456'; 
    const baseUrl = 'http://localhost:5173';
    
    // Dados para a criação
    const now = Date.now();
    const eventName = `Seminário Teste DCC E2E ${now}`;
    const eventSigla = 'STEST';
    const editionYear = new Date().getFullYear() + 2; // Ex: 2027
    const articleTitle = `Artigo E2E teste Eng Soft ${now}`;
    const articleAuthors = 'Fulano de Tal';
    const promoterEntity = 'DCC Eventos';
    const articlePageStart = 10;
    const articlePageEnd = 20;

    // Ação de pré-teste: Cria o arquivo dummy se não existir (apenas o nome é importante para o teste)
    before(() => {
        // Assegura que o arquivo dummy existe na pasta fixtures para o upload
        cy.writeFile('cypress/fixtures/dummy.pdf', 'Conteúdo de teste PDF');
    });

    it('Deve criar um evento, uma edição e um artigo com upload de PDF', () => {
        // --- 1. Login como Admin e navegação ---
        cy.log('Passo 1: Login como Admin');
        cy.visit(`${baseUrl}/admin`);
        cy.get('input[placeholder="Email"]').type(adminEmail);
        cy.get('input[placeholder="Senha"]').type(adminPassword);
        cy.get('button[type="submit"]').click();

        // Asserção de Login: O botão de criar evento deve estar visível no painel
        cy.contains('Gerencie eventos e suas edições.').should('be.visible');
        cy.contains('button', 'Novo Evento').should('be.visible');

        // --- 2. Criação do Evento ---
        cy.log('Passo 2: Criação do Evento');
        cy.contains('button', 'Novo Evento').click();
        
        // Espera o modal (EventForm.jsx) aparecer
        const eventModalTitle = 'Criar Novo Evento';
        cy.get('h2').contains(eventModalTitle).should('be.visible');

        // Preenche o formulário do evento
        cy.get('label').contains('Nome:').next('input').type(eventName);
        cy.get('label').contains('Sigla:').next('input').type(eventSigla);
        cy.get('label').contains('Entidade promotora:').next('input').type(promoterEntity); 

        // Salva
        cy.contains('button', 'Salvar').click();
        
        // AGUARDA E ASSERÇÃO CRÍTICA: Espera o modal sumir completamente
        cy.contains('h2', eventModalTitle).should('not.exist');
        
        // Espera um pouco para a lista de eventos ser recarregada do backend
        cy.wait(500); 

        // Asserção: Evento criado e visível na lista
        cy.contains('div', eventName).should('be.visible');
        
        // --- 3. Criação da Edição ---
        cy.log('Passo 3: Criação da Edição');
        
        // 3.1. Expande o evento recém-criado 
        // Note: o `parents('.div')` é uma correção de seletor defensiva
        cy.contains('div', eventName)
          .parents('div[style*="grid-template-columns"]') 
          .find('button')
          .contains('+')
          .click();
        
        // 3.2. Clica no botão Criar Edição do evento
        cy.contains('div', eventName)
          .parents('div[style*="grid-template-columns"]')
          .find('button')
          .contains('Criar Edição')
          .click();
          
        // Espera o modal de edição (EditionForm.jsx) aparecer
        const editionModalTitle = `Criar Nova Edição para ${eventName}`;
        cy.get('h2').contains(editionModalTitle).should('be.visible');

        // Preenche o formulário da edição
        cy.get('label').contains('Ano:').next('input[type="number"]').type(editionYear);
        cy.get('label').contains('Local:').next('input').type('Belo Horizonte');

        cy.contains('button', 'Salvar').click();
        
        // Asserção: Confirma a criação
        cy.contains('Edição criada com sucesso!').should('be.visible');
        cy.contains('button', 'Fechar').click();
        
        // AGUARDA E ASSERÇÃO CRÍTICA: Espera o modal sumir
        cy.contains('h2', editionModalTitle).should('not.exist');
        
        // Asserção: Edição visível no painel expandido
        cy.get('div[style*="background-color: rgb(58, 58, 60)"]')
          .contains('div', `${editionYear}`)
          .should('be.visible');

        // --- 4. Criação do Artigo ---
        cy.log('Passo 4: Criação do Artigo com PDF');

        // Clica no botão "Adicionar Artigo" (no componente ArticleManager)
        cy.contains('button', 'Adicionar Artigo').click();
        
        // Espera o modal de artigo (ArticleForm.jsx) aparecer
        const articleModalTitle = 'Criar Novo Artigo';
        cy.get('h2').contains(articleModalTitle).should('be.visible');

        // Preenche os dados do artigo
        cy.get('label').contains('Título:').next('input').type(articleTitle);
        cy.get('label').contains('Autores').next('input').type(articleAuthors);
        cy.get('label').contains('Nome do Evento:').next('input').type(eventName);
        
        cy.get('label').contains('Ano:').next('input[type="number"]').clear().type(editionYear); 
        cy.get('label').contains('Página Inicial:').next('input[type="number"]').type(articlePageStart);
        cy.get('label').contains('Página Final:').next('input[type="number"]').type(articlePageEnd);
        
        // Simulação do Upload de Arquivo
        cy.get('input[type="file"]').selectFile('cypress/fixtures/dummy.pdf'); 

        // Clica em Salvar
        cy.contains('button', 'Salvar').click();
        
        // AGUARDA E ASSERÇÃO CRÍTICA: Espera o modal do artigo desaparecer
        cy.contains('h2', articleModalTitle).should('not.exist');
        
        // --- 5. Verificação do Artigo na Lista e Detalhe ---
        cy.log('Passo 5: Verificação do Artigo na Lista');
        
        // Encontra o container da Lista de Artigos pelo seu H2
        const articleListContainer = cy.contains('h2', 'Lista de Artigos').parent(); 

        // Asserção 5.1: Artigo visível na lista
        articleListContainer.contains(articleTitle).should('be.visible');
        
        // Asserção 5.2: Clica no link do artigo
        articleListContainer
          .contains('a', articleTitle) 
          .click();

        // Asserção 5.3: Verifica se está na página de detalhe
        cy.url().should('include', '/article/');
        cy.contains('h1', articleTitle).should('be.visible');
        cy.contains(`Autores: ${articleAuthors}`).should('be.visible');
        cy.contains(`Evento: ${eventName} (${editionYear})`).should('be.visible');
    });

    // ====================================================================
    //  TESTE 2: Prevenção de Duplicação de Evento
    // ====================================================================

    it('Deve exibir mensagem de erro ao tentar criar evento duplicado', () => {
        const duplicateEventName = `Evento Duplicado E2E ${Date.now()}`;
        const errorMessage = 'Já existe evento com esse nome'; // Mensagem do backend

        // --- 1. Login (reutilizado) ---
        cy.log('Passo D1: Login como Admin');
        cy.visit(`${baseUrl}/admin`);
        cy.get('input[placeholder="Email"]').type(adminEmail);
        cy.get('input[placeholder="Senha"]').type(adminPassword);
        cy.get('button[type="submit"]').click();
        cy.contains('button', 'Novo Evento').should('be.visible');

        // --- 2. Criação do PRIMEIRO Evento (Sucesso) ---
        cy.log('Passo D2: Criar o primeiro evento (base)');
        cy.contains('button', 'Novo Evento').click();
        
        const eventModalTitle = 'Criar Novo Evento';
        cy.get('h2').contains(eventModalTitle).should('be.visible');

        // Preenche o formulário
        cy.get('label').contains('Nome:').next('input').type(duplicateEventName);
        cy.get('label').contains('Sigla:').next('input').type('DUP');
        cy.get('label').contains('Entidade promotora:').next('input').type('Test Corp'); 

        // Salva com sucesso
        cy.contains('button', 'Salvar').click();
        cy.contains('h2', eventModalTitle).should('not.exist');
        cy.wait(500); 
        cy.contains('div', duplicateEventName).should('be.visible');

        // --- 3. Tenta criar o SEGUNDO Evento (Duplicado) ---
        cy.log('Passo D3: Tentar criar o evento duplicado');
        cy.contains('button', 'Novo Evento').click();
        cy.get('h2').contains(eventModalTitle).should('be.visible');

        // Preenche com o MESMO nome
        cy.get('label').contains('Nome:').next('input').type(duplicateEventName);
        cy.get('label').contains('Sigla:').next('input').type('DUP2');
        cy.get('label').contains('Entidade promotora:').next('input').type('Test Corp'); 

        // Salva - A API deve retornar 400
        cy.contains('button', 'Salvar').click();
        
        // --- 4. Verificação da Mensagem de Erro ---
        cy.log('Passo D4: Verificar se a mensagem de erro aparece');
        
        // O frontend (AdminPage.jsx) exibe o erro em uma tag <p style={{ color: 'red' }}>
        // ou usa o `setError(err?.response?.data?.detail || 'Erro ao salvar evento')`
        // O erro do backend é "Já existe evento com esse nome"
        cy.contains('p', errorMessage).should('be.visible');

        // --- 5. Limpeza (Fechar o Modal de Erro e Remover o Evento Original) ---
        cy.log('Passo D5: Limpeza do evento duplicado');
        
        // Cancela o modal
        cy.contains('button', 'Cancelar').click();
        cy.contains('h2', eventModalTitle).should('not.exist');

        // Remove o evento que foi criado com sucesso no Passo D2
        cy.contains('div', duplicateEventName)
            .parents('div[style*="grid-template-columns"]') 
            .find('button')
            .contains('Remover')
            .click();
        
        // Confirma a exclusão
        cy.on('window:confirm', () => true);
        cy.contains('div', duplicateEventName).should('not.exist');
    });

    // ====================================================================
    //  TESTE 3: Criação de um novo evento após a remoção de um evento anterior (Sanity Check)
    // ====================================================================

    it('Deve permitir a criação de um novo evento após a remoção de um evento anterior', () => {
        const deletedEventName = `Evento a ser Deletado ${Date.now()}`;
        const newEventName = `Evento Criado Depois ${Date.now()}`;
        
        // --- 1. Login ---
        cy.log('Passo P1: Login como Admin');
        cy.visit(`${baseUrl}/admin`);
        cy.get('input[placeholder="Email"]').type(adminEmail);
        cy.get('input[placeholder="Senha"]').type(adminPassword);
        cy.get('button[type="submit"]').click();
        cy.contains('button', 'Novo Evento').should('be.visible');

        // --- 2. Criação do Evento que será deletado ---
        cy.log('Passo P2: Criação do evento a ser deletado');
        cy.contains('button', 'Novo Evento').click();
        const eventModalTitle = 'Criar Novo Evento';
        cy.get('h2').contains(eventModalTitle).should('be.visible');
        cy.get('label').contains('Nome:').next('input').type(deletedEventName);
        cy.get('label').contains('Sigla:').next('input').type('DEL');
        cy.contains('button', 'Salvar').click();
        cy.contains('h2', eventModalTitle).should('not.exist');
        cy.wait(500); 
        cy.contains('div', deletedEventName).should('be.visible');

        // --- 3. Remoção do Evento ---
        cy.log('Passo P3: Remoção do evento');
        cy.contains('div', deletedEventName)
            .parents('div[style*="grid-template-columns"]') 
            .find('button')
            .contains('Remover')
            .click();
        cy.on('window:confirm', () => true);
        cy.contains('div', deletedEventName).should('not.exist');
        cy.wait(500); 

        // --- 4. Criação de um NOVO Evento ---
        cy.log('Passo P4: Criação de um novo evento');
        cy.contains('button', 'Novo Evento').click();
        cy.get('h2').contains(eventModalTitle).should('be.visible');
        cy.get('label').contains('Nome:').next('input').type(newEventName);
        cy.get('label').contains('Sigla:').next('input').type('NEW');
        
        // Salva - Deve ter sucesso
        cy.contains('button', 'Salvar').click();
        
        // --- 5. Verificação de Sucesso ---
        cy.log('Passo P5: Verificação do novo evento');
        cy.contains('h2', eventModalTitle).should('not.exist');
        cy.contains('div', newEventName).should('be.visible');

        // --- 6. Limpeza ---
        cy.log('Passo P6: Limpeza do novo evento');
        cy.contains('div', newEventName)
            .parents('div[style*="grid-template-columns"]') 
            .find('button')
            .contains('Remover')
            .click();
        cy.on('window:confirm', () => true);
        cy.contains('div', newEventName).should('not.exist');
    });
});