"""
Agent routes changes for OAuth Codex support.

Apply to: evo-ai-processor-community/src/api/agent_routes.py

2 changes:
1. Add OAuth schema imports to the existing import block
2. Modify create_api_key route to pass auth_type
3. Add 4 new OAuth endpoints (after existing apikey routes, before folder routes)

All existing routes remain UNCHANGED.
"""


# ===========================================================================
# CHANGE 1: Add imports (line 49-58)
# ===========================================================================

# ADD to the existing import from src.schemas.schemas:
# from src.schemas.schemas import (
#     Agent,
#     AgentCreate,
#     AgentFolder,
#     AgentFolderCreate,
#     AgentFolderUpdate,
#     ApiKey,
#     ApiKeyCreate,
#     ApiKeyUpdate,
#     OAuthDeviceCodeRequest,      # <-- NEW
#     OAuthDeviceCodeResponse,     # <-- NEW
#     OAuthDevicePollRequest,      # <-- NEW
#     OAuthDevicePollResponse,     # <-- NEW
#     OAuthStatusResponse,         # <-- NEW
# )

# ADD new import:
# from src.services.oauth_codex_service import (
#     initiate_device_code_flow,
#     poll_device_code,
#     get_oauth_status,
#     revoke_oauth,
# )


# ===========================================================================
# CHANGE 2: Modify create_api_key route (line 111-124)
# ===========================================================================

# BEFORE:
# @router.post("/apikeys", response_model=ApiKey, status_code=status.HTTP_201_CREATED)
# async def create_api_key(
#     key: ApiKeyCreate,
#     db: Session = Depends(get_db),
#     payload: dict = Depends(get_jwt_token),
# ):
#     """Create a new API key"""
#     await verify_user_client(payload, db, key.client_id)
#     db_key = apikey_service.create_api_key(
#         db, key.client_id, key.name, key.provider, key.key_value
#     )
#     return db_key

# AFTER:
# @router.post("/apikeys", response_model=ApiKey, status_code=status.HTTP_201_CREATED)
# async def create_api_key(
#     key: ApiKeyCreate,
#     db: Session = Depends(get_db),
#     payload: dict = Depends(get_jwt_token),
# ):
#     """Create a new API key"""
#     await verify_user_client(payload, db, key.client_id)
#     db_key = apikey_service.create_api_key(
#         db, key.client_id, key.name, key.provider,
#         key.key_value, key.auth_type,                  # <-- ADDED auth_type
#     )
#     return db_key


# ===========================================================================
# CHANGE 3: Add 4 OAuth endpoints
# Insert AFTER delete_api_key route (line ~244) and BEFORE folder routes (line ~247)
# ===========================================================================

# --- OAuth Codex Device Code Flow ---
#
# @router.post(
#     "/oauth/codex/device-code",
#     response_model=OAuthDeviceCodeResponse,
#     status_code=status.HTTP_200_OK,
# )
# async def oauth_codex_device_code(
#     req: OAuthDeviceCodeRequest,
#     db: Session = Depends(get_db),
#     payload: dict = Depends(get_jwt_token),
# ):
#     """Initiate OAuth Codex device code flow.
#
#     Returns a user_code and verification_uri. The user must visit the URI
#     and enter the code to authorize their ChatGPT subscription.
#     """
#     await verify_user_client(payload, db, req.client_id)
#     return initiate_device_code_flow(db, req.client_id, req.name)
#
#
# @router.post(
#     "/oauth/codex/device-poll",
#     response_model=OAuthDevicePollResponse,
#     status_code=status.HTTP_200_OK,
# )
# async def oauth_codex_device_poll(
#     req: OAuthDevicePollRequest,
#     db: Session = Depends(get_db),
#     payload: dict = Depends(get_jwt_token),
# ):
#     """Poll for device code authorization status.
#
#     Call this at the interval specified by device-code response.
#     Returns 'pending', 'complete', 'expired', or 'error'.
#     """
#     key = apikey_service.get_api_key(db, req.key_id)
#     if not key:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found"
#         )
#     await verify_user_client(payload, db, key.client_id)
#     return poll_device_code(db, req.key_id)
#
#
# @router.get(
#     "/oauth/codex/status/{key_id}",
#     response_model=OAuthStatusResponse,
#     status_code=status.HTTP_200_OK,
# )
# async def oauth_codex_status(
#     key_id: uuid.UUID,
#     x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
#     db: Session = Depends(get_db),
#     payload: dict = Depends(get_jwt_token),
# ):
#     """Get OAuth Codex connection status for a key."""
#     await verify_user_client(payload, db, x_client_id)
#     key = apikey_service.get_api_key(db, key_id)
#     if not key:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found"
#         )
#     if key.client_id != x_client_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="API Key does not belong to the specified client",
#         )
#     return get_oauth_status(db, key_id)
#
#
# @router.delete(
#     "/oauth/codex/{key_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# async def oauth_codex_revoke(
#     key_id: uuid.UUID,
#     x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
#     db: Session = Depends(get_db),
#     payload: dict = Depends(get_jwt_token),
# ):
#     """Revoke OAuth Codex connection (deactivate key and clear tokens)."""
#     await verify_user_client(payload, db, x_client_id)
#     key = apikey_service.get_api_key(db, key_id)
#     if not key:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found"
#         )
#     if key.client_id != x_client_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="API Key does not belong to the specified client",
#         )
#     revoke_oauth(db, key_id)


# ===========================================================================
# SUMMARY OF ENDPOINTS
# ===========================================================================
#
# Existing (UNCHANGED):
#   POST   /api/v1/agents/apikeys              - Create API key
#   GET    /api/v1/agents/apikeys              - List API keys
#   GET    /api/v1/agents/apikeys/{key_id}     - Get API key
#   PUT    /api/v1/agents/apikeys/{key_id}     - Update API key
#   DELETE /api/v1/agents/apikeys/{key_id}     - Delete API key
#
# New OAuth (added):
#   POST   /api/v1/agents/oauth/codex/device-code     - Start device code flow
#   POST   /api/v1/agents/oauth/codex/device-poll      - Poll for authorization
#   GET    /api/v1/agents/oauth/codex/status/{key_id}  - Check connection status
#   DELETE /api/v1/agents/oauth/codex/{key_id}         - Revoke OAuth connection
#
# All endpoints require JWT + verify_user_client for ownership verification.
