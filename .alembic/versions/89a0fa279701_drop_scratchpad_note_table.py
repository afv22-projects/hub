"""drop_scratchpad_note_table

Revision ID: 89a0fa279701
Revises: a6df9286ae8b
Create Date: 2026-02-28 07:58:25.544500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89a0fa279701'
down_revision: Union[str, Sequence[str], None] = 'a6df9286ae8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table('reflect--scratchpad_note')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        'reflect--scratchpad_note',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.Column('promoted_to_goal_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['promoted_to_goal_id'], ['reflect--goal.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
