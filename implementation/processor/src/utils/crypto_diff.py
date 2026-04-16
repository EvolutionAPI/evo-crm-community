"""
Crypto extension for OAuth data encryption.

Apply to: evo-ai-processor-community/src/utils/crypto.py

ADD these two functions at the end of the existing file.
The existing encrypt_api_key() and decrypt_api_key() remain unchanged.
"""


# --- ADD AFTER existing functions (line 69) ---

# import json  <-- add to imports at top of file

# def encrypt_oauth_data(oauth_dict: dict) -> str:
#     """Encrypt OAuth token data (dict -> JSON -> Fernet encrypted string).
#
#     Used to store OAuth access_token, refresh_token, id_token, account_id
#     securely in the api_keys.oauth_data column.
#     """
#     if not oauth_dict:
#         return ""
#     try:
#         json_str = json.dumps(oauth_dict)
#         return fernet.encrypt(json_str.encode()).decode()
#     except Exception as e:
#         logger.error(f"Error encrypting OAuth data: {str(e)}")
#         raise
#
#
# def decrypt_oauth_data(encrypted_data: str) -> dict:
#     """Decrypt Fernet-encrypted OAuth data back to dict.
#
#     Returns dict with keys: access_token, refresh_token, id_token,
#     expires_at, account_id, plan_type
#     """
#     if not encrypted_data:
#         return {}
#     try:
#         json_str = fernet.decrypt(encrypted_data.encode()).decode()
#         return json.loads(json_str)
#     except Exception as e:
#         logger.error(f"Error decrypting OAuth data: {str(e)}")
#         raise
