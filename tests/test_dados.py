"""Testes dos dados e das ferramentas. Correr: python3 -m unittest discover -s tests -v"""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import build  # noqa: E402
from common import carregar, chave_alfabetica, slug  # noqa: E402
from validate import validar  # noqa: E402


class TestSlug(unittest.TestCase):
    def test_acentos_e_espacos(self):
        self.assertEqual(slug("Quiçama"), "quicama")
        self.assertEqual(slug("Icolo e Bengo"), "icolo-e-bengo")
        self.assertEqual(slug("Cuanza-Norte"), "cuanza-norte")
        self.assertEqual(slug("Bié"), "bie")


class TestDados(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = carregar()

    def test_totais_da_lei_14_24(self):
        self.assertEqual(len(self.dados["provincias"]), 21)
        self.assertEqual(len(self.dados["municipios"]), 326)

    def test_validador_sem_erros(self):
        erros, _ = validar(self.dados)
        self.assertEqual(erros, [])

    def test_provincias_novas(self):
        ids = {p["id"] for p in self.dados["provincias"]}
        for novo in ("icolo-e-bengo", "moxico-leste", "cubango", "cuando"):
            self.assertIn(novo, ids)
        self.assertNotIn("cuando-cubango", ids)  # já não existe como província

    def test_luanda_capital_e_sede(self):
        luanda = next(p for p in self.dados["provincias"] if p["id"] == "luanda")
        self.assertEqual(luanda["sede"], "Ingombota")

    def test_validador_detecta_municipio_orfao(self):
        dados = carregar()
        dados["municipios"][0]["provincia_id"] = "inexistente"
        erros, _ = validar(dados)
        self.assertTrue(any("inexistente" in e for e in erros))

    def test_validador_detecta_id_duplicado(self):
        dados = carregar()
        dados["municipios"].append(dict(dados["municipios"][0]))
        erros, _ = validar(dados)
        self.assertTrue(any("duplicado" in e for e in erros))


class TestOrdemAlfabetica(unittest.TestCase):
    def test_provincias_em_ordem_alfabetica(self):
        f = build.construir(build.API)
        nomes = [p["nome"] for p in json.loads(f["provincias.json"])["dados"]]
        self.assertEqual(nomes[:4], ["Bengo", "Benguela", "Bié", "Cabinda"])
        self.assertEqual(nomes[-1], "Zaire")
        self.assertEqual(nomes, sorted(nomes, key=chave_alfabetica))

    def test_municipios_planos_em_ordem_alfabetica(self):
        f = build.construir(build.API)
        nomes = [m["nome"] for m in json.loads(f["municipios.json"])["dados"]]
        self.assertEqual(nomes, sorted(nomes, key=chave_alfabetica))

    def test_municipios_por_provincia_em_ordem_alfabetica(self):
        f = build.construir(build.API)
        for p in json.loads(f["angola.json"])["provincias"]:
            nomes = [m["nome"] for m in p["municipios"]]
            self.assertEqual(nomes, sorted(nomes, key=chave_alfabetica), p["id"])

    def test_ordem_da_lei_preservada(self):
        f = build.construir(build.API)
        por_id = {p["id"]: p for p in json.loads(f["provincias.json"])["dados"]}
        self.assertEqual(por_id["cabinda"]["ordem_lei"], 1)
        self.assertEqual(por_id["cuando"]["ordem_lei"], 21)

    def test_validador_detecta_csv_desordenado(self):
        dados = carregar()
        dados["provincias"].reverse()
        erros, _ = validar(dados)
        self.assertTrue(any("alfabética" in e for e in erros))


class TestComunasNull(unittest.TestCase):
    def test_comunas_por_preencher_sao_null(self):
        f = build.construir(build.API)
        mun = json.loads(f["municipios/luanda-ingombota.json"])["dados"]
        self.assertIsNone(mun["comunas"])
        self.assertIsNone(mun["total_comunas"])
        self.assertIsNone(json.loads(f["comunas.json"])["dados"])
        self.assertIsNone(json.loads(f["provincias.json"])["meta"]["totais"]["comunas"])
        arvore = json.loads(f["angola.json"])["provincias"]
        self.assertIsNone(arvore[0]["municipios"][0]["comunas"])


class TestSite(unittest.TestCase):
    def test_links_da_pagina_inicial_existem_na_api(self):
        import re

        html = (build.RAIZ / "site" / "index.html").read_text(encoding="utf-8")
        links = set(re.findall(r'href="(api/v1/[^"]+)"', html))
        self.assertTrue(links, "a página deve ligar aos endpoints")
        for link in links:
            self.assertTrue((build.RAIZ / link).exists(), f"link partido: {link}")
        copiar = set(re.findall(r'data-copy="(api/v1/[^"]+)"', html))
        self.assertEqual(copiar, links)


class TestBuild(unittest.TestCase):
    def test_api_em_disco_esta_actualizada(self):
        esperado = build.construir(build.API)
        self.assertEqual(build.lado_a_lado(esperado, build.API), [])

    def test_estrutura_dos_ficheiros(self):
        f = build.construir(build.API)
        self.assertIn("provincias/luanda.json", f)
        self.assertIn("municipios/luanda-ingombota.json", f)
        luanda = json.loads(f["provincias/luanda.json"])["dados"]
        self.assertEqual(luanda["total_municipios"], 16)
        self.assertEqual(len(luanda["municipios"]), 16)
        arvore = json.loads(f["angola.json"])["provincias"]
        self.assertEqual(sum(len(p["municipios"]) for p in arvore), 326)

    def test_sqlite(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "angola.sqlite"
            build.gerar_sqlite(caminho)
            con = sqlite3.connect(caminho)
            self.assertEqual(con.execute("select count(*) from provincias").fetchone()[0], 21)
            self.assertEqual(con.execute("select count(*) from municipios").fetchone()[0], 326)
            n = con.execute(
                "select count(*) from municipios m join provincias p on p.id = m.provincia_id "
                "where p.id = 'malanje'"
            ).fetchone()[0]
            self.assertEqual(n, 27)
            con.close()


if __name__ == "__main__":
    unittest.main()
