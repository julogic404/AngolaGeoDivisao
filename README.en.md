# 🇦🇴 Open Data Angola

> Angola's administrative divisions as clean, ready-to-use open data: **21 provinces** and **326 municipalities**, each traced to the article of the law that defines it. Static JSON API, CSV and SQLite. No server, no dependencies.

[Versão em português](README.md)

## Why

In 2024 Angola went from 18 to 21 provinces and from 164 to 326 municipalities (Law 14/24 of 5 September 2024). Most lists online, and a lot of software, still use the old division. This project provides a **correct, current and traceable** source, with a validator that catches silent errors (totals, duplicates, broken references).

## Status (v0.1.0)

| Level | In project | Official | Status |
|---|---|---|---|
| Provinces | 21 | 21 | ✅ complete |
| Municipalities | 326 | 326 | ✅ complete |
| Communes | `null` (not loaded) | 378 | 🚧 help wanted |
| Neighbourhoods (bairros) | 0 | n/a | 🗺️ planned |

## Quick start

Single file for offline / low-bandwidth apps: [`api/v1/angola.json`](api/v1/angola.json) (full province → municipality → commune tree).

Static API (via GitHub Pages):

```text
/api/v1/index.json
/api/v1/provincias.json
/api/v1/provincias/luanda.json
/api/v1/municipios/luanda-ingombota.json
```

```python
import json, urllib.request
url = ".../api/v1/provincias.json"
for p in json.load(urllib.request.urlopen(url))["dados"]:
    print(p["nome"], "->", p["sede"])  # already alphabetical
```

Build a SQLite database: `python3 scripts/build.py --sqlite` → `dist/angola.sqlite`.

All lists are **alphabetical** (accents ignored). The order used in the law is kept in `ordem_lei`. Communes not yet loaded are `null` (not an empty list), meaning "unknown yet".

Field names are in Portuguese (`provincias`, `municipios`, `comunas`, `nome`, `sede`, `lei_artigo`).

## Contributing

The biggest need is the **378 communes**. Edit `data/comunas.csv`, open a pull request, and CI validates it. See [CONTRIBUTING.md](CONTRIBUTING.md) (Portuguese).

## License

© 2026 JuLogic 404 and contributors. Code: [MIT](LICENSE). Data: [CC BY 4.0](LICENSE-DATA). Primary source: Lei n.º 14/24 (Diário da República, I Série, n.º 171). Not an official publication of the Angolan State; the published law prevails.
