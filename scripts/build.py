#!/usr/bin/env python3
"""Gera a API estática em api/v1/ a partir dos CSV (e, opcionalmente, um SQLite).

Uso:
    python3 scripts/build.py            # gera api/v1/*.json
    python3 scripts/build.py --sqlite   # também gera dist/angola.sqlite
    python3 scripts/build.py --check    # falha se api/v1/ estiver desactualizada (CI)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

from common import API, RAIZ, carregar, chave_alfabetica, ler_meta
from validate import validar


def _json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def construir(destino: Path) -> dict[str, str]:
    """Devolve {caminho_relativo: conteúdo} de todos os ficheiros da API."""
    dados = carregar()
    meta = ler_meta()
    # Todas as listas saem por ordem alfabética (sem acentos), não pela ordem da lei.
    provs = sorted(dados["provincias"], key=lambda p: chave_alfabetica(p["nome"]))
    muns = sorted(
        dados["municipios"],
        key=lambda m: (chave_alfabetica(m["provincia_id"]), chave_alfabetica(m["nome"])),
    )
    comunas = sorted(
        dados["comunas"],
        key=lambda c: (chave_alfabetica(c["municipio_id"]), chave_alfabetica(c["nome"])),
    )

    nome_prov = {p["id"]: p["nome"] for p in provs}
    nome_mun = {m["id"]: m for m in muns}

    muns_por_prov: dict[str, list[dict]] = {}
    for m in muns:
        muns_por_prov.setdefault(m["provincia_id"], []).append(m)
    comunas_por_mun: dict[str, list[dict]] = {}
    for c in comunas:
        comunas_por_mun.setdefault(c["municipio_id"], []).append(c)

    ficheiros: dict[str, str] = {}

    # null = ainda não carregadas (diferente de "zero comunas")
    totais = {
        "provincias": len(provs),
        "municipios": len(muns),
        "comunas": len(comunas) or None,
    }
    meta_pub = {
        "versao": meta["versao"],
        "verificado_em": meta["verificado_em"],
        "fonte_primaria": meta["fonte_primaria"],
        "licenca_dados": meta["licenca_dados"],
        "totais": totais,
        "totais_oficiais": meta["totais_oficiais"],
    }

    ficheiros["index.json"] = _json(
        {
            "meta": meta_pub,
            "endpoints": {
                "provincias": "provincias.json",
                "provincia": "provincias/{id}.json",
                "municipios": "municipios.json",
                "municipio": "municipios/{id}.json",
                "comunas": "comunas.json",
                "tudo": "angola.json",
            },
        }
    )

    provs_pub = []
    for p in provs:
        provs_pub.append(
            {
                "id": p["id"],
                "ordem_lei": p["ordem_lei"],
                "nome": p["nome"],
                "sede": p["sede"],
                "origem": p["origem"],
                "lei_artigo": p["lei_artigo"],
                "total_municipios": len(muns_por_prov.get(p["id"], [])),
            }
        )
    ficheiros["provincias.json"] = _json({"meta": meta_pub, "dados": provs_pub})

    muns_pub = []
    for m in muns:
        muns_pub.append(
            {
                "id": m["id"],
                "nome": m["nome"],
                "provincia_id": m["provincia_id"],
                "provincia": nome_prov[m["provincia_id"]],
                "lei_artigo": m["lei_artigo"],
                "total_comunas": (
                    len(comunas_por_mun[m["id"]]) if m["id"] in comunas_por_mun else None
                ),
            }
        )
    # Lista plana: por nome do município (desempate pela província).
    muns_planos = sorted(
        muns_pub, key=lambda m: (chave_alfabetica(m["nome"]), chave_alfabetica(m["provincia"]))
    )
    ficheiros["municipios.json"] = _json({"meta": meta_pub, "dados": muns_planos})

    comunas_pub = [
        {
            "id": c["id"],
            "nome": c["nome"],
            "municipio_id": c["municipio_id"],
            "municipio": nome_mun[c["municipio_id"]]["nome"],
            "provincia_id": nome_mun[c["municipio_id"]]["provincia_id"],
            "lei_artigo": c["lei_artigo"],
        }
        for c in comunas
    ]
    ficheiros["comunas.json"] = _json({"meta": meta_pub, "dados": comunas_pub or None})

    for p, pp in zip(provs, provs_pub):
        detalhe = dict(pp)
        detalhe["municipios"] = [
            {"id": m["id"], "nome": m["nome"], "lei_artigo": m["lei_artigo"]}
            for m in muns_por_prov.get(p["id"], [])
        ]
        ficheiros[f"provincias/{p['id']}.json"] = _json({"meta": meta_pub, "dados": detalhe})

    for m, mp in zip(muns, muns_pub):
        detalhe = dict(mp)
        detalhe["comunas"] = (
            [{"id": c["id"], "nome": c["nome"]} for c in comunas_por_mun[m["id"]]]
            if m["id"] in comunas_por_mun
            else None
        )
        ficheiros[f"municipios/{m['id']}.json"] = _json({"meta": meta_pub, "dados": detalhe})

    arvore = []
    for p, pp in zip(provs, provs_pub):
        no = dict(pp)
        no["municipios"] = []
        for m in muns_por_prov.get(p["id"], []):
            no["municipios"].append(
                {
                    "id": m["id"],
                    "nome": m["nome"],
                    "comunas": (
                        [{"id": c["id"], "nome": c["nome"]} for c in comunas_por_mun[m["id"]]]
                        if m["id"] in comunas_por_mun
                        else None
                    ),
                }
            )
        arvore.append(no)
    ficheiros["angola.json"] = _json({"meta": meta_pub, "provincias": arvore})
    return ficheiros


def escrever(ficheiros: dict[str, str], destino: Path) -> None:
    if destino.exists():
        shutil.rmtree(destino)
    for rel, conteudo in ficheiros.items():
        alvo = destino / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(conteudo, encoding="utf-8")


def gerar_sqlite(caminho: Path) -> None:
    dados = carregar()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if caminho.exists():
        caminho.unlink()
    con = sqlite3.connect(caminho)
    con.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE provincias (
            id TEXT PRIMARY KEY, ordem_lei INTEGER NOT NULL, nome TEXT NOT NULL,
            sede TEXT NOT NULL, origem TEXT, lei_artigo INTEGER NOT NULL);
        CREATE TABLE municipios (
            id TEXT PRIMARY KEY, provincia_id TEXT NOT NULL REFERENCES provincias(id),
            nome TEXT NOT NULL, lei_artigo INTEGER NOT NULL);
        CREATE TABLE comunas (
            id TEXT PRIMARY KEY, municipio_id TEXT NOT NULL REFERENCES municipios(id),
            nome TEXT NOT NULL, lei_artigo INTEGER);
        """
    )
    con.executemany(
        "INSERT INTO provincias VALUES (?,?,?,?,?,?)",
        [(p["id"], p["ordem_lei"], p["nome"], p["sede"], p["origem"], p["lei_artigo"])
         for p in sorted(dados["provincias"], key=lambda p: chave_alfabetica(p["nome"]))],
    )
    con.executemany(
        "INSERT INTO municipios VALUES (?,?,?,?)",
        [(m["id"], m["provincia_id"], m["nome"], m["lei_artigo"]) for m in dados["municipios"]],
    )
    con.executemany(
        "INSERT INTO comunas VALUES (?,?,?,?)",
        [(c["id"], c["municipio_id"], c["nome"], c["lei_artigo"]) for c in dados["comunas"]],
    )
    con.commit()
    con.close()


def lado_a_lado(esperado: dict[str, str], destino: Path) -> list[str]:
    """Compara o que seria gerado com o que está em disco."""
    diferencas = []
    existentes = {
        str(p.relative_to(destino)) for p in destino.rglob("*.json")
    } if destino.exists() else set()
    for rel, conteudo in esperado.items():
        alvo = destino / rel
        if not alvo.exists() or alvo.read_text(encoding="utf-8") != conteudo:
            diferencas.append(rel)
    diferencas += sorted(existentes - set(esperado))
    return diferencas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--sqlite", action="store_true", help="gera também dist/angola.sqlite")
    ap.add_argument("--check", action="store_true", help="não escreve; falha se api/v1 estiver desactualizada")
    args = ap.parse_args()

    erros, _ = validar()
    if erros:
        print("Dados inválidos; corre scripts/validate.py", file=sys.stderr)
        return 1

    ficheiros = construir(API)
    if args.check:
        dif = lado_a_lado(ficheiros, API)
        if dif:
            print("api/v1 desactualizada. Corre: python3 scripts/build.py", file=sys.stderr)
            for d in dif[:10]:
                print(f"  - {d}", file=sys.stderr)
            return 1
        print("OK: api/v1 está actualizada.")
        return 0

    escrever(ficheiros, API)
    print(f"API gerada: {len(ficheiros)} ficheiros em {API.relative_to(RAIZ)}")
    if args.sqlite:
        destino = RAIZ / "dist" / "angola.sqlite"
        gerar_sqlite(destino)
        print(f"SQLite gerado: {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
