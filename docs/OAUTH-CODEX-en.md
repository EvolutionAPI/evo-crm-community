# OAuth Codex (OpenAI) — ChatGPT Subscription Authentication for Evo CRM

## Overview

This implementation adds **OpenAI OAuth Codex** as an alternative authentication method in Evo CRM, allowing users with **ChatGPT Plus** ($20/mo) or **ChatGPT Pro** ($200/mo) subscriptions to use GPT-5.x models directly, without needing a separate OpenAI API key.

The approach is **hybrid**: OAuth Codex works alongside existing API keys. No current functionality is changed or removed.

---

## Solution Architecture

### Current flow (API Keys)

```
User pastes API key (sk-...) in frontend
  -> Backend encrypts with Fernet (AES-128-CBC)
  -> Saves to api_keys.encrypted_key in PostgreSQL
  -> AgentBuilder decrypts and passes to LiteLlm(model, api_key)
  -> LiteLLM routes to the correct provider
```

### New flow (OAuth Codex)

```
User selects "ChatGPT (OAuth)" in frontend
  -> Clicks "Connect with ChatGPT"
  -> Backend initiates device code flow with auth.openai.com
  -> User receives code (e.g., ABCD-1234)
  -> User visits auth.openai.com/codex/device and enters the code
  -> Backend receives OAuth tokens, encrypts and saves to PostgreSQL
  -> AgentBuilder detects auth_type='oauth_codex'
  -> Decrypts tokens, checks validity, auto-refreshes if expired
  -> Passes token as Bearer to chatgpt.com/backend-api/codex
  -> Response returns through existing pipeline
```

### Technical Decision: openai/ prefix (not chatgpt/)

Source code analysis of LiteLLM confirmed that the `chatgpt/` provider **ignores the `api_key` parameter** and always reads tokens from a global `auth.json` file. This is incompatible with multi-tenancy (each client has their own token).

The solution uses the `openai/` provider with custom parameters:
- `api_base` = `https://chatgpt.com/backend-api/codex`
- `api_key` = tenant's OAuth token (used as Bearer)
- `extra_headers` = ChatGPT-Account-Id, originator

Google ADK's `LiteLlm` passes `**kwargs` via `_additional_args` to `litellm.acompletion()`, confirmed in source code (SHA 7d13696c). Each tenant gets their own instance with zero shared global state.

---

## Available Models

| Model | Minimum Plan |
|-------|-------------|
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

## Database Changes

### Migration: `a1b2c3d4e5f6_add_oauth_codex_support`

```sql
ALTER TABLE api_keys ADD COLUMN auth_type VARCHAR(20) DEFAULT 'api_key' NOT NULL;
ALTER TABLE api_keys ADD COLUMN oauth_data TEXT;
ALTER TABLE api_keys ALTER COLUMN encrypted_key DROP NOT NULL;

-- Data integrity constraints
CHECK (auth_type IN ('api_key', 'oauth_codex'))
CHECK ((auth_type = 'api_key' AND encrypted_key IS NOT NULL) OR
       (auth_type = 'oauth_codex' AND oauth_data IS NOT NULL))
```

**Backward compatible:** existing records automatically receive `auth_type='api_key'`.

**Reversible:** `alembic downgrade -1` removes the columns with no data loss.

---

## New Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/v1/agents/oauth/codex/device-code` | Initiate device code flow |
| POST | `/api/v1/agents/oauth/codex/device-poll` | Check if user authorized |
| GET | `/api/v1/agents/oauth/codex/status/{key_id}` | OAuth connection status |
| DELETE | `/api/v1/agents/oauth/codex/{key_id}` | Revoke OAuth connection |

All require JWT + client ownership verification.

---

## Security

### LiteLLM Upgrade: v1.68.0 -> v1.83.3

The original repository uses `litellm>=1.68.0,<1.69.0` (released May 2025). This version has the following known vulnerabilities:

#### CVE-2026-35030 — OIDC Authentication Bypass (CRITICAL)

LiteLLM used only the **first 20 characters** of a JWT as the cache key. This allowed different tokens with the same first 20 characters to share the same authenticated session, enabling complete OIDC authentication bypass.

**Fixed in:** v1.83.0 (uses full JWT hash as cache key)

#### Supply Chain Attack — TeamPCP (March 2026)

On March 24, 2026, LiteLLM versions **v1.82.7** and **v1.82.8** on PyPI were compromised by a threat group called TeamPCP:

1. The group compromised **Trivy** (Aqua Security's vulnerability scanner)
2. Malicious Trivy executed in LiteLLM's CI/CD via GitHub Actions
3. Extracted PyPI publishing credentials (`PYPI_PUBLISH_PASSWORD`) via memory dump
4. Published malicious versions that:
   - Collected all environment credentials (AWS, GCP, Azure, K8s, SSH, DB)
   - Encrypted and exfiltrated to attacker-controlled server
   - Installed persistence via systemd service
   - Executed additional payloads on command

Versions were removed from PyPI in ~40 minutes but accumulated tens of thousands of downloads.

#### v1.83.3-stable — Secure

Version v1.83.3 was built on the new **CI/CD v2 pipeline** with:

| Measure | Detail |
|---------|--------|
| SHA pinning | GitHub Actions pinned by immutable commit SHA |
| Trusted Publishers (OIDC) | Short-lived tokens replace static passwords |
| Cosign signing | Docker images cryptographically signed |
| SLSA provenance | Verifiable build provenance |
| Isolated environments | Ephemeral build and publish environments |

**Verified SHA-256 hashes:**
```
wheel:  eab4d2e1871cac0239799c33eb724d239116bf1bd275e287f92ae76ba8c7a05a
tar.gz: 38a452f708f9bb682fdfc3607aa44d68cfe936bf4a18683b0cdc5fb476424a6f
```

#### Compatibility: google-adk==0.3.0

Issue #4367 (google/adk-python) documents that LiteLLM >=1.81.3 changes the `response_schema` format for Gemini 2.0+ models. ADK 0.3.0 may have issues with structured output on those models. **OpenAI/ChatGPT/Anthropic models are NOT affected.**

### OAuth Implementation Security

| Aspect | Status |
|--------|--------|
| Tokens in logs | No tokens are logged (access, refresh, id) |
| Tokens in API responses | Never returned to frontend |
| Encryption at rest | Fernet (AES-128-CBC + HMAC-SHA256) |
| Thread-safety | SELECT FOR UPDATE with try/finally + db.rollback() |
| CSRF | JWT Bearer (stateless, CSRF-immune) |
| XSS | verificationUri validated (rejects javascript:) |
| SQL injection | SQLAlchemy ORM (parameterized queries) |
| Device code storage | Server-side only (never exposed to frontend) |

---

## Implementation Files

### New (6 files)

| File | Service |
|------|---------|
| `src/config/oauth_constants.py` | Processor |
| `src/services/oauth_codex_service.py` | Processor |
| `migrations/versions/a1b2c3d4e5f6_add_oauth_codex_support.py` | Processor |
| `frontend/types/oauth.ts` | Frontend |
| `frontend/app/agents/dialogs/OAuthDeviceCodeFlow.tsx` | Frontend |
| `frontend/app/agents/components/OAuthStatusBadge.tsx` | Frontend |

### Modified (9 files)

| File | Change |
|------|--------|
| `src/models/models.py` | +auth_type, +oauth_data, encrypted_key nullable |
| `src/schemas/schemas.py` | +auth_type, key_value optional, +5 OAuth schemas |
| `src/utils/crypto.py` | +encrypt_oauth_data(), +decrypt_oauth_data() |
| `src/services/apikey_service.py` | auth_type in create, get_api_key_record() |
| `src/api/agent_routes.py` | +4 OAuth endpoints |
| `src/services/adk/agent_builder.py` | OAuth branch in _create_llm_agent() |
| `frontend/types/aiModels.ts` | +1 provider, +9 models |
| `frontend/services/agentService.ts` | +4 OAuth functions |
| `frontend/app/agents/dialogs/ApiKeysDialog.tsx` | Conditional OAuth UI |

### Tests (22 tests)

| Class | Tests |
|-------|-------|
| TestCryptoOAuthData | 3 — encryption round-trip |
| TestApiKeyAuthType | 6 — creation, defaults, validation |
| TestDeviceCodeFlow | 3 — initiate, poll pending/expired |
| TestTokenRefresh | 3 — fresh, expired, missing key |
| TestOAuthStatus | 3 — connected, disconnected, standard key |
| TestRevokeOAuth | 2 — revoke and nonexistent |
| TestModelRemapping | 3 — chatgpt/ -> openai/ |
| TestMigrationCompat | 1 — backward compatibility |

### Nginx Gateway

OAuth routes must be added **before** the generic `/api/v1/agents/*` route in nginx:

```nginx
location ~ ^/api/v1/agents/oauth/ {
    proxy_pass $processor_service$request_uri;
}

location ~ ^/api/v1/agents/apikeys {
    proxy_pass $processor_service$request_uri;
}
```

---

## Deployment

### New environment variables

```env
CODEX_ENABLED=true
CODEX_CLIENT_ID=app_EMoamEEZ73f0CkXaXp7hrann
```

### pyproject.toml

```toml
# Before:
"litellm>=1.68.0,<1.69.0"

# After:
"litellm==1.83.3"
```

### Migration

Runs automatically on processor startup (`alembic upgrade head`).
