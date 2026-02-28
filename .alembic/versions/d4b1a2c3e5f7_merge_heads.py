"""merge heads

Revision ID: d4b1a2c3e5f7
Revises: 15c85a88b1c2, 89a0fa279701
Create Date: 2026-02-28 15:10:00.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'd4b1a2c3e5f7'
down_revision: Union[str, Sequence[str], None] = ('15c85a88b1c2', '89a0fa279701')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
