"""
Schema changes for OAuth Codex support.

Apply these changes to: evo-ai-processor-community/src/schemas/schemas.py

All Agent/Client/MCP/Tool/Folder schemas remain UNCHANGED.
Only ApiKey schemas are modified + new OAuth schemas added.
"""


# --- MODIFIED: ApiKeyBase ---
# BEFORE:
# class ApiKeyBase(BaseModel):
#     name: str
#     provider: str
#
# AFTER:
# class ApiKeyBase(BaseModel):
#     name: str
#     provider: str
#     auth_type: str = "api_key"                        <-- NEW FIELD


# --- MODIFIED: ApiKeyCreate ---
# BEFORE:
# class ApiKeyCreate(ApiKeyBase):
#     client_id: UUID4
#     key_value: str                                    <-- WAS REQUIRED
#
# AFTER:
# class ApiKeyCreate(ApiKeyBase):
#     client_id: UUID4
#     key_value: Optional[str] = None                   <-- NOW OPTIONAL
#
#     @validator("key_value")
#     def validate_key_value(cls, v, values):
#         auth_type = values.get("auth_type", "api_key")
#         if auth_type == "api_key" and not v:
#             raise ValueError("key_value is required for api_key auth type")
#         return v


# --- MODIFIED: ApiKeyUpdate ---
# ADDED: auth_type: Optional[str] = None


# --- MODIFIED: ApiKey (response) ---
# ADDED: oauth_connected: Optional[bool] = None


# --- NEW SCHEMAS ---

# class OAuthDeviceCodeRequest(BaseModel):
#     client_id: UUID4
#     name: str
#
# class OAuthDeviceCodeResponse(BaseModel):
#     user_code: str
#     verification_uri: str
#     expires_in: int
#     interval: int
#     key_id: UUID4
#
# class OAuthDevicePollRequest(BaseModel):
#     key_id: UUID4
#
# class OAuthDevicePollResponse(BaseModel):
#     status: str   # "pending", "complete", "expired", "error"
#     key_id: Optional[UUID4] = None
#     message: Optional[str] = None
#
# class OAuthStatusResponse(BaseModel):
#     key_id: UUID4
#     connected: bool
#     expires_at: Optional[datetime] = None
#     account_id: Optional[str] = None
#     plan_type: Optional[str] = None
