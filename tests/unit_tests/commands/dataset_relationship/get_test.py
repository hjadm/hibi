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
from pytest_mock import MockerFixture

from superset.commands.dataset_relationship.get import GetDatasetRelationshipCommand
from superset.commands.dataset_relationship.exceptions import (
    DatasetRelationshipForbiddenError,
    DatasetRelationshipNotFoundError,
)
from superset.exceptions import SupersetSecurityException


@pytest.fixture
def mock_relationship() -> MagicMock:
    """Create a mock DatasetRelationship."""
    rel = MagicMock()
    rel.id = 1
    rel.source_dataset_id = 10
    rel.source_dataset = MagicMock()
    rel.source_dataset.id = 10
    return rel


@pytest.fixture
def mock_security_manager() -> MagicMock:
    """Create a mock security_manager."""
    sm = MagicMock()
    sm.can_access.return_value = True
    return sm


def test_get_command_success(
    mocker: MockerFixture, mock_relationship: MagicMock
) -> None:
    """Test successful retrieval of a dataset relationship."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.get.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_relationship

    with patch("superset.commands.dataset_relationship.get.security_manager"):
        from superset import security_manager

        mocker.patch.object(
            security_manager, "can_access", return_value=True
        )

        command = GetDatasetRelationshipCommand(model_id=1)
        result = command.run()

        assert result == mock_relationship
        dao.find_by_id.assert_called_once_with(1)


def test_get_command_not_found(mocker: MockerFixture) -> None:
    """Test GetDatasetRelationshipCommand raises NotFoundError when relationship doesn't exist."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.get.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = None

    command = GetDatasetRelationshipCommand(model_id=999)

    with pytest.raises(DatasetRelationshipNotFoundError):
        command.run()

    dao.find_by_id.assert_called_once_with(999)


def test_get_command_forbidden_when_user_lacks_permission(
    mocker: MockerFixture, mock_relationship: MagicMock
) -> None:
    """Test GetDatasetRelationshipCommand raises ForbiddenError when user lacks read access."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.get.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_relationship

    mock_sm = MagicMock()
    mock_sm.can_access.return_value = False

    with patch(
        "superset.commands.dataset_relationship.get.security_manager", mock_sm
    ):
        command = GetDatasetRelationshipCommand(model_id=1)

        with pytest.raises(DatasetRelationshipForbiddenError):
            command.run()


def test_get_command_forbidden_on_security_exception(
    mocker: MockerFixture, mock_relationship: MagicMock
) -> None:
    """Test GetDatasetRelationshipCommand raises ForbiddenError when SupersetSecurityException occurs."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.get.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_relationship

    mock_sm = MagicMock()
    mock_sm.can_access.side_effect = SupersetSecurityException("Access denied")

    with patch(
        "superset.commands.dataset_relationship.get.security_manager", mock_sm
    ):
        command = GetDatasetRelationshipCommand(model_id=1)

        with pytest.raises(DatasetRelationshipForbiddenError):
            command.run()


def test_get_command_validate_checks_existence(
    mocker: MockerFixture, mock_relationship: MagicMock
) -> None:
    """Test that validate() checks relationship existence."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.get.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = mock_relationship

    command = GetDatasetRelationshipCommand(model_id=1)
    command.validate()

    dao.find_by_id.assert_called_once_with(1)


def test_get_command_validate_raises_not_found(
    mocker: MockerFixture,
) -> None:
    """Test that validate() raises NotFoundError when relationship doesn't exist."""
    dao = mocker.patch(
        "superset.commands.dataset_relationship.get.DatasetRelationshipDAO"
    )
    dao.find_by_id.return_value = None

    command = GetDatasetRelationshipCommand(model_id=999)

    with pytest.raises(DatasetRelationshipNotFoundError):
        command.validate()
