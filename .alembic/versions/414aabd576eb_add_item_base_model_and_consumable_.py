"""Add Item base model and Consumable model with joined table inheritance

Revision ID: 414aabd576eb
Revises: fca8a2cd3e28
Create Date: 2026-02-11 19:02:35.357605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '414aabd576eb'
down_revision: Union[str, Sequence[str], None] = 'fca8a2cd3e28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the base item table
    op.create_table('pantry--item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('needed', sa.Boolean(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )

    # Migrate existing ingredient data to the item table
    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO "pantry--item" (id, name, needed, type)
        SELECT id, name, needed, 'ingredient' FROM "pantry--ingredient"
    """))

    # Recreate pantry--ingredient table using batch mode (required for SQLite)
    with op.batch_alter_table('pantry--ingredient', schema=None, recreate='always') as batch_op:
        batch_op.drop_column('name')
        batch_op.drop_column('needed')
        batch_op.create_foreign_key('fk_ingredient_item', 'pantry--item', ['id'], ['id'])

    # Create the consumable table
    op.create_table('pantry--consumable',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category', sa.Enum('CLEANING', 'PAPER_PRODUCTS', 'PERSONAL_CARE', 'KITCHEN_SUPPLIES', 'BATHROOM_SUPPLIES', 'OTHER', name='consumablecategory'), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['pantry--item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Drop unused table if it exists
    connection.execute(sa.text('DROP TABLE IF EXISTS "second_thought--justification"'))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Restore data from item table back to ingredient table
    connection = op.get_bind()

    # Add columns back to ingredient table using batch mode
    with op.batch_alter_table('pantry--ingredient', schema=None, recreate='always') as batch_op:
        batch_op.drop_constraint('fk_ingredient_item', type_='foreignkey')
        batch_op.add_column(sa.Column('name', sa.VARCHAR(), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('needed', sa.BOOLEAN(), nullable=False, server_default='0'))

    # Migrate data back from item table
    connection.execute(sa.text("""
        UPDATE "pantry--ingredient"
        SET name = (SELECT name FROM "pantry--item" WHERE "pantry--item".id = "pantry--ingredient".id),
            needed = (SELECT needed FROM "pantry--item" WHERE "pantry--item".id = "pantry--ingredient".id)
    """))

    # Recreate second_thought table
    op.create_table('second_thought--justification',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('ts', sa.DATETIME(), nullable=False),
    sa.Column('domain', sa.VARCHAR(), nullable=False),
    sa.Column('url', sa.VARCHAR(), nullable=False),
    sa.Column('reason', sa.VARCHAR(), nullable=False),
    sa.Column('duration', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    # Drop new tables
    op.drop_table('pantry--consumable')
    op.drop_table('pantry--item')
    # ### end Alembic commands ###
