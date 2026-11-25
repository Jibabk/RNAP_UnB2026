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
