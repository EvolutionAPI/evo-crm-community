"""
OAuth Codex (OpenAI) constants and configuration.

New file — add to: evo-ai-processor-community/src/config/oauth_constants.py
"""

import os


# OpenAI Codex OAuth client (public, used by Codex CLI and all OAuth tools)
CODEX_CLIENT_ID = os.getenv("CODEX_CLIENT_ID", "app_EMoamEEZ73f0CkXaXp7hrann")

# Auth endpoints
CODEX_AUTH_BASE = "https://auth.openai.com"
CODEX_TOKEN_URL = f"{CODEX_AUTH_BASE}/oauth/token"
CODEX_DEVICE_CODE_URL = f"{CODEX_AUTH_BASE}/api/accounts/deviceauth/usercode"
CODEX_DEVICE_POLL_URL = f"{CODEX_AUTH_BASE}/api/accounts/deviceauth/token"
CODEX_DEVICE_VERIFY_URL = f"{CODEX_AUTH_BASE}/codex/device"

# API endpoint for ChatGPT subscription models
CODEX_API_BASE = "https://chatgpt.com/backend-api/codex"

# OAuth scopes
CODEX_SCOPES = "openid profile email offline_access"

# Token refresh buffer (refresh if expiring within this many seconds)
CODEX_TOKEN_REFRESH_BUFFER_SECONDS = 60

# Device code polling timeout (15 minutes, per OpenAI spec)
CODEX_DEVICE_CODE_TIMEOUT_SECONDS = 900

# Required headers for Codex API calls
CODEX_ORIGINATOR = "codex_cli_rs"
CODEX_USER_AGENT = "codex_cli_rs/0.38.0"

# JWT claim path for extracting ChatGPT account ID from id_token
CODEX_JWT_AUTH_CLAIM = "https://api.openai.com/auth"
CODEX_JWT_ACCOUNT_ID_KEY = "chatgpt_account_id"
