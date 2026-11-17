# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). Versões semânticas: dados novos = *minor*, correcções = *patch*, mudança de formato = *major*.

## [0.1.0] - 2026-11-16

### Adicionado
- 21 províncias e 326 municípios segundo a Lei n.º 14/24, com `lei_artigo` por unidade.
- API estática em `api/v1/` (JSON), geração opcional de SQLite.
- Validador (`scripts/validate.py`), gerador (`scripts/build.py`) e testes.
- Documentação em português e inglês, guia de contribuição.

### Formato
- Províncias, municípios (e comunas) por ordem alfabética sem acentos, nos CSV e na API. A ordem da lei fica em `ordem_lei`.
- Comunas por carregar vêm como `null` (campos `comunas` e `total_comunas`, `comunas.json` e `meta.totais.comunas`), não como lista vazia ou zero.

### Pendente
- Comunas (0/378), códigos da Lei 8/25, população, coordenadas, bairros.
