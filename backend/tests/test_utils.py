import unittest
from app.utils import parse_bibtex_to_artigo_schema
from pydantic import ValidationError

# GERADOR POR IA

class TestUtilsParseBibtex(unittest.TestCase):
    def setUp(self):
        # simple, well-formed single entry
        self.single_bib = '''@inproceedings{sbes-paper3,
                        title={Um Estudo sobre Testes},
                        author={Davi Freitas and Breno Miranda},
                        booktitle={Anais do Simpósio},
                        year={2025},
                        pages={10--20},
                        publisher={Editora Exemplo},
                        location={São Paulo}
}
'''

        # two entries: one missing pages, the other missing year
        self.multi_bib = '''@inproceedings{paper-one,
                        title={Primeiro Trabalho},
                        author={Autor Um},
                        booktitle={Anais A},
                        year={2023}
}

                    @inproceedings{paper-two,
                    title={Segundo Trabalho},
                    author={Autor Dois},
                    booktitle={Anais B},
                    pages={5--8}
}
'''

        # malformed entry (missing required title)
        self.bad_bib = '''@inproceedings{bad-paper,
                        author={Sem Titulo},
                        booktitle={Anais X}
}
'''

    def test_parse_single_entry_full(self):
        artigos = parse_bibtex_to_artigo_schema(self.single_bib)
        self.assertEqual(len(artigos), 1)
        artigo, chave = artigos[0]
        self.assertEqual(chave, 'sbes-paper3')
        self.assertEqual(artigo.titulo, 'Um Estudo sobre Testes')
        self.assertEqual(artigo.autores, 'Davi Freitas and Breno Miranda')
        self.assertEqual(artigo.booktitle, 'Anais do Simpósio')
        self.assertEqual(artigo.publisher, 'Editora Exemplo')
        self.assertEqual(artigo.location, 'São Paulo')
        self.assertEqual(artigo.ano, 2025)
        self.assertEqual(artigo.pagina_inicial, 10)
        self.assertEqual(artigo.pagina_final, 20)

    def test_parse_multiple_entries_and_missing_fields(self):
        artigos = parse_bibtex_to_artigo_schema(self.multi_bib)
        self.assertEqual(len(artigos), 2)
        a1, k1 = artigos[0]
        a2, k2 = artigos[1]
        self.assertEqual(k1, 'paper-one')
        self.assertEqual(k2, 'paper-two')
        # first has year, no pages
        self.assertEqual(a1.ano, 2023)
        self.assertIsNone(a1.pagina_inicial)
        self.assertIsNone(a1.pagina_final)
        # second has pages, no year
        self.assertIsNone(a2.ano)
        self.assertEqual(a2.pagina_inicial, 5)
        self.assertEqual(a2.pagina_final, 8)

    def test_parse_missing_required_raises(self):
        # missing title should raise a pydantic ValidationError when constructing ArtigoSchema
        with self.assertRaises(ValidationError):
            parse_bibtex_to_artigo_schema(self.bad_bib)


if __name__ == '__main__':
    unittest.main()
