# Dataset Relationship Engine — Phase 1

> **Status:** Phase 1 complete (Backend & Engine)
> **Branch:** `feature/dataset-relationships-design`
> **Feature Flag:** `DATASET_RELATIONSHIPS` (default `False`)

## Overview

The Dataset Relationship Engine allows Superset users to declare explicit
relationships between datasets (tables) so that charts and dashboards can
automatically perform JOINs, cross-database merges, cross-filter propagation,
and hierarchical drill-downs.

Phase 1 delivers the **backend foundation**: database schema, ORM models,
data-access layer, business-logic commands, a dual-mode query engine, and a
REST API for full CRUD management of relationships.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    REST API Layer                        │
│  superset/dataset_relationship/api.py                   │
│  superset/dataset_relationship/schemas.py               │
├─────────────────────────────────────────────────────────┤
│                   Command Layer                         │
│  superset/commands/dataset_relationship/                │
│    ├── create.py   (CreateDatasetRelationshipCommand)   │
│    ├── update.py   (UpdateDatasetRelationshipCommand)   │
│    ├── delete.py   (DeleteDatasetRelationshipCommand)   │
│    └── exceptions.py                                    │
├─────────────────────────────────────────────────────────┤
│                     DAO Layer                           │
│  superset/daos/dataset_relationship.py                  │
│    └── DatasetRelationshipDAO                           │
├─────────────────────────────────────────────────────────┤
│                    ORM Models                           │
│  superset/models/dataset_relationships.py               │
│    ├── DatasetRelationship                              │
│    └── DatasetRelationshipColumn                        │
├─────────────────────────────────────────────────────────┤
│                   Query Engine                          │
│  superset/common/relationship_query_injector.py         │
│    └── RelationshipQueryInjector  (same-DB SQL JOINs)   │
│  superset/common/cross_database_merger.py               │
│    └── CrossDatabaseMerger        (cross-DB Pandas)     │
├─────────────────────────────────────────────────────────┤
│  Integration Points (helpers.py)                        │
│  superset/models/helpers.py                             │
│    ├── _maybe_inject_relationship_joins()               │
│    └── _maybe_apply_cross_db_merges()                   │
├─────────────────────────────────────────────────────────┤
│                   Database Schema                       │
│  migrations/…/a8b9c0d1e2f3_add_dataset_relationships.py │
│    ├── dataset_relationships                            │
│    └── dataset_relationship_columns                     │
└─────────────────────────────────────────────────────────┘
```

---

## Database Tables

### `dataset_relationships`

| Column               | Type        | Notes                                 |
|----------------------|-------------|---------------------------------------|
| `id`                 | Integer PK  | Auto-increment                        |
| `uuid`               | String(36)  | Unique identifier                     |
| `source_dataset_id`  | Integer FK  | References `tables.id` (CASCADE)      |
| `target_dataset_id`  | Integer FK  | References `tables.id` (CASCADE)      |
| `relationship_type`  | String(20)  | `one_to_one`, `one_to_many`, etc.     |
| `join_type`          | String(10)  | `INNER`, `LEFT`, `RIGHT`, `FULL`      |
| `is_cross_database`  | Boolean     | Auto-detected                         |
| `is_active`          | Boolean     | Soft enable/disable                   |
| `name`               | String(256) | Human-readable label                  |
| `description`        | Text        | Optional description                  |
| `created_on` / `changed_on` | DateTime | Audit timestamps               |
| `created_by_fk` / `changed_by_fk` | Integer FK | Audit user refs        |

**Unique constraint:** `(source_dataset_id, target_dataset_id)`

### `dataset_relationship_columns`

| Column               | Type        | Notes                                 |
|----------------------|-------------|---------------------------------------|
| `id`                 | Integer PK  | Auto-increment                        |
| `relationship_id`    | Integer FK  | References `dataset_relationships.id` |
| `source_column_name` | String(256) | Column in source dataset              |
| `target_column_name` | String(256) | Column in target dataset              |
| `operator`           | String(10)  | Default `=`                           |
| `ordinal`            | Integer     | For multi-column join ordering        |

---

## Key Components

### ORM Models (`superset/models/dataset_relationships.py`)

- **`DatasetRelationship`** — represents a declared link between two datasets.
  Includes validation methods and a `to_dict()` serializer.
- **`DatasetRelationshipColumn`** — maps individual column pairs for the JOIN
  condition within a relationship.

### DAO (`superset/daos/dataset_relationship.py`)

`DatasetRelationshipDAO` extends `BaseDAO` and provides:

| Method                 | Description                                        |
|------------------------|----------------------------------------------------|
| `find_by_id`           | Fetch with eager-loaded columns                    |
| `find_by_datasets`     | Lookup by source + target IDs                      |
| `find_active`          | All active relationships                           |
| `find_by_dataset_id`   | All relationships involving a dataset              |
| `validate_uniqueness`  | Check duplicate source/target pair                 |
| `create` / `update`    | Persist with nested column handling                |
| `delete`               | Cascade deletion                                   |

### Commands (`superset/commands/dataset_relationship/`)

| Command   | Validations                                                |
|-----------|------------------------------------------------------------|
| **Create** | Self-reference, dataset existence, uniqueness, column names, auto `is_cross_database` |
| **Update** | Partial update, re-validates changed fields, recalculates cross-DB flag |
| **Delete** | Existence check, batch deletion                            |

Custom exceptions provide typed HTTP errors (404, 403, 422, 500).

### Query Engine

#### Same-Database: `RelationshipQueryInjector`

Injects SQL `JOIN` clauses directly into the SQLAlchemy `Select` object
before it is sent to the database. Supports `INNER`, `LEFT`, `RIGHT`, and
`FULL` joins with multi-column ON clauses.

#### Cross-Database: `CrossDatabaseMerger`

Performs Pandas DataFrame merges at the application level when source and
target datasets live in different databases. Includes:

- **Memory guard** — estimates result size and aborts if > `RELATIONSHIP_MAX_MERGE_ROWS` (default 100 000).
- **Timeout** — enforces `RELATIONSHIP_QUERY_TIMEOUT` (default 30 s) via `SIGALRM`.
- **Column conflict resolution** — auto-suffixes overlapping column names.

### Integration (`superset/models/helpers.py`)

Two private methods are injected into the `ExploreMixin`:

1. `_maybe_inject_relationship_joins(tbl)` — called inside `get_sqla_query()`.
2. `_maybe_apply_cross_db_merges(result)` — called inside `get_query_result()`.

Both are guarded by the `DATASET_RELATIONSHIPS` feature flag and fail
gracefully, falling back to the original query/result on error.

---

## REST API

**Base path:** `/api/v1/dataset_relationship/`

| Method   | Endpoint                | Description             |
|----------|-------------------------|-------------------------|
| `GET`    | `/`                     | List relationships      |
| `GET`    | `/<id>`                 | Get single relationship |
| `POST`   | `/`                     | Create relationship     |
| `PUT`    | `/<id>`                 | Update relationship     |
| `DELETE`  | `/<id>`                | Delete relationship     |
| `DELETE`  | `/` (bulk via rison)   | Bulk delete             |
| `GET`    | `/related/<column>`     | Related field values    |
| `GET`    | `/distinct/<column>`    | Distinct column values  |

All endpoints are protected by `@protect()` and follow standard Superset
API response schemas.

---

## Configuration (`superset/config.py`)

```python
# Feature flag (under DEFAULT_FEATURE_FLAGS)
"DATASET_RELATIONSHIPS": False,

# Safety limits
RELATIONSHIP_MAX_MERGE_ROWS = 100_000
RELATIONSHIP_QUERY_TIMEOUT = 30  # seconds
```

---

## Tests

| File                                                         | Covers                          |
|--------------------------------------------------------------|---------------------------------|
| `tests/unit_tests/daos/dataset_relationship_test.py`         | DAO CRUD + validation           |
| `tests/unit_tests/common/test_cross_database_merger.py`      | Merge joins, memory, timeout    |
| `tests/unit_tests/common/test_relationship_query_injector.py`| SQL injection, ON clauses       |

Run tests:

```bash
pytest tests/unit_tests/daos/dataset_relationship_test.py -v
pytest tests/unit_tests/common/test_cross_database_merger.py -v
pytest tests/unit_tests/common/test_relationship_query_injector.py -v
```

---

## Migration

```bash
superset db upgrade   # applies a8b9c0d1e2f3_add_dataset_relationships
```

---

## Next Phases

- **Phase 2 — Frontend & Model View:** Visual relationship canvas with
  `@xyflow/react`, extended column picker in Explore, dashboard metadata
  integration.
- **Phase 3 — Advanced Interactions:** Cross-filter propagation through
  relationships, hierarchical drill-down, native filter translation.

---

## Files Changed / Added (Phase 1)

```
NEW  superset/migrations/versions/2026-05-14_10-00_a8b9c0d1e2f3_add_dataset_relationships.py
NEW  superset/models/dataset_relationships.py
NEW  superset/daos/dataset_relationship.py
NEW  superset/commands/dataset_relationship/__init__.py
NEW  superset/commands/dataset_relationship/exceptions.py
NEW  superset/commands/dataset_relationship/create.py
NEW  superset/commands/dataset_relationship/update.py
NEW  superset/commands/dataset_relationship/delete.py
NEW  superset/common/cross_database_merger.py
NEW  superset/common/relationship_query_injector.py
NEW  superset/dataset_relationship/__init__.py
NEW  superset/dataset_relationship/api.py
NEW  superset/dataset_relationship/schemas.py
NEW  superset/dataset_relationship/README.md
NEW  tests/unit_tests/daos/dataset_relationship_test.py
NEW  tests/unit_tests/common/test_cross_database_merger.py
NEW  tests/unit_tests/common/test_relationship_query_injector.py
MOD  superset/models/__init__.py
MOD  superset/models/helpers.py
MOD  superset/config.py
```
