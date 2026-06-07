# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from superset.common.relationship_merger import RelationshipMerger


@pytest.fixture
def mock_relationship() -> MagicMock:
    """Create a mock DatasetRelationship."""
    rel = MagicMock()
    rel.id = 1
    rel.source_dataset_id = 10
    rel.target_dataset_id = 20
    rel.join_type = "LEFT"
    return rel


@pytest.fixture
def mock_relationship_columns() -> list[MagicMock]:
    """Create mock relationship columns."""
    col1 = MagicMock()
    col1.source_column_name = "customer_id"
    col1.target_column_name = "id"
    col1.ordinal = 0
    return [col1]


@pytest.fixture
def sample_source_df() -> pd.DataFrame:
    """Create a sample source DataFrame."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "customer_id": [100, 200, 300],
        "total": [10.5, 20.0, 30.0],
    })


@pytest.fixture
def sample_target_df() -> pd.DataFrame:
    """Create a sample target DataFrame."""
    return pd.DataFrame({
        "id": [100, 200, 300],
        "name": ["Alice", "Bob", "Charlie"],
        "email": ["alice@example.com", "bob@example.com", "charlie@example.com"],
    })


def test_merge_simple_dataframes(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge() with simple DataFrames."""
    mock_relationship.columns = mock_relationship_columns

    with patch("superset.common.relationship_merger.RelationshipQueryCache") as mock_cache:
        mock_cache.get.return_value = None

        result = RelationshipMerger.merge(
            source_df=sample_source_df,
            target_df=sample_target_df,
            relationship=mock_relationship,
        )

        # Result should have columns from both DataFrames
        assert "id" in result.columns
        assert "customer_id" in result.columns
        assert "total" in result.columns
        assert "name" in result.columns
        assert "email" in result.columns
        # Left join should keep all source rows
        assert len(result) == 3


def test_merge_inner_join(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge() with INNER join type."""
    mock_relationship.join_type = "INNER"
    mock_relationship.columns = mock_relationship_columns

    # Create target with non-matching ID to test inner join
    target_df = pd.DataFrame({
        "id": [100, 200],  # Only 2 matches, no 300
        "name": ["Alice", "Bob"],
    })

    with patch("superset.common.relationship_merger.RelationshipQueryCache") as mock_cache:
        mock_cache.get.return_value = None

        result = RelationshipMerger.merge(
            source_df=sample_source_df,
            target_df=target_df,
            relationship=mock_relationship,
        )

        # Inner join should only have matching rows
        assert len(result) == 2


def test_merge_right_join(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge() with RIGHT join type."""
    mock_relationship.join_type = "RIGHT"
    mock_relationship.columns = mock_relationship_columns

    with patch("superset.common.relationship_merger.RelationshipQueryCache") as mock_cache:
        mock_cache.get.return_value = None

        result = RelationshipMerger.merge(
            source_df=sample_source_df,
            target_df=sample_target_df,
            relationship=mock_relationship,
        )

        # Right join should keep all target rows
        assert len(result) == 3


def test_merge_full_outer_join(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge() with FULL OUTER join type."""
    mock_relationship.join_type = "FULL"
    mock_relationship.columns = mock_relationship_columns

    # Create source with non-matching customer_id
    source_df = pd.DataFrame({
        "id": [1, 2],
        "customer_id": [100, 999],  # 999 doesn't exist in target
        "total": [10.5, 20.0],
    })

    with patch("superset.common.relationship_merger.RelationshipQueryCache") as mock_cache:
        mock_cache.get.return_value = None

        result = RelationshipMerger.merge(
            source_df=source_df,
            target_df=sample_target_df,
            relationship=mock_relationship,
        )

        # Full outer join should have all rows from both
        assert len(result) >= 3


def test_merge_with_selected_columns(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge() with selected_columns parameter."""
    mock_relationship.columns = mock_relationship_columns

    with patch("superset.common.relationship_merger.RelationshipQueryCache") as mock_cache:
        mock_cache.get.return_value = None

        result = RelationshipMerger.merge(
            source_df=sample_source_df,
            target_df=sample_target_df,
            relationship=mock_relationship,
            selected_columns=["name"],  # Only include name column
        )

        # Result should have source columns plus only 'name' from target
        assert "id" in result.columns
        assert "customer_id" in result.columns
        assert "total" in result.columns
        assert "name" in result.columns
        # email should not be included
        assert "email" not in result.columns


def test_merge_cache_hit(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge() returns cached result when available."""
    mock_relationship.columns = mock_relationship_columns
    cached_result = [{"id": 1, "name": "Cached"}]

    with patch("superset.common.relationship_merger.RelationshipQueryCache") as mock_cache:
        mock_cache.get.return_value = cached_result

        result = RelationshipMerger.merge(
            source_df=sample_source_df,
            target_df=sample_source_df,  # Doesn't matter when cache hits
            relationship=mock_relationship,
        )

        # Should return cached result as DataFrame
        assert isinstance(result, pd.DataFrame)
        # Cache should be checked
        mock_cache.get.assert_called_once()
        # pd.merge should not be called when cache hits
        assert not any(call[0] == "pd.merge" for call in mock_cache.mock_calls)


def test_merge_cache_miss(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge() performs merge when cache misses."""
    mock_relationship.columns = mock_relationship_columns

    with patch("superset.common.relationship_merger.RelationshipQueryCache") as mock_cache:
        mock_cache.get.return_value = None  # Cache miss
        mock_cache.set.return_value = None

        result = RelationshipMerger.merge(
            source_df=sample_source_df,
            target_df=sample_target_df,
            relationship=mock_relationship,
        )

        # Should perform the merge
        assert isinstance(result, pd.DataFrame)
        # Should attempt to cache the result
        mock_cache.set.assert_called_once()


def test_merge_force_fresh_bypasses_cache(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge() bypasses cache when force_fresh=True."""
    mock_relationship.columns = mock_relationship_columns

    with patch("superset.common.relationship_merger.RelationshipQueryCache") as mock_cache:
        result = RelationshipMerger.merge(
            source_df=sample_source_df,
            target_df=sample_target_df,
            relationship=mock_relationship,
            force_fresh=True,
        )

        # Should perform the merge
        assert isinstance(result, pd.DataFrame)
        # Cache should NOT be checked when force_fresh is True
        mock_cache.get.assert_not_called()


def test_merge_no_columns_raises_error(
    mock_relationship: MagicMock,
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge() raises ValueError when relationship has no columns."""
    mock_relationship.columns = []

    with pytest.raises(ValueError, match="no column mappings"):
        RelationshipMerger.merge(
            source_df=sample_source_df,
            target_df=sample_target_df,
            relationship=mock_relationship,
        )


def test_merge_missing_source_column_raises_error(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge() raises ValueError when source column is missing."""
    mock_relationship_columns[0].source_column_name = "nonexistent_column"
    mock_relationship.columns = mock_relationship_columns

    with patch("superset.common.relationship_merger.RelationshipQueryCache") as mock_cache:
        mock_cache.get.return_value = None

        with pytest.raises(ValueError, match="Source column 'nonexistent_column' not found"):
            RelationshipMerger.merge(
                source_df=sample_source_df,
                target_df=sample_target_df,
                relationship=mock_relationship,
            )


def test_merge_missing_target_column_raises_error(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge() raises ValueError when target column is missing."""
    mock_relationship_columns[0].target_column_name = "nonexistent_column"
    mock_relationship.columns = mock_relationship_columns

    with patch("superset.common.relationship_merger.RelationshipQueryCache") as mock_cache:
        mock_cache.get.return_value = None

        with pytest.raises(ValueError, match="Target column 'nonexistent_column' not found"):
            RelationshipMerger.merge(
                source_df=sample_source_df,
                target_df=sample_target_df,
                relationship=mock_relationship,
            )


def test_merge_applies_row_limit(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
) -> None:
    """Test RelationshipMerger.merge() applies row limit from config."""
    mock_relationship.columns = mock_relationship_columns

    # Create DataFrames exceeding the limit
    large_source_df = pd.DataFrame({
        "customer_id": list(range(200000)),
        "value": list(range(200000)),
    })
    large_target_df = pd.DataFrame({
        "id": list(range(200000)),
        "name": [f"User{i}" for i in range(200000)],
    })

    with patch("superset.common.relationship_merger.current_app") as mock_app:
        mock_app.config.get.return_value = 100000  # 100k limit

        with patch("superset.common.relationship_merger.RelationshipQueryCache") as mock_cache:
            mock_cache.get.return_value = None

            result = RelationshipMerger.merge(
                source_df=large_source_df,
                target_df=large_target_df,
                relationship=mock_relationship,
            )

            # Result should be limited (may have fewer rows due to join, but not more than limit)
            assert len(result) <= 100000


def test_merge_multiple_two_relationships(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge_multiple() with 2 relationships."""
    mock_relationship.columns = mock_relationship_columns

    # Create second relationship
    rel2 = MagicMock()
    rel2.id = 2
    rel2.source_dataset_id = 20  # This would be chained
    rel2.target_dataset_id = 30
    rel2.join_type = "LEFT"
    rel2.columns = mock_relationship_columns

    target_dfs = {
        20: sample_target_df,
        30: sample_target_df,
    }

    with patch("superset.common.relationship_merger.current_app") as mock_app:
        mock_app.config.get.return_value = 5  # Max 5 relationships

        with patch("superset.common.relationship_merger.RelationshipMerger.merge") as mock_merge:
            mock_merge.return_value = sample_source_df

            result = RelationshipMerger.merge_multiple(
                source_df=sample_source_df,
                target_dfs=target_dfs,
                relationships=[mock_relationship, rel2],
            )

            # Should call merge for each relationship
            assert mock_merge.call_count == 2


def test_merge_multiple_exceeds_limit_raises_error(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge_multiple() raises ValueError when exceeding max relationships."""
    mock_relationship.columns = mock_relationship_columns

    # Create 6 relationships (exceeding default limit of 5)
    relationships = [MagicMock(id=i, columns=mock_relationship_columns) for i in range(6)]

    target_dfs = {i: sample_source_df for i in range(6)}

    with patch("superset.common.relationship_merger.current_app") as mock_app:
        mock_app.config.get.return_value = 5  # Max 5 relationships

        with pytest.raises(ValueError, match="Cannot merge more than 5"):
            RelationshipMerger.merge_multiple(
                source_df=sample_source_df,
                target_dfs=target_dfs,
                relationships=relationships,
            )


def test_merge_multiple_missing_target_dataframe_raises_error(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge_multiple() raises ValueError when target DataFrame is missing."""
    mock_relationship.columns = mock_relationship_columns
    mock_relationship.target_dataset_id = 999

    with patch("superset.common.relationship_merger.current_app") as mock_app:
        mock_app.config.get.return_value = 5

        with pytest.raises(ValueError, match="Target DataFrame for dataset ID 999"):
            RelationshipMerger.merge_multiple(
                source_df=sample_source_df,
                target_dfs={10: sample_source_df},  # Missing 999
                relationships=[mock_relationship],
            )


def test_merge_multiple_with_selected_columns_map(
    mock_relationship: MagicMock,
    mock_relationship_columns: list[MagicMock],
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger.merge_multiple() with selected_columns_map."""
    mock_relationship.columns = mock_relationship_columns

    selected_map = {1: ["name"]}  # Only include 'name' for relationship 1

    target_dfs = {20: sample_target_df}

    with patch("superset.common.relationship_merger.current_app") as mock_app:
        mock_app.config.get.return_value = 5

        with patch("superset.common.relationship_merger.RelationshipMerger.merge") as mock_merge:
            mock_merge.return_value = sample_source_df

            result = RelationshipMerger.merge_multiple(
                source_df=sample_source_df,
                target_dfs=target_dfs,
                relationships=[mock_relationship],
                selected_columns_map=selected_map,
            )

            # Merge should be called with selected_columns
            call_kwargs = mock_merge.call_args[1]
            assert call_kwargs["selected_columns"] == ["name"]


def test_build_merge_key_creates_deterministic_key(
    mock_relationship: MagicMock,
) -> None:
    """Test RelationshipMerger._build_merge_key() creates deterministic keys."""
    key1 = RelationshipMerger._build_merge_key(
        source_df_hash="abc123",
        target_df_hash="def456",
        relationship_id=1,
        join_type="LEFT",
        selected_columns=["name", "email"],
    )

    key2 = RelationshipMerger._build_merge_key(
        source_df_hash="abc123",
        target_df_hash="def456",
        relationship_id=1,
        join_type="LEFT",
        selected_columns=["email", "name"],  # Different order, but same set
    )

    # Keys should be identical (sorted columns)
    assert key1 == key2

    # Different params should produce different keys
    key3 = RelationshipMerger._build_merge_key(
        source_df_hash="xyz789",  # Different hash
        target_df_hash="def456",
        relationship_id=1,
        join_type="LEFT",
        selected_columns=["name", "email"],
    )

    assert key1 != key3


def test_hash_dataframe_creates_consistent_hash(
    sample_source_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger._hash_dataframe() creates consistent hashes."""
    hash1 = RelationshipMerger._hash_dataframe(sample_source_df)
    hash2 = RelationshipMerger._hash_dataframe(sample_source_df)

    # Same DataFrame should produce same hash
    assert hash1 == hash2

    # Different DataFrame should produce different hash
    different_df = sample_source_df.copy()
    different_df.iloc[0, 0] = 999
    hash3 = RelationshipMerger._hash_dataframe(different_df)

    assert hash1 != hash3


def test_apply_row_limit_truncates_when_exceeded() -> None:
    """Test RelationshipMerger._apply_row_limit() truncates DataFrame when exceeded."""
    df = pd.DataFrame({"value": range(200)})
    max_rows = 100

    result = RelationshipMerger._apply_row_limit(df, max_rows)

    assert len(result) == 100
    assert list(result["value"]) == list(range(100))


def test_apply_row_limit_passes_when_not_exceeded(
    sample_source_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger._apply_row_limit() passes DataFrame through when not exceeded."""
    result = RelationshipMerger._apply_row_limit(sample_source_df, 10000)

    # Should return the same DataFrame
    assert len(result) == len(sample_source_df)


def test_sanitize_column_name() -> None:
    """Test RelationshipMerger._sanitize_column_name() sanitizes special characters."""
    assert RelationshipMerger._sanitize_column_name("user.name") == "user_name"
    assert RelationshipMerger._sanitize_column_name("user name") == "user_name"
    assert RelationshipMerger._sanitize_column_name("user-name") == "user_name"
    assert RelationshipMerger._sanitize_column_name("user_name") == "user_name"


def test_merge_with_fallback_invalid_relationship(
    sample_source_df: pd.DataFrame,
    sample_target_df: pd.DataFrame,
) -> None:
    """Test RelationshipMerger handles invalid relationship gracefully."""
    # Create a relationship that will fail validation
    mock_rel = MagicMock()
    mock_rel.columns = None  # Invalid: no columns

    with pytest.raises(ValueError, match="no column mappings"):
        RelationshipMerger.merge(
            source_df=sample_source_df,
            target_df=sample_target_df,
            relationship=mock_rel,
        )
