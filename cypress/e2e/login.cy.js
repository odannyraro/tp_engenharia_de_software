describe('E2E: Fluxo de Autenticação', () => {
  
  const baseUrl = 'http://localhost:5173';

    // ====================================================================
    //  TESTE 1: Teste de login com as credenciais corretas
    // ====================================================================
  
  it('Deve permitir o login de um usuário (Admin) e verificar a home', () => {
    
    cy.visit(`${baseUrl}/login`);

    // Preenche os campos de e-mail e senha
    cy.get('input[type="email"]').type('teste@example.com'); // Exemplo de Admin
    cy.get('input[type="password"]').type('123456'); // Substitua pela senha real

    // Clica no botão de Login
    cy.get('button[type="submit"]').click();

    // Verifica o estado após o login
    // Após o login, o Header deve exibir o nome do usuário ou o botão de Logout
    cy.wait(500); // Dá um tempo para o React processar a mudança
    cy.get('nav').contains('Logout').should('be.visible');
  });


    // ====================================================================
    //  TESTE 2: Teste Login com credenciais inválidas
    // ====================================================================

  it('Deve falhar ao tentar logar com credenciais inválidas', () => {
      cy.visit(`${baseUrl}/login`);
      cy.get('input[type="email"]').type('usuario@invalido.com');
      cy.get('input[type="password"]').type('senhaerrada');
      cy.get('button[type="submit"]').click();
      
      // Verifica se a mensagem de erro aparece na tela
      cy.contains('Usuário não encontrado ou credenciais inválidas').should('be.visible');
  });
});