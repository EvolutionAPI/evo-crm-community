# HARDOFF: Evo CRM + OAuth Codex OpenAI — Documentacao Completa

## 1. ARQUITETURA DO EVO CRM

```
Browser → Cloudflare → Traefik (porta 443)
                          ├─ crm.grupomirandas.com.br → evocrm_frontend (React, porta 80)
                          ├─ api-crm.grupomirandas.com.br → evocrm_gateway (Nginx, porta 3030)
                          │     ├─ /api/v1/auth/* → evocrm_auth (Rails, porta 3001)
                          │     ├─ /api/v1/agents/* → evocrm_core (Go, porta 5555)
                          │     ├─ /api/v1/chat/* → evocrm_processor (Python, porta 8000)
                          │     ├─ /api/v1/agents/[id]/integrations → evocrm_processor
                          │     └─ /* (catch-all) → evocrm_crm (Rails, porta 3000)
                          └─ api-crm + PathPrefix(/api/v1/agents/oauth) [priority 10]
                                → evocrm_processor (Python, porta 8000) [via Traefik labels]
```

### Servicos

| Servico | Stack | Imagem | Porta |
|---|---|---|---|
| evocrm_auth | Ruby/Rails | ghcr.io/neritondias/evo-auth:test | 3001 |
| evocrm_crm | Ruby/Rails | ghcr.io/neritondias/evo-crm:test | 3000 |
| evocrm_core | Go/Gin | ghcr.io/neritondias/evo-core:test | 5555 |
| evocrm_processor | Python/FastAPI | ghcr.io/neritondias/evo-processor:test | 8000 |
| evocrm_frontend | React/Vite | ghcr.io/neritondias/evo-frontend:test | 80 |
| evocrm_gateway | Nginx | evoapicloud/evo-crm-gateway:develop | 3030 |
| evocrm_bot_runtime | Go | evoapicloud/evo-bot-runtime:latest | 8080 |

### Problema critico: "Not Found"
O erro "Not Found" que aparece repetidamente e do **Traefik**, nao dos servicos. Acontece quando:
- O Traefik reinicia e demora para redescobrir servicos (aguardar 30s)
- O Cloudflare esta com proxy desligado e o certificado TLS falha
- Force updates mudam IPs dos containers e o Traefik precisa redescobrir

**Solucao:** sempre manter Cloudflare com proxy LIGADO. Apos qualquer redeploy, aguardar 30-60 segundos. Se persistir, forcar update do Traefik e aguardar.

---

## 2. GATEWAY E ROTEAMENTO

O gateway original (`evoapicloud/evo-crm-gateway:develop`) tem nomes fixos no nginx.conf mas usa env vars para resolver:
- `AUTH_UPSTREAM=evocrm_auth:3001`
- `CRM_UPSTREAM=evocrm_crm:3000`
- `CORE_UPSTREAM=evocrm_core:5555`
- `PROCESSOR_UPSTREAM=evocrm_processor:8000`
- `BOT_RUNTIME_UPSTREAM=evocrm_bot_runtime:8080`

**PROBLEMA:** O gateway roteia `/api/v1/agents/*` para o **Core (Go)**, NAO para o Processor (Python). As rotas OAuth estao no Processor mas o gateway manda para o Core → 404.

**SOLUCAO:** Adicionamos labels Traefik no processor para rotear `/api/v1/agents/oauth/*` diretamente, bypassando o gateway:
```yaml
evocrm_processor:
  deploy:
    labels:
      - traefik.enable=1
      - traefik.docker.network=gmnet
      - traefik.http.routers.evocrm_oauth.rule=Host(`api-crm.grupomirandas.com.br`) && PathPrefix(`/api/v1/agents/oauth`)
      - traefik.http.routers.evocrm_oauth.entrypoints=websecure
      - traefik.http.routers.evocrm_oauth.priority=10
      - traefik.http.routers.evocrm_oauth.tls.certresolver=letsencryptresolver
      - traefik.http.routers.evocrm_oauth.service=evocrm_oauth
      - traefik.http.services.evocrm_oauth.loadbalancer.server.port=8000
      - traefik.http.services.evocrm_oauth.loadbalancer.passHostHeader=true
```

**NAO usar gateway customizado** (tentamos e quebrou o site). Manter `evoapicloud/evo-crm-gateway:develop`.

---

## 3. BANCO DE DADOS

### Tabela `evo_core_api_keys` (gerenciada pelo Core Go + Processor Python)

A tabela original tem:
```sql
id UUID PRIMARY KEY
name VARCHAR(255) NOT NULL UNIQUE
provider VARCHAR(255) NOT NULL
key TEXT NOT NULL
is_active BOOLEAN DEFAULT TRUE
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

### Colunas adicionadas para OAuth (migration manual, NAO via Alembic):
```sql
ALTER TABLE evo_core_api_keys ADD COLUMN IF NOT EXISTS auth_type VARCHAR(20) NOT NULL DEFAULT 'api_key';
ALTER TABLE evo_core_api_keys ADD COLUMN IF NOT EXISTS oauth_data TEXT;
ALTER TABLE evo_core_api_keys ALTER COLUMN key DROP NOT NULL;
```

**IMPORTANTE:** A coluna se chama `key` (nao `encrypted_key`). O model SQLAlchemy do processor deve mapear para `key`, nao `encrypted_key`. O Alembic NAO funciona neste projeto porque as tabelas sao criadas pelo Core (Go), nao pelo Processor (Python). O `alembic_version` esta vazio.

### Constraint UNIQUE em `name`
Existe `idx_evo_core_api_keys_name_unique` — nao pode ter duas keys com o mesmo nome. O OAuth cria keys com o email do usuario como nome, entao cada tentativa duplicada falha. Precisa ou usar nomes unicos (com timestamp) ou remover a constraint.

---

## 4. LITELLM E CHATGPT/ PROVIDER

### Como LiteLLM funciona com ChatGPT subscription

**FATO CRITICO: LiteLLM IGNORA o parametro `api_key` para modelos `chatgpt/`.**

O provider `chatgpt/` tem seu proprio `Authenticator` que:
1. Le tokens de `~/.config/litellm/chatgpt/auth.json`
2. Se nao existe, inicia device code flow no terminal
3. Faz auto-refresh de tokens expirados
4. Envia headers especiais para `chatgpt.com/backend-api/codex`

### auth.json format
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "id_token": "eyJ...",
  "expires_at": 1750000000,
  "account_id": "user-xxxxxxxxxxxx"
}
```

### Env vars que controlam
- `CHATGPT_TOKEN_DIR` — diretorio do auth.json (default: `~/.config/litellm/chatgpt`)
- `CHATGPT_AUTH_FILE` — nome do arquivo (default: `auth.json`)
- `CHATGPT_API_BASE` — endpoint (default: `https://chatgpt.com/backend-api/codex`)
- `CHATGPT_ORIGINATOR` — header originator (default: `codex_cli_rs`)

### Headers enviados pelo chatgpt/ provider
```
Authorization: Bearer <access_token>
content-type: application/json
accept: text/event-stream
originator: codex_cli_rs
user-agent: codex_cli_rs/0.38.0 (linux x86_64)
ChatGPT-Account-Id: <account_id>
session_id: <uuid>
```

### Endpoint
`POST https://chatgpt.com/backend-api/codex/responses` (Responses API, NAO chat/completions)

### Integracao no agent_builder
Para usar OAuth com LiteLLM:
```python
# 1. Buscar tokens do banco
tokens = get_raw_oauth_tokens(db, agent.api_key_id)

# 2. Escrever auth.json (LiteLLM le daqui)
write_chatgpt_auth_json(tokens)

# 3. Usar prefixo chatgpt/ SEM api_key
LiteLlm(model="chatgpt/gpt-5.4")  # SEM api_key, SEM api_base
```

**Problemas de multi-tenancy:** auth.json e global. Se dois usuarios chamam ao mesmo tempo, um sobrescreve o outro. Usar file locking (fcntl) mitiga parcialmente.

### Modelos disponiveis via ChatGPT subscription
```
chatgpt/gpt-5.4
chatgpt/gpt-5.4-pro
chatgpt/gpt-5.3-codex
chatgpt/gpt-5.3-codex-spark
chatgpt/gpt-5.3-instant
chatgpt/gpt-5.3-chat-latest
chatgpt/gpt-5.2-codex
chatgpt/gpt-5.2
chatgpt/gpt-5.1-codex-max
chatgpt/gpt-5.1-codex-mini
```

---

## 5. OAUTH CODEX — FLUXO PKCE (MODELO EVO-NEXUS)

### Constantes CORRETAS
```python
CODEX_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"  # Client ID publico do Codex
CODEX_AUTH_URL = "https://auth.openai.com/oauth/authorize"
CODEX_TOKEN_URL = "https://auth.openai.com/oauth/token"
CODEX_REDIRECT_URI = "http://localhost:1455/auth/callback"
CODEX_SCOPES = "openid profile email offline_access"
```

### Fluxo completo (como o evo-nexus faz)

```
1. Usuario clica "Connect with ChatGPT" no frontend
2. Frontend chama POST /api/v1/agents/oauth/codex/auth-start
3. Backend:
   a. Gera code_verifier = secrets.token_urlsafe(64)
   b. Gera code_challenge = base64url(sha256(code_verifier))
   c. Gera state = secrets.token_urlsafe(32)
   d. Salva {pending_verifier, state} criptografado em api_keys.oauth_data
   e. Cria ApiKey com auth_type="oauth_codex", is_active=False
   f. Retorna authorize_url + key_id
4. Frontend abre authorize_url em nova aba
5. Usuario faz login no ChatGPT e autoriza
6. OpenAI redireciona para http://localhost:1455/auth/callback?code=XXX&state=YYY
7. Browser mostra erro (localhost nao existe) — ESPERADO
8. Usuario copia URL da barra de enderecos
9. Cola no input do CRM
10. Frontend chama POST /api/v1/agents/oauth/codex/auth-complete {key_id, callback_url}
11. Backend:
    a. Extrai code da URL
    b. Busca code_verifier do banco (descriptografa oauth_data)
    c. POST para https://auth.openai.com/oauth/token:
       grant_type=authorization_code
       code=XXX
       redirect_uri=http://localhost:1455/auth/callback
       client_id=app_EMoamEEZ73f0CkXaXp7hrann
       code_verifier=<verifier>
    d. Recebe access_token, refresh_token, id_token
    e. Extrai account_id do JWT
    f. Salva tokens criptografados em oauth_data
    g. Seta is_active=True
12. Sucesso!
```

### Endpoints do processor
```
POST /api/v1/agents/oauth/codex/auth-start     — Inicia PKCE, retorna URL
POST /api/v1/agents/oauth/codex/auth-complete   — Troca code por tokens
GET  /api/v1/agents/oauth/codex/status/{key_id} — Status da conexao
DELETE /api/v1/agents/oauth/codex/{key_id}      — Revogar
POST /api/v1/agents/oauth/codex/internal/token/{key_id} — Service-to-service
```

---

## 6. REPOSITORIOS E BRANCHES

| Repo | Fork | Branch | O que tem |
|---|---|---|---|
| evo-ai-processor-community | NeritonDias/evo-ai-processor-community | feat/oauth-codex | OAuth service, routes, schemas, constants, agent_builder |
| evo-ai-frontend-community | NeritonDias/evo-ai-frontend-community | feat/oauth-codex | OAuthBrowserFlow, OAuthStatusBadge, ApiKeysModal, agentService |
| evo-ai-crm-community | NeritonDias/evo-ai-crm-community | feat/oauth-audio-transcription | audio_transcription_service com OAuth |
| evo-crm (monorepo) | NeritonDias/evo-crm | test/all-fixes | Submodule pointers, build workflow, nginx |

### GitHub Token
`<SEU_GITHUB_TOKEN>` (NeritonDias)

### Build workflow
GitHub Actions em NeritonDias/evo-crm branch test/all-fixes:
`.github/workflows/build-test.yml` builda 6 imagens para `ghcr.io/neritondias/*:test`

---

## 7. PROBLEMAS CONHECIDOS E SOLUCOES

### "Not Found" do Traefik
- Causa: Traefik perde referencia aos servicos apos force updates
- Solucao: Aguardar 30-60s. Se persistir, `docker service update --force $(docker service ls -q -f name=traefik)` e aguardar

### Core service 500 (cached plan)
- Causa: Go cacheia plano SQL, colunas novas (auth_type, oauth_data) confundem
- Solucao: `docker service update --force evocrm_evocrm_core`

### Processor 503 (auth validation)
- Causa: Falta `EVO_AUTH_BASE_URL` — processor tenta validar JWT em localhost
- Solucao: Adicionar `EVO_AUTH_BASE_URL=http://evocrm_auth:3001` no YAML do processor

### OAuth duplicate key
- Causa: UNIQUE constraint em name, tentativas repetidas criam conflito
- Solucao: `DELETE FROM evo_core_api_keys WHERE auth_type = 'oauth_codex';`

### OAuth error da OpenAI
- Causa: client_id ou scopes errados
- Solucao: Verificar oauth_constants.py tem `app_EMoamEEZ73f0CkXaXp7hrann` e `openid profile email offline_access`

### Frontend VITE vars
- VITE_* sao build-time, nao runtime
- WebSocket mostra `VITE_WS_URL_PLACEHOLDER` — imagem buildada sem dominio correto
- Para corrigir: rebuildar frontend com VITE_* como build-args no Dockerfile

---

## 8. YAML CORRETO PARA DEPLOY

```yaml
version: "3.7"
services:
  evocrm_gateway:
    image: evoapicloud/evo-crm-gateway:develop  # NUNCA trocar por customizado
    networks: [gmnet]
    environment:
      - AUTH_UPSTREAM=evocrm_auth:3001
      - CRM_UPSTREAM=evocrm_crm:3000
      - CORE_UPSTREAM=evocrm_core:5555
      - PROCESSOR_UPSTREAM=evocrm_processor:8000
      - BOT_RUNTIME_UPSTREAM=evocrm_bot_runtime:8080
    deploy:
      labels:
        - traefik.enable=1
        - traefik.docker.network=gmnet
        - traefik.http.routers.evocrm_gateway.rule=Host(`api-crm.grupomirandas.com.br`)
        - traefik.http.routers.evocrm_gateway.entrypoints=websecure
        - traefik.http.routers.evocrm_gateway.priority=1
        - traefik.http.routers.evocrm_gateway.tls.certresolver=letsencryptresolver
        - traefik.http.routers.evocrm_gateway.service=evocrm_gateway
        - traefik.http.services.evocrm_gateway.loadbalancer.server.port=3030

  evocrm_processor:
    image: ghcr.io/neritondias/evo-processor:test
    environment:
      - EVO_AUTH_BASE_URL=http://evocrm_auth:3001  # OBRIGATORIO
      - ENCRYPTION_KEY=Bu-3lfmq_mRWcw5Rf57ltnzVvTzj6DUhGDlOjq2xjIQ=
      # ... outras vars
    deploy:
      labels:  # OBRIGATORIO para OAuth funcionar
        - traefik.enable=1
        - traefik.docker.network=gmnet
        - traefik.http.routers.evocrm_oauth.rule=Host(`api-crm.grupomirandas.com.br`) && PathPrefix(`/api/v1/agents/oauth`)
        - traefik.http.routers.evocrm_oauth.entrypoints=websecure
        - traefik.http.routers.evocrm_oauth.priority=10
        - traefik.http.routers.evocrm_oauth.tls.certresolver=letsencryptresolver
        - traefik.http.routers.evocrm_oauth.service=evocrm_oauth
        - traefik.http.services.evocrm_oauth.loadbalancer.server.port=8000
```

---

## 9. CHECKLIST PARA DEPLOY LIMPO

1. Dropar banco: `DROP DATABASE evocrm; CREATE DATABASE evocrm;`
2. Pull todas imagens: `docker pull ghcr.io/neritondias/evo-{auth,crm,core,processor,frontend}:test`
3. Deploy pelo Portainer com YAML correto
4. Aguardar 2 minutos para migrations rodarem
5. Aplicar migration OAuth manualmente:
   ```sql
   ALTER TABLE evo_core_api_keys ADD COLUMN IF NOT EXISTS auth_type VARCHAR(20) NOT NULL DEFAULT 'api_key';
   ALTER TABLE evo_core_api_keys ADD COLUMN IF NOT EXISTS oauth_data TEXT;
   ALTER TABLE evo_core_api_keys ALTER COLUMN key DROP NOT NULL;
   INSERT INTO alembic_version (version_num) VALUES ('a1b2c3d4e5f6') ON CONFLICT DO NOTHING;
   ```
6. Reiniciar Core: `docker service update --force evocrm_evocrm_core`
7. Acessar `https://crm.grupomirandas.com.br` — setup inicial

---

## 10. PROXIMOS PASSOS PARA OAUTH FUNCIONAR

1. **Verificar que oauth_constants.py tem os valores corretos** (client_id e scopes)
2. **Testar endpoint auth-start** manualmente para confirmar URL correta
3. **Resolver erro "Erro de autenticacao" da OpenAI** — pode ser que o client_id publico `app_EMoamEEZ73f0CkXaXp7hrann` nao aceita PKCE de browser (apenas do CLI). Se for o caso, alternativa e Device Code Flow que funciona do servidor
4. **Resolver "Error loading API keys"** — Core Go quebra com colunas novas, precisa restart
5. **Implementar token exchange (auth-complete)** e testar end-to-end
6. **Resolver multi-tenancy do auth.json** para produção
