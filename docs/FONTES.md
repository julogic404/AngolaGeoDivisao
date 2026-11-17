# Fontes e metodologia

## Fonte primária

**Lei n.º 14/24, de 5 de Setembro de 2024** (Lei da Divisão Político-Administrativa), Diário da República, I Série, n.º 171. Fixa **21 províncias, 326 municípios e 378 comunas** e revoga a Lei n.º 18/16.

- Texto consolidado consultado: AngoLEX, <https://angolex.com/paginas/leis/lei-da-divisao-politico-administrativa-14a-24a.html>
- Rectificação n.º 10/24, de 9 de Dezembro (indicada no AngoLEX). **Ainda por verificar contra os dados**; ver "Limitações".

## Como os dados foram extraídos (v0.1.0)

- **Províncias**: nomes e sedes do artigo 2.º, n.º 3; a sequência em que a lei as lista fica em `ordem_lei`; as listas publicadas seguem a ordem alfabética.
- **Municípios**: lista construída a partir do índice de artigos da lei (um artigo "Município de X" por município). Cada município guarda o número do artigo (`lei_artigo`).
- **Verificação do total**: a soma dá exactamente 326, igual ao total fixado no artigo 2.º, n.º 1.
- **Verificação cruzada** (contagens por província em fontes independentes da lei): Cabinda 10 (art. 5.º da própria lei), Bengo 12 (INE, Recenseamento 2024), Icolo e Bengo 7 (imprensa/Wikipédia), Malanje 27 (Wikipédia pt), Bié 19 (INE, Recenseamento 2024). Estas contagens estão codificadas em `scripts/validate.py`.

## Outras fontes úteis (ainda não incorporadas)

- Lei n.º 8/25, de 16 de Setembro: Codificação das Unidades Territoriais (códigos oficiais). <https://lex.ao/docs/assembleia-nacional/2025/lei-n-o-8-25-de-16-de-setembro/>
- INE: Resultados definitivos do Recenseamento Geral da População e da Habitação 2024 (população por município e comuna).
- Ministério da Administração do Território: <https://mat.gov.ao/web/mapa-de-angola>

## Limitações conhecidas

1. **Comunas**: ainda não incluídas (0 de 378); a API devolve `null`. Estão descritas nos artigos "Composição" da lei.
2. **Grafias**: seguem o índice da lei. Há variações na imprensa (ex.: *Kuanza* / *Cuanza*, *Kilamba* / *Quilamba*); `nome` mantém a grafia da lei.
3. **Rectificação 10/24**: pode ter corrigido nomes ou artigos. Revisão pendente; correcções bem-vindas por *issue*.
4. **Sede da província**: a lei indica um *município* como sede (ex.: Cunene → Cuanhama). O nome da cidade correspondente (ex.: Ondjiva) não faz parte dos dados desta versão.
5. **Implementação gradual**: a lei prevê a instalação gradual das novas estruturas; a existência legal de uma unidade não implica que já esteja em funcionamento administrativo pleno.
6. **Alterações futuras**: a divisão pode mudar. Ver `meta.json` (`verificado_em`) e o `CHANGELOG.md`.
