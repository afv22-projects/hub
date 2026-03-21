# Pantry to mdorm Migration Research Report

## Executive Summary

This report analyzes the feasibility of migrating the pantry module from SQLAlchemy to mdorm. The pantry module is a food/recipe management system with complex relationships and inheritance patterns. mdorm is a lightweight markdown-based ORM with Pydantic integration.

**Key Finding:** mdorm currently supports ~40% of the features needed for pantry. Several significant features must be built before migration is feasible.

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

| Feature                 | Pantry Usage                        | mdorm Support               | Gap            |
| ----------------------- | ----------------------------------- | --------------------------- | -------------- |
| UUID primary keys       | All models use UUID PKs             | Uses `title` (string) as PK | **Needs work** |
| Unique constraints      | `name` field on items               | Not supported               | **Needs work** |
| Enum fields             | `category` on Consumable/Ingredient | Not supported               | **Needs work** |
| Boolean fields          | `needed` on DBItem                  | `BooleanSpec`               | Supported      |
| String fields           | `name`, `notes`                     | `StringSpec`                | Supported      |
| JSON/List fields        | `sources`, `tags` on Recipe         | Not supported               | **Needs work** |
| Polymorphic inheritance | DBItem → DBConsumable/DBIngredient  | Not supported               | **Needs work** |

### 2.2 Relationship Features

| Feature                | Pantry Usage                               | mdorm Support        | Gap            |
| ---------------------- | ------------------------------------------ | -------------------- | -------------- |
| Many-to-Many           | Recipe ↔ Ingredient                        | Not supported        | **Needs work** |
| Association tables     | `recipe_ingredient_assoc`                  | Not supported        | **Needs work** |
| Back-references        | `ingredient.recipes`, `recipe.ingredients` | `RelationToOneSpec` only | **Needs work** |
| Relationship traversal | `db_ingredient.recipes`                    | Not supported        | **Needs work** |

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
| Upsert                  | Manual check + create/update  | Not supported          | **Needs work** |
| IntegrityError handling | Duplicate name detection      | Not supported          | **Needs work** |

### 2.5 Advanced Features

| Feature         | Pantry Usage         | mdorm Support        | Gap            |
| --------------- | -------------------- | -------------------- | -------------- |
| Transactions    | Implicit via session | Basic SQLite commits | Partial        |
| Cascade deletes | Relationship cleanup | Not supported        | **Needs work** |
| Validation      | Pydantic schemas     | Pydantic-based       | Supported      |

---

## 3. Detailed Gap Analysis

### 3.1 Critical Gaps (Must Build)

#### 1. Many-to-Many Relationships

**AFV:** MDorm already has a one-to-many called RelationToManySpec. Is the only difference between that and a many-to-many field type the back-population?

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

**mdorm gap:** Only has `RelationToOneSpec` for single references. Needs:

- `RelationToManySpec` with bidirectional sync
- Storage format for many-to-many (inline list or separate association files)
- Automatic back-reference population

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

#### 3. Enum Field Support

**Current pantry usage:**

```python
class DBConsumable(DBItem):
    category: Mapped[ConsumableCategory] = mapped_column(Enum(ConsumableCategory))
```

**mdorm gap:** No enum field spec. Needs:

- `EnumSpec(EnumClass)` field type
- Serialization to/from string in frontmatter
- Validation against enum values

#### 4. List/JSON Fields

**Current pantry usage:**

```python
class DBRecipe:
    sources: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[list] = mapped_column(JSON, default=list)
```

**mdorm gap:** No list/JSON field support. Needs:

- `ListSpec()` for simple string lists
- Serialization format (comma-separated in frontmatter, or YAML list)

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

#### 6. Polymorphic Inheritance

**AFV:** This is a nice to have at my scale. If turning MDorm into a producion tool, it would be more necessary, but for now we can just define each model separately.

**Current pantry usage:**

```python
class DBItem(DBBase):
    __mapper_args__ = {"polymorphic_on": "type", "polymorphic_identity": "item"}

class DBConsumable(DBItem):
    __mapper_args__ = {"polymorphic_identity": "consumable"}
```

**Workaround possible:** Could use separate model classes without inheritance, duplicating shared fields. Less elegant but functional.

#### 7. Upsert Operations

**AFV:** Technically mdorm's update is an upsert since it just writes the obj passed to it to the file. I need to clean up the API here to make behavior more expected.

**Current pantry usage:**

```python
# PUT endpoints do create-or-update
existing = db.query(Model).filter_by(name=name).first()
if existing:
    # update
else:
    # create
```

**mdorm gap:** No built-in upsert. Needs:

- `db.upsert(obj)` method
- Or could be implemented at application layer

#### 8. UUID vs Title as Primary Key

**AFV:** Using the title as the key was a design decision. It will require updating the front end too to support no UUIDs, but this was intentional.

**Current pantry usage:** All models use UUID primary keys.
**mdorm design:** Uses `title` (filename) as primary key.

**Options:**

- Use name/title as PK (breaking change for API)
- Add UUID field support to mdorm
- Store UUID in frontmatter, keep title as filename

### 3.3 Minor Gaps (Nice to Have)

**AFV:** Another consideration is handling ingredient name changes. If I update the title of an ingredient, we should probably cascade that change to relevent recipes.

#### 9. Cascade Deletes

When deleting an ingredient, should it be removed from all recipes?

**AFV:** No. The core motivation of MDorm is to have persistent, human-readable files for future use.

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
| Section fields       | `SectionSpec()` for body content                     |
| Single relations     | `RelationToOneSpec("ModelName")`                         |
| Model registration   | Auto-registration via metaclass                      |
| Lazy loading         | `MDorm(path, lazy_load=True)`                        |

---

## 5. Implementation Roadmap

### Phase 1: Core Field Types (Required)

1. **EnumSpec** - Enum field support with validation
2. **ListSpec** - Simple list storage in frontmatter
3. **Filtering** - `db.filter(Model, **kwargs)` for field-based queries

### Phase 2: Relationships (Required)

4. **RelationToManySpec improvements** - Bidirectional many-to-many
5. **Back-reference population** - Auto-populate reverse relations
6. **Association storage** - Decide on storage format

### Phase 3: Constraints & Validation (Required)

7. **Unique constraints** - Field-level uniqueness validation
8. **Upsert operation** - `db.upsert(obj)` method

### Phase 4: Migration Helpers (Recommended)

9. **UUID field support** - Optional UUID primary key alongside title
10. **Migration scripts** - SQLite → Markdown file conversion

### Phase 5: Advanced Features (Optional)

11. **Polymorphic models** - Inheritance support
12. **Cascade operations** - Relationship cleanup on delete
13. **Compound filters** - AND/OR query support

---

## 6. Estimated Effort

| Phase   | Features                        | Complexity |
| ------- | ------------------------------- | ---------- |
| Phase 1 | EnumSpec, ListSpec, Filtering   | Medium     |
| Phase 2 | Many-to-many relationships      | High       |
| Phase 3 | Unique constraints, Upsert      | Low-Medium |
| Phase 4 | UUID support, Migration scripts | Medium     |
| Phase 5 | Polymorphism, Cascades          | High       |

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

1. **Start with Phase 1** - EnumSpec and ListSpec are straightforward and unblock Recipe migration
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
