# Pantry Module: Int → UUID Primary Key Migration Plan

## Overview

This document outlines the plan to migrate all pantry module tables from integer primary keys to UUIDs.

### Important: Multi-App Database

This SQLite database is shared by multiple apps:
- **Pantry** - ingredients, consumables, recipes
- **Reflect** - goals, weekly check-ins, monthly reviews
- **Second Thought** - justification logs

The migration **only affects pantry tables**. All other tables (reflect, second_thought, transaction) remain untouched.

---

## Migration Strategy

The migration is handled entirely within a single Alembic migration file that:
1. Exports existing pantry data
2. Drops and recreates pantry tables with String (UUID) primary keys
3. Re-imports data with new UUIDs

**Migration file:** `.alembic/versions/e8a1b2c3d4f5_pantry_uuid_primary_keys.py`

This approach:
- Avoids complex Alembic batch operations on inheritance hierarchies
- Preserves data with automatic UUID generation and FK remapping
- Keeps migration history intact (chains from `d4b1a2c3e5f7`)
- Leaves non-pantry tables completely untouched

---

## Current Schema

```
pantry--item (base table)
├── id: Integer (PK)
├── name: String (unique)
├── needed: Boolean
└── type: String (discriminator)

pantry--ingredient (joined inheritance)
├── id: Integer (PK, FK → pantry--item.id)
└── category: Enum

pantry--consumable (joined inheritance)
├── id: Integer (PK, FK → pantry--item.id)
└── category: Enum

pantry--recipe (independent)
├── id: Integer (PK)
├── name: String
├── notes: String
├── sources: JSON
└── tags: JSON

pantry--recipe_ingredient_assoc (junction table)
├── recipe_id: Integer (FK → pantry--recipe.id)
├── ingredient_id: Integer (FK → pantry--ingredient.id)
└── UNIQUE(recipe_id, ingredient_id)
```

---

## Target Schema

```
pantry--item (base table)
├── id: String/UUID (PK)      ← Changed
├── name: String (unique)
├── needed: Boolean
└── type: String (discriminator)

pantry--ingredient (joined inheritance)
├── id: String/UUID (PK, FK)  ← Changed
└── category: Enum

pantry--consumable (joined inheritance)
├── id: String/UUID (PK, FK)  ← Changed
└── category: Enum

pantry--recipe (independent)
├── id: String/UUID (PK)      ← Changed
├── name: String
├── notes: String
├── sources: JSON
└── tags: JSON

pantry--recipe_ingredient_assoc (junction table)
├── recipe_id: String/UUID (FK)      ← Changed
├── ingredient_id: String/UUID (FK)  ← Changed
└── UNIQUE(recipe_id, ingredient_id)
```

---

## Pre-Migration: Update Model Definitions

Before running the migration, ensure the SQLAlchemy models are updated:

### DBItem (`db/pantry/item.py`)

```python
id: Mapped[str] = mapped_column(
    String,
    primary_key=True,
    default=lambda: str(uuid.uuid4())
)
```

### DBIngredient (`db/pantry/ingredient.py`)

```python
id: Mapped[str] = mapped_column(ForeignKey("pantry--item.id"), primary_key=True)
```

### DBConsumable (`db/pantry/consumable.py`)

```python
id: Mapped[str] = mapped_column(ForeignKey("pantry--item.id"), primary_key=True)
```

### DBRecipe (`db/pantry/recipe.py`)

```python
id: Mapped[str] = mapped_column(
    String, primary_key=True, default=lambda: str(uuid.uuid4())
)
```

### Association Table (`db/pantry/recipe_ingredient_assoc.py`)

```python
Column("recipe_id", String, ForeignKey("pantry--recipe.id")),
Column("ingredient_id", String, ForeignKey("pantry--ingredient.id")),
```

### Pydantic Schemas (`schemas/pantry/*.py`)

Update ID field types from `int` to `str`.

---

## Running the Migration

### 1. Backup Database

```bash
cp app.db app.db.backup.$(date +%Y%m%d_%H%M%S)
```

### 2. Run Migration

```bash
alembic upgrade head
```

### 3. Verify Schema

```bash
sqlite3 app.db ".schema 'pantry--item'"
# Should show: id TEXT PRIMARY KEY (or VARCHAR)
```

### 4. Verify Data

```bash
sqlite3 app.db <<EOF
SELECT COUNT(*) as items FROM "pantry--item";
SELECT COUNT(*) as ingredients FROM "pantry--ingredient";
SELECT COUNT(*) as consumables FROM "pantry--consumable";
SELECT COUNT(*) as recipes FROM "pantry--recipe";
SELECT COUNT(*) as associations FROM "pantry--recipe_ingredient_assoc";
EOF
```

---

## Post-Migration Validation

### Test ORM Operations

```python
from db import get_db
from db.pantry import DBIngredient, DBRecipe

with next(get_db()) as db:
    # Test reading
    ingredients = db.query(DBIngredient).all()
    print(f"Found {len(ingredients)} ingredients")

    # Test polymorphism
    for ing in ingredients[:3]:
        print(f"  {ing.name} (id: {ing.id}, type: {type(ing).__name__})")

    # Test relationships
    recipes = db.query(DBRecipe).all()
    for recipe in recipes[:3]:
        print(f"Recipe: {recipe.name}, ingredients: {len(recipe.ingredients)}")
```

### Test API Endpoints

- GET all ingredients/consumables/recipes
- GET single item by UUID
- Create new items (should auto-generate UUIDs)
- Update existing items
- Test recipe-ingredient associations

---

## Rollback Plan

### Using Alembic Downgrade

```bash
alembic downgrade d4b1a2c3e5f7
```

The migration includes a full downgrade path that converts UUIDs back to integers.

### Using Database Backup

```bash
cp app.db.backup.TIMESTAMP app.db
```

---

## Checklist

- [x] **Pre-Migration**
  - [x] Update `DBItem.id` to String with UUID default
  - [x] Update `DBIngredient.id` type
  - [x] Update `DBConsumable.id` type
  - [x] Update `DBRecipe.id` to String with UUID default
  - [x] Update `recipe_ingredient_assoc` column types
  - [x] Update Pydantic schemas (int → str)

- [x] **Migration**
  - [x] Backup database
  - [x] Run `alembic upgrade head`
  - [x] Verify schema changes
  - [x] Verify row counts match

- [x] **Validation**
  - [x] Test ORM queries
  - [x] Test polymorphic inheritance
  - [x] Test relationships (recipe ↔ ingredients)
  - [x] Test API endpoints
  - [x] Create new items (verify UUID generation)

---

## Files Modified

| File | Changes |
|------|---------|
| `db/pantry/item.py` | `id`: Integer → String (UUID) |
| `db/pantry/ingredient.py` | `id`: Integer → String |
| `db/pantry/consumable.py` | `id`: Integer → String |
| `db/pantry/recipe.py` | `id`: Integer → String (UUID), `ingredient_ids` return type |
| `db/pantry/recipe_ingredient_assoc.py` | Column types: Integer → String |
| `schemas/pantry/*.py` | ID field types: int → str |
| `.alembic/versions/e8a1b2c3d4f5_pantry_uuid_primary_keys.py` | New migration file |

---

## Notes

- The `type` discriminator column in `pantry--item` remains unchanged (still String)
- Existing unique constraint on `name` is unaffected
- The `needed` boolean field is unaffected
- JSON fields (`sources`, `tags`) are unaffected
- Enum fields (`category`) are unaffected
- Non-pantry tables (reflect--, second_thought--, transaction) are untouched
