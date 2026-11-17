# 🇦🇴 Dados Abertos de Angola

> Divisão político-administrativa de Angola em dados abertos, prontos a usar: **21 províncias** e **326 municípios**, com referência ao artigo da lei que define cada um. API estática (JSON), CSV e SQLite, sem servidor e sem dependências.

[English version](README.en.md)

## Porquê

Em 2024 Angola passou de 18 para 21 províncias e de 164 para 326 municípios (Lei n.º 14/24, de 5 de Setembro). Quase todas as listas na internet, e muito software, ainda usam a divisão antiga. Quem constrói formulários de morada, sistemas de entrega, saúde, educação, estatística ou comércio precisa de uma fonte **correcta, actual e rastreável**.

Este projecto é essa fonte: cada linha aponta para o artigo da lei de onde vem, e um validador impede erros silenciosos (totais, duplicados, referências partidas).

## Estado actual (v0.1.0)

| Nível | No projecto | Oficial (Lei 14/24) | Estado |
|---|---|---|---|
| Províncias | 21 | 21 | ✅ completo |
| Municípios | 326 | 326 | ✅ completo |
| Comunas | `null` (por carregar) | 378 | 🚧 a caminho, **contribuições bem-vindas** |
| Bairros | 0 | — | 🗺️ planeado |

Contagens por província confirmadas em fontes independentes: Cabinda 10, Bengo 12, Icolo e Bengo 7, Malanje 27, Bié 19. Os totais (21/326) são verificados automaticamente em cada alteração.

## Uso rápido

### Ficheiro único (ideal para apps offline ou com internet lenta)

[`api/v1/angola.json`](api/v1/angola.json) contém a árvore completa província → município → comuna. Descarrega uma vez e guarda no dispositivo.

### API estática

Publicada via GitHub Pages (substitui `<utilizador>` pelo teu):

```text
https://<utilizador>.github.io/dados-abertos-angola/api/v1/index.json
https://<utilizador>.github.io/dados-abertos-angola/api/v1/provincias.json
https://<utilizador>.github.io/dados-abertos-angola/api/v1/provincias/luanda.json
https://<utilizador>.github.io/dados-abertos-angola/api/v1/municipios/luanda-ingombota.json
```

Ou directamente do repositório, sem Pages:
`https://raw.githubusercontent.com/<utilizador>/dados-abertos-angola/main/api/v1/provincias.json`

### Exemplos

**JavaScript**
```js
const r = await fetch(".../api/v1/provincias/malanje.json");
const { dados } = await r.json();
console.log(dados.nome, dados.total_municipios); // Malanje 27
```

**Python (sem instalar nada)**
```python
import json, urllib.request
url = ".../api/v1/provincias.json"
for p in json.load(urllib.request.urlopen(url))["dados"]:
    print(p["nome"], "→", p["sede"])  # já vem por ordem alfabética
```

**SQL (SQLite)**
```bash
python3 scripts/build.py --sqlite     # gera dist/angola.sqlite
sqlite3 dist/angola.sqlite "select p.nome, count(*) from municipios m
  join provincias p on p.id = m.provincia_id group by p.id order by 2 desc limit 5;"
```

**Kotlin / Android**: copia `api/v1/angola.json` para `assets/` e lê com `kotlinx.serialization`. Funciona 100% offline.

## Estrutura

```text
data/            ← FONTE DA VERDADE (CSV editáveis por qualquer pessoa)
  provincias.csv
  municipios.csv
  comunas.csv
  meta.json
api/v1/          ← gerada a partir dos CSV (não editar à mão)
site/index.html  ← página inicial (GitHub Pages)
scripts/
  validate.py    ← valida totais, duplicados, referências
  build.py       ← gera api/v1 (e SQLite com --sqlite)
tests/           ← python3 -m unittest discover -s tests
docs/FONTES.md   ← de onde vem cada dado
```

## Modelo de dados

- `id`: texto estável sem acentos (`icolo-e-bengo`, `luanda-ingombota`). Município = `<provincia>-<nome>`; comuna = `<municipio>-<nome>`.
- `nome`: grafia **como na lei** (ex.: `Cuanza-Norte`, `Kilamba Kiaxi`).
- `sede` (províncias): sede **tal como definida na lei**. Atenção: a lei dá como sede o *município* (ex.: Cunene tem sede no município do Cuanhama; Bengo, no Dande).
- **Ordem**: todas as listas vêm por **ordem alfabética** (sem contar acentos: *Bié* fica entre *Benguela* e *Cabinda*). `municipios.json` é uma lista plana por nome do município; dentro de cada província, os municípios também estão por ordem alfabética. A ordem em que a lei lista as províncias fica guardada em `ordem_lei` (1 a 21).
- **`null` = ainda não carregado**: enquanto as comunas não estiverem no projecto, `comunas` e `total_comunas` vêm a `null` (e não como lista vazia/zero), para não se confundir "ainda não sabemos" com "não tem".
- `origem`: província de que se desanexou, quando aplicável (Icolo e Bengo ← Luanda; Moxico Leste ← Moxico; Cubango e Cuando ← Cuando Cubango).
- `lei_artigo`: artigo da Lei n.º 14/24 onde a unidade é definida.

Ver `data/*.csv` para as colunas exactas.

## Contribuir

O maior contributo possível agora é **completar as 378 comunas**: cada município tem as suas comunas descritas no artigo "Composição" a seguir ao artigo do município. Vê o [CONTRIBUTING.md](CONTRIBUTING.md): é só editar um CSV e abrir um pull request; o CI diz-te logo se algo está errado.

Também ajudam: correcções de grafia, localidades e bairros (com fonte), coordenadas, e traduções.

## Roadmap

- [x] Províncias e municípios (Lei 14/24)
- [ ] Comunas (378)
- [ ] Códigos oficiais da Lei n.º 8/25 (Codificação das Unidades Territoriais)
- [ ] População por unidade (Censo 2024, INE)
- [ ] Coordenadas dos centros das unidades
- [ ] Bairros e localidades de grandes cidades (Luanda, Huambo, Benguela, Lubango…)
- [ ] Pacotes `pip` e `npm`

## Licenças

- **Autoria**: © 2026 JuLogic 404 e contribuidores
- **Código** (`scripts/`, `tests/`): [MIT](LICENSE)
- **Dados** (`data/`, `api/`): [CC BY 4.0](LICENSE-DATA): usa livremente, inclusive comercialmente, citando este projecto.

A fonte primária é a lei publicada em Diário da República; ver [docs/FONTES.md](docs/FONTES.md).

> Este projecto não é uma publicação oficial do Estado angolano. Em caso de dúvida, prevalece o texto da lei publicado em Diário da República.
