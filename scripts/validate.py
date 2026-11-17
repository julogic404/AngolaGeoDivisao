#!/usr/bin/env python3
"""Valida os CSV em data/. Termina com código != 0 se houver erros.

Uso:  python3 scripts/validate.py
"""
from __future__ import annotations

import sys

from common import SLUG_RE, carregar, chave_alfabetica, slug

# Totais fixados pela Lei n.º 14/24, de 5 de Setembro de 2024.
TOTAL_PROVINCIAS = 21
TOTAL_MUNICIPIOS = 326
TOTAL_COMUNAS = 378

# Contagens por província confirmadas em fontes independentes da lei
# (INE - Recenseamento 2024, texto da própria lei, imprensa).
CONTAGENS_CONFIRMADAS = {
    "cabinda": 10,
    "bengo": 12,
    "icolo-e-bengo": 7,
    "malanje": 27,
    "bie": 19,
}


def validar(dados: dict | None = None) -> tuple[list[str], list[str]]:
    dados = dados or carregar()
    erros: list[str] = []
    avisos: list[str] = []
    provs, muns, comunas = dados["provincias"], dados["municipios"], dados["comunas"]

    # --- totais -----------------------------------------------------------
    if len(provs) != TOTAL_PROVINCIAS:
        erros.append(f"esperadas {TOTAL_PROVINCIAS} províncias, encontradas {len(provs)}")
    if len(muns) != TOTAL_MUNICIPIOS:
        erros.append(f"esperados {TOTAL_MUNICIPIOS} municípios, encontrados {len(muns)}")
    if len(comunas) != TOTAL_COMUNAS:
        avisos.append(
            f"comunas incompletas: {len(comunas)}/{TOTAL_COMUNAS} (contribuições bem-vindas)"
        )

    # --- províncias -------------------------------------------------------
    ids_prov = set()
    for p in provs:
        if not SLUG_RE.match(p["id"]):
            erros.append(f"província: id inválido '{p['id']}'")
        if p["id"] != slug(p["nome"]):
            erros.append(f"província: id '{p['id']}' não corresponde ao nome '{p['nome']}'")
        if p["id"] in ids_prov:
            erros.append(f"província: id duplicado '{p['id']}'")
        ids_prov.add(p["id"])
        if not p["nome"].strip() or not p["sede"].strip():
            erros.append(f"província '{p['id']}': nome/sede vazio")
    ordens = sorted(p["ordem_lei"] for p in provs)
    if ordens != list(range(1, len(provs) + 1)):
        erros.append("províncias: a coluna 'ordem_lei' deve ser 1..N sem falhas")
    nomes_prov = [chave_alfabetica(p["nome"]) for p in provs]
    if nomes_prov != sorted(nomes_prov):
        erros.append("províncias: o CSV deve estar por ordem alfabética do nome")

    # --- municípios -------------------------------------------------------
    ids_mun = set()
    por_prov: dict[str, list[dict]] = {}
    for m in muns:
        if not SLUG_RE.match(m["id"]):
            erros.append(f"município: id inválido '{m['id']}'")
        esperado = f"{m['provincia_id']}-{slug(m['nome'])}"
        if m["id"] != esperado:
            erros.append(f"município: id '{m['id']}' deveria ser '{esperado}'")
        if m["id"] in ids_mun:
            erros.append(f"município: id duplicado '{m['id']}'")
        ids_mun.add(m["id"])
        if m["provincia_id"] not in ids_prov:
            erros.append(f"município '{m['id']}': província inexistente '{m['provincia_id']}'")
        if not m["nome"].strip():
            erros.append(f"município '{m['id']}': nome vazio")
        por_prov.setdefault(m["provincia_id"], []).append(m)

    # artigos da lei crescem dentro de cada província e depois do artigo da província
    art_prov = {p["id"]: p["lei_artigo"] for p in provs}
    for pid, lista in por_prov.items():
        artigos = [m["lei_artigo"] for m in lista]
        if len(artigos) != len(set(artigos)):
            erros.append(f"província '{pid}': dois municípios com o mesmo artigo da lei")
        if artigos and min(artigos) <= art_prov.get(pid, 0):
            erros.append(f"província '{pid}': município com artigo anterior ao da província")
        nomes = [chave_alfabetica(m["nome"]) for m in lista]
        if nomes != sorted(nomes):
            erros.append(f"província '{pid}': municípios não estão por ordem alfabética")
    chaves = [(chave_alfabetica(m["provincia_id"]), chave_alfabetica(m["nome"])) for m in muns]
    if chaves != sorted(chaves):
        erros.append("municípios: o CSV deve estar ordenado por província e nome")

    for p in provs:
        if p["id"] not in por_prov:
            erros.append(f"província '{p['id']}' não tem municípios")
        # a sede provincial (como definida na lei) existe como município da própria província
        nomes = {m["nome"] for m in por_prov.get(p["id"], [])}
        if p["sede"] not in nomes and p["id"] in por_prov:
            avisos.append(
                f"província '{p['id']}': sede '{p['sede']}' não é município da província "
                "(verificar grafia)"
            )

    for pid, esperado in CONTAGENS_CONFIRMADAS.items():
        n = len(por_prov.get(pid, []))
        if n != esperado:
            erros.append(f"província '{pid}': {n} municípios, confirmados {esperado}")

    # --- comunas ----------------------------------------------------------
    ids_com = set()
    chaves_com = [(chave_alfabetica(c["municipio_id"]), chave_alfabetica(c["nome"])) for c in comunas]
    if chaves_com != sorted(chaves_com):
        erros.append("comunas: o CSV deve estar ordenado por município e nome")
    for c in comunas:
        if c["id"] in ids_com:
            erros.append(f"comuna: id duplicado '{c['id']}'")
        ids_com.add(c["id"])
        if c["municipio_id"] not in ids_mun:
            erros.append(f"comuna '{c['id']}': município inexistente '{c['municipio_id']}'")
        if c["id"] != f"{c['municipio_id']}-{slug(c['nome'])}":
            erros.append(f"comuna: id '{c['id']}' não corresponde a município+nome")

    return erros, avisos


def main() -> int:
    erros, avisos = validar()
    for a in avisos:
        print(f"AVISO: {a}")
    for e in erros:
        print(f"ERRO:  {e}")
    if erros:
        print(f"\n{len(erros)} erro(s).")
        return 1
    print("OK: dados válidos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
