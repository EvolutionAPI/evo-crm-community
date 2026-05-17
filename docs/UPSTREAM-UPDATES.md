# Upstream Updates — Guia de actualização do fork

> Como trazer updates do upstream EvolutionAPI para o WizzDesk sem perder o branding.

---

## Arquitectura

O WizzDesk é um fork de dois repositórios EvolutionAPI com branding próprio:

| Submodule | Fork (origin) | Upstream |
|---|---|---|
| `evo-ai-crm-community` | `agencywizz/evo-ai-crm-community` (`wizz` branch) | `EvolutionAPI/evo-crm-community` |
| `evo-ai-frontend-community` | `agencywizz/evo-ai-frontend-community` (`wizz` branch) | `EvolutionAPI/evo-ai-frontend-community` |

Os outros 6 submodules (`evo-ai-core-service-community`, `evo-ai-processor-community`, `evo-auth-service-community`, `evo-bot-runtime`, `evolution-api`, `evolution-go`) não têm branding divergente — pull directo sem risco.

---

## Setup de remotes (uma vez por ambiente)

```bash
# CRM
git -C evo-ai-crm-community remote add upstream https://github.com/EvolutionAPI/evo-crm-community.git

# Frontend
git -C evo-ai-frontend-community remote add upstream https://github.com/EvolutionAPI/evo-ai-frontend-community.git

# Confirmar (deve mostrar origin=agencywizz e upstream=EvolutionAPI)
git -C evo-ai-crm-community remote -v
git -C evo-ai-frontend-community remote -v
```

---

## Actualização com branding preservado

```bash
make sync-upstream
```

Ou manualmente:

```bash
for sub in evo-ai-crm-community evo-ai-frontend-community; do
  echo "=== Actualizando $sub ==="
  git -C "$sub" fetch upstream
  git -C "$sub" checkout wizz
  git -C "$sub" rebase upstream/main
  # Se houver conflitos: resolver, manter versão wizz, depois:
  #   git -C "$sub" rebase --continue
  git -C "$sub" push origin wizz --force-with-lease
done
```

---

## Conflitos esperados (e como resolvê-los)

| Ficheiro | Conflito provável | Acção |
|---|---|---|
| `evo-ai-crm-community/config/installation_config.yml` | Upstream adiciona novas flags | Manter bloco WizzDesk, aceitar novas flags do upstream |
| `evo-ai-crm-community/lib/tasks/branding.rake` | Upstream altera defaults | Manter defaults WizzDesk |
| `evo-ai-frontend-community/index.html` | Upstream adiciona scripts | Manter `<title>WizzDesk</title>` e meta description |
| `evo-ai-frontend-community/public/` | Upstream adiciona assets | Manter logos WizzDesk |

**Locales en-GB não conflituam** — são ficheiros novos que o upstream não conhece.

---

## Validação pós-update

```bash
# 1. Verificar que "Evo CRM" não aparece em config
grep -r "Evo CRM\|EvoCloud" evo-ai-crm-community/config/ evo-ai-frontend-community/index.html
# → deve retornar vazio

# 2. Build local
docker compose build --no-cache evo-frontend evo-crm

# 3. Verificar título no browser
# Abrir http://localhost e verificar: tab = "WizzDesk"
```

---

## Submodules sem fork (actualização directa)

Para os 6 submodules sem branding próprio:

```bash
for sub in evo-ai-core-service-community evo-ai-processor-community evo-auth-service-community evo-bot-runtime evolution-api evolution-go; do
  git submodule update --remote "$sub"
done
git add .
git commit -m "chore: bump upstream-only submodules"
```

> ⚠️ **Regra:** Se precisar de alterar qualquer ficheiro dentro destes submodules, forke primeiro para `agencywizz/` e configure remote + wizz branch **antes** de editar.
