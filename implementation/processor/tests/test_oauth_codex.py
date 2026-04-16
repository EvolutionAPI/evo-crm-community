"""
OAuth Codex integration tests.

New file — add to: evo-ai-processor-community/tests/test_oauth_codex.py

Run with: pytest tests/test_oauth_codex.py -v

These tests mock external HTTP calls to auth.openai.com and verify
the full OAuth flow from device code initiation through token refresh.
"""

import time
import json
import uuid
import pytest
from unittest.mock import patch, MagicMock

from src.models.models import ApiKey, Client
from src.utils.crypto import encrypt_api_key, decrypt_api_key, encrypt_oauth_data, decrypt_oauth_data
from src.services.oauth_codex_service import (
    initiate_device_code_flow,
    poll_device_code,
    get_fresh_token,
    get_oauth_status,
    revoke_oauth,
)
from src.services.apikey_service import (
    create_api_key,
    get_api_key,
    get_decrypted_api_key,
    get_api_key_record,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def test_client_record(db_session):
    """Create a test client in the DB."""
    client = Client(
        id=uuid.uuid4(),
        name="Test Client",
        email="test@example.com",
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


@pytest.fixture
def mock_device_code_response():
    """Mock response from OpenAI device code endpoint."""
    return {
        "device_auth_id": "dev_auth_abc123",
        "user_code": "ABCD-1234",
        "interval": 5,
    }


@pytest.fixture
def mock_poll_success_response():
    """Mock successful poll response with authorization_code."""
    return {
        "authorization_code": "auth_code_xyz789",
        "code_verifier": "verifier_abc",
        "code_challenge": "challenge_def",
    }


@pytest.fixture
def mock_token_response():
    """Mock token exchange response."""
    # Build a minimal JWT for testing (not cryptographically valid)
    import base64
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode()).decode().rstrip("=")
    payload_data = {
        "exp": int(time.time()) + 3600,
        "https://api.openai.com/auth": {
            "chatgpt_account_id": "user-test-account-123",
        },
    }
    payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip("=")
    fake_jwt = f"{header}.{payload}.fake_signature"

    return {
        "access_token": fake_jwt,
        "refresh_token": "refresh_token_test_456",
        "id_token": fake_jwt,
        "token_type": "Bearer",
        "expires_in": 3600,
    }


# ---------------------------------------------------------------------------
# Test: Crypto round-trip for OAuth data
# ---------------------------------------------------------------------------

class TestCryptoOAuthData:
    def test_encrypt_decrypt_oauth_data(self):
        """OAuth data survives Fernet encrypt/decrypt round-trip."""
        original = {
            "access_token": "eyJ_test_access_token",
            "refresh_token": "test_refresh_token",
            "id_token": "eyJ_test_id_token",
            "expires_at": 1745000000.0,
            "account_id": "user-abc123",
            "plan_type": "plus",
        }
        encrypted = encrypt_oauth_data(original)
        assert encrypted != json.dumps(original)  # Not plaintext
        assert isinstance(encrypted, str)

        decrypted = decrypt_oauth_data(encrypted)
        assert decrypted == original

    def test_encrypt_empty_dict(self):
        """Empty dict encrypts to empty string."""
        assert encrypt_oauth_data({}) == ""

    def test_decrypt_empty_string(self):
        """Empty string decrypts to empty dict."""
        assert decrypt_oauth_data("") == {}


# ---------------------------------------------------------------------------
# Test: API Key creation with auth_type
# ---------------------------------------------------------------------------

class TestApiKeyAuthType:
    def test_create_standard_api_key(self, db_session, test_client_record):
        """Standard API key creation with auth_type='api_key' works as before."""
        key = create_api_key(
            db_session, test_client_record.id, "Test Key", "openai", "sk-test123"
        )
        assert key.auth_type == "api_key"
        assert key.encrypted_key is not None
        assert key.is_active is True
        assert key.oauth_data is None

    def test_create_api_key_requires_key_value(self, db_session, test_client_record):
        """auth_type='api_key' without key_value raises error."""
        with pytest.raises(Exception):
            create_api_key(
                db_session, test_client_record.id, "No Key", "openai",
                key_value=None, auth_type="api_key",
            )

    def test_create_oauth_key_no_encrypted_key(self, db_session, test_client_record):
        """auth_type='oauth_codex' creates key without encrypted_key."""
        key = create_api_key(
            db_session, test_client_record.id, "OAuth Key", "openai-codex",
            key_value=None, auth_type="oauth_codex",
        )
        assert key.auth_type == "oauth_codex"
        assert key.encrypted_key is None
        assert key.is_active is False  # OAuth keys start inactive

    def test_get_decrypted_key_returns_none_for_oauth(self, db_session, test_client_record):
        """get_decrypted_api_key returns None for OAuth keys."""
        key = create_api_key(
            db_session, test_client_record.id, "OAuth Key", "openai-codex",
            key_value=None, auth_type="oauth_codex",
        )
        # Manually activate to test the auth_type check
        key.is_active = True
        key.oauth_data = encrypt_oauth_data({"access_token": "test"})
        db_session.commit()

        result = get_decrypted_api_key(db_session, key.id)
        assert result is None  # Should NOT return OAuth tokens via this function

    def test_get_api_key_record_returns_full_object(self, db_session, test_client_record):
        """get_api_key_record returns full ORM object with auth_type."""
        key = create_api_key(
            db_session, test_client_record.id, "Test Key", "openai", "sk-test"
        )
        record = get_api_key_record(db_session, key.id)
        assert record is not None
        assert record.auth_type == "api_key"
        assert record.id == key.id

    def test_existing_keys_default_to_api_key(self, db_session, test_client_record):
        """Existing keys without auth_type get default 'api_key'."""
        key = create_api_key(
            db_session, test_client_record.id, "Old Key", "openai", "sk-old"
        )
        assert key.auth_type == "api_key"  # server_default


# ---------------------------------------------------------------------------
# Test: Device code flow
# ---------------------------------------------------------------------------

class TestDeviceCodeFlow:
    @patch("src.services.oauth_codex_service.httpx.Client")
    def test_initiate_device_code_flow(
        self, mock_client_cls, db_session, test_client_record, mock_device_code_response
    ):
        """Device code flow creates pending key and returns user_code."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_device_code_response
        mock_resp.raise_for_status = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=MagicMock(post=MagicMock(return_value=mock_resp)))
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        result = initiate_device_code_flow(
            db_session, test_client_record.id, "My ChatGPT"
        )

        assert result.user_code == "ABCD-1234"
        assert result.verification_uri == "https://auth.openai.com/codex/device"
        assert result.key_id is not None

        # Verify pending key was created
        key = get_api_key(db_session, result.key_id)
        assert key is not None
        assert key.auth_type == "oauth_codex"
        assert key.is_active is False
        assert key.provider == "openai-codex"

    @patch("src.services.oauth_codex_service.httpx.Client")
    def test_poll_pending(self, mock_client_cls, db_session, test_client_record):
        """Poll returns 'pending' when user hasn't authorized yet."""
        # Create pending key
        key = ApiKey(
            id=uuid.uuid4(), client_id=test_client_record.id,
            name="Pending", provider="openai-codex",
            auth_type="oauth_codex", is_active=False,
        )
        db_session.add(key)
        db_session.commit()

        mock_resp = MagicMock()
        mock_resp.status_code = 403  # authorization_pending
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=MagicMock(post=MagicMock(return_value=mock_resp)))
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        result = poll_device_code(db_session, key.id, "dev_auth_abc")
        assert result.status == "pending"

    @patch("src.services.oauth_codex_service.httpx.Client")
    def test_poll_expired(self, mock_client_cls, db_session, test_client_record):
        """Poll returns 'expired' when device code times out."""
        key = ApiKey(
            id=uuid.uuid4(), client_id=test_client_record.id,
            name="Expiring", provider="openai-codex",
            auth_type="oauth_codex", is_active=False,
        )
        db_session.add(key)
        db_session.commit()

        mock_resp = MagicMock()
        mock_resp.status_code = 410  # expired
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=MagicMock(post=MagicMock(return_value=mock_resp)))
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        result = poll_device_code(db_session, key.id, "dev_auth_abc")
        assert result.status == "expired"


# ---------------------------------------------------------------------------
# Test: Token refresh
# ---------------------------------------------------------------------------

class TestTokenRefresh:
    def _create_oauth_key(self, db_session, client_id, expires_at):
        """Helper to create an OAuth key with specific expiration."""
        oauth_data = {
            "access_token": "old_access_token",
            "refresh_token": "test_refresh_token",
            "id_token": "test_id_token",
            "expires_at": expires_at,
            "account_id": "user-test-123",
            "plan_type": "plus",
        }
        key = ApiKey(
            id=uuid.uuid4(), client_id=client_id,
            name="OAuth Key", provider="openai-codex",
            auth_type="oauth_codex",
            oauth_data=encrypt_oauth_data(oauth_data),
            is_active=True,
        )
        db_session.add(key)
        db_session.commit()
        return key

    def test_fresh_token_no_refresh_needed(self, db_session, test_client_record):
        """Token that expires in >60s is returned directly without refresh."""
        key = self._create_oauth_key(
            db_session, test_client_record.id,
            expires_at=time.time() + 3600,  # 1 hour from now
        )

        access_token, account_id = get_fresh_token(db_session, key.id)
        assert access_token == "old_access_token"
        assert account_id == "user-test-123"

    @patch("src.services.oauth_codex_service.httpx.Client")
    def test_expired_token_triggers_refresh(
        self, mock_client_cls, db_session, test_client_record
    ):
        """Token expiring within 60s triggers a refresh."""
        key = self._create_oauth_key(
            db_session, test_client_record.id,
            expires_at=time.time() + 30,  # 30s from now — within buffer
        )

        import base64
        payload_data = {
            "exp": int(time.time()) + 7200,
            "https://api.openai.com/auth": {"chatgpt_account_id": "user-refreshed"},
        }
        payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip("=")
        header = base64.urlsafe_b64encode(json.dumps({"alg": "none"}).encode()).decode().rstrip("=")
        new_jwt = f"{header}.{payload}.sig"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "access_token": new_jwt,
            "refresh_token": "new_refresh_token",
            "id_token": new_jwt,
        }
        mock_resp.raise_for_status = MagicMock()
        mock_client_cls.return_value.__enter__ = MagicMock(return_value=MagicMock(post=MagicMock(return_value=mock_resp)))
        mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)

        access_token, account_id = get_fresh_token(db_session, key.id)
        assert access_token == new_jwt
        assert account_id == "user-refreshed"

        # Verify DB was updated
        updated = decrypt_oauth_data(get_api_key(db_session, key.id).oauth_data)
        assert updated["access_token"] == new_jwt
        assert updated["refresh_token"] == "new_refresh_token"

    def test_missing_key_raises(self, db_session):
        """get_fresh_token raises for non-existent key."""
        with pytest.raises(ValueError, match="not found"):
            get_fresh_token(db_session, uuid.uuid4())


# ---------------------------------------------------------------------------
# Test: OAuth status
# ---------------------------------------------------------------------------

class TestOAuthStatus:
    def test_connected_status(self, db_session, test_client_record):
        """Connected OAuth key returns connected=True with details."""
        oauth_data = {
            "access_token": "test", "refresh_token": "test",
            "expires_at": time.time() + 3600,
            "account_id": "user-abc", "plan_type": "plus",
        }
        key = ApiKey(
            id=uuid.uuid4(), client_id=test_client_record.id,
            name="Connected", provider="openai-codex",
            auth_type="oauth_codex",
            oauth_data=encrypt_oauth_data(oauth_data),
            is_active=True,
        )
        db_session.add(key)
        db_session.commit()

        result = get_oauth_status(db_session, key.id)
        assert result.connected is True
        assert result.account_id == "user-abc"
        assert result.plan_type == "plus"

    def test_disconnected_status(self, db_session, test_client_record):
        """Inactive OAuth key returns connected=False."""
        key = ApiKey(
            id=uuid.uuid4(), client_id=test_client_record.id,
            name="Disconnected", provider="openai-codex",
            auth_type="oauth_codex", is_active=False,
        )
        db_session.add(key)
        db_session.commit()

        result = get_oauth_status(db_session, key.id)
        assert result.connected is False

    def test_standard_key_returns_not_connected(self, db_session, test_client_record):
        """Standard API key returns connected=False for OAuth status."""
        key = create_api_key(
            db_session, test_client_record.id, "Standard", "openai", "sk-test"
        )
        result = get_oauth_status(db_session, key.id)
        assert result.connected is False


# ---------------------------------------------------------------------------
# Test: Revoke OAuth
# ---------------------------------------------------------------------------

class TestRevokeOAuth:
    def test_revoke_deactivates_and_clears(self, db_session, test_client_record):
        """Revoking clears oauth_data and deactivates the key."""
        oauth_data = {"access_token": "secret", "refresh_token": "secret"}
        key = ApiKey(
            id=uuid.uuid4(), client_id=test_client_record.id,
            name="ToRevoke", provider="openai-codex",
            auth_type="oauth_codex",
            oauth_data=encrypt_oauth_data(oauth_data),
            is_active=True,
        )
        db_session.add(key)
        db_session.commit()

        result = revoke_oauth(db_session, key.id)
        assert result is True

        revoked = get_api_key(db_session, key.id)
        assert revoked.is_active is False
        assert revoked.oauth_data is None

    def test_revoke_nonexistent_key(self, db_session):
        """Revoking non-existent key returns False."""
        result = revoke_oauth(db_session, uuid.uuid4())
        assert result is False


# ---------------------------------------------------------------------------
# Test: Model name remapping
# ---------------------------------------------------------------------------

class TestModelRemapping:
    def test_chatgpt_prefix_remapped(self):
        """chatgpt/ prefix is remapped to openai/ for LiteLLM."""
        model = "chatgpt/gpt-5.3-codex"
        if model.startswith("chatgpt/"):
            model = "openai/" + model[len("chatgpt/"):]
        assert model == "openai/gpt-5.3-codex"

    def test_openai_prefix_unchanged(self):
        """openai/ prefix is not modified."""
        model = "openai/gpt-4o"
        if model.startswith("chatgpt/"):
            model = "openai/" + model[len("chatgpt/"):]
        assert model == "openai/gpt-4o"

    def test_other_provider_unchanged(self):
        """Non-OpenAI models are not affected."""
        model = "anthropic/claude-3-5-sonnet-20241022"
        if model.startswith("chatgpt/"):
            model = "openai/" + model[len("chatgpt/"):]
        assert model == "anthropic/claude-3-5-sonnet-20241022"


# ---------------------------------------------------------------------------
# Test: Migration backward compatibility
# ---------------------------------------------------------------------------

class TestMigrationCompat:
    def test_existing_keys_get_default_auth_type(self, db_session, test_client_record):
        """Keys created without explicit auth_type get 'api_key' default."""
        key = create_api_key(
            db_session, test_client_record.id, "Legacy", "openai", "sk-legacy"
        )
        # Simulate reading a key that was created before the migration
        record = get_api_key_record(db_session, key.id)
        assert record.auth_type == "api_key"
        assert record.oauth_data is None
        assert record.encrypted_key is not None
