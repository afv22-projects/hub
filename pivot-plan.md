# Goal Pivot Feature Implementation Plan

## Overview

This document outlines the implementation plan for adding **goal pivoting** functionality to Reflect. Pivoting allows a user to transition from one goal to a new goal while maintaining a traceable connection between them.

### What is a Pivot?

A pivot occurs when a goal's direction fundamentally changes—not just minor updates, but a significant shift in focus. The new goal should:
1. Be a distinct, new goal with its own lifecycle
2. Maintain a reference back to the original goal it pivoted from
3. Optionally carry forward context (like why the pivot happened)

---

## Current State Analysis

### Existing Goal Structure

```
DBGoal
├── id (UUID, auto-generated)
├── title
├── priority (P1, P2, P3)
├── exit_criteria
├── action_plan
├── status (ACTIVE, COMPLETED, PIVOTED, ARCHIVED)
├── created_at (ms timestamp, auto-generated)
├── month_created (YYYY-MM)
├── weekly_check_ins (relationship)
└── month_outcomes (relationship)
```

### Key Observations

1. **PIVOTED status already exists** - The `GoalStatus` enum already includes `PIVOTED`, indicating this feature was anticipated
2. **No existing goal-to-goal relationships** - Goals are currently independent entities
3. **History tracking is in place** - Using `sqlalchemy-history` for change tracking
4. **GoalOutcome enum has PIVOTED** - Month outcomes can already be marked as pivoted

---

## Implementation Plan

### Phase 1: Database Schema Changes

#### 1.1 Add Pivot Fields to DBGoal

Add two new optional fields to the `DBGoal` model:

| Field | Type | Description |
|-------|------|-------------|
| `pivoted_from_id` | `String` (FK, nullable) | Reference to the goal this was pivoted from |
| `pivot_reason` | `String` (nullable) | Explanation for why the pivot occurred |

**File:** [db/reflect/goal.py](db/reflect/goal.py)

```python
# New fields to add
pivoted_from_id: Mapped[str | None] = mapped_column(
    String,
    ForeignKey("reflect--goal.id", ondelete="SET NULL"),
    nullable=True
)
pivot_reason: Mapped[str | None] = mapped_column(String, nullable=True)

# New relationship
pivoted_from: Mapped["DBGoal | None"] = relationship(
    "DBGoal",
    remote_side=[id],
    foreign_keys=[pivoted_from_id],
    backref="pivoted_to"
)
```

**Design Decisions:**
- `ondelete="SET NULL"`: If the original goal is deleted, the pivot reference becomes null (preserves the pivoted goal)
- Self-referential relationship allows navigating both directions (pivoted_from and pivoted_to)

#### 1.2 Create Alembic Migration

**File:** `.alembic/versions/xxxx_add_goal_pivot_fields.py`

```python
def upgrade():
    op.add_column('reflect--goal', sa.Column('pivoted_from_id', sa.String(), nullable=True))
    op.add_column('reflect--goal', sa.Column('pivot_reason', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_goal_pivoted_from',
        'reflect--goal',
        'reflect--goal',
        ['pivoted_from_id'],
        ['id'],
        ondelete='SET NULL'
    )

def downgrade():
    op.drop_constraint('fk_goal_pivoted_from', 'reflect--goal', type_='foreignkey')
    op.drop_column('reflect--goal', 'pivot_reason')
    op.drop_column('reflect--goal', 'pivoted_from_id')
```

---

### Phase 2: Schema Updates

#### 2.1 Update Pydantic Schemas

**File:** [schemas/reflect/goal.py](schemas/reflect/goal.py)

```python
# New schema for pivot request
class GoalPivot(BaseModel):
    """Request body for pivoting a goal."""
    title: str
    priority: GoalPriority
    exit_criteria: str
    action_plan: str
    pivot_reason: str | None = None


# Update Goal response schema
class Goal(GoalBase):
    id: str
    status: GoalStatus
    created_at: int
    month_created: str
    pivoted_from_id: str | None = None  # NEW
    pivot_reason: str | None = None      # NEW

    model_config = ConfigDict(from_attributes=True)


# New schema for goal with pivot chain context
class GoalWithPivotChain(Goal):
    """Goal with full pivot history."""
    pivot_chain: list["GoalSummary"] = []


class GoalSummary(BaseModel):
    """Minimal goal info for pivot chains."""
    id: str
    title: str
    status: GoalStatus
    created_at: int
```

---

### Phase 3: API Endpoints

#### 3.1 Add Pivot Endpoint

**File:** [routes/reflect/goals.py](routes/reflect/goals.py)

```python
@router.post("/{goal_id}/pivot", response_model=dict)
def pivot_goal(
    goal_id: str,
    pivot_data: GoalPivot,
    db: Session = Depends(get_db)
):
    """
    Pivot an existing goal into a new goal.

    This will:
    1. Set the original goal's status to PIVOTED
    2. Create a new goal with pivoted_from_id pointing to the original
    3. Return the new goal's ID
    """
    # Get original goal
    original_goal = db.get(DBGoal, goal_id)
    if not original_goal:
        raise HTTPException(404, f"Goal not found (id: {goal_id})")

    if original_goal.status != GoalStatus.ACTIVE:
        raise HTTPException(400, "Can only pivot active goals")

    # Create new pivoted goal
    new_goal = DBGoal(
        title=pivot_data.title,
        priority=pivot_data.priority,
        exit_criteria=pivot_data.exit_criteria,
        action_plan=pivot_data.action_plan,
        status=GoalStatus.ACTIVE,
        month_created=get_current_month(),  # or inherit from original?
        pivoted_from_id=goal_id,
        pivot_reason=pivot_data.pivot_reason,
    )

    # Mark original as pivoted
    original_goal.status = GoalStatus.PIVOTED

    db.add(new_goal)
    db.commit()

    return {"id": new_goal.id, "pivoted_from_id": goal_id}
```

#### 3.2 Add Pivot Chain Endpoint

```python
@router.get("/{goal_id}/pivot-chain", response_model=list[GoalSummary])
def get_pivot_chain(goal_id: str, db: Session = Depends(get_db)):
    """
    Get the full pivot history for a goal.

    Returns all goals in the pivot chain, from the original to the current.
    """
    db_goal = db.get(DBGoal, goal_id)
    if not db_goal:
        raise HTTPException(404, f"Goal not found (id: {goal_id})")

    chain = []

    # Walk backwards to find the root
    current = db_goal
    ancestors = []
    while current.pivoted_from:
        ancestors.insert(0, current.pivoted_from)
        current = current.pivoted_from

    # Walk forwards to get descendants
    descendants = []
    to_process = [db_goal]
    while to_process:
        current = to_process.pop(0)
        for child in current.pivoted_to:
            descendants.append(child)
            to_process.append(child)

    chain = ancestors + [db_goal] + descendants
    return [GoalSummary(
        id=g.id,
        title=g.title,
        status=g.status,
        created_at=g.created_at
    ) for g in chain]
```

#### 3.3 Update Get Goal Endpoint

Optionally include pivot context in the response:

```python
@router.get("/{goal_id}", response_model=Goal)
def get_goal(
    goal_id: str,
    include_pivot_chain: bool = Query(False),
    db: Session = Depends(get_db)
):
    db_goal = db.get(DBGoal, goal_id)
    if not db_goal:
        raise HTTPException(404, f"Goal not found (id: {goal_id})")

    if include_pivot_chain:
        # Return GoalWithPivotChain instead
        ...

    return db_goal
```

---

### Phase 4: Testing

#### 4.1 Unit Tests

**File:** `tests/reflect/test_goal_pivot.py`

Test cases to implement:
1. Successfully pivot an active goal
2. Cannot pivot a non-active goal (COMPLETED, ARCHIVED, already PIVOTED)
3. Pivot chain retrieval works correctly
4. Deleting original goal sets pivoted_from_id to NULL (doesn't delete pivoted goal)
5. History includes pivot operation
6. Pivot reason is optional but stored correctly when provided

---

## API Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/goals/{id}/pivot` | Create a new goal by pivoting from existing |
| GET | `/goals/{id}/pivot-chain` | Get full pivot history for a goal |
| GET | `/goals/{id}?include_pivot_chain=true` | Get goal with pivot context |

---

## Data Model Summary

```
┌─────────────────────┐      pivoted_from_id      ┌─────────────────────┐
│      Goal A         │◄──────────────────────────│      Goal B         │
│  status: PIVOTED    │                           │  status: ACTIVE     │
│                     │                           │  pivot_reason: ...  │
└─────────────────────┘                           └─────────────────────┘
        │                                                   │
        │ pivoted_to (backref)                              │
        └───────────────────────────────────────────────────┘
```

---

## Implementation Order

1. **Database Migration** - Add new columns to goal table
2. **Model Updates** - Add fields and relationship to DBGoal
3. **Schema Updates** - Add GoalPivot, update Goal schema
4. **API Endpoints** - Implement pivot and pivot-chain endpoints
5. **Tests** - Write comprehensive test coverage

---

## Note on History Tracking

The `operation_type` field in `sqlalchemy-history` is **hardcoded** and cannot be extended with custom values:

```python
# From sqlalchemy-history source
class Operation:
    INSERT = 0
    UPDATE = 1
    DELETE = 2
```

A pivot operation will appear in history as:
- **Original goal**: An `UPDATE` operation where `status` changed to `PIVOTED`
- **New goal**: An `INSERT` operation (standard creation)

To identify pivot events in the application layer:
1. Check if a goal's history shows status changing to `PIVOTED`
2. Query for goals with `pivoted_from_id` pointing to the pivoted goal
3. Cross-reference timestamps to correlate the operations

---

## Open Questions / Decisions Needed

1. **Month inheritance**: Should the new goal inherit `month_created` from the original, or use the current month?
   - **Decision**: Use current month (pivot is a fresh start)

2. **Check-in handling**: What happens to weekly check-ins when a goal is pivoted?
   - Recommendation: Keep them with the original goal (historical record)

3. **Multiple pivots**: Can a goal be pivoted multiple times (chain of pivots)?
   - Recommendation: Yes, support chains (A → B → C)

4. **Unpivot**: Should there be an "undo pivot" feature?
   - Recommendation: Not in initial implementation; can manually delete new goal and update old goal's status

5. **Cascade behavior**: What happens to the pivot chain if a middle goal is deleted?
   - Current plan: SET NULL breaks the chain at that point
   - Alternative: Prevent deletion of goals that have been pivoted from

---

## Files to Modify

| File | Changes |
|------|---------|
| [db/reflect/goal.py](db/reflect/goal.py) | Add pivot fields and relationship |
| [schemas/reflect/goal.py](schemas/reflect/goal.py) | Add GoalPivot, GoalSummary, update Goal |
| [enums/reflect.py](enums/reflect.py) | No changes needed |
| [routes/reflect/goals.py](routes/reflect/goals.py) | Add pivot endpoints, update get_goal |
| `.alembic/versions/` | New migration file |
| `tests/reflect/` | New test file for pivot functionality |
