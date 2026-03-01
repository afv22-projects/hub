"""pantry_uuid_primary_keys

Revision ID: e8a1b2c3d4f5
Revises: d4b1a2c3e5f7
Create Date: 2026-03-01 16:00:00.000000

Migrates pantry tables from INTEGER to UUID (String) primary keys.
Only affects pantry tables - reflect and second_thought tables are unchanged.
"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8a1b2c3d4f5'
down_revision: Union[str, Sequence[str], None] = 'd4b1a2c3e5f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migrate pantry tables from INTEGER to UUID primary keys."""
    connection = op.get_bind()

    # Step 1: Export existing data
    items = connection.execute(sa.text('SELECT id, name, needed, type FROM "pantry--item"')).fetchall()
    ingredients = connection.execute(sa.text('SELECT id, category FROM "pantry--ingredient"')).fetchall()
    consumables = connection.execute(sa.text('SELECT id, category FROM "pantry--consumable"')).fetchall()
    recipes = connection.execute(sa.text('SELECT id, name, notes, sources, tags FROM "pantry--recipe"')).fetchall()
    assocs = connection.execute(sa.text('SELECT recipe_id, ingredient_id FROM "pantry--recipe_ingredient_assoc"')).fetchall()

    # Step 2: Create ID mappings (old int -> new UUID)
    item_id_map = {row[0]: str(uuid.uuid4()) for row in items}
    recipe_id_map = {row[0]: str(uuid.uuid4()) for row in recipes}

    # Step 3: Drop tables in correct order (respecting FK constraints)
    op.drop_table('pantry--recipe_ingredient_assoc')
    op.drop_table('pantry--ingredient')
    op.drop_table('pantry--consumable')
    op.drop_table('pantry--item')
    op.drop_table('pantry--recipe')

    # Step 4: Recreate tables with String (UUID) primary keys
    op.create_table('pantry--item',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('needed', sa.Boolean(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table('pantry--recipe',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('notes', sa.String(), nullable=False),
        sa.Column('sources', sa.JSON(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('pantry--ingredient',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('category', sa.Enum('DAIRY', 'MEAT', 'PRODUCE', 'GRAINS', 'SPICES', 'CONDIMENTS', 'CANNED', 'FROZEN', 'BAKERY', 'BEVERAGES', 'SNACKS', 'OTHER', name='ingredientcategory'), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['pantry--item.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('pantry--consumable',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('category', sa.Enum('CLEANING', 'PAPER_PRODUCTS', 'PERSONAL_CARE', 'KITCHEN_SUPPLIES', 'BATHROOM_SUPPLIES', 'OTHER', name='consumablecategory'), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['pantry--item.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('pantry--recipe_ingredient_assoc',
        sa.Column('recipe_id', sa.String(), nullable=True),
        sa.Column('ingredient_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['ingredient_id'], ['pantry--ingredient.id'], ),
        sa.ForeignKeyConstraint(['recipe_id'], ['pantry--recipe.id'], ),
        sa.UniqueConstraint('recipe_id', 'ingredient_id', name='uq_recipe_ingredient')
    )

    # Step 5: Re-import data with new UUIDs
    for row in items:
        old_id, name, needed, item_type = row
        new_id = item_id_map[old_id]
        connection.execute(
            sa.text('INSERT INTO "pantry--item" (id, name, needed, type) VALUES (:id, :name, :needed, :type)'),
            {"id": new_id, "name": name, "needed": needed, "type": item_type}
        )

    for row in recipes:
        old_id, name, notes, sources, tags = row
        new_id = recipe_id_map[old_id]
        connection.execute(
            sa.text('INSERT INTO "pantry--recipe" (id, name, notes, sources, tags) VALUES (:id, :name, :notes, :sources, :tags)'),
            {"id": new_id, "name": name, "notes": notes, "sources": sources, "tags": tags}
        )

    for row in ingredients:
        old_id, category = row
        new_id = item_id_map[old_id]
        connection.execute(
            sa.text('INSERT INTO "pantry--ingredient" (id, category) VALUES (:id, :category)'),
            {"id": new_id, "category": category}
        )

    for row in consumables:
        old_id, category = row
        new_id = item_id_map[old_id]
        connection.execute(
            sa.text('INSERT INTO "pantry--consumable" (id, category) VALUES (:id, :category)'),
            {"id": new_id, "category": category}
        )

    for row in assocs:
        old_recipe_id, old_ingredient_id = row
        new_recipe_id = recipe_id_map[old_recipe_id]
        new_ingredient_id = item_id_map[old_ingredient_id]
        connection.execute(
            sa.text('INSERT INTO "pantry--recipe_ingredient_assoc" (recipe_id, ingredient_id) VALUES (:recipe_id, :ingredient_id)'),
            {"recipe_id": new_recipe_id, "ingredient_id": new_ingredient_id}
        )


def downgrade() -> None:
    """Revert pantry tables back to INTEGER primary keys."""
    connection = op.get_bind()

    # Step 1: Export current UUID data
    items = connection.execute(sa.text('SELECT id, name, needed, type FROM "pantry--item"')).fetchall()
    ingredients = connection.execute(sa.text('SELECT id, category FROM "pantry--ingredient"')).fetchall()
    consumables = connection.execute(sa.text('SELECT id, category FROM "pantry--consumable"')).fetchall()
    recipes = connection.execute(sa.text('SELECT id, name, notes, sources, tags FROM "pantry--recipe"')).fetchall()
    assocs = connection.execute(sa.text('SELECT recipe_id, ingredient_id FROM "pantry--recipe_ingredient_assoc"')).fetchall()

    # Step 2: Create ID mappings (UUID -> new int)
    item_id_map = {row[0]: idx + 1 for idx, row in enumerate(items)}
    recipe_id_map = {row[0]: idx + 1 for idx, row in enumerate(recipes)}

    # Step 3: Drop tables
    op.drop_table('pantry--recipe_ingredient_assoc')
    op.drop_table('pantry--ingredient')
    op.drop_table('pantry--consumable')
    op.drop_table('pantry--item')
    op.drop_table('pantry--recipe')

    # Step 4: Recreate tables with INTEGER primary keys
    op.create_table('pantry--item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('needed', sa.Boolean(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table('pantry--recipe',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('notes', sa.String(), nullable=False),
        sa.Column('sources', sa.JSON(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('pantry--ingredient',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.Enum('DAIRY', 'MEAT', 'PRODUCE', 'GRAINS', 'SPICES', 'CONDIMENTS', 'CANNED', 'FROZEN', 'BAKERY', 'BEVERAGES', 'SNACKS', 'OTHER', name='ingredientcategory'), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['pantry--item.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('pantry--consumable',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.Enum('CLEANING', 'PAPER_PRODUCTS', 'PERSONAL_CARE', 'KITCHEN_SUPPLIES', 'BATHROOM_SUPPLIES', 'OTHER', name='consumablecategory'), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['pantry--item.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('pantry--recipe_ingredient_assoc',
        sa.Column('recipe_id', sa.Integer(), nullable=True),
        sa.Column('ingredient_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['ingredient_id'], ['pantry--ingredient.id'], ),
        sa.ForeignKeyConstraint(['recipe_id'], ['pantry--recipe.id'], ),
        sa.UniqueConstraint('recipe_id', 'ingredient_id', name='uq_recipe_ingredient')
    )

    # Step 5: Re-import data with integer IDs
    for row in items:
        uuid_id, name, needed, item_type = row
        new_id = item_id_map[uuid_id]
        connection.execute(
            sa.text('INSERT INTO "pantry--item" (id, name, needed, type) VALUES (:id, :name, :needed, :type)'),
            {"id": new_id, "name": name, "needed": needed, "type": item_type}
        )

    for row in recipes:
        uuid_id, name, notes, sources, tags = row
        new_id = recipe_id_map[uuid_id]
        connection.execute(
            sa.text('INSERT INTO "pantry--recipe" (id, name, notes, sources, tags) VALUES (:id, :name, :notes, :sources, :tags)'),
            {"id": new_id, "name": name, "notes": notes, "sources": sources, "tags": tags}
        )

    for row in ingredients:
        uuid_id, category = row
        new_id = item_id_map[uuid_id]
        connection.execute(
            sa.text('INSERT INTO "pantry--ingredient" (id, category) VALUES (:id, :category)'),
            {"id": new_id, "category": category}
        )

    for row in consumables:
        uuid_id, category = row
        new_id = item_id_map[uuid_id]
        connection.execute(
            sa.text('INSERT INTO "pantry--consumable" (id, category) VALUES (:id, :category)'),
            {"id": new_id, "category": category}
        )

    for row in assocs:
        uuid_recipe_id, uuid_ingredient_id = row
        new_recipe_id = recipe_id_map[uuid_recipe_id]
        new_ingredient_id = item_id_map[uuid_ingredient_id]
        connection.execute(
            sa.text('INSERT INTO "pantry--recipe_ingredient_assoc" (recipe_id, ingredient_id) VALUES (:recipe_id, :ingredient_id)'),
            {"recipe_id": new_recipe_id, "ingredient_id": new_ingredient_id}
        )
