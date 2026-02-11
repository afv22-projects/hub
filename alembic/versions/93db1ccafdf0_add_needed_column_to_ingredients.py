"""add needed column to ingredients

Revision ID: 93db1ccafdf0
Revises: 77ce233f1fe9
Create Date: 2026-02-11 12:28:08.851300

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93db1ccafdf0'
down_revision: Union[str, Sequence[str], None] = '77ce233f1fe9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add needed column to pantry--ingredient table
    op.add_column(
        'pantry--ingredient',
        sa.Column('needed', sa.Boolean(), nullable=False, server_default='0')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove needed column from pantry--ingredient table
    op.drop_column('pantry--ingredient', 'needed')
