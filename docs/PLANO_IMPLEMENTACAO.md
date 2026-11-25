# Plano de implementação — TerraFM-Temporal (Projeto 2, RNAP 2026/2)

- **Versão:** 24/11/2026
- **Prazo-alvo:** 14/12/2026, com 15/12 de folga. Ajuste as datas se o prazo oficial for outro.
- **Ferramenta de desenvolvimento:** Claude Code no VS Code.
- **Escopo:** este documento é a referência de escopo, fases e critérios de pronto. Mudanças de escopo devem ser registradas aqui antes de virar código.

---

## 0. Decisões já tomadas e consequências

| Decisão | Consequência para o projeto |
|---|---|
| Prazo de ~3 semanas | Desenvolver primeiro um MVP. As extensões só entram se os marcos forem cumpridos. |
| MVP incremental | Primeiro: S2 em composições, treino em Extrema e mapa anual. Depois, em ordem de prioridade: datas reais de aquisição, saída por trajetória, Sentinel-1 e séries por aquisição. |
| Imagens do Brazil Data Cube (BDC), cubo `S2-16D-2` | O BDC **não tem Sentinel-1**: nenhuma coleção S1 foi encontrada. O MVP usa só o Sentinel-2. A hipótese H2 (S1+S2) vira extensão, com o S1 RTC do Planetary Computer, ou trabalho futuro. |
| Treino em Extrema e teste nas Posses | A sub-bacia das Posses tem só ~1.200 ha, o que dá 2–3 recortes de 224×224. Ela fica reservada para teste e fiscalização. O treino usa o resto do município. |
| Normalização oficial do TerraFM (25/11) | O commit `e245c347` do upstream publicou `normalize(x, "s2_l2a")`, a ordem das bandas e a licença MIT. O wrapper recebe DN brutos e usa essa normalização; a sondagem da seção 4.7 só a confirma. |
| Desenvolvimento nesta máquina, execução em outra (25/11) | Os testes rodam na GTX 1650 de 4 GB; as rodadas completas, em outra máquina, com RTX 2070 Max-Q de 8 GB. O `environment.yml` serve às duas, que são Turing (sm_75). |

> **Impacto no artigo final.** O roteiro fala em S1+S2 e só nas Posses. O artigo terá de dizer que o MVP usa apenas S2 (BDC) e treina em Extrema. Se o S1 entrar como extensão, isso também precisa constar.

---

## 1. Objetivo do MVP e critérios de pronto

**Pipeline completo:** cubo S2 do BDC → TerraFM-B congelado → cabeça temporal → mapa anual floresta/não floresta a 10 m (2017–2025) → ano de início e idade da regeneração → indicador de conformidade por APP nas Posses.

**Pronto quando:**
1. `scripts/` reproduz de ponta a ponta, a partir de arquivos de configuração, o download, os rótulos, os embeddings, o treino, a avaliação e o relatório por APP.
2. Existe uma tabela de resultados no conjunto de teste (Posses, rótulos de referência) com:
   - **P**, o modelo proposto;
   - **B3**, o TerraFM data a data;
   - **B2**, uma rede temporal treinada do zero;
   - **B1**, o método clássico;
   - **MapBiomas**, como referência.
3. Pelo menos duas ablações rodadas (A1 e A2, seção 4.6).
4. Há figuras para o artigo: mapas, ano de início, indicador por APP e exemplos de trajetórias.
5. O repositório GitHub `Jibabk/RNAP_UnB2026` está publicado, com README de reprodução.

---

## 2. Ambiente

**Recomendação:** Windows nativo com Miniforge (conda-forge), VS Code e a extensão do Claude Code. É o caminho com menos peças para 3 semanas.

| Item | Escolha | Observação |
|---|---|---|
| Python | 3.11, num ambiente conda chamado `rnap` | Instalar GDAL e rasterio pelo conda-forge, não pelo pip. |
| PyTorch | 2.14.1 com CUDA 12.6 (wheel `cu126`, pelo pip) | Desenvolvimento e testes na GTX 1650 de 4 GB; rodadas completas em outra máquina, com RTX 2070 Max-Q de 8 GB. Inferência do TerraFM em fp16. |
| Mamba | `mambapy` 1.2.0 (PyTorch puro) | O `mamba-ssm` usado pelo MambaSL só roda em Linux com NVIDIA. Usar WSL2 só se o `mambapy` for lento demais. Com sequências de ~200 passos e d=128, o `mambapy` deve bastar. |
| Dados geoespaciais | `pystac-client`, `odc-stac` (ou `stackstac`), `rasterio`, `rioxarray`, `xarray`, `zarr`, `geopandas`, `shapely`, `pyproj` | |
| Treino e avaliação | `numpy`, `pandas`, `scikit-learn`, `ruptures`, `tqdm`, `pyyaml`, `matplotlib`, `tensorboard` | |
| Opcional | `earthengine-api` (MapBiomas pelo GEE) e `planetary-computer` (S1 RTC, extensão) | |

**Armazenamento:** prever ~30 GB livres fora do git, por exemplo em `D:\UNB\TCC\dados_rnap\`. Estimativa na seção 3.6.

---

## 3. Dados

### 3.1 Área de estudo e partições
- **Área total:** município de Extrema (MG). A grade de recortes de 224×224 px, ou 2,24 km, é alinhada à grade do BDC (Albers, `BDC_SM_V2`, 10 m).
- **Teste:** a sub-bacia das Posses, mais um buffer de 500 m. Nenhum pixel do teste entra no treino.
- **Validação:** blocos espaciais, ~20% dos recortes de treino, sorteados por bloco e não por pixel.
- **Transferência (extensão):** Joanópolis e Nazaré Paulista (SP).

### 3.2 Imagens: BDC `S2-16D-2`
- **Produto:** "Sentinel-2/MSI – Level-2A – Data Cube – LCF 16 days". As composições são de 16 dias, com o pixel de menor cobertura de nuvem (*Least Cloud Cover First*). Período: de 2017-01-01 até hoje. Pixel de 10 m.
- **Bandas (12):** `B01 B02 B03 B04 B05 B06 B07 B08 B8A B09 B11 B12`, em uint16, com escala 0,0001 e nodata 0. São exatamente os 12 canais que o ramo S2 do TerraFM espera.
- **Auxiliares:**
  - `SCL`, a classificação de cena;
  - `CLEAROB`, o número de observações limpas (0 = sem observação válida);
  - `TOTALOB`;
  - `PROVENANCE`, o **dia do ano da aquisição** escolhida para cada pixel;
  - `NDVI`, `EVI` e `NBR`, em int16 com escala 0,0001.
- **Série:** 2017–2025, ~23 composições por ano, ~207 passos.
- **Acesso:** STAC em `https://data.inpe.br/bdc/stac/v1/`, coleção `S2-16D-2`. Os assets são COGs. ⚠ Conferir na Fase 0 se o download exige token (o BDC já exigiu `access_token` gratuito).
- **Formato local:** Zarr por recorte, com os arrays `x[T,12,224,224]` (uint16), `valid[T,224,224]` (bool), `doy[T,224,224]` (int16) e `date[T]`.

### 3.3 Rótulos fracos: MapBiomas Coleção 11 (30 m, anual)
- **Classes relevantes:** 3 = Formação Florestal (alvo), 9 = Silvicultura (**não** é floresta nativa; o eucalipto é comum na região), 15 = Pastagem, 21 = Mosaico de usos, 12 = Formação Campestre e 11 = Campo Alagado.
- **Alvo binário:** floresta = classe 3; não floresta = o resto. Pixels de nodata são mascarados.
- **Acesso:** o download direto pelo site está **suspenso**, e o MapBiomas indica os assets no Google Earth Engine.
  - Opção 1: conta GEE gratuita e exportação do recorte de Extrema para 2017–2025.
  - Opção 2: o toolkit de recorte do MapBiomas.
  - Plano B: uma coleção anterior no bucket público, se ainda estiver acessível.
- **Alinhamento:** reprojetar para a grade do BDC a 10 m por vizinho mais próximo. Registrar a perda de resolução, porque o rótulo é de 30 m.
- ⚠ Confirmar na Fase 0 que a Coleção 11 cobre 2025 (deduzido, não confirmado).

### 3.4 Rótulos de referência (ouro), para teste
- **Quantidade:** ~200 pontos estratificados pela trajetória no MapBiomas, sobretudo nas Posses:

| Estrato | Pontos |
|---|---|
| Floresta estável | 40 |
| Não floresta estável | 40 |
| Ganho de floresta entre 2018 e 2024 | 60 (sobreamostrado, é raro) |
| Perda | 20 |
| Silvicultura | 20 |
| Aleatórios dentro de APP | 20 |

  Se houver poucos pontos de ganho nas Posses, completar com blocos de teste de Extrema.
- **Interpretação:** ano a ano (2017–2025), com o histórico do Google Earth Pro e as composições RGB do próprio cubo.
- **Arquivo:** `data/gold/pontos_referencia.csv`, com as colunas `id, lon, lat, estrato, y2017..y2025 (1/0/-1 incerto), fonte, obs`.
- **Tempo:** ~6–8 h, divididas entre 26/11 e 04/12. Esta é a tarefa manual mais longa; comece cedo.

### 3.5 APP e limites
- **APP:** camada de APP do SICAR/CAR, no download público por município (Extrema). Plano B: faixas de 30 m sobre a hidrografia (IBGE ou ANA) e raio de 50 m em torno das nascentes.
- **Sub-bacia das Posses:** ottobacias da ANA ou delimitação por MDE. Plano B: polígono digitalizado a partir do mapa do programa.

### 3.6 Volume estimado
- **Recortes:** ~50–70 recortes de 224×224 intersectam o município. Isso dá ~207 passos × ~1,35 MB por recorte e data ≈ **15–20 GB** sem compressão, e menos com Zarr comprimido.
- **Tokens do TerraFM:** 196×768 em fp16 ≈ 0,3 MB por recorte e data, o que dá ≈ **3–5 GB**.
- **Inferência:** ~15 mil passagens do ViT-B, alguns minutos na RTX 2070. O gargalo é o download.

---

## 4. Modelo e comparações

### 4.1 Encoder: TerraFM-B congelado
- **Código:** `terrafm.py` copiado sem alterações para `src/terrafm_temporal/encoders/third_party/`, do commit `e245c347` (13/11/2026), com o LICENSE ao lado. Licença MIT para o código e os pesos; os trechos do DINO são Apache-2.0. Pesos: `MBZUAI/TerraFM`, arquivo `TerraFM-B.pth`.
- **Cuidados com o código público:**
  - `forward()` aceita **um sensor por vez** (2 canais = S1, 12 = S2) e devolve **só o CLS**.
  - Todos os métodos usam `is_l2a=False` (stem **L1C**) por padrão. Para L2A, passar `is_l2a=True`.
  - Os tokens de patch vêm de `get_intermediate_layers(x, n=1, is_l2a=True, norm=True)` (196×768) ou de `extract_feature(..., out_indices=[3,5,7,11], is_l2a=True)` (mapas 14×14). Sem `norm=True`, os tokens saem antes da LayerNorm final.
- **Normalização e ordem de bandas:** ambas são oficiais desde o commit `e245c347`. A entrada são DN brutos (refletância×10000, o uint16 do BDC sem aplicar a escala), normalizados com `normalize(x, "s2_l2a")`, na ordem `S2_BANDS` = `B01…B08, B8A, B09, B11, B12`, que é a mesma do BDC. O README desaconselha o z-score por conjunto de dados. A sondagem da seção 4.7 confirma essa escolha.
- **Validade do token:** ≥50% de pixels limpos no patch de 16×16 (`CLEAROB>0` e SCL ∉ {0,1,3,8,9,10}).

### 4.2 Modelo proposto P (TerraFM-Temporal)
Para cada posição de token (14×14 por recorte):
1. **Projeção:** 768 → d = 128.
2. **Codificação de data:** dia do ano **real da aquisição**, a mediana de `PROVENANCE` no patch, codificada por seno e cosseno, mais um embedding do ano.
3. **Sequência:** só os passos válidos (máscara), o que dá uma série irregular, na linha da taxonomia do PYRREGULAR.
4. **Codificador temporal:** um bloco Mamba de camada única (`mambapy`) com as mudanças do MambaSL que se aplicam aqui:
   - projeção de entrada convolucional com kernel proporcional ao comprimento;
   - sem o termo de *skip* D.
   Antes de implementar, conferir no repositório do MambaSL (MIT) como cada mudança foi feita.
5. **Pooling anual:** o *pooling* adaptativo multi-cabeça do MambaSL é aplicado **dentro da janela de cada ano**. Saem 9 embeddings anuais por token. É a adaptação que transforma a classificação da série inteira do MambaSL em saída por ano.
6. **Decodificador a 10 m:**
   - os mapas anuais 14×14×128 são reamostrados para 224×224;
   - eles são concatenados com a mediana anual das 12 bandas e do NDVI/NBR a 10 m;
   - 3–4 camadas convolucionais produzem um logit por pixel e ano.
7. **Perda:** entropia cruzada binária com peso de classe (`pos_weight`), mascarada onde o rótulo é inválido.

### 4.3 Pós-processamento
- **Ano de início:** a* = primeiro ano em que ŷ(a−1)=0 e ŷ=1 por **k=2** anos seguidos. Isso vale para os inícios de 2018 a 2024; k=3 entra como análise de sensibilidade.
- **Idade:** 2025 − a*. As áreas regeneradas antes de 2017 aparecem como "floresta estável", sem idade.
- **APP:** F_j é a fração de floresta da APP j em 2025. Gera-se um alerta quando F_j < λ, com λ ∈ {0,5; 0,7; 0,9} em análise de sensibilidade.

### 4.4 Baselines (alinhadas à pergunta de pesquisa do roteiro)
| Id | Método | Para quê |
|---|---|---|
| **B3** | TerraFM data a data: mesmos tokens e mesmo decodificador; a cabeça temporal é trocada pela média anual dos tokens válidos | Comparação central (H1): isola o efeito da modelagem temporal |
| **B2** | Rede temporal do zero: TempCNN por pixel sobre as 12 bandas e o NDVI da série anual (~23 passos) → floresta por ano | Mostra o valor do modelo de fundação |
| **B1** | Clássico: mediana anual de NBR/NDVI por pixel, limiar ajustado no treino e mesma regra de início; opcionalmente, segmentação com `ruptures` | Método clássico de segmentação temporal |
| **Ref** | MapBiomas comparado com os rótulos de referência | Qualidade do rótulo fraco |

### 4.5 Métricas
- **Mapa anual:** F1 de floresta e acurácia balanceada nos pontos de referência e nos pixels do MapBiomas do teste.
- **Ganho:** F1 nos pontos do estrato "ganho".
- **Ano de início:** acurácia exata e com tolerância de ±1 ano.
- **APP:** erro absoluto de F_j em relação à referência e concordância do alerta.
- **Variabilidade:** P e B3 com 3 sementes, se houver tempo, relatando média ± desvio.

### 4.6 Ablações, em ordem de prioridade
- **A1 — data:** dia real (`PROVENANCE`) × data nominal da composição × sem codificação de data. *Na série de composições, é o que liga o projeto ao PYRREGULAR.*
- **A2 — codificador:** Mamba (MambaSL) × L-TAE. A versão com L-TAE equivale ao protocolo do PANGAEA.
- **A3 — máscara:** descartar os passos inválidos × mantê-los com nuvem.
- **Extensões, só se os marcos forem cumpridos:**
  - **E1:** saída como classe de trajetória (MambaSL quase sem mudanças);
  - **E2:** Sentinel-1 RTC (Planetary Computer) com fusão tardia dos tokens S1 e S2;
  - **E3:** frações de rótulos de referência;
  - **E4:** série por aquisição (cenas `S2_L2A`).

### 4.7 Verificação de sanidade (antes de treinar qualquer coisa)
- **Teste:** sondagem linear (regressão logística) sobre os tokens de **uma data**, com o rótulo "fração de floresta do MapBiomas no patch > 0,5".
- **Critério:** a acurácia balanceada deve ficar claramente acima de 0,5 (meta: > 0,8). Essa verificação confirma a normalização oficial e a ordem das bandas.
- **Se falhar:** parar e investigar antes de seguir. A refletância ×1e-4 e o z-score por banda entram só como diagnóstico.

---

## 5. Estrutura do repositório

```
ProjetoFinalRNAP_UnB2026/
├── CLAUDE.md                     # instruções para o Claude Code
├── README.md                     # como reproduzir
├── environment.yml
├── .gitignore                    # data/, outputs/, *.pth, *.zarr
├── configs/
│   ├── aoi.yaml                  # Extrema, Posses, buffers, anos
│   ├── data.yaml                 # BDC, bandas, MapBiomas, caminhos
│   └── model/{p_mamba,p_ltae,b3,b2}.yaml
├── src/terrafm_temporal/
│   ├── data/      (bdc.py, mapbiomas.py, app.py, tiling.py, dataset.py)
│   ├── encoders/  (terrafm_wrapper.py, third_party/terrafm.py)
│   ├── models/    (temporal_mamba.py, ltae.py, decoder.py, baselines.py)
│   ├── train.py, evaluate.py, postprocess.py, utils.py
├── scripts/
│   ├── 01_download_bdc.py   02_labels_mapbiomas.py   03_app_layers.py
│   ├── 04_extract_tokens.py 05_sanity_probe.py       06_train.py
│   ├── 07_evaluate.py       08_app_report.py         09_figures.py
├── tests/                        # testes rápidos com 1 recorte × 1 ano
├── notebooks/                    # só exploração; nada de resultado final
├── docs/
│   ├── PLANO_IMPLEMENTACAO.md    # este arquivo
│   ├── registro_uso_ia_claude_code.md
│   └── roteiro/ (roteiro_projeto2.tex, .pdf)
├── article/                      # artigo IEEE (LaTeX)
├── slides/
├── data/      (fora do git)
└── outputs/   (fora do git: runs/<data>_<nome>/{config.yaml, metrics.json, logs})
```

---

## 6. Metodologia de trabalho com o Claude Code

**Ciclo de cada tarefa** (uma tarefa = um item do cronograma):
1. **Planejar:** abrir o Claude Code no modo de planejamento e pedir o plano da tarefa, citando a seção deste documento. Revisar o plano antes de aceitar.
2. **Implementar** em pequenos passos. Cada script lê um YAML de `configs/` e não usa caminhos absolutos no código.
3. **Testar rápido:** rodar sempre primeiro no mini-AOI (1 recorte × 1 ano) e depois na área toda.
4. **Rodar de verdade:** treinos e downloads longos rodam em segundo plano. Os logs vão para `outputs/runs/...`, e o Claude Code lê os logs; não os resume de memória.
5. **Commit** com mensagem clara, um por tarefa concluída.
6. **Registro de IA:** ao fim de cada sessão, acrescentar uma entrada em `docs/registro_uso_ia_claude_code.md`. Esse registro vai para o relatório de 2 páginas.

**Regras** (repetidas no `CLAUDE.md`):
- Fazer só o que a tarefa pede. Mudança de escopo é discutida e registrada aqui primeiro.
- Números de resultado vêm só de arquivos em `outputs/`, nunca de estimativa.
- Registrar configuração, semente e hash do commit em cada experimento.

**Agentes do projeto** (`.claude/agents/`):
- **`orchestrator` (Opus):** executa, com `superpowers:subagent-driven-development`, um plano de fase aprovado em `docs/superpowers/plans/`. Trabalha numa branch `fN-<nome>` e para nos pontos que exigem o aluno.
- **`geo-data` (§3) e `model-engineer` (§4), ambos Sonnet:** implementam e testam só no mini-AOI. A rodada completa é feita pela sessão principal, em segundo plano.
- **`results-auditor`:** só lê. Roda antes de C3, C4 e da entrega.

Cada uso entra no registro de IA com o modelo de cada agente.

**Prompts sugeridos por fase:**
- **F0:** "Leia docs/PLANO_IMPLEMENTACAO.md. Crie a estrutura do repositório da seção 5, o environment.yml da seção 2 e o .gitignore. Não implemente lógica ainda."
- **F0:** "Implemente encoders/terrafm_wrapper.py conforme a seção 4.1: carregar TerraFM-B, forward L2A com is_l2a=True e saída de tokens 196×768. Teste com tensor aleatório e com 1 recorte real."
- **F1:** "Implemente data/bdc.py e scripts/01_download_bdc.py (seção 3.2) para baixar o mini-AOI de 2024 e salvar em Zarr. Depois rode para Extrema 2017–2025 em segundo plano."
- **F2:** "Implemente 04_extract_tokens.py e 05_sanity_probe.py (seções 4.1 e 4.7) e confirme a normalização oficial (`normalize(x, "s2_l2a")`)."
- **F3:** "Implemente B3 e P (seções 4.2 a 4.4) com treino em Extrema, validação por blocos e teste nas Posses. Comece pelo mini-AOI."

---

## 7. Cronograma (24/11 a 14/12)

| Datas | Fase | Entregas | Marco |
|---|---|---|---|
| 24–25/11 | **F0 Ambiente** | Ambiente conda, repositório git e GitHub, CLAUDE.md, wrapper do TerraFM, conferência das pendências da seção 9 | — |
| 25–28/11 | **F1 Dados** | Polígonos de Extrema, Posses e APP; download do cubo BDC; recortes; MapBiomas alinhado; **início dos rótulos de referência** | **C1 (27/11):** 1 recorte real → tokens 14×14×768 |
| 28–30/11 | **F2 Embeddings** | Tokens pré-calculados, sondagem de sanidade, classe Dataset, divisão espacial | **C2 (30/11):** sanidade > 0,8 e dataset pronto |
| 01–04/12 | **F3 Modelos** | B3 e P (Mamba) treinados, pós-processamento, script de avaliação | **C3 (04/12):** primeira tabela P × B3; referência concluída |
| 04–07/12 | **F4 Baselines** | B1, B2 e P com L-TAE (A2); Ref MapBiomas × referência | — |
| 08–10/12 | **F5 Análise** | A1 e A3, sementes, indicador por APP, figuras; **congelar resultados em 10/12** | **C4 (10/12):** tabela final |
| 10–14/12 | **F6 Escrita** | Artigo IEEE (6–8 p.), 4 slides, relatório de IA (2 p.), README | **C5 (14/12):** entrega |

**Paralelismo:**
- Os rótulos de referência são interpretados em sessões curtas entre 26/11 e 04/12, enquanto downloads e treinos rodam.
- Introdução e trabalhos relacionados do artigo vêm do roteiro. A seção de método é escrita durante F3–F4.

**Regra de corte:** se C2 atrasar mais de 2 dias, cortar A3, B1-ruptures e as extensões. Se C3 atrasar, P usa só L-TAE e o Mamba fica como ablação.

---

## 8. Riscos e planos B

| Risco | Sinal | Plano B |
|---|---|---|
| BDC exige token ou está lento | Falha no download de teste (F0) | Registrar token gratuito; baixar só o mini-AOI enquanto isso; reduzir para 1 composição por mês |
| MapBiomas só pelo GEE | Download suspenso | Conta GEE gratuita; plano B: coleção anterior no bucket público |
| Normalização errada do TerraFM | Sanidade < 0,7 | Testar outras escalas e ordem de bandas; consultar as issues do repositório |
| Poucos eventos de regeneração em 2017–2025 | Poucos pixels de ganho no MapBiomas | Sobreamostrar o ganho no treino; relatar a limitação; usar k=2 |
| Silvicultura confundida com floresta | Erros no estrato silvicultura | Rótulo explícito (classe 9 = 0); relatar a matriz de confusão por estrato |
| Rótulo de 30 m × saída de 10 m | Bordas ruidosas | Avaliar nos pontos de referência; perda opcional que ignora bordas de classe |
| `mambapy` lento | Época > 15 min | Reduzir d e T; L-TAE como principal; WSL2 com `mamba-ssm` |
| GPU de 8 GB insuficiente | Falta de memória | Tokens pré-calculados, fp16, lotes de recortes menores, acumulação de gradiente |
| Tempo | Marcos atrasados | Regra de corte da seção 7 |

---

## 9. Pendências a verificar na Fase 0
1. Se o BDC exige token para baixar os assets do `S2-16D-2` e qual a forma de uso. → **Resposta (2026-11-25):** não exige. Um GET parcial (`Range: bytes=0-16383`) do COG `S2-16D_V2_029030_20240727_B04.tif` respondeu 206 sem token. Fonte: https://data.inpe.br/bdc/data/s2-16d/v2/029/030/2024/07/27/S2-16D_V2_029030_20240727_B04.tif
2. O caminho do MapBiomas Coleção 11: asset no GEE, os anos (inclui 2025?) e as regras de exportação.
3. A ordem das bandas do Major-TOM L2A e se ela coincide com a do BDC: `B01…B08, B8A, B09, B11, B12`. → **Resposta (2026-11-25):** coincide. O `S2_BANDS` do `terrafm.py` é `B01…B08, B8A, B09, B11, B12`, igual à ordem do BDC. A ordem interna do Major-TOM não foi conferida, porque o upstream documenta a entrada do modelo. Fonte: https://github.com/mbzuai-oryx/TerraFM/blob/e245c347ab1ef94e8d14b40dcd5f12d310b03f32/terrafm.py#L29
4. A disponibilidade da camada de APP do SICAR para Extrema e o polígono da sub-bacia das Posses.
5. O arquivo do modelo no repositório do MambaSL: como foram feitos o kernel escalado, a remoção do D e o pooling adaptativo.
6. A área exata do município e o número final de recortes, para recalcular o volume de dados.
