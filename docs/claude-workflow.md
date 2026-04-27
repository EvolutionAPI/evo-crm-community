# Workflow com Claude Code — 3 rotinas, 3 momentos

Tem **3 rotinas** registradas em `.claude/commands/` que cobrem o ciclo de vida de bug e feature aqui no repo.

| Rotina | Quando usar |
|--------|-------------|
| `/bugs-to-linear-routine` | Você quer **registrar bugs no Linear** |
| `/pm-bug-dev-routine` | Você vai **consertar uma bug** que já está no Linear |
| `/pm-feature-dev-routine` | Você vai **implementar uma feature** que já está no Linear |

Todas pausam pra te pedir aprovação antes de fazer qualquer coisa "pesada" (criar issue, commitar, abrir PR).

---

## 1. Reportar bugs — `/bugs-to-linear-routine`

**Quando usar:** alguém te reportou bugs (Slack, QA call, email, beta) e você quer subir no Linear de forma padronizada.

**Como invocar:** digita `/bugs-to-linear-routine` e cola os bugs (até 3 por vez).

**Exemplo:**

```
/bugs-to-linear-routine

- Bug: filtro de pipeline some quando recarrego a página.
  severity: high, module: frontend.

- Bug: badge de notification não atualiza ao receber mensagem nova de outro inbox.
  severity: low, module: frontend
```

**Campos por bug:**

- `title` — obrigatório
- `description` — obrigatório (uma frase já basta)
- `severity` — obrigatório (`critical` / `high` / `medium` / `low`)
- `module`, `steps`, `expected`, `actual` — opcionais (quanto mais informação, melhor a issue fica)

**O que ela faz:**

1. Gera um spec por bug
2. Te mostra um preview e pergunta `APROVADO?`
3. Você responde **APROVADO**
4. Cria as issues no Linear, atribui pra **você**, posta o spec como comment
5. Te devolve os links

> Se você quiser atribuir pra outra pessoa, manda `ASSIGNEE=email@evofoundation.com.br` antes da lista de bugs.

---

## 2. Consertar uma bug — `/pm-bug-dev-routine EVO-XXXX`

**Quando usar:** você pegou uma issue de bug (label `Bug`) no Linear e vai implementar a fix.

**Como invocar:**

```
/pm-bug-dev-routine EVO-1000
```

(aceita ID ou URL Linear inteira)

**O que ela faz, em ordem:**

1. Lê a issue do Linear (título, descrição, comments)
2. Faz `git fetch` + cria `fix/EVO-XXXX` a partir do `develop` em cada submódulo afetado
3. Te mostra o plano de fix → **espera APROVADO**
4. Implementa a fix + roda os testes (rspec / tsc / lint / vitest / etc.)
5. Te mostra resumo pré-delivery → **espera APROVADO**
6. Commita, push, abre PR(s) target `develop`
7. Move issue pra `In Review`, posta comment com `cc @Davidson`, reassign pro Davidson
8. Volta pro `develop` local e dá `git pull` pra ficar sincronizado

**Quando o Davidson responder o review:**

- ✅ **APROVOU** → ele cuida do merge, você **vai pra próxima task**, não precisa fazer nada
- 🔄 **CHANGES_REQUESTED** → roda **a mesma rotina de novo** com o mesmo ID. Ela detecta o checklist do review e trata como input, implementa as correções e dá push no MESMO PR
- 🚫 **BLOCKED** → roda a rotina de novo pra ela te mostrar o blocker e decidir o caminho

---

## 3. Implementar uma feature — `/pm-feature-dev-routine EVO-XXXX`

**Quando usar:** você pegou uma issue de feature/épico (label `Feature` ou `História`) no Linear.

**Como invocar:**

```
/pm-feature-dev-routine EVO-989
```

**O que muda em relação à rotina de bug:**

- Faz **discovery** em `_evo/` antes (procura specs BMAD existentes)
- Plano é mais detalhado (por submódulo, ordem data → backend → frontend, contratos de API)
- Tem **gate de teste do usuário** no meio: a rotina pausa, te dá URLs e ações pra testar, você confirma que passou
- Faz um **QA pass** automático antes de abrir PR (security audit, edge cases, UX)
- Branch é `feat/EVO-XXXX` (não `fix/`)

Resto é igual: aprovação, commit, PR target `develop`, Linear `In Review`, reassign Davidson.

---

## Convenções

- **Conversa com Claude:** PT
- **Tudo que vai pra fora** (commits, PRs, Linear comments, nome de branch): inglês
- **Branch:** `fix/<ISSUE_ID>` ou `feat/<ISSUE_ID>` no submódulo (NUNCA mexe na branch do monorepo raiz)
- **PR target:** sempre `develop`
- **Reviewer:** Davidson (default do time, todas as rotinas reassignam pra ele)
- **Linear status final:** `In Review` — quem move pra `Done` é o reviewer

---

## Pré-requisitos (uma vez por máquina)

1. **Claude Code** instalado e logado
2. **MCP Linear** autenticado — primeira invocação abre o auth no browser. Se expirar no meio: `/mcp` re-autoriza.
3. **`gh` CLI** logado: `gh auth status` deve estar OK
4. Repo clonado com submódulos: `git clone --recurse-submodules ...` (ou `git submodule update --init --recursive` depois)

---

## Problemas comuns

| Sintoma | Solução |
|---------|---------|
| MCP do Linear expirou no meio | `/mcp` → re-autoriza → diz pra Claude continuar |
| Vite quebra após pull no frontend (`Cannot find module ...`) | `pnpm install` no submódulo |
| Rails não pegou mudança após pull | Reinicia `bin/rails server` |
| Rotina parou dizendo "working tree dirty" | Commit, stash explícito, ou descarta as mudanças locais. A rotina não mexe em WIP seu sem permissão |
| Filtros de conversa dando 500 | `develop` do `evo-ai-crm-community` está desatualizado. `git pull --ff-only origin develop` lá e reinicia o Rails |

---

## Onde encontrar mais detalhe

- Os arquivos de cada rotina estão em [`.claude/commands/`](../.claude/commands/) — abre e lê os steps se quiser entender exatamente o que cada uma faz
- Skills BMAD em [`.claude/skills/`](../.claude/skills/)
- Workflows BMAD em [`_evo/bmm/workflows/`](../_evo/bmm/workflows/)
