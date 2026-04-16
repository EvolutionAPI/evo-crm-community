"""
OAuth Codex service — v2 (post debug sweep fixes).

REPLACES: oauth_codex_service.py

Fixes applied from Debug Sweep (Phase 8):
- [HIGH] device_code stored server-side in pending oauth_data (Agent 3, Item 13)
- [HIGH] get_fresh_token wrapped in try/finally with db.rollback() (Agent 2, Items 2,5,9)
- [HIGH] db.refresh(key) after FOR UPDATE lock (Agent 2, Item 3)
- [HIGH] 401 handler restructured — single transaction, no double-commit (Agent 2, Items 2,10)
- [MEDIUM] Name validation in initiate_device_code_flow (Agent 3, Item 12)
- [MEDIUM] Log message sanitized in _extract_account_id (Agent 1, Item 1)
"""

import time
import logging
import uuid
from typing import Tuple, Optional

import httpx
import jwt

from sqlalchemy.orm import Session

from src.models.models import ApiKey
from src.utils.crypto import encrypt_oauth_data, decrypt_oauth_data
from src.config.oauth_constants import (
    CODEX_CLIENT_ID,
    CODEX_TOKEN_URL,
    CODEX_DEVICE_CODE_URL,
    CODEX_DEVICE_POLL_URL,
    CODEX_DEVICE_VERIFY_URL,
    CODEX_SCOPES,
    CODEX_TOKEN_REFRESH_BUFFER_SECONDS,
    CODEX_JWT_AUTH_CLAIM,
    CODEX_JWT_ACCOUNT_ID_KEY,
    CODEX_API_BASE,
    CODEX_ORIGINATOR,
    CODEX_USER_AGENT,
)
from src.schemas.schemas import (
    OAuthDeviceCodeResponse,
    OAuthDevicePollResponse,
    OAuthStatusResponse,
)

logger = logging.getLogger(__name__)

_HTTP_TIMEOUT = 30.0


def _extract_account_id(id_token: str) -> Optional[str]:
    """Extract chatgpt_account_id from JWT claims.

    Note: verify_signature=False is intentional and safe here. We are only extracting
    the account_id metadata field from a token received over TLS directly from
    auth.openai.com. We do NOT use this data for authentication decisions — the
    token itself is passed as-is to the OpenAI API which validates it server-side.
    Verifying the signature would require fetching OpenAI's JWKS endpoint on every
    call, adding latency and a network dependency with no security benefit.
    """
    try:
        claims = jwt.decode(id_token, options={"verify_signature": False})  # nosec: see docstring
        auth_claims = claims.get(CODEX_JWT_AUTH_CLAIM)
        if isinstance(auth_claims, dict):
            account_id = auth_claims.get(CODEX_JWT_ACCOUNT_ID_KEY)
            if isinstance(account_id, str) and account_id:
                return account_id
        return None
    except Exception:
        # FIX Agent 1 Item 1: Don't log str(e) — JWT lib may include token fragments
        logger.warning("Failed to parse id_token for account_id extraction")
        return None


def _extract_token_expiry(access_token: str) -> float:
    """Extract expiration timestamp from access_token JWT. Falls back to now+3600.

    Note: verify_signature=False is intentional — same rationale as _extract_account_id.
    We only read the 'exp' claim for cache TTL purposes, not for security decisions.
    """
    try:
        claims = jwt.decode(access_token, options={"verify_signature": False})  # nosec: see docstring
        exp = claims.get("exp")
        if exp:
            return float(exp)
    except Exception:
        pass
    return time.time() + 3600


# ---------------------------------------------------------------------------
# 1. INITIATE DEVICE CODE FLOW
# ---------------------------------------------------------------------------

def initiate_device_code_flow(
    db: Session, client_id: uuid.UUID, name: str
) -> OAuthDeviceCodeResponse:
    """Start OAuth device code flow. Creates a pending ApiKey record."""

    # FIX Agent 3 Item 12: Validate name is not empty/whitespace
    if not name or not name.strip():
        raise ValueError("Name is required to start the OAuth flow")

    with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
        resp = client.post(
            CODEX_DEVICE_CODE_URL,
            json={"client_id": CODEX_CLIENT_ID},
        )
        resp.raise_for_status()
        data = resp.json()

    device_code = data.get("device_auth_id") or data.get("device_code")
    user_code = data.get("user_code")
    interval = data.get("interval", 5)

    if not device_code or not user_code:
        raise ValueError("Invalid response from OpenAI device code endpoint")

    # FIX Agent 3 Item 13: Store device_code server-side in pending oauth_data
    # so poll_device_code can retrieve it without the frontend sending it
    pending_oauth = encrypt_oauth_data({"pending_device_code": device_code})

    pending_key = ApiKey(
        id=uuid.uuid4(),
        client_id=client_id,
        name=name.strip(),
        provider="openai-codex",
        auth_type="oauth_codex",
        encrypted_key=None,
        oauth_data=pending_oauth,  # FIX: now stores pending device_code
        is_active=False,
    )
    db.add(pending_key)
    db.commit()
    db.refresh(pending_key)

    logger.info(f"OAuth device code flow initiated for client {client_id}, key_id={pending_key.id}")

    return OAuthDeviceCodeResponse(
        user_code=user_code,
        verification_uri=CODEX_DEVICE_VERIFY_URL,
        expires_in=900,
        interval=interval,
        key_id=pending_key.id,
    )


# ---------------------------------------------------------------------------
# 2. POLL DEVICE CODE
# ---------------------------------------------------------------------------

def poll_device_code(
    db: Session, key_id: uuid.UUID
) -> OAuthDevicePollResponse:
    """Poll OpenAI for device code authorization status.

    FIX Agent 3 Item 13: device_code is now read from server-side storage
    instead of being passed from the frontend.
    """
    key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not key:
        return OAuthDevicePollResponse(status="error", message="Key not found")

    # Already completed
    if key.is_active and key.oauth_data:
        stored = decrypt_oauth_data(key.oauth_data)
        if "access_token" in stored:
            return OAuthDevicePollResponse(status="complete", key_id=key_id)

    # FIX Agent 3 Item 13: Read device_code from server-side storage
    device_code = None
    if key.oauth_data:
        stored = decrypt_oauth_data(key.oauth_data)
        device_code = stored.get("pending_device_code")

    if not device_code:
        return OAuthDevicePollResponse(
            status="error", key_id=key_id, message="Missing device code"
        )

    # Poll OpenAI
    with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
        resp = client.post(
            CODEX_DEVICE_POLL_URL,
            json={
                "client_id": CODEX_CLIENT_ID,
                "device_auth_id": device_code,
            },
        )

    if resp.status_code in (403, 428):
        return OAuthDevicePollResponse(status="pending", key_id=key_id)

    if resp.status_code == 410:
        key.is_active = False
        db.commit()
        return OAuthDevicePollResponse(
            status="expired", key_id=key_id, message="Device code expired"
        )

    if resp.status_code != 200:
        return OAuthDevicePollResponse(
            status="error", key_id=key_id,
            message=f"Unexpected status {resp.status_code}",
        )

    # Success — extract authorization_code and exchange for tokens
    poll_data = resp.json()
    authorization_code = poll_data.get("authorization_code")
    code_verifier = poll_data.get("code_verifier")

    if not authorization_code:
        return OAuthDevicePollResponse(
            status="error", key_id=key_id, message="No authorization_code in response"
        )

    with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
        token_resp = client.post(
            CODEX_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": authorization_code,
                "client_id": CODEX_CLIENT_ID,
                "code_verifier": code_verifier or "",
                "redirect_uri": "http://localhost:1455/auth/callback",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_resp.raise_for_status()
        tokens = token_resp.json()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    id_token = tokens.get("id_token", "")

    if not access_token or not refresh_token:
        return OAuthDevicePollResponse(
            status="error", key_id=key_id, message="Missing tokens in response"
        )

    account_id = _extract_account_id(id_token) or _extract_account_id(access_token) or ""
    expires_at = _extract_token_expiry(access_token)

    oauth_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "id_token": id_token,
        "expires_at": expires_at,
        "account_id": account_id,
        "plan_type": "plus",
    }
    key.oauth_data = encrypt_oauth_data(oauth_data)
    key.is_active = True
    db.commit()

    logger.info(f"OAuth Codex connected for key_id={key_id}, account={account_id}")
    return OAuthDevicePollResponse(status="complete", key_id=key_id)


# ---------------------------------------------------------------------------
# 3. GET FRESH TOKEN (thread-safe, with all debug fixes)
# ---------------------------------------------------------------------------

def get_fresh_token(db: Session, key_id: uuid.UUID) -> Tuple[str, str]:
    """Get a valid access token for the given OAuth key.

    Thread-safe: uses SELECT FOR UPDATE with try/finally rollback.
    Auto-refreshes expired tokens.

    FIX Agent 2 Items 2,3,5,9,10: Consolidated fix with try/finally,
    db.refresh(), single-transaction 401 handling.
    """
    try:
        # Row-level lock to prevent concurrent refresh
        key = (
            db.query(ApiKey)
            .filter(ApiKey.id == key_id, ApiKey.is_active == True)
            .with_for_update()
            .first()
        )

        if not key or not key.oauth_data:
            raise ValueError(f"OAuth key {key_id} not found or not connected")

        # FIX Agent 2 Item 3: Force re-read after lock to bypass identity map cache
        db.refresh(key)

        oauth = decrypt_oauth_data(key.oauth_data)
        access_token = oauth.get("access_token", "")
        refresh_token = oauth.get("refresh_token", "")
        expires_at = oauth.get("expires_at", 0)
        account_id = oauth.get("account_id", "")

        # Token still valid — return it
        if expires_at > time.time() + CODEX_TOKEN_REFRESH_BUFFER_SECONDS:
            db.commit()  # Release FOR UPDATE lock
            return access_token, account_id

        # --- Token expired or near-expiry: refresh ---
        logger.info(f"Refreshing OAuth token for key_id={key_id}")

        try:
            with httpx.Client(timeout=_HTTP_TIMEOUT) as client:
                resp = client.post(
                    CODEX_TOKEN_URL,
                    data={
                        "client_id": CODEX_CLIENT_ID,
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "scope": CODEX_SCOPES,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                resp.raise_for_status()
                new_tokens = resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                # FIX Agent 2 Item 2,10: Single transaction, no double-commit
                key.is_active = False
                db.commit()
                raise ValueError(
                    f"OAuth refresh token revoked for key_id={key_id}. "
                    "User must re-authenticate via device code flow."
                )
            # Non-401 server error: try stale token grace period
            if expires_at > time.time() - 300:
                db.commit()
                logger.warning(f"Token refresh got {e.response.status_code} for key_id={key_id}, using stale token")
                return access_token, account_id
            raise
        except httpx.HTTPError:
            # Network error — return stale token if within grace period
            if expires_at > time.time() - 300:
                db.commit()
                logger.warning(f"Token refresh network error for key_id={key_id}, using stale token")
                return access_token, account_id
            raise ValueError(f"Token refresh failed for key_id={key_id} and token is expired")

        # Update stored tokens
        new_access = new_tokens.get("access_token", access_token)
        new_refresh = new_tokens.get("refresh_token", refresh_token)
        new_id_token = new_tokens.get("id_token", oauth.get("id_token", ""))
        new_expires_at = _extract_token_expiry(new_access)
        new_account_id = (
            _extract_account_id(new_id_token)
            or _extract_account_id(new_access)
            or account_id
        )

        updated_oauth = {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "id_token": new_id_token,
            "expires_at": new_expires_at,
            "account_id": new_account_id,
            "plan_type": oauth.get("plan_type", "plus"),
        }
        key.oauth_data = encrypt_oauth_data(updated_oauth)
        db.commit()

        logger.info(f"OAuth token refreshed for key_id={key_id}")
        return new_access, new_account_id

    except Exception:
        # FIX Agent 2 Items 2,5,9: Always release FOR UPDATE lock on any exception
        db.rollback()
        raise


# ---------------------------------------------------------------------------
# 4. GET OAUTH STATUS
# ---------------------------------------------------------------------------

def get_oauth_status(db: Session, key_id: uuid.UUID) -> OAuthStatusResponse:
    """Get connection status for an OAuth Codex key."""
    key = db.query(ApiKey).filter(ApiKey.id == key_id).first()

    if not key or key.auth_type != "oauth_codex":
        return OAuthStatusResponse(key_id=key_id, connected=False)

    if not key.oauth_data or not key.is_active:
        return OAuthStatusResponse(key_id=key_id, connected=False)

    oauth = decrypt_oauth_data(key.oauth_data)

    # Pending keys (only have pending_device_code) are not "connected"
    if "access_token" not in oauth:
        return OAuthStatusResponse(key_id=key_id, connected=False)

    from datetime import datetime, timezone
    expires_at_dt = None
    exp_ts = oauth.get("expires_at", 0)
    if exp_ts:
        expires_at_dt = datetime.fromtimestamp(exp_ts, tz=timezone.utc)

    return OAuthStatusResponse(
        key_id=key_id,
        connected=True,
        expires_at=expires_at_dt,
        account_id=oauth.get("account_id"),
        plan_type=oauth.get("plan_type"),
    )


# ---------------------------------------------------------------------------
# 5. REVOKE OAUTH
# ---------------------------------------------------------------------------

def revoke_oauth(db: Session, key_id: uuid.UUID) -> bool:
    """Revoke OAuth connection.

    Deletes the ApiKey record entirely instead of setting oauth_data=None,
    because the chk_auth_data CHECK constraint requires oauth_data IS NOT NULL
    for auth_type='oauth_codex' rows.
    """
    key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not key:
        return False

    db.delete(key)
    db.commit()

    logger.info(f"OAuth Codex revoked and deleted for key_id={key_id}")
    return True
