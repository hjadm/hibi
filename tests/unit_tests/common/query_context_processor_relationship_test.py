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

from superset.common.query_context_processor import BaseQueryContextProcessor


@pytest.fixture
def mock_query_context() -> MagicMock:
    """Create a mock QueryContext."""
    qc = MagicMock()
    qc.datasource = MagicMock()
    qc.datasource.id = 10
    qc.form_data = {}
    qc.active_relationships = None
    return qc


@pytest.fixture
def mock_processor(mock_query_context: MagicMock) -> BaseQueryContextProcessor:
    """Create a BaseQueryContextProcessor instance for testing."""
    processor = MagicMock(spec=BaseQueryContextProcessor)
    processor._query_context = mock_query_context
    processor._qc_datasource = mock_query_context.datasource

    # Bind real methods from BaseQueryContextProcessor
    processor.get_query_result = BaseQueryContextProcessor.get_query_result.__get__(
        processor, BaseQueryContextProcessor
    )

    return processor


@pytest.fixture
def mock_query_object() -> MagicMock:
    """Create a mock QueryObject."""
    qo = MagicMock()
    qo.to_dict.return_value = {}
    return qo


@pytest.fixture
def mock_query_result() -> MagicMock:
    """Create a mock QueryResult."""
    result = MagicMock()
    result.df = pd.DataFrame({"id": [1, 2, 3], "value": [10, 20, 30]})
    result.query = "SELECT * FROM table"
    result.duration = 0.5
    result.status = MagicMock()
    return result


def test_get_query_result_without_active_relationships(
    mock_processor: MagicMock,
    mock_query_object: MagicMock,
    mock_query_result: MagicMock,
) -> None:
    """Test get_query_result() behaves normally when no active_relationships."""
    mock_processor._query_context.active_relationships = None
    mock_processor._qc_datasource.get_query_result.return_value = mock_query_result

    result = mock_processor.get_query_result(mock_query_object)

    assert result == mock_query_result
    mock_processor._qc_datasource.get_query_result.assert_called_once_with(
        mock_query_object
    )


def test_get_query_result_with_empty_active_relationships(
    mock_processor: MagicMock,
    mock_query_object: MagicMock,
    mock_query_result: MagicMock,
) -> None:
    """Test get_query_result() behaves normally when active_relationships is empty."""
    mock_processor._query_context.active_relationships = []
    mock_processor._qc_datasource.get_query_result.return_value = mock_query_result

    result = mock_processor.get_query_result(mock_query_object)

    assert result == mock_query_result
    mock_processor._qc_datasource.get_query_result.assert_called_once_with(
        mock_query_object
    )


def test_get_query_result_with_active_relationships_calls_processor(
    mock_processor: MagicMock,
    mock_query_object: MagicMock,
    mock_query_result: MagicMock,
) -> None:
    """Test get_query_result() calls _get_query_result_with_relationships when active_relationships present."""
    mock_processor._query_context.active_relationships = [
        {"relationship_id": 1, "target_columns": ["name"]}
    ]

    # Mock the relationship processing path
    with patch(
        "superset.common.query_context_processor.BaseQueryContextProcessor._get_query_result_with_relationships"
    ) as mock_with_rels:
        mock_with_rels.return_value = mock_query_result

        result = mock_processor.get_query_result(mock_query_object)

        assert result == mock_query_result
        mock_with_rels.assert_called_once()


def test_get_query_result_fallback_on_relationship_error(
    mock_processor: MagicMock,
    mock_query_object: MagicMock,
    mock_query_result: MagicMock,
) -> None:
    """Test get_query_result() falls back to normal query on relationship error."""
    mock_processor._query_context.active_relationships = [
        {"relationship_id": 1}
    ]
    mock_processor._qc_datasource.get_query_result.return_value = mock_query_result

    # Mock _get_query_result_with_relationships to raise an error
    with patch.object(
        BaseQueryContextProcessor,
        "_get_query_result_with_relationships",
        side_effect=Exception("Relationship error"),
    ):
        result = mock_processor.get_query_result(mock_query_object)

        # Should fall back to normal query
        assert result == mock_query_result
        mock_processor._qc_datasource.get_query_result.assert_called_once_with(
            mock_query_object
        )


def test_get_query_result_with_relationships_feature_flag_disabled(
    mock_processor: MagicMock,
    mock_query_object: MagicMock,
    mock_query_result: MagicMock,
) -> None:
    """Test _get_query_result_with_relationships() returns normal query when feature flag disabled."""
    mock_processor._query_context.active_relationships = [
        {"relationship_id": 1}
    ]
    mock_processor._qc_datasource.get_query_result.return_value = mock_query_result

    with patch("superset.common.query_context_processor.is_feature_enabled") as mock_feat:
        mock_feat.return_value = False

        # Need to create a real instance to test the actual method
        real_processor = BaseQueryContextProcessor(mock_processor._query_context)

        result = real_processor._get_query_result_with_relationships(
            mock_query_object, [{"relationship_id": 1}]
        )

        assert result == mock_query_result


def test_get_query_result_with_relationships_exceeds_max_limit(
    mock_processor: MagicMock,
    mock_query_object: MagicMock,
) -> None:
    """Test _get_query_result_with_relationships() raises error when exceeding max relationships."""
    mock_processor._query_context.active_relationships = [
        {"relationship_id": i} for i in range(6)  # 6 relationships (exceeds default 5)
    ]

    with patch("superset.common.query_context_processor.current_app") as mock_app:
        mock_app.config.get.return_value = 5

        real_processor = BaseQueryContextProcessor(mock_processor._query_context)

        with pytest.raises(Exception):  # Raises QueryObjectValidationError
            real_processor._get_query_result_with_relationships(
                mock_query_object, mock_processor._query_context.active_relationships
            )


def test_get_cross_db_query_result_delegates_to_merger(
    mock_query_context: MagicMock,
    mock_query_object: MagicMock,
    mock_query_result: MagicMock,
) -> None:
    """Test _get_cross_db_query_result() delegates to RelationshipMerger correctly."""
    # Create mock relationships
    mock_rel = MagicMock()
    mock_rel.id = 1
    mock_rel.target_dataset_id = 20
    mock_rel.columns = [MagicMock(source_column_name="id", target_column_name="id")]

    # Create mock target dataset
    mock_target_dataset = MagicMock()
    mock_target_dataset.get_query_result.return_value = MagicMock(
        df=pd.DataFrame({"id": [1, 2], "name": ["Alice", "Bob"]})
    )

    mock_query_context.datasource.id = 10
    mock_query_context.active_relationships = [
        {"relationship_id": 1, "target_columns": ["name"]}
    ]

    real_processor = BaseQueryContextProcessor(mock_query_context)

    with patch("superset.common.query_context_processor.DatasetDAO") as mock_dataset_dao:
        mock_dataset_dao.find_by_id.return_value = mock_target_dataset

        with patch(
            "superset.common.query_context_processor.RelationshipMerger"
        ) as mock_merger:
            mock_merger.merge_multiple.return_value = pd.DataFrame({
                "id": [1, 2],
                "value": [10, 20],
                "name": ["Alice", "Bob"],
            })

            result = real_processor._get_cross_db_query_result(
                mock_query_object,
                [mock_rel],
                mock_query_context.active_relationships,
            )

            # Should have called the merger
            mock_merger.merge_multiple.assert_called_once()


def test_get_same_db_query_result_with_join_injection(
    mock_query_context: MagicMock,
    mock_query_object: MagicMock,
    mock_query_result: MagicMock,
) -> None:
    """Test _get_same_db_query_result() uses JOIN injection for same-database relationships."""
    mock_rel = MagicMock()
    mock_rel.id = 1
    mock_rel.name = "test_rel"

    mock_query_context.datasource.query.return_value = mock_query_result

    real_processor = BaseQueryContextProcessor(mock_query_context)

    with patch.object(
        BaseQueryContextProcessor,
        "_augment_query_object_with_relationship_columns",
        return_value=mock_query_object,
    ):
        result = real_processor._get_same_db_query_result(mock_query_object, [mock_rel])

        assert result == mock_query_result
        mock_query_context.datasource.query.assert_called_once()


def test_get_same_db_query_result_fallback_on_error(
    mock_query_context: MagicMock,
    mock_query_object: MagicMock,
    mock_query_result: MagicMock,
) -> None:
    """Test _get_same_db_query_result() falls back to normal query on error."""
    mock_rel = MagicMock()
    mock_rel.id = 1

    mock_query_context.datasource.query.side_effect = Exception("Injection failed")
    mock_query_context.datasource.get_query_result.return_value = mock_query_result

    real_processor = BaseQueryContextProcessor(mock_query_context)

    with patch.object(
        BaseQueryContextProcessor,
        "_augment_query_object_with_relationship_columns",
        return_value=mock_query_object,
    ):
        result = real_processor._get_same_db_query_result(mock_query_object, [mock_rel])

        # Should fall back to get_query_result
        assert result == mock_query_result
        mock_query_context.datasource.get_query_result.assert_called_once()


def test_get_cross_db_query_result_empty_source_df(
    mock_query_context: MagicMock,
    mock_query_object: MagicMock,
) -> None:
    """Test _get_cross_db_query_result() returns early when source DataFrame is empty."""
    mock_rel = MagicMock()
    mock_rel.id = 1
    mock_rel.target_dataset_id = 20

    mock_query_context.datasource.id = 10
    mock_query_context.active_relationships = [{"relationship_id": 1}]

    empty_df = pd.DataFrame()
    empty_result = MagicMock()
    empty_result.df = empty_df

    real_processor = BaseQueryContextProcessor(mock_query_context)

    with patch.object(
        BaseQueryContextProcessor,
        "_create_target_query_object",
        return_value=mock_query_object,
    ):
        # Mock get_query_result to return empty df
        mock_query_context.datasource.get_query_result.return_value = empty_result

        result = real_processor._get_cross_db_query_result(
            mock_query_object, [mock_rel], mock_query_context.active_relationships
        )

        # Should return early with the empty result
        assert result == empty_result


def test_get_cross_db_query_result_handles_missing_target_dataset(
    mock_query_context: MagicMock,
    mock_query_object: MagicMock,
    mock_query_result: MagicMock,
) -> None:
    """Test _get_cross_db_query_result() handles missing target dataset gracefully."""
    mock_rel = MagicMock()
    mock_rel.id = 1
    mock_rel.target_dataset_id = 999

    mock_query_context.datasource.id = 10
    mock_query_context.datasource.get_query_result.return_value = mock_query_result

    real_processor = BaseQueryContextProcessor(mock_query_context)

    with patch("superset.common.query_context_processor.DatasetDAO") as mock_dataset_dao:
        mock_dataset_dao.find_by_id.return_value = None  # Target not found

        result = real_processor._get_cross_db_query_result(
            mock_query_object, [mock_rel], [{"relationship_id": 1}]
        )

        # Should return source result (no target to merge)
        assert result == mock_query_result


def test_augment_query_object_with_relationship_columns(
    mock_query_context: MagicMock,
) -> None:
    """Test _augment_query_object_with_relationship_columns() adds target columns."""
    mock_rel = MagicMock()
    mock_rel.id = 1

    mock_query_context.active_relationships = [
        {"relationship_id": 1, "target_columns": ["name", "email"]}
    ]

    mock_qo = MagicMock()
    mock_qo.columns = [{"column_name": "id"}]

    real_processor = BaseQueryContextProcessor(mock_query_context)

    result = real_processor._augment_query_object_with_relationship_columns(
        mock_qo, [mock_rel]
    )

    # Should have added name and email to columns
    assert result is not None
    # Verify columns were added (checking the result would have the augmented columns)
    column_names = [c.get("column_name") if isinstance(c, dict) else str(c) for c in result.columns]
    assert "name" in column_names
    assert "email" in column_names


def test_create_target_query_object(
    mock_query_context: MagicMock,
) -> None:
    """Test _create_target_query_object() creates appropriate query object for target dataset."""
    mock_rel = MagicMock()
    mock_rel.id = 1
    mock_rel.columns = [
        MagicMock(source_column_name="customer_id", target_column_name="id")
    ]

    source_qo = MagicMock()
    source_qo.columns = [{"column_name": "customer_id"}, {"column_name": "total"}]
    source_qo.groupby = []
    source_qo.metrics = []

    mock_query_context.active_relationships = [
        {"relationship_id": 1, "target_columns": ["name"]}
    ]

    real_processor = BaseQueryContextProcessor(mock_query_context)

    result = real_processor._create_target_query_object(
        source_qo, mock_rel, mock_query_context.active_relationships
    )

    # Should create query object with join columns + selected columns
    assert result is not None


def test_get_query_result_with_relationships_no_valid_relationships(
    mock_query_context: MagicMock,
    mock_query_object: MagicMock,
    mock_query_result: MagicMock,
) -> None:
    """Test _get_query_result_with_relationships() returns normal query when no valid relationships found."""
    mock_query_context.active_relationships = [{"relationship_id": 999}]
    mock_query_context.datasource.get_query_result.return_value = mock_query_result

    real_processor = BaseQueryContextProcessor(mock_query_context)

    with patch("superset.common.query_context_processor.is_feature_enabled") as mock_feat:
        mock_feat.return_value = True

        with patch("superset.common.query_context_processor.DatasetRelationshipDAO") as mock_dao:
            mock_dao.find_by_id.return_value = None  # No relationships found

            result = real_processor._get_query_result_with_relationships(
                mock_query_object, mock_query_context.active_relationships
            )

            # Should fall back to normal query
            assert result == mock_query_result
