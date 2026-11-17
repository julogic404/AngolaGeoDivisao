"""Utilitários partilhados pelos scripts (apenas biblioteca padrão)."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "data"
API = RAIZ / "api" / "v1"

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def slug(texto: str) -> str:
    """'Quiçama' -> 'quicama'; 'Icolo e Bengo' -> 'icolo-e-bengo'."""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-zA-Z0-9]+", "-", texto.lower()).strip("-")


def chave_alfabetica(texto: str) -> str:
    """Chave de ordenação alfabética ignorando acentos e maiúsculas.

    'Bié' fica entre 'Benguela' e 'Cabinda'; 'Moxico' antes de 'Moxico Leste'.
    """
    return slug(texto)


def ler_csv(nome: str) -> list[dict[str, str]]:
    with open(DADOS / nome, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ler_meta() -> dict:
    with open(DADOS / "meta.json", encoding="utf-8") as f:
        return json.load(f)


def carregar() -> dict:
    """Carrega as três tabelas já com tipos corrigidos."""
    provincias = ler_csv("provincias.csv")
    for p in provincias:
        p["ordem_lei"] = int(p["ordem_lei"])
        p["lei_artigo"] = int(p["lei_artigo"])
        p["origem"] = p["origem"] or None
    municipios = ler_csv("municipios.csv")
    for m in municipios:
        m["lei_artigo"] = int(m["lei_artigo"])
    comunas = ler_csv("comunas.csv")
    for c in comunas:
        c["lei_artigo"] = int(c["lei_artigo"]) if c["lei_artigo"] else None
    return {"provincias": provincias, "municipios": municipios, "comunas": comunas}
