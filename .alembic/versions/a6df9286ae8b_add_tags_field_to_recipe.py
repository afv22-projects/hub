"""Add tags field to recipe

Revision ID: a6df9286ae8b
Revises: b6bb6e680abe
Create Date: 2026-02-13 12:16:33.500199

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a6df9286ae8b"
down_revision: Union[str, Sequence[str], None] = "b6bb6e680abe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "pantry--recipe",
        sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("pantry--recipe", "tags")
