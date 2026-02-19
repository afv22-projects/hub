"""add category to ingredients

Revision ID: 77ce233f1fe9
Revises: fe79425efa9a
Create Date: 2026-02-11 12:02:37.538355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77ce233f1fe9'
down_revision: Union[str, Sequence[str], None] = 'fe79425efa9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum type for ingredient categories
    ingredient_category_enum = sa.Enum(
        'DAIRY', 'MEAT', 'PRODUCE', 'GRAINS', 'SPICES', 'CONDIMENTS',
        'CANNED', 'FROZEN', 'BAKERY', 'BEVERAGES', 'SNACKS', 'OTHER',
        name='ingredientcategory'
    )
    ingredient_category_enum.create(op.get_bind(), checkfirst=True)

    # Add category column to pantry--ingredient table
    op.add_column(
        'pantry--ingredient',
        sa.Column('category', ingredient_category_enum, nullable=False, server_default='OTHER')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove category column from pantry--ingredient table
    op.drop_column('pantry--ingredient', 'category')

    # Drop enum type
    sa.Enum(name='ingredientcategory').drop(op.get_bind(), checkfirst=True)
