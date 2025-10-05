from playwright.sync_api import Page, expect

def test_app_routing(page: Page):
    """
    This test verifies that the basic routing of the application works correctly.
    It navigates between the main pages and takes a screenshot of the final state.
    """

    # 1. Arrange: Go to the application's home page.
    page.goto("http://localhost:5173/")

    # 2. Assert: Check if the HomePage is rendered correctly.
    # We expect to see the main heading and the header links.
    expect(page.get_by_role("heading", name="Página Principal / Busca")).to_be_visible()
    expect(page.get_by_role("link", name="Home")).to_be_visible()
    expect(page.get_by_role("link", name="Inscrever-se")).to_be_visible()
    expect(page.get_by_role("link", name="Admin")).to_be_visible()

    # 3. Act & Assert: Navigate to the Subscribe page and verify.
    page.get_by_role("link", name="Inscrever-se").click()
    expect(page.get_by_role("heading", name="Inscreva-se para Notificações")).to_be_visible()

    # 4. Act & Assert: Navigate to the Admin page and verify.
    page.get_by_role("link", name="Admin").click()
    expect(page.get_by_role("heading", name="Painel do Administrador")).to_be_visible()

    # 5. Act & Assert: Navigate back to the Home page and verify.
    page.get_by_role("link", name="Home").click()
    expect(page.get_by_role("heading", name="Página Principal / Busca")).to_be_visible()

    # 6. Screenshot: Capture the final result for visual verification.
    page.screenshot(path="jules-scratch/verification/verification.png")