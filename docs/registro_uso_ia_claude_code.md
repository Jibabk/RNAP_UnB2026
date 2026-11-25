# Registro de uso de IA — Claude Code (Projeto 2, RNAP 2026/2)
Aluno: Jean · Disciplina: Redes Neurais e Aprendizado Profundo (UnB) · Prof. Díbio
Objetivo: documentar de forma específica e detalhada o uso de modelos de IA no desenvolvimento do projeto. As entradas novas entram no final, e as antigas não são editadas.

## Ferramentas e modelos de IA utilizados (resumo)
| Ferramenta / modelo | Fornecedor | Para que foi usada |
|---|---|---|
| Claude Code (extensão do VS Code), modelo `claude-opus-5-5` | Anthropic | Planejamento e configuração dos agentes do projeto |
| Subagentes do Claude Code, alias `sonnet` (Claude Sonnet 5.5, conforme o `Co-Authored-By` dos commits) | Anthropic | Implementação e revisão de cada tarefa da F0 |
| Subagente `web-fetch` do Claude Code, alias `haiku` | Anthropic | Tentativa de ler PDFs de fontes na F0 (sem sucesso) |

## Entradas

### [2026-11-25] Configuração dos subagentes e do orquestrador do Claude Code
- **Etapa:** ambiente
- **Ferramenta:** Claude Code (VS Code), modelo `claude-opus-5-5`.
  - No planejamento, a IA também usou o subagente `web-fetch`, para ler a documentação do Claude Code (`code.claude.com/docs/en/sub-agents` e `/settings`), e a ferramenta `advisor`, para pedir uma segunda opinião sobre a abordagem.
  - Skills consultadas: `brainstorming`, `subagent-driven-development`, `using-git-worktrees` e `writing-plans`, do plugin superpowers 7.0.2, e `registro-uso-ia`.
- **Pedido do aluno:**
  - ler o plano de implementação e, antes de começar, ajudar a configurar agentes que o auxiliem;
  - em seguida, usar o superpowers para configurar também um orquestrador Opus para o projeto.
- **O que a IA fez:**
  - Leu `docs/PLANO_IMPLEMENTACAO.md`, `CLAUDE.md` e os arquivos do superpowers: `SKILL.md`, `implementer-prompt.md`, `references/final-review.md` e `scripts/sdd-workspace` do `subagent-driven-development`; `references/claude-code-tools.md`; `using-git-worktrees`; e `writing-plans`.
  - Fez duas perguntas ao aluno:
    - quais papéis de agente ele queria; escolhidos: auditor de resultados, dados geoespaciais e modelo e treino;
    - onde rodar o orquestrador; escolhido: como subagente.
  - Escreveu o plano no modo de planejamento, e o aluno o aprovou.
  - Criou quatro arquivos em `.claude/agents/`:
    - `orchestrator.md`, com `opus`;
    - `geo-data.md`, `model-engineer.md` e `results-auditor.md`, com `sonnet`.
  - Acrescentou o parágrafo "Agentes do projeto" ao §6 de `docs/PLANO_IMPLEMENTACAO.md`.
  - Validou o frontmatter dos quatro arquivos com PyYAML, usando o Python do sistema.
  - Depois da revisão pelo `advisor`, fez dois ajustes:
    - o `orchestrator` agora também para quando o repositório não tem commits;
    - o `geo-data` e o `model-engineer` ganharam a ferramenta `Skill`, para carregar o `test-driven-development` quando um plano exigir. Essa ferramenta não constava do plano aprovado.
  - Criou este arquivo de registro.
- **Resultado:**
  - quatro agentes em `.claude/agents/`, com frontmatter YAML válido (nome, descrição, ferramentas e modelo);
  - §6 do plano atualizado.
- **Verificação humana:** a preencher pelo aluno
- **Limitações/erros:**
  - Esta sessão não reconheceu os agentes novos e respondeu `Agent type 'results-auditor' not found`. A causa provável é que a pasta `.claude/agents/` foi criada depois do início da sessão. Por isso, as verificações 1 a 3 do plano ficam pendentes até o Claude Code ser reaberto:
    1. `/agents`;
    2. o auditor sem `outputs/`;
    3. o orquestrador sem git.
  - Não foi testado se o aninhamento orquestrador → implementador funciona nesta instalação. A documentação informa até 3 níveis.
  - Parte da resposta do `web-fetch` sobre o aninhamento de subagentes veio como resumo da página, não como texto literal.
  - Decisões tomadas pela IA, e não pelo aluno:
    - branch por fase sem worktree;
    - `sonnet` para os implementadores;
    - `scripts/09_figures.py` atribuído ao `model-engineer`, embora o plano aprovado citasse só `04–08`;
    - tarefas de infraestrutura (estrutura, `environment.yml`, `.gitignore`, README) atribuídas ao `general-purpose`.
  - O registro principal no Projeto "TCC Jean" (`claude/registro-uso-ia.md`) não foi atualizado nesta sessão. As ferramentas `project_read` e `project_write` não estão disponíveis no Claude Code, e o `SendToProject` só envia mensagens a Projetos do claude.ai/code: não lê nem grava arquivos.

### [2026-11-25] Plano da Fase F0 com a skill writing-plans
- **Etapa:** ambiente
- **Ferramenta:** Claude Code (VS Code), modelo `claude-opus-5-5`.
  - Também usou a ferramenta `advisor`, para pedir uma segunda opinião antes de escrever o plano, e a skill `superpowers:writing-plans` (plugin superpowers 7.0.2).
- **Pedido do aluno:**
  - "escreva o plano F0 com o writing-plans";
  - depois de revisar o plano: seguir o nome do repositório no GitHub; a outra máquina é uma RTX 2070; commitar; instalar o Miniforge.
- **O que a IA fez:**
  - Leu `docs/PLANO_IMPLEMENTACAO.md`, `CLAUDE.md`, os quatro agentes de `.claude/agents/` e este registro.
  - Fez verificações de leitura (nenhum arquivo do projeto foi alterado, exceto os dois citados abaixo):
    - `git status` e `git log`: 1 commit; remote `Jibabk/RNAP_UnB2026`;
    - `nvidia-smi` e Win32_VideoController: a GPU é uma GTX 1650 de 4 GB;
    - conda: não está instalado;
    - TerraFM no GitHub (`gh api`): o commit `e245c347` (13/11/2026) trouxe `normalize()`, `is_l2a` nos métodos e a licença MIT;
    - API do Hugging Face: sha256 e tamanho de `TerraFM-B.pth`;
    - STAC do BDC: um GET parcial de um COG respondeu 206 sem token;
    - índice de wheels do PyTorch, PyPI do `mambapy` e código do `mamba.py` no GitHub;
    - API de malhas do IBGE: bbox de Extrema;
    - escolha do ponto do mini-AOI dentro do município e do tile 029030;
    - `winget search miniforge`.
  - Os arquivos baixados ficaram só no scratchpad da sessão, fora do repositório.
  - Fez quatro perguntas ao aluno:
    - normalização: escolhida a `normalize` oficial;
    - atualizar a documentação: escolhido sim, numa tarefa da F0;
    - máquina: desenvolver e testar nesta e executar em outra;
    - recorte real na F0: escolhido sim, como teste de rede.
  - Criou `docs/superpowers/plans/2026-11-25-f0-ambiente.md`, com 8 tarefas.
  - Depois da revisão do `advisor`, ajustou o plano:
    - a Tarefa 1 também corrige o prompt da F2 no §6;
    - a regra `.gitignore` ganhou âncora (`/data/`).
  - Com as respostas do aluno, fixou no plano a RTX 2070 Max-Q de 8 GB como máquina de execução e `Jibabk/RNAP_UnB2026` como nome do repositório.
  - Instalou o Miniforge3 26.9.4-2 com `winget install --id CondaForge.Miniforge3 -e --scope user --silent`:
    - pasta `C:\Users\jeanb\miniforge3`;
    - `conda 26.9.4`, com o canal `conda-forge`.
  - Tentou rodar `conda init powershell bash`, mas o classificador do modo automático do Claude Code negou a ação, porque ela altera os perfis do shell. A IA não tentou contornar o bloqueio.
  - Acrescentou esta entrada e fez o commit do plano e do registro na `main`.
- **Resultado:**
  - o plano da F0 está salvo e aprovado pelo aluno, mas ainda não foi executado;
  - o Miniforge está instalado, porém o `conda` ainda não está no PATH.
- **Verificação humana:** a preencher pelo aluno
- **Limitações/erros:**
  - Os valores fixados no plano foram lidos das fontes em 25/11/2026 e podem mudar: versões, hashes e o ponto do mini-AOI.
  - Não foi verificado se o ponto do mini-AOI fica fora das Posses + 500 m. Isso fica para a F1.
  - O roteiro entregue cita o repositório `Jibabk/ProjetoFinalRNAP_UnB2026`, mas o aluno escolheu manter `Jibabk/RNAP_UnB2026`. O roteiro não foi alterado.
  - O `conda init` está pendente: o aluno precisa rodá-lo e reabrir o VS Code antes de executar o plano.
  - Decisões técnicas tomadas pela IA, e não pelo aluno:
    - `norm=True` nos tokens;
    - `torch==2.14.1+cu126`;
    - `earthengine-api` incluído e `planetary-computer` excluído;
    - `pyproject.toml`, `configs/model/terrafm.yaml` e `scripts/00_download_weights.py`, fora do §5;
    - âncora `/data/` no `.gitignore`.

### [2026-11-25] Execução do plano da F0 pelo orquestrador
- **Etapa:** ambiente
- **Ferramenta:** Claude Code (VS Code), modelo `claude-opus-5-5` na sessão principal.
  - A sessão principal despachou o agente `orchestrator` (`claude-opus-5-5`). Ele seguiu a skill `superpowers:subagent-driven-development` e consultou 3 vezes a ferramenta `advisor`.
  - O orquestrador fez 20 despachos de subagentes (lista abaixo). A sessão principal usou a skill `registro-uso-ia` e a ferramenta `Monitor`.
- **Pedido do aluno:**
  - "execute o plano docs/superpowers/plans/2026-11-25-f0-ambiente.md com o orchestrator";
  - depois: "ok, me avise quando terminar".
- **O que a IA fez:**
  - **Sessão principal, antes do despacho:**
    - leu o início do plano e o `.claude/agents/orchestrator.md`;
    - verificou que o `conda` não está no PATH dos shells, mas responde pelo caminho completo `C:\Users\jeanb\miniforge3\Scripts\conda.exe` (`conda 26.9.4`);
    - despachou o orquestrador com esse contexto. A instrução foi chamar o conda pelo caminho completo, sem alterar o PATH do sistema nem o perfil.
  - **Orquestrador, primeira etapa:**
    - criou a branch `f0-ambiente`;
    - executou as Tarefas 1, 2, 3 (Passos 1–5), 6 e 7, com um implementador e um revisor por tarefa;
    - parou na parada obrigatória 5, o download dos pesos.
  - **Sessão principal, download dos pesos:**
    - leu `scripts/00_download_weights.py` e `download_file` (`src/terrafm_temporal/utils.py`);
    - rodou o download em segundo plano, com log em `outputs/logs/f0_download_weights.log`, e acompanhou o tamanho do `.part` com um monitor;
    - conferiu com `sha256sum`: `8bdb6a4cfd707a09d79f4790119daa9d76bb316b6ea756c6eb305f99d1797a06`, 451862010 bytes, iguais aos fixados no plano.
  - **Orquestrador, retomada:**
    - Tarefa 3, Passo 7: `1 passed`, rodado pelo implementador da Tarefa 4;
    - Tarefas 4, 5 e 8;
    - revisão final da branch (`opus`) e uma onda de correções de texto (M1 e M2).
  - **Despachos do orquestrador** (agente/modelo):
    - T1, T2 e T8: implementador `general-purpose`/sonnet;
    - T3, T4 e T7: implementador `model-engineer`/sonnet;
    - T5 e T6: implementador `geo-data`/sonnet;
    - um revisor `general-purpose`/sonnet por tarefa;
    - T6: um `web-fetch`/haiku, que não conseguiu ler os PDFs;
    - revisão final `general-purpose`/opus;
    - onda de correções: fixer e re-revisão `general-purpose`/sonnet.
  - **Commits** na `f0-ambiente`, de `86582ae` a `6b5935e` (9 commits, todos com `Co-Authored-By: Claude Sonnet 5.5`):
    - Tarefa 1: `CLAUDE.md`, `docs/PLANO_IMPLEMENTACAO.md` e `.claude/agents/model-engineer.md`;
    - Tarefa 2: esqueleto do repositório, `environment.yml`, `.gitignore`, `pyproject.toml` e env `rnap`;
    - Tarefa 3: `src/terrafm_temporal/utils.py`, `configs/model/terrafm.yaml` e `scripts/00_download_weights.py`;
    - Tarefa 4: `terrafm.py` e LICENSE do upstream (`e245c347`) em `encoders/third_party/`, e o wrapper `TerraFMEncoder`;
    - Tarefa 5: configs do mini-AOI e do BDC, e o teste com 1 janela real;
    - Tarefas 6 e 7: respostas da §9;
    - Tarefa 8: comandos no `CLAUDE.md`.
  - **Sessão principal, conferência final no HEAD `6b5935e`:**
    - `pytest tests -q -rs` deu `61 passed in 45.31s`, sem skip, nesta máquina (GTX 1650). O log está em `outputs/logs/f0_pytest_final.log`;
    - `git ls-files | grep -E "\.pth$|\.zarr|^data/|^outputs/"` não devolveu nenhuma linha;
    - os 6 itens da §9 têm "Resposta"; 9.4 e 9.6 são parciais.
  - Acrescentou esta entrada e as duas linhas da tabela-resumo.
- **Resultado:**
  - a F0 está implementada na branch `f0-ambiente`, ainda sem push e sem merge;
  - o `TerraFMEncoder` gera tokens 196×768 de uma janela real do BDC (item `S2-16D_V2_029030_20240625`);
  - os pesos estão em `data/weights/TerraFM-B.pth`, fora do git;
  - o ledger do orquestrador está em `.superpowers/sdd/2026-11-25-f0-ambiente/progress.md`, fora do git.
- **Verificação humana:** a preencher pelo aluno
- **Limitações/erros:**
  - **Fato errado ainda no `CLAUDE.md` e no PLANO (I1, revisão final):** as bandas estão "em uint16", mas os COGs do BDC estão gravados em int16, embora o STAC declare uint16. `PROVENANCE` é int16 com nodata −1. A correção não foi aplicada e espera a decisão do aluno. Enquanto isso, o teste da Tarefa 5 converte para uint16 depois de checar que não há negativos (R13).
  - **Comando de teste no `CLAUDE.md` (M6):** com dois `-m`, o pytest só usa o último. Para combinar os dois, o certo é `-m "not network and not gpu"`.
  - **Comparação fp16 × fp32:** o cosseno de 0,99999875 foi medido com DN sintéticos, não com dados reais. A comparação com dados reais fica para a F2.
  - **Testes:** rodaram só nesta máquina, não na RTX 2070.
  - **Desvio de TLS:** na Tarefa 6, o implementador `geo-data` tentou um `curl -k` ao SICAR, que desliga a verificação TLS. O classificador negou, e ele refez sem `-k`.
  - **`pypdf`:** na Tarefa 6, o `pypdf` foi instalado com `pip install --target` numa pasta temporária, fora do env `rnap` e do repositório (R11).
  - **Arquivos fora do lugar:** dois JSON do SNIRH foram gravados na raiz do repositório e retirados antes do commit.
  - **Leitura dos PDFs:** o `web-fetch`/haiku não leu os PDFs da Embrapa e do PCJ. O orquestrador conferiu o 1.196,7 ha e o "1200 ha" com um script stdlib no scratchpad.
  - **Decisões tomadas pela IA, e não pelo aluno** (rulings do ledger):
    - adiantar as Tarefas 6 e 7 para antes das 4 e 5 (R7);
    - gerar os briefs com awk, porque o `task-brief` da skill não reconhece títulos em português (R6);
    - converter int16 para uint16 em `_read_window` (R13);
    - usar `method="GET"` na busca STAC (R14);
    - não aplicar o I1 (R16);
    - manter o workspace `.superpowers/sdd/` (R15);
    - triagem dos itens estacionados da revisão final (R18).
  - **Ambiente:** o `conda init` continua pendente, e o `conda` não está no PATH dos shells.
  - **Registro principal:** o `claude/registro-uso-ia.md` do Projeto "TCC Jean" não foi atualizado, porque as ferramentas de Projects não estão disponíveis no Claude Code.

### [2026-11-25] Correção do dtype das bandas do BDC e do comando de teste
- **Etapa:** ambiente
- **Ferramenta:** Claude Code (VS Code), modelo `claude-opus-5-5`, sem subagentes.
- **Pedido do aluno:**
  - "push e o merge devem ser feitos apenas quando aprovados pelo usuário";
  - "a correção deve entrar nesta branch" (I1, da revisão final da F0);
  - "entre junto com a do item 2" (M6).
- **O que a IA fez:**
  - Conferiu o dtype no BDC antes de editar, com um script no scratchpad (`pystac-client` + `rasterio`, env `rnap`), sobre o item `S2-16D_V2_029030_20240625`:
    - B01, B04, B08 e B12 estão em `int16` no COG, com nodata 0;
    - o STAC declara `data_type: uint16` em `eo:bands`, com min 0 e max 10000;
    - `PROVENANCE` está em `int16`, com nodata −1; SCL, CLEAROB e TOTALOB estão em `uint8`.
  - Corrigiu o texto em três lugares:
    - `CLAUDE.md`, item "Bandas": int16 no COG, uint16 no STAC, converter para uint16 na leitura depois de checar negativos, e `PROVENANCE` em int16 com nodata −1;
    - `CLAUDE.md` e `docs/PLANO_IMPLEMENTACAO.md` §4.1: "o uint16 do BDC" virou "o DN do BDC";
    - `docs/PLANO_IMPLEMENTACAO.md` §3.2: as bandas estão "gravadas em int16 (o STAC declara uint16)".
  - Corrigiu o comando de teste no `CLAUDE.md`: para pular os testes de rede e os de GPU juntos, um só `-m "not network and not gpu"`.
  - Conferiu a correção com o pytest:
    - `-m "not network" -m "not gpu"` deu `58 passed, 3 deselected`, ou seja, só o último `-m` valeu;
    - `-m "not network and not gpu"` deu `55 passed, 6 deselected`;
    - 6 testes têm os marcadores `network` ou `gpu`.
  - Manteve como estavam a linha 79 do PLANO e o `geo-data.md`, que guardam `x` em uint16 no Zarr local. Os dois já seguem a regra de converter na leitura.
  - Não fez push nem merge.
- **Resultado:** um commit de documentação na branch `f0-ambiente`.
- **Verificação humana:** a preencher pelo aluno
- **Limitações/erros:**
  - O dtype foi conferido em um único item do BDC. Não foi verificado se todos os itens de 2017–2025 seguem o mesmo padrão.
  - "Sem negativos" vem do intervalo declarado no STAC (0 a 10000) e da checagem numa janela, no teste da Tarefa 5. Não foi conferido na imagem inteira.

### [2026-11-25] Push e merge da F0
- **Etapa:** ambiente
- **Ferramenta:** Claude Code (VS Code), modelo `claude-opus-5-5`, com a skill `superpowers:finishing-a-development-branch`.
- **Pedido do aluno:** "pode fazer o push e o merge".
- **O que a IA fez:**
  - Conferiu que `main` e `origin/main` estavam em `2736d86`, que é a base da `f0-ambiente`.
  - Rodou `git push -u origin f0-ambiente`.
  - Fez o merge da branch na `main` com `git merge --ff-only f0-ambiente`, em fast-forward e sem commit de merge.
  - Rodou a suíte completa na `main` depois do merge: `61 passed in 55.23s`, sem skip. O log está em `outputs/logs/f0_pytest_merged_main.log`.
  - Rodou `git push origin main` (`2736d86..ce08cd0`).
  - Não apagou a branch local `f0-ambiente` nem o workspace `.superpowers/sdd/2026-11-25-f0-ambiente/`.
- **Resultado:** `main`, `origin/main` e `origin/f0-ambiente` apontam para `ce08cd0`.
- **Verificação humana:** a preencher pelo aluno
- **Limitações/erros:**
  - Esta entrada foi escrita depois do push e ainda não foi commitada.
  - A entrada anterior diz "Não fez push nem merge", o que era verdade quando ela foi escrita.
