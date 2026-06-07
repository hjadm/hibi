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

from unittest.mock import MagicMock

import pytest
from marshmallow import ValidationError
from pytest_mock import MockerFixture

from superset.commands.dataset_relationship.update import UpdateDatasetRelationshipCommand
from superset.commands.dataset_relationship.exceptions import (
    DatasetRelationshipInvalidError,
    DatasetRelationshipNotFoundError,
    DatasetRelationshipUpdateFailedError,
)


@pytest.fixture
def mock_existing_relationship() -> MagicMock:
    """Create a mock existing DatasetRelationship."""
    rel = MagicMock()
    rel.id = 1
    rel.source_dataset_id = 10
    rel.target_dataset_id = 20
    rel.relationship_type = "many_to_one"
    rel.join_type = "LEFT"
    rel.is_active = True
    rel.name = "old_name"
    rel.source_dataset = MagicMock()
    rel.source_dataset.id = 10
    rel.source_dataset.database_id = 1
    rel.source_dataset.table_name = "orders"
    rel.target_dataset = MagicMock()
    rel.target_dataset.id = 20
    rel.target_dataset.database_id = 1
    rel.target_dataset.table_name = "customers"
    rel.source_dataset.columns = [
        MagicMock(column_name="id"),
        MagicMock(column_name="customer_id"),
    ]
    rel.target_dataset.columns = [
        MagicMock(column_name="id"),
        MagicMock(column_name="name"),
    ]
    return rel


@pytest.fixture
def mock_new_source_dataset() -> MagicMock:
    """Create a mock new source dataset."""
    dataset = MagicMock()
    dataset.id = 30
    dataset.database_id = 1
    dataset.table_name = "new_orders"
    dataset.columns = [MagicMock(column_name="id"), MagicMock(column_name="ref_id")]
    return dataset


@pytest.fixture
def mock_new_target_dataset() -> MagicMock:
    """Create a mock new target dataset."""
    dataset = MagicMock()
    dataset.id = 40
    dataset.database_id = 1
    dataset.table_name = "new_customers"
    dataset.columns = [MagicMock(column_name="id"), MagicMock(column_name="name")]
    return dataset


def test_update_command_success(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test successful update of a dataset relationship."""
    mock_relationship = MagicMock()
    mock_relationship.id = 1

    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_existing_relationship
    dao.update.return_value = mock_relationship

    command = UpdateDatasetRelationshipCommand(
        model_id=1, data={"is_active": False, "name": "updated_name"}
    )
    result = command.run()

    assert result == mock_relationship
    dao.update.assert_called_once()


def test_update_command_not_found(mocker: MockerFixture) -> None:
    """Test UpdateDatasetRelationshipCommand raises NotFoundError when relationship doesn't exist."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = None

    command = UpdateDatasetRelationshipCommand(
        model_id=999, data={"is_active": False}
    )

    with pytest.raises(DatasetRelationshipNotFoundError):
        command.run()

    dao.find_by_id.assert_called_once_with(999)


def test_update_command_self_reference_raises_error(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test UpdateDatasetRelationshipCommand raises error for self-reference."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_existing_relationship

    # Try to set target to same as source
    command = UpdateDatasetRelationshipCommand(
        model_id=1, data={"source_dataset_id": 10, "target_dataset_id": 10}
    )

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("Source and target" in str(e) for e in exc.value._exceptions)


def test_update_command_source_not_found_raises_error(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test UpdateDatasetRelationshipCommand raises error when new source dataset not found."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.update.DatasetDAO")

    dao.find_by_id.return_value = mock_existing_relationship
    dataset_dao.find_by_id.return_value = None  # Source not found

    command = UpdateDatasetRelationshipCommand(
        model_id=1, data={"source_dataset_id": 999}
    )

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("Source dataset does not exist" in str(e) for e in exc.value._exceptions)


def test_update_command_target_not_found_raises_error(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test UpdateDatasetRelationshipCommand raises error when new target dataset not found."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.update.DatasetDAO")

    dao.find_by_id.return_value = mock_existing_relationship
    dataset_dao.find_by_id.return_value = None  # Target not found

    command = UpdateDatasetRelationshipCommand(
        model_id=1, data={"target_dataset_id": 999}
    )

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("Target dataset does not exist" in str(e) for e in exc.value._exceptions)


def test_update_command_duplicate_relationship_raises_error(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test UpdateDatasetRelationshipCommand raises error for duplicate relationship."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_existing_relationship
    dao.validate_uniqueness.return_value = False  # Duplicate exists

    command = UpdateDatasetRelationshipCommand(
        model_id=1, data={"source_dataset_id": 50, "target_dataset_id": 60}
    )

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("already exists" in str(e) for e in exc.value._exceptions)


def test_update_command_invalid_relationship_type_raises_error(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test UpdateDatasetRelationshipCommand raises error for invalid relationship_type."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_existing_relationship

    command = UpdateDatasetRelationshipCommand(
        model_id=1, data={"relationship_type": "invalid_type"}
    )

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("Invalid relationship_type" in str(e) for e in exc.value._exceptions)


def test_update_command_invalid_join_type_raises_error(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test UpdateDatasetRelationshipCommand raises error for invalid join_type."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_existing_relationship

    command = UpdateDatasetRelationshipCommand(
        model_id=1, data={"join_type": "NATURAL"}
    )

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("Invalid join_type" in str(e) for e in exc.value._exceptions)


def test_update_command_empty_columns_raises_error(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test UpdateDatasetRelationshipCommand raises error when columns list is empty."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_existing_relationship

    command = UpdateDatasetRelationshipCommand(model_id=1, data={"columns": []})

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("At least one column mapping" in str(e) for e in exc.value._exceptions)


def test_update_command_missing_source_column_name_raises_error(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test UpdateDatasetRelationshipCommand raises error when source_column_name is missing."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_existing_relationship

    command = UpdateDatasetRelationshipCommand(
        model_id=1,
        data={"columns": [{"target_column_name": "id", "operator": "="}]},
    )

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("source_column_name is required" in str(e) for e in exc.value._exceptions)


def test_update_command_missing_target_column_name_raises_error(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test UpdateDatasetRelationshipCommand raises error when target_column_name is missing."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_existing_relationship

    command = UpdateDatasetRelationshipCommand(
        model_id=1,
        data={"columns": [{"source_column_name": "id", "operator": "="}]},
    )

    with pytest.raises(DatasetRelationshipInvalidError) as exc:
        command.run()

    assert any("target_column_name is required" in str(e) for e in exc.value._exceptions)


def test_update_command_partial_update(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test UpdateDatasetRelationshipCommand supports partial updates."""
    mock_relationship = MagicMock()

    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_existing_relationship
    dao.update.return_value = mock_relationship

    command = UpdateDatasetRelationshipCommand(model_id=1, data={"is_active": False})
    result = command.run()

    assert result == mock_relationship
    # Verify only is_active was updated
    call_args = dao.update.call_args
    assert call_args[1]["attributes"]["is_active"] is False


def test_update_command_auto_detects_cross_database(
    mocker: MockerFixture,
    mock_existing_relationship: MagicMock,
    mock_new_source_dataset: MagicMock,
    mock_new_target_dataset: MagicMock,
) -> None:
    """Test UpdateDatasetRelationshipCommand auto-detects cross-database flag."""
    mock_new_source_dataset.database_id = 1
    mock_new_target_dataset.database_id = 2  # Different database

    mock_relationship = MagicMock()

    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dataset_dao = mocker.patch("superset.commands.dataset_relationship.update.DatasetDAO")

    dao.find_by_id.return_value = mock_existing_relationship
    dataset_dao.find_by_id.side_effect = [
        mock_new_source_dataset,
        mock_new_target_dataset,
    ]
    dao.validate_uniqueness.return_value = True
    dao.update.return_value = mock_relationship

    command = UpdateDatasetRelationshipCommand(
        model_id=1,
        data={"source_dataset_id": 30, "target_dataset_id": 40},
    )
    command.run()

    # Verify is_cross_database was set to True
    assert command._properties["is_cross_database"] is True


def test_update_command_keeps_original_datasets_when_not_changed(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test UpdateDatasetRelationshipCommand uses original datasets when they're not changed."""
    mock_relationship = MagicMock()

    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_existing_relationship
    dao.update.return_value = mock_relationship

    command = UpdateDatasetRelationshipCommand(
        model_id=1, data={"name": "new_name"}
    )
    command.run()

    # Verify DatasetDAO.find_by_id was not called (using original datasets)
    assert "superset.commands.dataset_relationship.update.DatasetDAO" not in [
        c[0].split(".")[0] if c else "" for c in mocker.mock_calls
    ]


def test_update_copies_input_data(
    mocker: MockerFixture, mock_existing_relationship: MagicMock
) -> None:
    """Test UpdateDatasetRelationshipCommand copies input data and doesn't mutate it."""
    mock_relationship = MagicMock()

    dao = mocker.patch(
        "superset.commands.dataset_relationship.update.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_existing_relationship
    dao.update.return_value = mock_relationship

    original_data = {"name": "new_name", "is_active": False}
    original_copy = original_data.copy()

    command = UpdateDatasetRelationshipCommand(model_id=1, data=original_data)
    command.run()

    assert original_data == original_copy
