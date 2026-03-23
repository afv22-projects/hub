"""
Migration script: Pantry v1 (SQLAlchemy) -> Pantry v2 (mdorm)

This script migrates data from the original SQLAlchemy-based Pantry database
to the new markdown-based Pantry v2 system.

Usage:
    uv run python scripts/migrate_pantry_v1_to_v2.py [OPTIONS]

Options:
    --dry-run        Preview changes without writing to disk
    --v1-db-uri      SQLite URI for v1 SQLAlchemy database (default: sqlite:///data/app.db)
    --models-dir     Directory for markdown model files (default: data/pantry)
    --db-url         SQLite URL for mdorm cache (default: sqlite:///data/pantry.db)
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hub.db import init_db as init_sqlalchemy_db, get_db as get_sqlalchemy_db
from hub.db.pantry import DBIngredient, DBConsumable, DBRecipe
from hub.pantry_v2 import init_db as init_mdorm_db, get_db as get_mdorm_db
from hub.pantry_v2.models import Ingredient, Consumable, Recipe


def migrate_ingredients(sqlalchemy_session, mdorm_db, dry_run: bool = False) -> int:
    """Migrate all ingredients from SQLAlchemy to mdorm."""
    ingredients = sqlalchemy_session.query(DBIngredient).all()
    count = 0

    for db_ingredient in ingredients:
        ingredient = Ingredient(
            title=db_ingredient.name,
            category=db_ingredient.category,
            needed=db_ingredient.needed,
        )

        if dry_run:
            print(f"  [DRY RUN] Would create ingredient: {ingredient.title}")
            print(f"    - category: {ingredient.category.value}")
            print(f"    - needed: {ingredient.needed}")
        else:
            # Check if already exists
            existing = mdorm_db.get_or_none(Ingredient, ingredient.title)
            if existing:
                print(f"  [SKIP] Ingredient already exists: {ingredient.title}")
                continue

            mdorm_db.create(ingredient)
            print(f"  [OK] Created ingredient: {ingredient.title}")

        count += 1

    return count


def migrate_consumables(sqlalchemy_session, mdorm_db, dry_run: bool = False) -> int:
    """Migrate all consumables from SQLAlchemy to mdorm."""
    consumables = sqlalchemy_session.query(DBConsumable).all()
    count = 0

    for db_consumable in consumables:
        consumable = Consumable(
            title=db_consumable.name,
            category=db_consumable.category,
            needed=db_consumable.needed,
        )

        if dry_run:
            print(f"  [DRY RUN] Would create consumable: {consumable.title}")
            print(f"    - category: {consumable.category.value}")
            print(f"    - needed: {consumable.needed}")
        else:
            # Check if already exists
            existing = mdorm_db.get_or_none(Consumable, consumable.title)
            if existing:
                print(f"  [SKIP] Consumable already exists: {consumable.title}")
                continue

            mdorm_db.create(consumable)
            print(f"  [OK] Created consumable: {consumable.title}")

        count += 1

    return count


def migrate_recipes(sqlalchemy_session, mdorm_db, dry_run: bool = False) -> int:
    """Migrate all recipes from SQLAlchemy to mdorm."""
    recipes = sqlalchemy_session.query(DBRecipe).all()
    count = 0

    for db_recipe in recipes:
        # Get ingredient names from the relationship
        ingredient_names = [ing.name for ing in db_recipe.ingredients]

        recipe = Recipe(
            title=db_recipe.name,
            labels=db_recipe.tags or [],
            ingredients=ingredient_names,
            notes=db_recipe.notes or "",
            sources=db_recipe.sources or [],
        )

        if dry_run:
            print(f"  [DRY RUN] Would create recipe: {recipe.title}")
            print(f"    - labels: {recipe.labels}")
            print(f"    - ingredients: {recipe.ingredients}")
            print(
                f"    - notes: {recipe.notes[:50]}..."
                if len(recipe.notes) > 50
                else f"    - notes: {recipe.notes}"
            )
            print(f"    - sources: {recipe.sources}")
        else:
            # Check if already exists
            existing = mdorm_db.get_or_none(Recipe, recipe.title)
            if existing:
                print(f"  [SKIP] Recipe already exists: {recipe.title}")
                continue

            mdorm_db.create(recipe)
            print(f"  [OK] Created recipe: {recipe.title}")

        count += 1

    return count


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Pantry data from v1 (SQLAlchemy) to v2 (mdorm)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to disk",
    )
    parser.add_argument(
        "--v1-db-uri",
        type=str,
        default="sqlite:///data/app.db",
        help="SQLite URI for v1 SQLAlchemy database (default: sqlite:///data/app.db)",
    )
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=Path("data/pantry"),
        help="Directory for markdown model files (default: data/pantry)",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default="sqlite:///data/pantry.db",
        help="SQLite URL for mdorm cache (default: sqlite:///data/pantry.db)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Pantry Migration: v1 (SQLAlchemy) -> v2 (mdorm)")
    print("=" * 60)

    if args.dry_run:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")

    # Initialize databases
    print("Initializing databases...")
    print(f"  v1 DB URI: {args.v1_db_uri}")
    print(f"  Models dir: {args.models_dir}")
    print(f"  DB URL: {args.db_url}")
    init_sqlalchemy_db(args.v1_db_uri)
    init_mdorm_db(models_dir=args.models_dir, db_url=args.db_url)

    # Get database sessions/instances
    sqlalchemy_gen = get_sqlalchemy_db()
    sqlalchemy_session = next(sqlalchemy_gen)
    mdorm_db = get_mdorm_db()

    try:
        # Migrate ingredients first (recipes depend on them)
        print("\n--- Migrating Ingredients ---")
        ing_count = migrate_ingredients(sqlalchemy_session, mdorm_db, args.dry_run)
        print(f"Ingredients processed: {ing_count}")

        # Migrate consumables
        print("\n--- Migrating Consumables ---")
        cons_count = migrate_consumables(sqlalchemy_session, mdorm_db, args.dry_run)
        print(f"Consumables processed: {cons_count}")

        # Migrate recipes (after ingredients so relationships work)
        print("\n--- Migrating Recipes ---")
        recipe_count = migrate_recipes(sqlalchemy_session, mdorm_db, args.dry_run)
        print(f"Recipes processed: {recipe_count}")

        # Summary
        print("\n" + "=" * 60)
        print("Migration Summary")
        print("=" * 60)
        print(f"  Ingredients: {ing_count}")
        print(f"  Consumables: {cons_count}")
        print(f"  Recipes:     {recipe_count}")
        print(f"  Total:       {ing_count + cons_count + recipe_count}")

        if args.dry_run:
            print("\n*** DRY RUN COMPLETE - Run without --dry-run to apply changes ***")
        else:
            print("\n*** Migration complete! ***")

    finally:
        # Clean up SQLAlchemy session
        try:
            next(sqlalchemy_gen)
        except StopIteration:
            pass


if __name__ == "__main__":
    main()
