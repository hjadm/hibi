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
"""Command for getting a dataset relationship."""
from __future__ import annotations

import logging
from typing import Any

from flask_appbuilder.models.sqla import Model

from superset.commands.base import BaseCommand
from superset.commands.dataset_relationship.exceptions import (
    DatasetRelationshipForbiddenError,
    DatasetRelationshipNotFoundError,
)
from superset.daos.dataset_relationship import DatasetRelationshipDAO
from superset.exceptions import SupersetSecurityException

logger = logging.getLogger(__name__)


class GetDatasetRelationshipCommand(BaseCommand):
    """Get a dataset relationship by ID.

    Expected ``model_id``:
        The primary key of the relationship to retrieve.

    Returns:
        The :class:`DatasetRelationship` instance.

    Raises:
        DatasetRelationshipNotFoundError: If the relationship doesn't exist.
        DatasetRelationshipForbiddenError: If the user lacks read access.
    """

    def __init__(self, model_id: int):
        self._model_id = model_id

    def run(self) -> Model:
        """Retrieve and return a dataset relationship.

        Returns:
            The :class:`DatasetRelationship` instance.

        Raises:
            DatasetRelationshipNotFoundError: If not found.
            DatasetRelationshipForbiddenError: If access is denied.
        """
        self.validate()
        relationship = DatasetRelationshipDAO.find_by_id(self._model_id)
        return relationship

    def validate(self) -> None:
        """Check that the relationship exists and the user has access.

        Raises:
            DatasetRelationshipNotFoundError: If relationship doesn't exist.
            DatasetRelationshipForbiddenError: If user lacks access.
        """
        relationship = DatasetRelationshipDAO.find_by_id(self._model_id)
        if not relationship:
            raise DatasetRelationshipNotFoundError()

        # Check read permission on the source dataset
        try:
            from superset import security_manager

            source_dataset = relationship.source_dataset
            if not security_manager.can_access(
                "can_read", source_dataset, "dataset"
            ):
                raise DatasetRelationshipForbiddenError()

        except SupersetSecurityException as ex:
            logger.error("Permission check failed for relationship %s", self._model_id)
            raise DatasetRelationshipForbiddenError() from ex
