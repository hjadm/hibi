# HIBI - Architecture Review: Dataset Relationships Module

**Date**: 2026-06-06  
**Author**: Claude (System Architecture Analysis)  
**Status**: Partial Implementation Complete

---

## Executive Summary

The HIBI fork of Apache Superset introduces a **Dataset Relationship Engine** that enables visual and programmatic relationships between datasets. This document provides a comprehensive architecture review, implementation status, and phased roadmap for completion.

### Current Implementation Status

| Layer | Status | Completeness |
|-------|--------|--------------|
| Database Models | ✅ Complete | 100% |
| DAOs | ✅ Complete | 100% |
| Migrations | ✅ Complete | 100% |
| Query Injection | ✅ Complete | 100% |
| Cache Layer | ✅ Complete | 100% |
| Frontend Components | ✅ Complete | 90% |
| Frontend Hooks | ✅ Complete | 90% |
| REST API | ❌ Missing | 0% |
| Commands | ❌ Missing | 0% |
| Schemas | ❌ Missing | 0% |
| Query Context Integration | ❌ Missing | 0% |
| Explore Integration | ❌ Missing | 0% |

---

## 1. Architecture Overview

### 1.1 Current Superset Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Explore    │  │  Dashboard   │  │   SQL Lab    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┴──────────────────┘                   │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │ REST API
┌────────────────────────────┼─────────────────────────────────────┐
│                            ▼                         BACKEND     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Flask App + FAB                        │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  REST APIs │ Views │ Commands │ DAOs │ Models             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│  ┌───────────────────────────┴─────────────────────────────┐    │
│  │                    Query Engine                         │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐    │    │
│  │  │   Query     │  │    Query     │  │   SQLAlchemy  │    │    │
│  │  │  Context    │  │   Factory    │  │   Connector  │    │    │
│  │  └─────────────┘  └──────────────┘  └──────────────┘    │    │
│  └──────────────────────────────────────────────────────────┘    │
│                              │                                   │
│  ┌───────────────────────────┴─────────────────────────────┐    │
│  │                    Database Layer                        │    │
│  │  PostgreSQL/MySQL ── SQLAlchemy ORM ── Models            │    │
│  └──────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

### 1.2 HIBI Relationships Architecture (Proposed)

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND - Explore View                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              RelationshipSidebar Panel                     │   │
│  │  - Shows available relationships for current dataset     │   │
│  │  - Toggle relationships on/off                           │   │
│  │  - Select target columns to include                      │   │
│  └────────────────────┬────────────────────────────────────┘   │
│                       │                                          │
│                       ▼ form_data.active_relationships          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Column Control (Modified)                   │   │
│  │  - Shows joined columns from related datasets            │   │
│  │  - Visual indicator for relationship-sourced columns    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ REST API Call
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND - REST API                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              DatasetRelationshipRestApi                   │   │
│  │  - GET    /dataset_relationship/                          │   │
│  │  - POST   /dataset_relationship/                          │   │
│  │  - GET    /dataset_relationship/{id}                      │   │
│  │  - PUT    /dataset_relationship/{id}                      │   │
│  │  - DELETE /dataset_relationship/{id}                      │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Commands (Business Logic)                    │   │
│  │  - CreateDatasetRelationshipCommand                      │   │
│  │  - UpdateDatasetRelationshipCommand                      │   │
│  │  - DeleteDatasetRelationshipCommand                      │   │
│  │  - GetDatasetRelationshipCommand                         │   │
│  └──────────────────────┬───────────────────────────────────┘   │
└───────────────────────────┼───────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY ENGINE (Enhanced)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              QueryContext (Modified)                      │   │
│  │  - Reads form_data.active_relationships                  │   │
│  │  - Calls RelationshipQueryInjector                        │   │
│  │  - Modifies SQLAlchemy query before execution             │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         RelationshipQueryInjector (Implemented)          │   │
│  │  - inject_joins(): Adds JOIN clauses to SQLAlchemy query  │   │
│  │  - build_on_clause(): Creates ON conditions              │   │
│  │  - Handles: INNER, LEFT, RIGHT, FULL joins                │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         RelationshipQueryCache (Implemented)             │   │
│  │  - Caches cross-database merge results                   │   │
│  │  - TTL-based invalidation                                │   │
│  │  - Dataset version tracking                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         SQLAlchemy Models (Implemented)                   │   │
│  │  - DatasetRelationship                                    │   │
│  │  - DatasetRelationshipColumn                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Tables (via Migration a8b9c0d1e2f3)               │   │
│  │  - dataset_relationships                                 │   │
│  │  - dataset_relationship_columns                          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Implemented Components (Analysis)

### 2.1 Database Layer ✅

**File**: `superset/models/dataset_relationships.py`

**Models**:
- `DatasetRelationship`: Main relationship entity
  - Fields: id, uuid, source_dataset_id, target_dataset_id, relationship_type, join_type, is_cross_database, is_active, name, description
  - Relationships: source_dataset, target_dataset, columns (one-to-many)
  - Validation: relationship_type, join_type, uniqueness

- `DatasetRelationshipColumn`: Column mapping within a relationship
  - Fields: id, relationship_id, source_column_name, target_column_name, operator, ordinal
  - Validation: operator values, column names

**Strengths**:
- Well-structured with proper SQLAlchemy patterns
- Comprehensive validation methods
- Audit support via AuditMixinNullable
- Proper cascade handling for column mappings

**Technical Debt**: None identified

### 2.2 Migration ✅

**File**: `superset/migrations/versions/2026-05-14_10-00_a8b9c0d1e2f3_add_dataset_relationships.py`

**Creates**:
- `dataset_relationships` table with proper indexes
- `dataset_relationship_columns` table
- Foreign keys to `tables.id` (SqlaTable)
- Unique constraints for data integrity

**Strengths**:
- Proper use of CASCADE for deletes
- Performance indexes on foreign keys and is_active flag
- Audit columns follow Superset patterns

### 2.3 DAO Layer ✅

**File**: `superset/daos/dataset_relationship.py`

**Methods**:
- `find_by_id()`: With eager loading of columns
- `find_by_datasets()`: Get relationship between specific dataset pair
- `find_active()`: Get all active relationships
- `find_by_dataset_id()`: Get all relationships for a dataset
- `validate_uniqueness()`: Check for duplicate relationships
- `create()`: Handle nested column creation
- `update()`: Handle column replacement
- `delete()`: Cascade delete

**Strengths**:
- Follows Superset DAO pattern (BaseDAO subclass)
- Eager loading prevents N+1 queries
- Proper error handling with logging

### 2.4 Query Injection Engine ✅

**File**: `superset/common/relationship_query_injector.py`

**Capabilities**:
- Inject JOIN clauses into SQLAlchemy Select objects
- Build ON clauses from column pairs
- Support for INNER, LEFT, RIGHT, FULL joins
- Proper handling of RIGHT JOIN via operand swapping
- Operator support: =, !=, >, <, >=, <=

**Methods**:
- `get_active_relationships()`: Fetch relationships for a dataset
- `get_same_db_relationships()`: Filter same-database relationships
- `get_cross_db_relationships()`: Filter cross-database relationships
- `build_on_clause()`: Create JOIN ON condition
- `inject_joins()`: Main injection method

**Strengths**:
- Stateless design for testability
- Proper SQLAlchemy integration
- Good error handling with custom exceptions
- Comprehensive logging

**Limitations**:
- Only handles same-database joins (SQL JOIN injection)
- Cross-database merges (Pandas) not implemented in injection layer

### 2.5 Cache Layer ✅

**File**: `superset/common/relationship_query_cache.py`

**Capabilities**:
- TTL-based caching (default 5 minutes)
- Dataset version tracking for invalidation
- Relationship-based invalidation
- Deterministic cache key generation

**Strengths**:
- Integrates with Superset's cache_manager
- Proper versioning strategy
- Graceful error handling

### 2.6 Frontend Implementation ✅ (90% complete)

**Location**: `superset-frontend/src/features/datasets/relationships/`

**Components**:
- `hooks/useExploreRelationships.ts`: Main hook for Explore integration
- `hooks/useRelationshipsApi.ts`: API client
- `hooks/useDashboardRelationshipMetadata.ts`: Dashboard integration
- `components/RelationshipSidebar/`: UI panel
- `components/RelationshipCanvas/`: Visual graph editor
- `components/RelationshipPanel/`: Detail view
- `types/index.ts`: TypeScript types

**Capabilities**:
- Toggle relationships on/off
- Select target columns
- Build form_data with active_relationships
- Column-to-relationship mapping
- Lazy loading of target columns

**Missing**: Integration with actual Explore UI (not wired in yet)

---

## 3. Missing Components (Gap Analysis)

### 3.1 REST API Layer ❌

**Missing Files**:
```
superset/
├── views/
│   └── dataset_relationship/                    # Create this directory
│       ├── __init__.py
│       └── api.py                               # DatasetRelationshipRestApi
└── schemas/
    └── dataset_relationship.py                 # Marshmallow schemas
```

**Required Implementation**:

```python
# superset/views/dataset_relationship/api.py
class DatasetRelationshipRestApi(BaseSupersetModelRestApi):
    # Endpoints needed:
    # GET    /api/v1/dataset_relationship/
    # POST   /api/v1/dataset_relationship/
    # GET    /api/v1/dataset_relationship/{id}
    # PUT    /api/v1/dataset_relationship/{id}
    # DELETE /api/v1/dataset_relationship/{id}
```

### 3.2 Command Layer ❌

**Missing Files**:
```
superset/commands/
└── dataset_relationship/                      # Create this directory
    ├── __init__.py
    ├── create.py                               # CreateDatasetRelationshipCommand
    ├── update.py                               # UpdateDatasetRelationshipCommand
    ├── delete.py                               # DeleteDatasetRelationshipCommand
    ├── get.py                                  # GetDatasetRelationshipCommand
    └── exceptions.py                           # Custom exceptions
```

**Pattern to Follow**: `superset/commands/chart/create.py`

### 3.3 Query Context Integration ❌

**File to Modify**: `superset/common/query_context.py`

**Required Changes**:
```python
class QueryContext:
    def __init__(self, ...):
        # Add:
        self.active_relationships = form_data.get('active_relationships', [])
    
    def get_payload(self, ...):
        # Call RelationshipQueryInjector before executing query
        if self.active_relationships:
            injector = RelationshipQueryInjector()
            # Inject JOINs into the query
```

**Integration Point**: Between query construction and execution

### 3.4 Explore Integration ❌

**Files to Modify**:
1. `superset/explore/views.py`: Add relationship panel to Explore UI
2. `superset-frontend/src/explore/components/ExploreViewContainer/`: Wire in RelationshipSidebar
3. `superset/charts/schemas.py`: Add active_relationships to query context schema

### 3.5 Semantic Layer Integration ❌

**Consideration**: Relationships should work with Semantic Layers (virtual datasets)

**Impact**: When a virtual dataset is involved, JOIN injection must:
1. Detect virtual dataset
2. Use Pandas merge instead of SQL JOIN
3. Apply cache layer for cross-database cases

---

## 4. Architectural Risks

### 4.1 High Priority Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Circular Import Issues** | High | Use lazy imports in QueryContext and Commands |
| **Cross-Database Performance** | High | Implement aggressive caching and consider async processing |
| **Schema Changes Breaking Relationships** | High | Add validation warnings when columns are renamed/deleted |
| **Permission Model Complexity** | Medium | Extend RLS to respect relationship boundaries |

### 4.2 Medium Priority Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **JOIN Performance with Large Tables** | Medium | Add query size limits and materialized view hints |
| **Relationship Graph Cycles** | Medium | Detect and prevent cycles during creation |
| **Filter Propagation Across Relationships** | Medium | Document filter behavior in cross-relationship scenarios |

### 4.3 Low Priority Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Frontend State Complexity** | Low | Use Recoil/Redux for predictable state management |
| **Cache Stampede** | Low | Implement cache locking for expensive merges |

---

## 5. Technical Debt Analysis

### 5.1 Current Debt

1. **Incomplete Cross-Database Implementation**
   - Cache layer exists but merge logic not implemented
   - Need Pandas merge pipeline

2. **No Schema Migration Validation**
   - Renaming a column breaks relationships silently
   - Need validation hooks

3. **Missing Relationship Graph Management**
   - No cycle detection
   - No impact analysis for deletion

### 5.2 Future Debt Prevention

1. **Comprehensive Testing**
   - Unit tests for injection logic
   - Integration tests for API
   - E2E tests for Explore flow

2. **Performance Monitoring**
   - Query time metrics for joined queries
   - Cache hit/miss tracking
   - Relationship usage analytics

---

## 6. Implementation Roadmap

### Phase 1: API Foundation (Week 1-2)

**Goal**: Expose Relationships via REST API

| Task | File | Estimate |
|------|------|----------|
| Create Marshmallow schemas | `superset/schemas/dataset_relationship.py` | 4h |
| Implement Commands | `superset/commands/dataset_relationship/` | 12h |
| Create REST API | `superset/views/dataset_relationship/api.py` | 8h |
| Add API to App initialization | `superset/__init__.py` | 2h |
| Unit tests | `tests/unit_tests/commands/dataset_relationship/` | 8h |
| Integration tests | `tests/integration_tests/dataset_relationship_api_tests.py` | 6h |

**Deliverables**:
- Full CRUD API for relationships
- Test coverage > 80%
- OpenAPI documentation

### Phase 2: Query Engine Integration (Week 3-4)

**Goal**: Make relationships functional in queries

| Task | File | Estimate |
|------|------|----------|
| Modify QueryContext | `superset/common/query_context.py` | 8h |
| Add schema validation | `superset/charts/schemas.py` | 4h |
| Implement cross-db merge | `superset/common/relationship_merger.py` | 16h |
| Cache integration | Update `relationship_query_cache.py` | 6h |
| Query tests | `tests/integration_tests/query_context_tests.py` | 8h |

**Deliverables**:
- Working JOIN injection in QueryContext
- Cross-database Pandas merge
- Cached merge results

### Phase 3: Explore UI Integration (Week 5-6)

**Goal**: Expose relationships in Explore interface

| Task | File | Estimate |
|------|------|----------|
| Add RelationshipSidebar to Explore | `superset-frontend/src/explore/` | 12h |
| Column control enhancements | `superset-frontend/src/explore/components/` | 8h |
| Form data synchronization | `superset-frontend/src/features/datasets/relationships/` | 6h |
| E2E tests | `superset-frontend/src/explore/**/*.test.tsx` | 8h |

**Deliverables**:
- Relationship panel in Explore
- Visual column indicators
- Toggle relationship functionality

### Phase 4: Dashboard & Polish (Week 7-8)

**Goal**: Complete dashboard integration and edge cases

| Task | File | Estimate |
|------|------|----------|
| Dashboard filter integration | `superset/charts/data/dashboard_filter_context.py` | 8h |
| Schema change validation | `superset/connectors/sqla/models.py` | 6h |
| Cycle detection | `superset/daos/dataset_relationship.py` | 4h |
| Performance optimization | Multiple files | 8h |
| Documentation | `docs/` | 8h |

**Deliverables**:
- Dashboard-compatible relationships
- Schema validation
- User documentation

---

## 7. File Inventory

### 7.1 Files to Create

```
superset/
├── schemas/
│   └── dataset_relationship.py              [NEW]
├── commands/
│   └── dataset_relationship/                [NEW DIR]
│       ├── __init__.py                      [NEW]
│       ├── create.py                        [NEW]
│       ├── update.py                        [NEW]
│       ├── delete.py                        [NEW]
│       ├── get.py                           [NEW]
│       └── exceptions.py                     [NEW]
├── views/
│   └── dataset_relationship/               [NEW DIR]
│       ├── __init__.py                      [NEW]
│       └── api.py                           [NEW]
└── common/
    └── relationship_merger.py               [NEW] - Pandas merge

tests/
├── unit_tests/
│   └── commands/
│       └── dataset_relationship/            [NEW DIR]
│           ├── create_test.py              [NEW]
│           ├── update_test.py              [NEW]
│           └── delete_test.py              [NEW]
└── integration_tests/
    └── dataset_relationship_api_tests.py   [NEW]
```

### 7.2 Files to Modify

```
superset/
├── __init__.py                              [MOD] - Register API
├── common/
│   └── query_context.py                    [MOD] - Inject relationships
├── charts/
│   ├── schemas.py                           [MOD] - Add active_relationships
│   └── data/
│       └── dashboard_filter_context.py     [MOD] - Relationship-aware filters
└── connectors/
    └── sqla/
        └── models.py                        [MOD] - Schema change validation

superset-frontend/src/
├── explore/
│   └── components/
│       └── ExploreViewContainer/           [MOD] - Add sidebar
└── features/
    └── datasets/
        └── relationships/
            └── hooks/
                └── useExploreRelationships.ts  [MOD] - Wire up to state
```

---

## 8. Testing Strategy

### 8.1 Unit Testing

- **Models**: Test validation, uniqueness, cascades
- **DAOs**: Test queries, eager loading, error cases
- **Commands**: Test business logic, permissions
- **Injector**: Test SQL generation, edge cases

### 8.2 Integration Testing

- **API**: Test CRUD flows, validation
- **Query**: Test actual query execution with joins
- **Cache**: Test cache hit/miss, invalidation

### 8.3 E2E Testing

- **Explore**: Create relationship, use in chart, verify results
- **Dashboard**: Create chart with relationship, add to dashboard
- **Cross-DB**: Test merge behavior

---

## 9. Performance Considerations

### 9.1 Query Performance

- JOIN injection is SQL-native (fast for same-database)
- Cross-database merges require:
  - Pull both datasets to Pandas
  - Perform merge in memory
  - Cache results aggressively

### 9.2 Caching Strategy

- Same-database: Leverage existing query cache
- Cross-database: Use `RelationshipQueryCache`
- Cache keys include: dataset IDs, column pairs, join type, filters

### 9.3 Limits and Safeguards

- Maximum active relationships per query: 5 (configurable)
- Maximum rows for cross-database merge: 100K (configurable)
- Query timeout for joined queries: 60s (configurable)

---

## 10. Security Considerations

### 10.1 Permission Model

- Relationship CRUD: Requires dataset ownership
- Query usage: Requires dataset access on both sides
- No automatic permission escalation

### 10.2 SQL Injection Prevention

- Column names are validated (whitelist from schema)
- Operators are limited to safe set
- SQLAlchemy parameterized queries

### 10.3 Data Leakage Prevention

- Cross-database merges respect RLS on both datasets
- No implicit data access via relationships

---

## 11. Conclusion

The Dataset Relationship Engine is **60% complete** with solid foundations:
- ✅ Database layer is production-ready
- ✅ Query injection engine is well-designed
- ✅ Frontend components are comprehensive
- ❌ Missing: API, Commands, Query Context integration

**Recommended Next Step**: Implement Phase 1 (API Foundation) to enable frontend-backend communication, followed by Phase 2 (Query Engine Integration) to make relationships functional.

**Estimated Total Completion Time**: 6-8 weeks for full production-ready implementation.

---

## Appendix: Related Files Reference

### Already Implemented (No Changes Needed)

- `superset/models/dataset_relationships.py` - Database models
- `superset/daos/dataset_relationship.py` - Data access layer
- `superset/migrations/versions/2026-05-14_10-00_a8b9c0d1e2f3_add_dataset_relationships.py` - Database migration
- `superset/common/relationship_query_injector.py` - JOIN injection logic
- `superset/common/relationship_query_cache.py` - Cache layer
- `superset-frontend/src/features/datasets/relationships/` - Frontend implementation

### Test Infrastructure Already Exists

- `tests/unit_tests/daos/dataset_relationship_test.py`
- `tests/unit_tests/models/` (relationship model tests should be added here)
- `logs/test_relationship_full.py` - Integration test script

### Documentation References

- `AGENTS.md` - Project context
- `CLAUDE.md` - Project instructions
