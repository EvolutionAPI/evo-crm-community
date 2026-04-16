"""
API Key service changes for OAuth Codex support.

Apply to: evo-ai-processor-community/src/services/apikey_service.py

3 changes: modify create_api_key, modify get_decrypted_api_key, add get_api_key_record.
All other functions (get_api_key, get_api_keys_by_client, update_api_key, delete_api_key)
remain UNCHANGED.
"""


# ===========================================================================
# CHANGE 1: Modify create_api_key signature and body
# ===========================================================================

# BEFORE (line 42-71):
# def create_api_key(
#     db: Session, client_id: uuid.UUID, name: str, provider: str, key_value: str
# ) -> ApiKey:
#     """Create a new encrypted API key"""
#     try:
#         encrypted = encrypt_api_key(key_value)
#         api_key = ApiKey(
#             client_id=client_id,
#             name=name,
#             provider=provider,
#             encrypted_key=encrypted,
#             is_active=True,
#         )
#         ...

# AFTER:
# def create_api_key(
#     db: Session,
#     client_id: uuid.UUID,
#     name: str,
#     provider: str,
#     key_value: str = None,
#     auth_type: str = "api_key",
# ) -> ApiKey:
#     """Create a new encrypted API key or OAuth Codex connection"""
#     try:
#         if auth_type == "api_key":
#             if not key_value:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="key_value is required for api_key auth type",
#                 )
#             encrypted = encrypt_api_key(key_value)
#         else:
#             encrypted = None  # OAuth keys don't store a static API key
#
#         api_key = ApiKey(
#             client_id=client_id,
#             name=name,
#             provider=provider,
#             encrypted_key=encrypted,
#             auth_type=auth_type,
#             is_active=(auth_type == "api_key"),  # OAuth keys start inactive
#         )
#         ...  (rest of function unchanged)


# ===========================================================================
# CHANGE 2: Modify get_decrypted_api_key to handle OAuth keys
# ===========================================================================

# BEFORE (line 128-138):
# def get_decrypted_api_key(db: Session, key_id: uuid.UUID) -> Optional[str]:
#     """Get the decrypted value of an API key"""
#     try:
#         key = get_api_key(db, key_id)
#         if not key or not key.is_active:
#             logger.warning(f"API key {key_id} not found or inactive")
#             return None
#         return decrypt_api_key(key.encrypted_key)
#     except Exception as e:
#         logger.error(f"Error decrypting API key {key_id}: {str(e)}")
#         return None

# AFTER:
# def get_decrypted_api_key(db: Session, key_id: uuid.UUID) -> Optional[str]:
#     """Get the decrypted value of an API key.
#     Returns None for OAuth keys (they use a different auth path in AgentBuilder).
#     """
#     try:
#         key = get_api_key(db, key_id)
#         if not key or not key.is_active:
#             logger.warning(f"API key {key_id} not found or inactive")
#             return None
#         if key.auth_type == "oauth_codex":
#             return None  # OAuth keys use get_fresh_token() in AgentBuilder
#         return decrypt_api_key(key.encrypted_key)
#     except Exception as e:
#         logger.error(f"Error decrypting API key {key_id}: {str(e)}")
#         return None


# ===========================================================================
# CHANGE 3: Add new function get_api_key_record (after get_decrypted_api_key)
# ===========================================================================

# ADD after get_decrypted_api_key (line ~139):
#
# def get_api_key_record(db: Session, key_id: uuid.UUID) -> Optional[ApiKey]:
#     """Get the full ApiKey record for auth_type checking in AgentBuilder.
#
#     Unlike get_decrypted_api_key which returns the decrypted key string,
#     this returns the full ORM object so the caller can check auth_type
#     and route to the appropriate authentication path.
#     """
#     try:
#         key = get_api_key(db, key_id)
#         if not key or not key.is_active:
#             logger.warning(f"API key record {key_id} not found or inactive")
#             return None
#         return key
#     except Exception as e:
#         logger.error(f"Error getting API key record {key_id}: {str(e)}")
#         return None
