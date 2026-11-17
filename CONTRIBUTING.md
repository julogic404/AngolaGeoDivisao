# Como contribuir

Obrigado por ajudares a ter dados correctos sobre Angola! Não precisas de saber programar: basta editar um ficheiro CSV.

## Regra de ouro

**Toda a linha tem fonte.** Não aceitamos dados "de memória" nem copiados de listas sem fonte. A fonte primária é a **Lei n.º 14/24, de 5 de Setembro** (Diário da República, I Série, n.º 171). O texto completo está, por exemplo, em <https://angolex.com/paginas/leis/lei-da-divisao-politico-administrativa-14a-24a.html>.

## Tarefa mais útil agora: completar as comunas (378)

Em `data/comunas.csv` (colunas `id,municipio_id,nome,lei_artigo`):

1. Escolhe **um município** (de preferência uma província inteira, para ser fácil de rever).
2. Na lei, procura o artigo do município (coluna `lei_artigo` em `data/municipios.csv`). O artigo seguinte, "Composição", diz que comunas ele compreende ("O Município de X compreende as Comunas de A, B e C…").
3. Acrescenta uma linha por comuna:
   - `id` = `<municipio_id>-<nome sem acentos, minúsculas, hífenes>` (ex.: `cabinda-cacongo-landana`)
   - `municipio_id` = o `id` do município em `municipios.csv`
   - `nome` = grafia **como na lei**
   - `lei_artigo` = número do artigo "Composição"
4. Nota: municípios sem artigo de "Composição" não têm comunas definidas na lei. **Não inventes comunas**: deixa sem linhas.
5. Corre as verificações (abaixo) e abre o pull request com a província indicada no título.

## Verificar localmente

Só precisas de Python 3.9+ (sem instalar nada):

```bash
python3 scripts/validate.py                 # valida os dados
python3 scripts/build.py                    # regenera api/v1 (obrigatório antes de commit)
python3 -m unittest discover -s tests       # corre os testes
```

> `api/v1/` é **gerada** a partir de `data/`. Nunca a edites à mão: corre `build.py` e inclui o resultado no commit. O CI falha se estiver desactualizada.

## Outras contribuições

- **Correcção de grafia**: abre uma *issue* "Correcção de dados" com o artigo da lei e a grafia correcta.
- **Novos campos** (população, coordenadas, códigos da Lei 8/25): abre primeiro uma *issue* a propor o campo e a fonte.
- **Bairros / localidades**: precisam de fonte oficial ou aberta com licença compatível (CC BY 4.0). Indica-a no PR. Não copies de fontes com direitos reservados.

## Convenções

- Codificação UTF-8, fim de linha `\n`, cabeçalho de CSV inalterado.
- Mantém os CSV por **ordem alfabética** (sem contar acentos): províncias por nome; municípios por província e nome; comunas por município e nome. A validação confere. `ordem_lei` guarda a ordem em que a lei lista as províncias.
- Um município sem linhas em `comunas.csv` aparece na API com `comunas: null` ("por carregar"). Ao acrescentares as suas comunas, passa a ser uma lista.
- Mensagens de commit curtas, em português ou inglês.

## Conduta

Sê respeitoso e construtivo. Dados sobre território podem ser sensíveis; mantemo-nos factuais e fiéis à lei publicada.
