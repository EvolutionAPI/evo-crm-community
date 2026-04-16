"""
AgentBuilder modification for OAuth Codex support.

Apply to: evo-ai-processor-community/src/services/adk/agent_builder.py

This is THE critical injection point. Only the _create_llm_agent method
is modified. All other methods remain UNCHANGED.

2 changes:
1. Add imports at top of file
2. Replace the API key resolution block (lines 135-182) in _create_llm_agent()
"""


# ===========================================================================
# CHANGE 1: Add imports (after line 44, before line 45)
# ===========================================================================

# EXISTING (line 44):
# from src.services.apikey_service import get_decrypted_api_key

# ADD after it:
# from src.services.apikey_service import get_api_key_record
# from src.services.oauth_codex_service import get_fresh_token
# from src.config.oauth_constants import (
#     CODEX_API_BASE,
#     CODEX_ORIGINATOR,
#     CODEX_USER_AGENT,
# )


# ===========================================================================
# CHANGE 2: Replace lines 135-182 in _create_llm_agent()
# ===========================================================================

# --- BEFORE (lines 135-182) ---
#
#         # Get API key from api_key_id
#         api_key = None
#
#         # Get API key from api_key_id
#         if hasattr(agent, "api_key_id") and agent.api_key_id:
#             decrypted_key = get_decrypted_api_key(self.db, agent.api_key_id)
#             if decrypted_key:
#                 logger.info(f"Using stored API key for agent {agent.name}")
#                 api_key = decrypted_key
#             else:
#                 logger.error(f"Stored API key not found for agent {agent.name}")
#                 raise ValueError(
#                     f"API key with ID {agent.api_key_id} not found or inactive"
#                 )
#         else:
#             # Check if there is an API key in the config (temporary field)
#             config_api_key = agent.config.get("api_key") if agent.config else None
#             if config_api_key:
#                 logger.info(f"Using config API key for agent {agent.name}")
#                 # Check if it is a UUID of a stored key
#                 try:
#                     key_id = uuid.UUID(config_api_key)
#                     decrypted_key = get_decrypted_api_key(self.db, key_id)
#                     if decrypted_key:
#                         logger.info("Config API key is a valid reference")
#                         api_key = decrypted_key
#                     else:
#                         # Use the key directly
#                         api_key = config_api_key
#                 except (ValueError, TypeError):
#                     # It is not a UUID, use directly
#                     api_key = config_api_key
#             else:
#                 logger.error(f"No API key configured for agent {agent.name}")
#                 raise ValueError(
#                     f"Agent {agent.name} does not have a configured API key"
#                 )
#
#         return (
#             LlmAgent(
#                 name=agent.name,
#                 model=LiteLlm(model=agent.model, api_key=api_key),
#                 instruction=formatted_prompt,
#                 description=agent.description,
#                 tools=all_tools,
#             ),
#             mcp_exit_stack,
#         )


# --- AFTER (replace lines 135-182 with this) ---
#
#         # Get API key / OAuth token for LLM authentication
#         api_key = None
#         model_name = agent.model
#         litellm_kwargs = {}
#
#         if hasattr(agent, "api_key_id") and agent.api_key_id:
#             # Try to get the full key record to check auth_type
#             key_record = get_api_key_record(self.db, agent.api_key_id)
#
#             if key_record and key_record.auth_type == "oauth_codex":
#                 # === OAuth Codex Flow ===
#                 # get_fresh_token handles expiry check and auto-refresh
#                 # Uses SELECT FOR UPDATE for thread-safe multi-tenant operation
#                 access_token, account_id = get_fresh_token(
#                     self.db, key_record.id
#                 )
#                 api_key = access_token
#
#                 # Remap model name: "chatgpt/gpt-5.3-codex" -> "openai/gpt-5.3-codex"
#                 # We use openai/ prefix because chatgpt/ provider IGNORES api_key
#                 # parameter and reads from a global auth.json file (not multi-tenant safe).
#                 # With openai/ prefix, api_key is used directly as Bearer token.
#                 if model_name.startswith("chatgpt/"):
#                     model_name = "openai/" + model_name[len("chatgpt/"):]
#
#                 litellm_kwargs = {
#                     "api_base": CODEX_API_BASE,
#                     "extra_headers": {
#                         "ChatGPT-Account-Id": account_id,
#                         "originator": CODEX_ORIGINATOR,
#                         "User-Agent": CODEX_USER_AGENT,
#                         "accept": "text/event-stream",
#                     },
#                 }
#                 logger.info(f"Using OAuth Codex token for agent {agent.name}")
#
#             elif key_record:
#                 # === Standard API Key Flow (UNCHANGED behavior) ===
#                 decrypted_key = get_decrypted_api_key(self.db, agent.api_key_id)
#                 if decrypted_key:
#                     logger.info(f"Using stored API key for agent {agent.name}")
#                     api_key = decrypted_key
#                 else:
#                     logger.error(f"Stored API key not found for agent {agent.name}")
#                     raise ValueError(
#                         f"API key with ID {agent.api_key_id} not found or inactive"
#                     )
#             else:
#                 logger.error(f"API key record not found for agent {agent.name}")
#                 raise ValueError(
#                     f"API key with ID {agent.api_key_id} not found or inactive"
#                 )
#         else:
#             # === Config fallback (UNCHANGED behavior) ===
#             config_api_key = agent.config.get("api_key") if agent.config else None
#             if config_api_key:
#                 logger.info(f"Using config API key for agent {agent.name}")
#                 try:
#                     key_id = uuid.UUID(config_api_key)
#                     decrypted_key = get_decrypted_api_key(self.db, key_id)
#                     if decrypted_key:
#                         logger.info("Config API key is a valid reference")
#                         api_key = decrypted_key
#                     else:
#                         api_key = config_api_key
#                 except (ValueError, TypeError):
#                     api_key = config_api_key
#             else:
#                 logger.error(f"No API key configured for agent {agent.name}")
#                 raise ValueError(
#                     f"Agent {agent.name} does not have a configured API key"
#                 )
#
#         return (
#             LlmAgent(
#                 name=agent.name,
#                 model=LiteLlm(model=model_name, api_key=api_key, **litellm_kwargs),
#                 instruction=formatted_prompt,
#                 description=agent.description,
#                 tools=all_tools,
#             ),
#             mcp_exit_stack,
#         )


# ===========================================================================
# HOW IT WORKS — Technical Explanation
# ===========================================================================
#
# For auth_type == "api_key" (existing behavior):
#   - get_decrypted_api_key() returns the Fernet-decrypted API key string
#   - LiteLlm(model="openai/gpt-4o", api_key="sk-...")
#   - litellm_kwargs is empty -> no api_base or extra_headers
#   - 100% identical to current production behavior
#
# For auth_type == "oauth_codex" (new behavior):
#   - get_fresh_token() returns (access_token, account_id)
#     - Checks token expiry, auto-refreshes if needed
#     - Uses SELECT FOR UPDATE for thread-safe concurrent access
#   - Model is remapped: "chatgpt/gpt-5.3-codex" -> "openai/gpt-5.3-codex"
#     - We use openai/ prefix because chatgpt/ provider in LiteLLM
#       IGNORES the api_key parameter (reads from global auth.json)
#     - openai/ prefix uses api_key directly as Authorization: Bearer header
#   - api_base overrides endpoint to chatgpt.com/backend-api/codex
#   - extra_headers adds ChatGPT-Account-Id and originator
#   - LiteLlm(model="openai/gpt-5.3-codex", api_key=token,
#             api_base="https://chatgpt.com/backend-api/codex",
#             extra_headers={...})
#   - Google ADK's LiteLlm stores **kwargs in _additional_args
#     and merges them into every litellm.acompletion() call
#   - Each tenant gets their own LiteLlm instance = zero shared state
#
# Config fallback path:
#   - Unchanged — still resolves api_key from agent.config
#   - Only handles static API keys (no OAuth in config fallback)
