# OAuth Codex (OpenAI) — Autenticacao por Assinatura ChatGPT para Evo CRM

## Visao Geral

Esta implementacao adiciona **OAuth Codex da OpenAI** como metodo alternativo de autenticacao no Evo CRM, permitindo que usuarios com assinatura **ChatGPT Plus** ($20/mes) ou **ChatGPT Pro** ($200/mes) utilizem modelos GPT-5.x diretamente, sem necessidade de uma API key separada da OpenAI.

A abordagem e **hibrida**: OAuth Codex funciona ao lado das API keys existentes. Nenhuma funcionalidade atual e alterada ou removida.

---

## Arquitetura da Solucao

### Como funciona hoje (API Keys)

```
Usuario cola API key (sk-...) no frontend
  -> Backend criptografa com Fernet (AES-128-CBC)
  -> Salva em api_keys.encrypted_key no PostgreSQL
  -> AgentBuilder descriptografa e passa para LiteLlm(model, api_key)
  -> LiteLLM roteia para o provider correto
```

### Como funciona com OAuth Codex (novo)

```
Usuario seleciona "ChatGPT (OAuth)" no frontend
  -> Clica "Conectar com ChatGPT"
  -> Backend inicia device code flow com auth.openai.com
  -> Usuario recebe codigo (ex: ABCD-1234)
  -> Usuario acessa auth.openai.com/codex/device e digita o codigo
  -> Backend recebe tokens OAuth, criptografa e salva no PostgreSQL
  -> AgentBuilder detecta auth_type='oauth_codex'
  -> Descriptografa tokens, verifica validade, refresh automatico se expirado
  -> Passa token como Bearer para chatgpt.com/backend-api/codex
  -> Resposta retorna normalmente pelo pipeline existente
```

### Decisao Tecnica: openai/ prefix (nao chatgpt/)

Analise do codigo-fonte do LiteLLM confirmou que o provider `chatgpt/` **ignora o parametro `api_key`** e sempre le tokens de um arquivo global `auth.json`. Isso e incompativel com multi-tenancy (cada cliente tem seu proprio token).

A solucao usa o provider `openai/` com parametros customizados:
- `api_base` = `https://chatgpt.com/backend-api/codex`
- `api_key` = token OAuth do tenant (usado como Bearer)
- `extra_headers` = ChatGPT-Account-Id, originator

O Google ADK `LiteLlm` passa `**kwargs` via `_additional_args` para `litellm.acompletion()`, confirmado no codigo-fonte (SHA 7d13696c). Cada tenant recebe sua propria instancia, sem estado global compartilhado.

---

## Modelos Disponiveis

| Modelo | Plano Minimo |
|--------|-------------|
| chatgpt/gpt-5.4 | ChatGPT Plus |
| chatgpt/gpt-5.4-pro | ChatGPT Plus |
| chatgpt/gpt-5.3-codex | ChatGPT Plus |
| chatgpt/gpt-5.3-codex-spark | ChatGPT Pro |
| chatgpt/gpt-5.3-instant | ChatGPT Plus |
| chatgpt/gpt-5.2-codex | ChatGPT Plus |
| chatgpt/gpt-5.2 | ChatGPT Plus |
| chatgpt/gpt-5.1-codex-max | ChatGPT Pro |
| chatgpt/gpt-5.1-codex-mini | ChatGPT Plus |

---

## Mudancas no Banco de Dados

### Migration: `a1b2c3d4e5f6_add_oauth_codex_support`

```sql
ALTER TABLE api_keys ADD COLUMN auth_type VARCHAR(20) DEFAULT 'api_key' NOT NULL;
ALTER TABLE api_keys ADD COLUMN oauth_data TEXT;
ALTER TABLE api_keys ALTER COLUMN encrypted_key DROP NOT NULL;

-- Constraints de integridade
CHECK (auth_type IN ('api_key', 'oauth_codex'))
CHECK ((auth_type = 'api_key' AND encrypted_key IS NOT NULL) OR
       (auth_type = 'oauth_codex' AND oauth_data IS NOT NULL))
```

**Backward compatible:** registros existentes recebem `auth_type='api_key'` automaticamente.

**Reversivel:** `alembic downgrade -1` remove as colunas sem perda de dados.

---

## Novos Endpoints

| Metodo | Rota | Descricao |
|--------|------|-----------|
| POST | `/api/v1/agents/oauth/codex/device-code` | Inicia device code flow |
| POST | `/api/v1/agents/oauth/codex/device-poll` | Verifica se usuario autorizou |
| GET | `/api/v1/agents/oauth/codex/status/{key_id}` | Status da conexao OAuth |
| DELETE | `/api/v1/agents/oauth/codex/{key_id}` | Revogar conexao OAuth |

Todos requerem JWT + verificacao de ownership do client.

---

## Seguranca

### Upgrade do LiteLLM: v1.68.0 -> v1.83.3

O repositorio original usa `litellm>=1.68.0,<1.69.0` (lancada em Maio 2025). Esta versao possui as seguintes vulnerabilidades conhecidas:

#### CVE-2026-35030 — Bypass de Autenticacao OIDC (CRITICO)

O LiteLLM usava apenas os **primeiros 20 caracteres** de um JWT como chave de cache. Isso permitia que tokens diferentes com os mesmos 20 caracteres iniciais compartilhassem a mesma sessao autenticada, possibilitando bypass completo da autenticacao OIDC.

**Corrigido em:** v1.83.0 (usa hash completo do JWT como chave de cache)

#### Supply Chain Attack — TeamPCP (Marco 2026)

Em 24 de Marco de 2026, as versoes **v1.82.7** e **v1.82.8** do LiteLLM no PyPI foram comprometidas por um grupo chamado TeamPCP:

1. O grupo comprometeu o **Trivy** (scanner de seguranca da Aqua Security)
2. O Trivy malicioso executou no CI/CD do LiteLLM via GitHub Actions
3. Extrairam a senha de publicacao do PyPI (`PYPI_PUBLISH_PASSWORD`) via dump de memoria
4. Publicaram versoes maliciosas que:
   - Coletavam todas as credenciais do ambiente (AWS, GCP, Azure, K8s, SSH, DB)
   - Criptografavam e exfiltravam para servidor controlado pelo atacante
   - Instalavam persistencia via systemd service
   - Executavam payloads adicionais sob comando

As versoes foram removidas do PyPI em ~40 minutos, mas acumularam dezenas de milhares de downloads.

#### v1.83.3-stable — Segura

A versao v1.83.3 foi construida no novo pipeline **CI/CD v2** com:

| Medida | Detalhe |
|--------|---------|
| SHA pinning | GitHub Actions pinadas por commit SHA imutavel |
| Trusted Publishers (OIDC) | Tokens short-lived substituem senhas estaticas |
| Cosign signing | Docker images assinadas criptograficamente |
| SLSA provenance | Build provenance verificavel |
| Ambientes isolados | Build e publish em ambientes efemeros |

**Hashes SHA-256 verificados:**
```
wheel:  eab4d2e1871cac0239799c33eb724d239116bf1bd275e287f92ae76ba8c7a05a
tar.gz: 38a452f708f9bb682fdfc3607aa44d68cfe936bf4a18683b0cdc5fb476424a6f
```

#### Compatibilidade: google-adk==0.3.0

A issue #4367 (google/adk-python) documenta que LiteLLM >=1.81.3 muda o formato de `response_schema` para modelos Gemini 2.0+. O ADK 0.3.0 pode ter problemas com structured output nesses modelos. **Modelos OpenAI/ChatGPT/Anthropic NAO sao afetados.**

### Seguranca da Implementacao OAuth

| Aspecto | Status |
|---------|--------|
| Tokens em logs | Nenhum token e logado (access, refresh, id) |
| Tokens em API responses | Nunca retornados ao frontend |
| Criptografia em repouso | Fernet (AES-128-CBC + HMAC-SHA256) |
| Thread-safety | SELECT FOR UPDATE com try/finally + db.rollback() |
| CSRF | JWT Bearer (stateless, imune a CSRF) |
| XSS | verificationUri validado (rejeita javascript:) |
| SQL injection | SQLAlchemy ORM (queries parametrizadas) |
| Device code storage | Server-side (nunca exposto ao frontend) |

---

## Arquivos da Implementacao

### Novos (6 arquivos)

| Arquivo | Servico |
|---------|---------|
| `src/config/oauth_constants.py` | Processor |
| `src/services/oauth_codex_service.py` | Processor |
| `migrations/versions/a1b2c3d4e5f6_add_oauth_codex_support.py` | Processor |
| `frontend/types/oauth.ts` | Frontend |
| `frontend/app/agents/dialogs/OAuthDeviceCodeFlow.tsx` | Frontend |
| `frontend/app/agents/components/OAuthStatusBadge.tsx` | Frontend |

### Modificados (9 arquivos)

| Arquivo | Mudanca |
|---------|---------|
| `src/models/models.py` | +auth_type, +oauth_data, encrypted_key nullable |
| `src/schemas/schemas.py` | +auth_type, key_value opcional, +5 OAuth schemas |
| `src/utils/crypto.py` | +encrypt_oauth_data(), +decrypt_oauth_data() |
| `src/services/apikey_service.py` | auth_type em create, get_api_key_record() |
| `src/api/agent_routes.py` | +4 endpoints OAuth |
| `src/services/adk/agent_builder.py` | Branch OAuth em _create_llm_agent() |
| `frontend/types/aiModels.ts` | +1 provider, +9 modelos |
| `frontend/services/agentService.ts` | +4 funcoes OAuth |
| `frontend/app/agents/dialogs/ApiKeysDialog.tsx` | UI condicional OAuth |

### Testes (22 testes)

| Classe | Testes |
|--------|--------|
| TestCryptoOAuthData | 3 — round-trip criptografia |
| TestApiKeyAuthType | 6 — criacao, defaults, validacao |
| TestDeviceCodeFlow | 3 — initiate, poll pending/expired |
| TestTokenRefresh | 3 — fresh, expired, missing key |
| TestOAuthStatus | 3 — connected, disconnected, standard key |
| TestRevokeOAuth | 2 — revoke e nonexistent |
| TestModelRemapping | 3 — chatgpt/ -> openai/ |
| TestMigrationCompat | 1 — backward compatibility |

### Nginx Gateway

As rotas OAuth precisam ser adicionadas **antes** da rota generica `/api/v1/agents/*` no nginx:

```nginx
location ~ ^/api/v1/agents/oauth/ {
    proxy_pass $processor_service$request_uri;
    # ... headers ...
}

location ~ ^/api/v1/agents/apikeys {
    proxy_pass $processor_service$request_uri;
    # ... headers ...
}
```

---

## Deploy

### Variaveis de ambiente (novas)

```env
CODEX_ENABLED=true
CODEX_CLIENT_ID=app_EMoamEEZ73f0CkXaXp7hrann
```

### pyproject.toml

```toml
# Antes:
"litellm>=1.68.0,<1.69.0"

# Depois:
"litellm==1.83.3"
```

### Migration

Executa automaticamente no startup do processor (`alembic upgrade head`).
