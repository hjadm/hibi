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
from pytest_mock import MockerFixture

from superset.commands.dataset_relationship.delete import DeleteDatasetRelationshipCommand
from superset.commands.dataset_relationship.exceptions import (
    DatasetRelationshipDeleteFailedError,
    DatasetRelationshipNotFoundError,
)


@pytest.fixture
def mock_relationship() -> MagicMock:
    """Create a mock DatasetRelationship."""
    rel = MagicMock()
    rel.id = 1
    return rel


@pytest.fixture
def mock_relationships() -> list[MagicMock]:
    """Create multiple mock DatasetRelationships."""
    rel1 = MagicMock()
    rel1.id = 1
    rel2 = MagicMock()
    rel2.id = 2
    return [rel1, rel2]


def test_delete_command_success(
    mocker: MockerFixture, mock_relationship: MagicMock
) -> None:
    """Test successful deletion of a dataset relationship."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.delete.DatasetRelationshipDAO"
    )
    dao.find_by_ids.return_value = [mock_relationship]
    dao.delete.return_value = None

    command = DeleteDatasetRelationshipCommand(model_ids=[1])
    command.run()

    dao.find_by_ids.assert_called_once_with([1])
    dao.delete.assert_called_once_with([mock_relationship])


def test_delete_command_bulk_success(
    mocker: MockerFixture, mock_relationships: list[MagicMock]
) -> None:
    """Test successful bulk deletion of dataset relationships."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.delete.DatasetRelationshipDAO"
    )
    dao.find_by_ids.return_value = mock_relationships
    dao.delete.return_value = None

    command = DeleteDatasetRelationshipCommand(model_ids=[1, 2])
    command.run()

    dao.find_by_ids.assert_called_once_with([1, 2])
    dao.delete.assert_called_once_with(mock_relationships)


def test_delete_command_not_found(mocker: MockerFixture) -> None:
    """Test DeleteDatasetRelationshipCommand raises NotFoundError when relationship doesn't exist."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.delete.DatasetRelationshipDAO"
    )
    dao.find_by_ids.return_value = []  # No relationships found

    command = DeleteDatasetRelationshipCommand(model_ids=[999])

    with pytest.raises(DatasetRelationshipNotFoundError):
        command.run()

    dao.find_by_ids.assert_called_once_with([999])


def test_delete_command_partial_not_found(
    mocker: MockerFixture, mock_relationship: MagicMock
) -> None:
    """Test DeleteDatasetRelationshipCommand raises NotFoundError when some relationships don't exist."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.delete.DatasetRelationshipDAO"
    )
    # Request 2 IDs, only return 1 relationship
    dao.find_by_ids.return_value = [mock_relationship]

    command = DeleteDatasetRelationshipCommand(model_ids=[1, 999])

    with pytest.raises(DatasetRelationshipNotFoundError):
        command.run()

    dao.find_by_ids.assert_called_once_with([1, 999])


def test_delete_command_empty_list(mocker: MockerFixture) -> None:
    """Test DeleteDatasetRelationshipCommand raises NotFoundError for empty model list."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.delete.DatasetRelationshipDAO"
    )
    dao.find_by_ids.return_value = []

    command = DeleteDatasetRelationshipCommand(model_ids=[])

    with pytest.raises(DatasetRelationshipNotFoundError):
        command.run()


def test_delete_command_validate_finds_relationships(
    mocker: MockerFixture, mock_relationships: list[MagicMock]
) -> None:
    """Test that validate() finds and stores relationships."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.delete.DatasetRelationshipDAO"
    )
    dao.find_by_ids.return_value = mock_relationships

    command = DeleteDatasetRelationshipCommand(model_ids=[1, 2])
    command.validate()

    assert command._models == mock_relationships
    dao.find_by_ids.assert_called_once_with([1, 2])


def test_delete_command_validate_raises_not_found(
    mocker: MockerFixture,
) -> None:
    """Test that validate() raises NotFoundError when relationships don't exist."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.delete.DatasetRelationshipDAO"
    )
    dao.find_by_ids.return_value = []

    command = DeleteDatasetRelationshipCommand(model_ids=[999])

    with pytest.raises(DatasetRelationshipNotFoundError):
        command.validate()

    assert command._models is None
