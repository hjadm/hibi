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

import pytest
from marshmallow import ValidationError
from pytest_mock import MockerFixture

from superset.commands.dataset_relationship.create import CreateDatasetRelationshipCommand
from superset.commands.dataset_relationship.exceptions import (
    DatasetRelationshipCreateFailedError,
    DatasetRelationshipInvalidError,
)


@pytest.fixture
def mock_source_dataset() -> MagicMock:
    """Create a mock source dataset."""
    dataset = MagicMock()
    dataset.id = 10
    dataset.database_id = 1
    dataset.table_name = "orders"
    dataset.columns = [
        MagicMock(column_name="id"),
        MagicMock(column_name="customer_id"),
        MagicMock(column_name="total"),
    ]
    return dataset


@pytest.fixture
def mock_target_dataset() -> MagicMock:
    """Create a mock target dataset."""
    dataset = MagicMock()
    dataset.id = 20
    dataset.database_id = 1
    dataset.table_name = "customers"
    dataset.columns = [
        MagicMock(column_name="id"),
        MagicMock(column_name="name"),
        MagicMock(column_name="email"),
    ]
    return dataset


@pytest.fixture
def valid_relationship_data() -> dict:
    """Return valid relationship data for testing."""
    return {
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "is_active": True,
        "name": "orders_to_customers",
        "description": "Join orders with customers",
        "columns": [
            {
                "source_column_name": "customer_id",
                "target_column_name": "id",
                "operator": "=",
                "ordinal": 0,
            }
        ],
    }


def test_create_command_success(
    mocker: MockerFixture,
    mock_source_dataset: MagicMock,
    mock_target_dataset: MagicMock,
    valid_relationship_data: dict,
) -> None:
    """Test successful creation of a dataset relationship."""
    mock_relationship = MagicMock()
    mock_relationship.id = 1

    dao = mocker.patch(
        "superset.commands.dataset_relationship.create.DatasetRelationshipDAO"
    )
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.create.DatasetDAO")

    dataset_dao.find_by_id.side_effect = [mock_source_dataset, mock_target_dataset]
    dao.validate_uniqueness.return_value = True
    dao.create.return_value = mock_relationship

    command = CreateDatasetRelationshipCommand(valid_relationship_data)
    result = command.run()

    assert result == mock_relationship
    dao.create.assert_called_once()


def test_create_command_self_reference_raises_error(
    mocker: MockerFixture,
    mock_source_dataset: MagicMock,
) -> None:
    """Test CreateDatasetRelationshipCommand raises error for self-reference."""
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.create.DatasetDAO")
    dataset_dao.find_by_id.return_value = mock_source_dataset

    data = {
        "source_dataset_id": 10,
        "target_dataset_id": 10,  # Same as source
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "columns": [
            {"source_column_name": "id", "target_column_name": "id", "operator": "="}
        ],
    }

    command = CreateDatasetRelationshipCommand(data)

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any(
        isinstance(e, ValidationError) and "Source and target" in str(e.messages[0])
        for e in exc.value._exceptions
    )


def test_create_command_source_not_found_raises_error(
    mocker: MockerFixture,
) -> None:
    """Test CreateDatasetRelationshipCommand raises error when source dataset not found."""
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.create.DatasetDAO")
    dataset_dao.find_by_id.return_value = None  # Source not found

    data = {
        "source_dataset_id": 999,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "columns": [
            {"source_column_name": "id", "target_column_name": "id", "operator": "="}
        ],
    }

    command = CreateDatasetRelationshipCommand(data)

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("Source dataset does not exist" in str(e) for e in exc.value._exceptions)


def test_create_command_target_not_found_raises_error(
    mocker: MockerFixture,
    mock_source_dataset: MagicMock,
) -> None:
    """Test CreateDatasetRelationshipCommand raises error when target dataset not found."""
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.create.DatasetDAO")
    dataset_dao.find_by_id.side_effect = [mock_source_dataset, None]

    data = {
        "source_dataset_id": 10,
        "target_dataset_id": 999,
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "columns": [
            {"source_column_name": "id", "target_column_name": "id", "operator": "="}
        ],
    }

    command = CreateDatasetRelationshipCommand(data)

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("Target dataset does not exist" in str(e) for e in exc.value._exceptions)


def test_create_command_duplicate_relationship_raises_error(
    mocker: MockerFixture,
    mock_source_dataset: MagicMock,
    mock_target_dataset: MagicMock,
) -> None:
    """Test CreateDatasetRelationshipCommand raises error for duplicate relationship."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.create.DatasetRelationshipDAO"
    )
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.create.DatasetDAO")

    dataset_dao.find_by_id.side_effect = [mock_source_dataset, mock_target_dataset]
    dao.validate_uniqueness.return_value = False  # Duplicate exists

    data = {
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "columns": [
            {"source_column_name": "id", "target_column_name": "id", "operator": "="}
        ],
    }

    command = CreateDatasetRelationshipCommand(data)

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("already exists" in str(e) for e in exc.value._exceptions)


def test_create_command_invalid_relationship_type_raises_error(
    mocker: MockerFixture,
) -> None:
    """Test CreateDatasetRelationshipCommand raises error for invalid relationship_type."""
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.create.DatasetDAO")
    mock_src = MagicMock()
    mock_tgt = MagicMock()
    dataset_dao.find_by_id.side_effect = [mock_src, mock_tgt]

    data = {
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "invalid_type",
        "join_type": "LEFT",
        "columns": [
            {"source_column_name": "id", "target_column_name": "id", "operator": "="}
        ],
    }

    command = CreateDatasetRelationshipCommand(data)

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("Invalid relationship_type" in str(e) for e in exc.value._exceptions)


def test_create_command_invalid_join_type_raises_error(
    mocker: MockerFixture,
) -> None:
    """Test CreateDatasetRelationshipCommand raises error for invalid join_type."""
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.create.DatasetDAO")
    mock_src = MagicMock()
    mock_tgt = MagicMock()
    dataset_dao.find_by_id.side_effect = [mock_src, mock_tgt]

    data = {
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "join_type": "NATURAL",  # Invalid join type
        "columns": [
            {"source_column_name": "id", "target_column_name": "id", "operator": "="}
        ],
    }

    command = CreateDatasetRelationshipCommand(data)

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("Invalid join_type" in str(e) for e in exc.value._exceptions)


def test_create_command_empty_columns_raises_error(
    mocker: MockerFixture,
) -> None:
    """Test CreateDatasetRelationshipCommand raises error when columns list is empty."""
    data = {
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "columns": [],  # Empty columns
    }

    command = CreateDatasetRelationshipCommand(data)

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("At least one column mapping" in str(e) for e in exc.value._exceptions)


def test_create_command_missing_source_column_name_raises_error(
    mocker: MockerFixture,
) -> None:
    """Test CreateDatasetRelationshipCommand raises error when source_column_name is missing."""
    data = {
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "columns": [
            {"target_column_name": "id", "operator": "="}  # Missing source_column_name
        ],
    }

    command = CreateDatasetRelationshipCommand(data)

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("source_column_name is required" in str(e) for e in exc.value._exceptions)


def test_create_command_missing_target_column_name_raises_error(
    mocker: MockerFixture,
) -> None:
    """Test CreateDatasetRelationshipCommand raises error when target_column_name is missing."""
    data = {
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "columns": [
            {"source_column_name": "id", "operator": "="}  # Missing target_column_name
        ],
    }

    command = CreateDatasetRelationshipCommand(data)

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("target_column_name is required" in str(e) for e in exc.value._exceptions)


def test_create_column_not_in_source_dataset_raises_error(
    mocker: MockerFixture,
    mock_source_dataset: MagicMock,
    mock_target_dataset: MagicMock,
) -> None:
    """Test CreateDatasetRelationshipCommand raises error when source column not found."""
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.create.DatasetDAO")
    dataset_dao.find_by_id.side_effect = [mock_source_dataset, mock_target_dataset]

    data = {
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "columns": [
            {
                "source_column_name": "nonexistent_column",
                "target_column_name": "id",
                "operator": "=",
            }
        ],
    }

    command = CreateDatasetRelationshipCommand(data)

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("not found in source dataset" in str(e) for e in exc.value._exceptions)


def test_create_column_not_in_target_dataset_raises_error(
    mocker: MockerFixture,
    mock_source_dataset: MagicMock,
    mock_target_dataset: MagicMock,
) -> None:
    """Test CreateDatasetRelationshipCommand raises error when target column not found."""
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.create.DatasetDAO")
    dataset_dao.find_by_id.side_effect = [mock_source_dataset, mock_target_dataset]

    data = {
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "columns": [
            {
                "source_column_name": "customer_id",
                "target_column_name": "nonexistent_column",
                "operator": "=",
            }
        ],
    }

    command = CreateDatasetRelationshipCommand(data)

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("not found in target dataset" in str(e) for e in exc.value._exceptions)


def test_create_auto_detects_cross_database(
    mocker: MockerFixture,
    mock_source_dataset: MagicMock,
    mock_target_dataset: MagicMock,
    valid_relationship_data: dict,
) -> None:
    """Test CreateDatasetRelationshipCommand auto-detects cross-database flag."""
    mock_source_dataset.database_id = 1
    mock_target_dataset.database_id = 2  # Different database

    mock_relationship = MagicMock()
    mock_relationship.id = 1

    dao = mocker.patch(
        "superset.commands.dataset_relationship.create.DatasetRelationshipDAO"
    )
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.create.DatasetDAO")

    dataset_dao.find_by_id.side_effect = [mock_source_dataset, mock_target_dataset]
    dao.validate_uniqueness.return_value = True
    dao.create.return_value = mock_relationship

    command = CreateDatasetRelationshipCommand(valid_relationship_data)
    command.run()

    # Verify is_cross_database was set to True
    assert command._properties["is_cross_database"] is True
    dao.create.assert_called_once()


def test_create_with_same_database_sets_cross_db_false(
    mocker: MockerFixture,
    mock_source_dataset: MagicMock,
    mock_target_dataset: MagicMock,
    valid_relationship_data: dict,
) -> None:
    """Test CreateDatasetRelationshipCommand sets is_cross_database=False for same database."""
    mock_source_dataset.database_id = 1
    mock_target_dataset.database_id = 1  # Same database

    mock_relationship = MagicMock()
    mock_relationship.id = 1

    dao = mocker.patch(
        "superset.commands.dataset_relationship.create.DatasetRelationshipDAO"
    )
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.create.DatasetDAO")

    dataset_dao.find_by_id.side_effect = [mock_source_dataset, mock_target_dataset]
    dao.validate_uniqueness.return_value = True
    dao.create.return_value = mock_relationship

    command = CreateDatasetRelationshipCommand(valid_relationship_data)
    command.run()

    # Verify is_cross_database was set to False
    assert command._properties["is_cross_database"] is False


def test_create_copies_input_data(
    mocker: MockerFixture,
    mock_source_dataset: MagicMock,
    mock_target_dataset: MagicMock,
) -> None:
    """Test CreateDatasetRelationshipCommand copies input data and doesn't mutate it."""
    mock_relationship = MagicMock()

    dao = mocker.patch(
        "superset.commands.dataset_relationship.create.DatasetRelationshipDAO"
    )
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.create.DatasetDAO")

    dataset_dao.find_by_id.side_effect = [mock_source_dataset, mock_target_dataset]
    dao.validate_uniqueness.return_value = True
    dao.create.return_value = mock_relationship

    original_data = {
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "columns": [
            {"source_column_name": "customer_id", "target_column_name": "id"}
        ],
    }
    original_copy = original_data.copy()

    command = CreateDatasetRelationshipCommand(original_data)
    command.run()

    assert original_data == original_copy
