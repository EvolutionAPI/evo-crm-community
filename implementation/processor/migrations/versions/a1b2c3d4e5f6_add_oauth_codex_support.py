"""add_oauth_codex_support

Revision ID: a1b2c3d4e5f6
Revises: 2df073c7b564
Create Date: 2026-04-16 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "2df073c7b564"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add OAuth Codex support to api_keys table."""
    op.add_column(
        "api_keys",
        sa.Column("auth_type", sa.String(20), server_default="api_key", nullable=False),
    )
    op.add_column(
        "api_keys",
        sa.Column("oauth_data", sa.Text(), nullable=True),
    )
    op.alter_column(
        "api_keys", "encrypted_key", existing_type=sa.String(), nullable=True,
    )
    op.create_check_constraint(
        "chk_auth_type", "api_keys", "auth_type IN ('api_key', 'oauth_codex')",
    )
    op.create_check_constraint(
        "chk_auth_data", "api_keys",
        "(auth_type = 'api_key' AND encrypted_key IS NOT NULL) OR "
        "(auth_type = 'oauth_codex' AND oauth_data IS NOT NULL)",
    )


def downgrade() -> None:
    """Remove OAuth Codex support from api_keys table."""
    op.drop_constraint("chk_auth_data", "api_keys", type_="check")
    op.drop_constraint("chk_auth_type", "api_keys", type_="check")
    op.alter_column(
        "api_keys", "encrypted_key", existing_type=sa.String(), nullable=False,
    )
    op.drop_column("api_keys", "oauth_data")
    op.drop_column("api_keys", "auth_type")
