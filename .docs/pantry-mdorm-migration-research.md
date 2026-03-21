# Pantry to mdorm Migration Research Report

## Executive Summary

This report analyzes the feasibility of migrating the pantry module from SQLAlchemy to mdorm. The pantry module is a food/recipe management system with complex relationships and inheritance patterns. mdorm is a lightweight markdown-based ORM with Pydantic integration.

**Key Finding:** mdorm currently supports ~60% of the features needed for pantry. With EnumSpec and ListSpec now complete, the main remaining gaps are filtering/querying, bidirectional many-to-many sync, and unique constraints.

---

## 1. Pantry Module Overview

### Purpose

The pantry module manages:

- **Ingredients**: Food items used in recipes (with categories)
- **Consumables**: Non-food household items (cleaning supplies, etc.)
- **Recipes**: Collections of ingredients with metadata (notes, sources, tags)

### Current Architecture

```
DBBase (Abstract base with UUID primary key)
  └── DBItem (Polymorphic base for pantry items)
      ├── DBConsumable
      └── DBIngredient
  └── DBRecipe
```

### Key Files

| Location                  | Purpose                                 |
| ------------------------- | --------------------------------------- |
| `src/hub/db/pantry/`      | SQLAlchemy models (5 files)             |
| `src/hub/routes/pantry/`  | FastAPI endpoints (29 total operations) |
| `src/hub/schemas/pantry/` | Pydantic schemas for API                |

---

## 2. Required Capabilities Analysis

### 2.1 Model Features

| Feature                 | Pantry Usage                        | mdorm Support               | Gap                 |
| ----------------------- | ----------------------------------- | --------------------------- | ------------------- |
| UUID primary keys       | All models use UUID PKs             | Uses `title` (string) as PK | Intentional design  |
| Unique constraints      | `name` field on items               | Not supported               | **Needs work**      |
| Enum fields             | `category` on Consumable/Ingredient | `EnumSpec`                  | ✅ Supported        |
| Boolean fields          | `needed` on DBItem                  | `BooleanSpec`               | ✅ Supported        |
| String fields           | `name`, `notes`                     | `StringSpec`                | ✅ Supported        |
| JSON/List fields        | `sources`, `tags` on Recipe         | `ListSpec`                  | ✅ Supported        |
| Polymorphic inheritance | DBItem → DBConsumable/DBIngredient  | Not supported               | Nice to have (skip) |

### 2.2 Relationship Features

| Feature                | Pantry Usage                               | mdorm Support            | Gap            |
| ---------------------- | ------------------------------------------ | ------------------------ | -------------- |
| Many-to-Many           | Recipe ↔ Ingredient                        | Not supported            | **Needs work** |
| Association tables     | `recipe_ingredient_assoc`                  | Not supported            | **Needs work** |
| Back-references        | `ingredient.recipes`, `recipe.ingredients` | `RelationToOneSpec` only | **Needs work** |
| Relationship traversal | `db_ingredient.recipes`                    | Not supported            | **Needs work** |

### 2.3 Query Features

| Feature                | Pantry Usage                  | mdorm Support          | Gap            |
| ---------------------- | ----------------------------- | ---------------------- | -------------- |
| Get by ID              | `db.get(Model, id)`           | `db.get(Model, title)` | Supported      |
| Get all                | `db.query(Model).all()`       | `db.all(Model)`        | Supported      |
| Filter by field        | `filter(Model.name == value)` | Not supported          | **Needs work** |
| Filter by relationship | `filter_by(name=name)`        | Not supported          | **Needs work** |
| `one_or_none()`        | Recipe/Ingredient lookups     | `get_or_none()`        | Supported      |

### 2.4 CRUD Operations

| Operation               | Pantry Usage                  | mdorm Support          | Gap            |
| ----------------------- | ----------------------------- | ---------------------- | -------------- |
| Create                  | `db.add()` + `db.commit()`    | `db.create()`          | Supported      |
| Read                    | `db.get()`, `db.query()`      | `db.get()`, `db.all()` | Partial        |
| Update                  | Modify + `db.commit()`        | `db.update()`          | Supported      |
| Delete                  | `db.delete()` + `db.commit()` | `db.delete()`          | Supported      |
| Upsert                  | Manual check + create/update  | `update()` is upsert   | API cleanup    |
| IntegrityError handling | Duplicate name detection      | Not supported          | **Needs work** |

### 2.5 Advanced Features

| Feature               | Pantry Usage         | mdorm Support        | Gap            |
| --------------------- | -------------------- | -------------------- | -------------- |
| Transactions          | Implicit via session | Basic SQLite commits | Partial        |
| Cascade deletes       | Relationship cleanup | Not supported        | Not needed     |
| Cascade title updates | N/A (UUID-based)     | Not supported        | **Needs work** |
| Validation            | Pydantic schemas     | Pydantic-based       | ✅ Supported   |

---

## 3. Detailed Gap Analysis

### 3.1 Critical Gaps (Must Build)

#### 1. Many-to-Many Relationships (Bidirectional Sync)

**Current pantry usage:**

```python
# Association table
recipe_ingredient_assoc = Table(
    "pantry--recipe_ingredient_assoc",
    Column("recipe_id", ForeignKey("pantry--recipe.id")),
    Column("ingredient_id", ForeignKey("pantry--ingredient.id")),
)

# Relationship definitions
class DBIngredient:
    recipes: Mapped[list["DBRecipe"]] = relationship(back_populates="ingredients")

class DBRecipe:
    ingredients: Mapped[list["DBIngredient"]] = relationship(back_populates="recipes")
```

**mdorm status:** Has `RelationToManySpec` for one-to-many relationships. For true many-to-many, needs:

- **Bidirectional sync**: When Recipe A is added to Ingredient X's `recipes`, Ingredient X should auto-appear in Recipe A's `ingredients`
- Automatic back-reference population on read

#### 2. Filtering/Querying

**Current pantry usage:**

```python
db.query(DBIngredient).filter(DBIngredient.name == name).first()
db.query(DBRecipe).filter_by(name=name).one_or_none()
```

**mdorm gap:** Only supports key-based lookups. Needs:

- `db.filter(Model, field=value)` or similar API
- Index support for efficient filtering
- Compound filters (AND/OR)

#### 3. ✅ Enum Field Support (Completed)

**Current pantry usage:**

```python
class DBConsumable(DBItem):
    category: Mapped[ConsumableCategory] = mapped_column(Enum(ConsumableCategory))
```

**mdorm support:** `EnumSpec(EnumClass)` field type with serialization to/from string in frontmatter and validation against enum values.

#### 4. ✅ List/JSON Fields (Completed)

**Current pantry usage:**

```python
class DBRecipe:
    sources: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[list] = mapped_column(JSON, default=list)
```

**mdorm support:** `ListSpec()` for simple string lists with YAML list serialization in frontmatter.

#### 5. Unique Constraints

**Current pantry usage:**

```python
class DBItem:
    name: Mapped[str] = mapped_column(String, unique=True)
```

**mdorm gap:** No constraint validation. Needs:

- Unique field validation on create/update
- `UniqueConstraint` decorator or field option
- Appropriate error raising

### 3.2 Moderate Gaps (Should Build)

#### 6. Polymorphic Inheritance (Nice to Have)

**Current pantry usage:**

```python
class DBItem(DBBase):
    __mapper_args__ = {"polymorphic_on": "type", "polymorphic_identity": "item"}

class DBConsumable(DBItem):
    __mapper_args__ = {"polymorphic_identity": "consumable"}
```

**Decision:** At current scale, separate model classes without inheritance is acceptable. Shared fields can be duplicated across models. This is less elegant but functional and avoids complexity. Polymorphic inheritance can be revisited if mdorm becomes a production tool.

#### 7. Upsert Operations (API Cleanup Needed)

**Current pantry usage:**

```python
# PUT endpoints do create-or-update
existing = db.query(Model).filter_by(name=name).first()
if existing:
    # update
else:
    # create
```

**mdorm status:** The `update()` method already behaves as upsert (writes object to file regardless of prior existence). API should be clarified to make this behavior explicit - consider renaming to `save()` or documenting upsert semantics clearly.

#### 8. UUID vs Title as Primary Key (Intentional Design)

**Current pantry usage:** All models use UUID primary keys.
**mdorm design:** Uses `title` (filename) as primary key.

**Decision:** Using title as primary key is an intentional design choice for mdorm. This provides human-readable file organization and simpler mental model. Migration will require frontend updates to work with title-based keys instead of UUIDs.

### 3.3 Minor Gaps (Nice to Have)

#### 9. Cascade Title Updates

When an ingredient's title (primary key) changes, references in related recipes become stale. mdorm should support cascading title updates to maintain referential integrity.

**Implementation options:**

- Hook into rename/update operations to find and update all references
- Store references by title and update related files when title changes
- Provide a `rename()` method that handles cascade updates

#### 10. Integrity Error Handling

Graceful handling of constraint violations with specific error types.

---

## 4. What mdorm Already Supports

| Feature              | Notes                                                |
| -------------------- | ---------------------------------------------------- |
| Pydantic integration | Models extend `BaseModel`                            |
| File-based storage   | Human-readable markdown files                        |
| SQLite caching       | Fast queries with mtime invalidation                 |
| Basic CRUD           | `create()`, `get()`, `update()`, `delete()`, `all()` |
| Boolean fields       | `BooleanSpec()`                                      |
| Integer fields       | `IntegerSpec()`                                      |
| String fields        | `StringSpec(max_length=...)`                         |
| Enum fields          | `EnumSpec(EnumClass)`                                |
| List fields          | `ListSpec()` for string lists                        |
| Section fields       | `SectionSpec()` for body content                     |
| Single relations     | `RelationToOneSpec("ModelName")`                     |
| Many relations       | `RelationToManySpec("ModelName")`                    |
| Model registration   | Auto-registration via metaclass                      |
| Lazy loading         | `MDorm(path, lazy_load=True)`                        |

---

## 5. Implementation Roadmap

### Phase 1: Core Field Types (Required)

1. **✅ EnumSpec** - Enum field support with validation
2. **✅ ListSpec** - Simple list storage in frontmatter
3. **✅ Filtering** - `db.filter(Model, **kwargs)` for field-based queries

### Phase 2: Relationships (Required)

4. **RelationToManySpec improvements** - Bidirectional many-to-many
5. **Back-reference population** - Auto-populate reverse relations
6. **Association storage** - Decide on storage format

### Phase 3: Constraints & Validation (Required)

7. **✅ Unique constraints** - Field-level uniqueness validation
8. **✅ Upsert operation** - `db.upsert(obj)` method

### Phase 4: Migration Helpers (Recommended)

9. **Cascade title updates** - Update references when a model's title changes
10. **Migration scripts** - SQLite → Markdown file conversion

### Phase 5: Advanced Features (Optional)

11. **Polymorphic models** - Inheritance support (low priority at current scale)
12. **Compound filters** - AND/OR query support

---

## 6. Estimated Effort

| Phase   | Features                                  | Complexity |
| ------- | ----------------------------------------- | ---------- |
| Phase 1 | ~~EnumSpec~~, ~~ListSpec~~, ~~Filtering~~ | Medium     |
| Phase 2 | Bidirectional many-to-many sync           | High       |
| Phase 3 | Unique constraints, ~~API cleanup~~       | Low-Medium |
| Phase 4 | Cascade title updates, Migration scripts  | Medium     |
| Phase 5 | Polymorphism, Compound filters            | High       |

---

## 7. Alternative Approaches

### Option A: Full mdorm Enhancement

Build all missing features into mdorm, then migrate pantry.

- **Pros:** Clean architecture, reusable for other modules
- **Cons:** Significant development effort

### Option B: Simplified Pantry Models

Restructure pantry to avoid complex features (no inheritance, simpler relationships).

- **Pros:** Faster migration, less mdorm work
- **Cons:** May require API changes, data migration

### Option C: Hybrid Approach

Keep complex models in SQLAlchemy, migrate simple ones to mdorm.

- **Pros:** Incremental migration
- **Cons:** Two ORMs to maintain

---

## 8. Recommendations

1. **Phase 1 progress** - EnumSpec and ListSpec are complete; filtering is the remaining Phase 1 item
2. **Prototype many-to-many** - This is the most complex feature; prototype before committing
3. **Consider API changes** - Using `name` as primary key (instead of UUID) simplifies mdorm usage
4. **Write migration scripts early** - Test data conversion before building all features
5. **Migrate incrementally** - Start with Recipe (simplest), then Ingredient, then Consumable

---

## Appendix A: Current Pantry Models

### DBItem (Base)

```python
class DBItem(DBBase):
    __tablename__ = "pantry--item"
    name: Mapped[str] = mapped_column(String, unique=True)
    needed: Mapped[bool] = mapped_column(Boolean, default=False)
    type: Mapped[str] = mapped_column(String(50))
```

### DBConsumable

```python
class DBConsumable(DBItem):
    __tablename__ = "pantry--consumable"
    id: Mapped[str] = mapped_column(ForeignKey("pantry--item.id"), primary_key=True)
    category: Mapped[ConsumableCategory] = mapped_column(Enum(ConsumableCategory))
```

### DBIngredient

```python
class DBIngredient(DBItem):
    __tablename__ = "pantry--ingredient"
    id: Mapped[str] = mapped_column(ForeignKey("pantry--item.id"), primary_key=True)
    category: Mapped[IngredientCategory] = mapped_column(Enum(IngredientCategory))
    recipes: Mapped[list["DBRecipe"]] = relationship(back_populates="ingredients")
```

### DBRecipe

```python
class DBRecipe(DBBase):
    __tablename__ = "pantry--recipe"
    name: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(String)
    sources: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    ingredients: Mapped[list["DBIngredient"]] = relationship(back_populates="recipes")
```

---

## Appendix B: Proposed mdorm Models (Post-Migration)

```python
from typing import Annotated
from src.mdorm import MarkdownModel
from src.mdorm.fields import BooleanSpec, EnumSpec, ListSpec, SectionSpec, RelationToManySpec

class Consumable(MarkdownModel):
    # title = name (used as filename/PK)
    needed: Annotated[bool, BooleanSpec()] = False
    category: Annotated[ConsumableCategory, EnumSpec(ConsumableCategory)]
    content: str = ""  # unused but required

class Ingredient(MarkdownModel):
    needed: Annotated[bool, BooleanSpec()] = False
    category: Annotated[IngredientCategory, EnumSpec(IngredientCategory)]
    recipes: Annotated[list[str], RelationToManySpec("Recipe")] = []
    content: str = ""

class Recipe(MarkdownModel):
    notes: Annotated[str, SectionSpec()] = ""
    sources: Annotated[list[str], ListSpec()] = []
    tags: Annotated[list[str], ListSpec()] = []
    ingredients: Annotated[list[str], RelationToManySpec("Ingredient")] = []
    content: str = ""  # main recipe content/instructions
```
