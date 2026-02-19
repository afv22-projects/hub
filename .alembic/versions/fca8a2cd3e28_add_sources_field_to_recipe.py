"""add sources field to recipe

Revision ID: fca8a2cd3e28
Revises: 8ed89148b566
Create Date: 2026-02-11 15:11:44.404638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fca8a2cd3e28'
down_revision: Union[str, Sequence[str], None] = '8ed89148b566'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add sources column as JSON with default empty list
    op.add_column('pantry--recipe', sa.Column('sources', sa.JSON(), nullable=False, server_default='[]'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove sources column
    op.drop_column('pantry--recipe', 'sources')
