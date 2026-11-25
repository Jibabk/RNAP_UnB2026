# Registro de uso de IA — Claude Code (Projeto 2, RNAP 2026/2)
Aluno: Jean · Disciplina: Redes Neurais e Aprendizado Profundo (UnB) · Prof. Díbio
Objetivo: documentar de forma específica e detalhada o uso de modelos de IA no desenvolvimento do projeto. As entradas novas entram no final, e as antigas não são editadas.

## Ferramentas e modelos de IA utilizados (resumo)
| Ferramenta / modelo | Fornecedor | Para que foi usada |
|---|---|---|
| Claude Code (extensão do VS Code), modelo `claude-opus-5-5` | Anthropic | Planejamento e configuração dos agentes do projeto |

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
