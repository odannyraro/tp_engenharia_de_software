import unittest
from app.models import Usuario, Evento, EdicaoEvento, Artigo, Subscriber

class TestUsuario(unittest.TestCase):
    def setUp(self):
        self.user = Usuario("marcelo", "marcelo@email.com", "123456")

    def test_criar_Usuario(self):
        self.assertEqual(self.user.nome, "marcelo")
        self.assertEqual(self.user.email, "marcelo@email.com")
        self.assertEqual(self.user.senha, "123456")
        self.assertFalse(self.user.admin)

class TestEvento(unittest.TestCase):
    def setUp(self):
        self.evento = Evento("Evento_teste", "ET", entidade_promotora="SBS")

    def test_criar_Evento(self):
        self.assertEqual(self.evento.nome, "Evento_teste")
        self.assertEqual(self.evento.sigla, "ET")
        self.assertIsNone(self.evento.descricao, None)
        self.assertIsNone(self.evento.site, None)
        self.assertEqual(self.evento.entidade_promotora, "SBS")

class TestEdicaoEvento(unittest.TestCase):
    def setUp(self):
        self.edicaoevento = EdicaoEvento(2025, 1, "UFMG")

    def test_criar_Evento(self):
        self.assertEqual(self.edicaoevento.ano, 2025)
        self.assertEqual(self.edicaoevento.id_evento, 1)
        self.assertEqual(self.edicaoevento.local, "UFMG")

class TestArtigo(unittest.TestCase):

    def setUp(self):
        self.artigo = Artigo(
            titulo="Um Estudo sobre Testes",
            autores="Davi Freitas and Breno Miranda",
            nome_evento="Simpósio Teste",
            ano=2025,
            pagina_inicial=10,
            pagina_final=20,
            caminho_pdf="/path/to/pdf.pdf",
            booktitle="Anais do Simpósio",
            publisher="Editora Exemplo",
            location="São Paulo",
            id_edicao=3
        )

    def test_criar_Artigo_campos(self):
        self.assertEqual(self.artigo.titulo, "Um Estudo sobre Testes")
        self.assertEqual(self.artigo.autores, "Davi Freitas and Breno Miranda")
        self.assertEqual(self.artigo.nome_evento, "Simpósio Teste")
        self.assertEqual(self.artigo.ano, 2025)
        self.assertEqual(self.artigo.pagina_inicial, 10)
        self.assertEqual(self.artigo.pagina_final, 20)
        self.assertEqual(self.artigo.caminho_pdf, "/path/to/pdf.pdf")
        self.assertEqual(self.artigo.booktitle, "Anais do Simpósio")
        self.assertEqual(self.artigo.publisher, "Editora Exemplo")
        self.assertEqual(self.artigo.location, "São Paulo")
        self.assertEqual(self.artigo.id_edicao, 3)

    def test_autores_format(self):
        partes = [p.strip() for p in self.artigo.autores.split(' and ') if p.strip()]
        self.assertIn('Davi Freitas', partes)
        self.assertIn('Breno Miranda', partes)

class TestSubscriber(unittest.TestCase):
    def setUp(self):
        self.sub = Subscriber("Davi Freitas", "davi@example.com")
    
    def test_sub(self):
        self.assertEqual(self.sub.nome, "Davi Freitas")
        self.assertEqual(self.sub.email, "davi@example.com")

if __name__ == "__main__":
    unittest.main()    