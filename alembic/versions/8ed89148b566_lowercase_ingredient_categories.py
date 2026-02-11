"""lowercase_ingredient_categories

Revision ID: 8ed89148b566
Revises: 93db1ccafdf0
Create Date: 2026-02-11 13:01:08.930468

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '8ed89148b566'
down_revision: Union[str, Sequence[str], None] = '93db1ccafdf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Update existing category values to lowercase
    op.execute("""
        UPDATE "pantry--ingredient"
        SET category = LOWER(category)
        WHERE category IN ('Dairy', 'Meat', 'Produce', 'Grains', 'Spices',
                          'Condiments', 'Canned', 'Frozen', 'Bakery',
                          'Beverages', 'Snacks', 'Other')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert category values back to titlecase
    op.execute("""
        UPDATE "pantry--ingredient"
        SET category = CASE
            WHEN category = 'dairy' THEN 'Dairy'
            WHEN category = 'meat' THEN 'Meat'
            WHEN category = 'produce' THEN 'Produce'
            WHEN category = 'grains' THEN 'Grains'
            WHEN category = 'spices' THEN 'Spices'
            WHEN category = 'condiments' THEN 'Condiments'
            WHEN category = 'canned' THEN 'Canned'
            WHEN category = 'frozen' THEN 'Frozen'
            WHEN category = 'bakery' THEN 'Bakery'
            WHEN category = 'beverages' THEN 'Beverages'
            WHEN category = 'snacks' THEN 'Snacks'
            WHEN category = 'other' THEN 'Other'
        END
        WHERE category IN ('dairy', 'meat', 'produce', 'grains', 'spices',
                          'condiments', 'canned', 'frozen', 'bakery',
                          'beverages', 'snacks', 'other')
    """)
