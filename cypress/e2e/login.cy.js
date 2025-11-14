describe('E2E: Fluxo de Autenticação', () => {
  
  const baseUrl = 'http://localhost:5173';
  
  it('Deve permitir o login de um usuário (Admin) e verificar a home', () => {
    
    // 1. Visita a página de login
    cy.visit(`${baseUrl}/login`);

    // 2. Preenche os campos de e-mail e senha
    // Use credenciais de um usuário já existente no seu banco de dados (ex: 'adm@example.com')
    cy.get('input[type="email"]').type('filipe.terra@hotmail.com'); // Exemplo de Admin
    cy.get('input[type="password"]').type('123456'); // Substitua pela senha real

    // 3. Clica no botão de Login
    cy.get('button[type="submit"]').click();

    // 4. Verifica o estado após o login
    // Após o login, o Header deve exibir o nome do usuário ou o botão de Logout
    cy.wait(500); // Dá um tempo para o React processar a mudança
    cy.get('nav').contains('Logout').should('be.visible');
  });

  it('Deve falhar ao tentar logar com credenciais inválidas', () => {
      cy.visit(`${baseUrl}/login`);
      cy.get('input[type="email"]').type('usuario@invalido.com');
      cy.get('input[type="password"]').type('senhaerrada');
      cy.get('button[type="submit"]').click();
      
      // Verifica se a mensagem de erro aparece na tela
      cy.contains('Usuário não encontrado ou credenciais inválidas').should('be.visible');
  });
});