# CLAUDE.md — TerraFM-Temporal (Projeto 2, RNAP 2026/2, UnB)

Responda sempre em **português**. O código, os identificadores e as mensagens de commit ficam em inglês. Comentários e documentação ficam em português.

## O projeto
O projeto fiscaliza a restauração de APPs no Conservador das Águas, em Extrema (MG), com séries temporais Sentinel-2. A arquitetura tem quatro partes:
1. **TerraFM-B congelado** (ICLR 2026) como encoder de cada data;
2. **cabeça temporal** com Mamba de camada única (inspirada no MambaSL) e codificação do dia real da aquisição;
3. **decodificador** a 10 m;
4. **mapa anual** de floresta 2017–2025 → ano de início e idade da regeneração → indicador por APP.

- **Fonte de verdade do escopo, das fases e do cronograma:** `docs/PLANO_IMPLEMENTACAO.md`. Leia a seção relevante antes de qualquer tarefa.
- **Roteiro entregue:** `docs/roteiro/`.

## Regras de trabalho
- **Faça só o que a tarefa pede.** Não acrescente funcionalidades, baselines, dependências, referências nem texto que não foram pedidos. Se algo parecer necessário, proponha e espere a confirmação.
- **Tarefas não triviais começam com um plano curto**, que cite a seção do plano de implementação e traga os critérios de pronto.
- **Mudanças de escopo** são registradas primeiro em `docs/PLANO_IMPLEMENTACAO.md`, com a aprovação do aluno.
- **Integridade dos resultados:**
  - nunca invente nem estime números de resultado; métricas só vêm de arquivos em `outputs/`;
  - todo experimento salva `config.yaml`, semente, hash do commit e `metrics.json` em `outputs/runs/<AAAAMMDD-HHMM>_<nome>/`.
- **Teste no mini-AOI primeiro** (1 recorte × 1 ano, `configs/aoi.yaml: mini`), e só depois rode na área toda.
- **Comandos longos** (downloads, extração de tokens, treinos) rodam em segundo plano, com log em arquivo. Acompanhe pelos logs.
- **Não versione** dados, pesos ou saídas: `data/`, `outputs/`, `*.pth`, `*.zarr` estão no `.gitignore`.
- **Caminhos** vêm sempre dos YAML em `configs/`; nada de caminho absoluto no código.

## Ambiente
- **Sistema:** Windows, conda env `rnap` (Python 3.11, PyTorch 2.14.1+cu126).
- **Máquinas:** desenvolvimento e testes nesta máquina, com GTX 1650 de 4 GB; rodadas completas em outra máquina, com RTX 2070 Max-Q de 8 GB. Use fp16 na inferência e lotes pequenos.
- **Mamba:** use `mambapy` (PyTorch puro). O `mamba-ssm` não roda no Windows.
- **Comandos:**
  - criar o ambiente: `conda env create -f environment.yml` e depois `conda run -n rnap --no-capture-output pip install -e . --no-deps`;
  - terminal interativo: `conda activate rnap`;
  - scripts: `conda run -n rnap --no-capture-output python scripts/<NN>_<nome>.py --config configs/<arquivo>.yaml`;
  - pesos do TerraFM-B: `conda run -n rnap --no-capture-output python scripts/00_download_weights.py --config configs/model/terrafm.yaml`;
  - testes: `conda run -n rnap --no-capture-output python -m pytest tests -q`. Sem rede, acrescente `-m "not network"`; sem GPU, `-m "not gpu"`.

## Fatos técnicos já verificados (não redescobrir)
- **BDC:**
  - STAC: `https://data.inpe.br/bdc/stac/v1/`, coleção `S2-16D-2` (composições LCF de 16 dias, 10 m, de 2017-01-01 em diante, grade `BDC_SM_V2`, projeção Albers).
  - Bandas: `B01 B02 B03 B04 B05 B06 B07 B08 B8A B09 B11 B12`, em uint16 com escala 1e-4 e nodata 0.
  - Auxiliares: `SCL`, `CLEAROB` (0 = sem observação limpa) e `PROVENANCE` (dia do ano da aquisição escolhida).
  - **Não há Sentinel-1 no BDC.**
  - Os assets abrem sem token: um GET parcial de um COG respondeu 206 em 25/11/2026.
- **TerraFM** (`github.com/mbzuai-oryx/TerraFM`, commit `e245c347` de 13/11/2026; pesos em `huggingface.co/MBZUAI/TerraFM`, revisão `86f62795`):
  - Licença MIT para o código e os pesos; os trechos do DINO são Apache-2.0.
  - `forward(x, is_l2a=False)` recebe **um sensor por vez** (2 canais = S1, 12 canais = S2) e devolve **só o token CLS**.
  - Todos os métodos usam `is_l2a=False` (stem **L1C**) por padrão. Para o BDC (L2A), passe sempre `is_l2a=True`.
  - Tokens de patch: `get_intermediate_layers(x, n=1, is_l2a=True, norm=True)` (196×768). Sem `norm=True`, eles saem antes da LayerNorm final.
  - Normalização oficial: `normalize(x, "s2_l2a")` sobre DN brutos (refletância×10000, o uint16 do BDC sem aplicar a escala). O README desaconselha o z-score por conjunto de dados.
  - Ordem das bandas (`S2_BANDS`): `B01…B08, B8A, B09, B11, B12`, a mesma do BDC.
  - O código público não tem a fusão S1/S2 por atenção cruzada.
- **MapBiomas Coleção 11** (30 m, anual): 3 = Formação Florestal (alvo); 9 = Silvicultura (**não** é floresta nativa); 15 = Pastagem; 21 = Mosaico; 12 = Formação Campestre; 11 = Campo Alagado. O download pelo site está suspenso, e os dados saem pelo GEE.
- **MambaSL** (`github.com/yoom618/MambaSL`, MIT, base TSLib) classifica a **série inteira**. Aqui, o pooling adaptativo é aplicado por janela anual.

## Registro de uso de IA (obrigatório na disciplina)
Ao fim de cada sessão de trabalho, acrescente **no final** de `docs/registro_uso_ia_claude_code.md` uma entrada neste formato. Nunca edite entradas antigas.
```
### [AAAA-MM-DD] <título curto>
- Etapa: (ambiente | dados | modelo | experimentos | análise | escrita)
- Ferramenta: Claude Code (VS Code), modelo <identificador exibido na sessão>
- Pedido do aluno: <resumo fiel>
- O que a IA fez: <arquivos criados/alterados, comandos rodados>
- Resultado: <o que funciona, onde está>
- Verificação humana: a preencher pelo aluno
- Limitações/erros: <falhas, suposições não verificadas>
```
