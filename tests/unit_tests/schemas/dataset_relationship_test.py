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

import pytest
from marshmallow import ValidationError

from superset.dataset_relationship.schemas import (
    DatasetRelationshipColumnPostSchema,
    DatasetRelationshipColumnPutSchema,
    DatasetRelationshipPostSchema,
    DatasetRelationshipPutSchema,
)


# =============================================================================
# DatasetRelationshipColumnPostSchema tests
# =============================================================================


def test_column_post_schema_all_fields() -> None:
    """Test loading all fields in column post schema."""
    schema = DatasetRelationshipColumnPostSchema()
    result = schema.load({
        "source_column_name": "customer_id",
        "target_column_name": "id",
        "operator": "=",
        "ordinal": 0,
    })
    assert result["source_column_name"] == "customer_id"
    assert result["target_column_name"] == "id"
    assert result["operator"] == "="
    assert result["ordinal"] == 0


def test_column_post_schema_required_fields_only() -> None:
    """Test loading with only required fields."""
    schema = DatasetRelationshipColumnPostSchema()
    result = schema.load({
        "source_column_name": "customer_id",
        "target_column_name": "id",
    })
    assert result["source_column_name"] == "customer_id"
    assert result["target_column_name"] == "id"
    assert result["operator"] == "="  # Default
    assert result["ordinal"] == 0  # Default


def test_column_post_schema_missing_source_column() -> None:
    """Test that missing source_column_name raises ValidationError."""
    schema = DatasetRelationshipColumnPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({"target_column_name": "id"})
    assert "source_column_name" in exc_info.value.messages


def test_column_post_schema_missing_target_column() -> None:
    """Test that missing target_column_name raises ValidationError."""
    schema = DatasetRelationshipColumnPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({"source_column_name": "customer_id"})
    assert "target_column_name" in exc_info.value.messages


def test_column_post_schema_empty_source_column() -> None:
    """Test that empty source_column_name raises ValidationError."""
    schema = DatasetRelationshipColumnPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({"source_column_name": "", "target_column_name": "id"})
    assert "source_column_name" in exc_info.value.messages


def test_column_post_schema_invalid_operator() -> None:
    """Test that invalid operator raises ValidationError."""
    schema = DatasetRelationshipColumnPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "source_column_name": "customer_id",
            "target_column_name": "id",
            "operator": "LIKE",  # Not in COLUMN_OPERATORS
        })
    assert "operator" in exc_info.value.messages


def test_column_post_schema_negative_ordinal() -> None:
    """Test that negative ordinal raises ValidationError."""
    schema = DatasetRelationshipColumnPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "source_column_name": "customer_id",
            "target_column_name": "id",
            "ordinal": -1,
        })
    assert "ordinal" in exc_info.value.messages


def test_column_post_schema_valid_operators() -> None:
    """Test that all valid operators are accepted."""
    schema = DatasetRelationshipColumnPostSchema()
    for operator in ["=", "!=", ">", "<", ">=", "<="]:
        result = schema.load({
            "source_column_name": "customer_id",
            "target_column_name": "id",
            "operator": operator,
        })
        assert result["operator"] == operator


# =============================================================================
# DatasetRelationshipColumnPutSchema tests
# =============================================================================


def test_column_put_schema_all_fields() -> None:
    """Test loading all fields in column put schema."""
    schema = DatasetRelationshipColumnPutSchema()
    result = schema.load({
        "id": 1,
        "source_column_name": "customer_id",
        "target_column_name": "id",
        "operator": "=",
        "ordinal": 0,
    })
    assert result["id"] == 1
    assert result["source_column_name"] == "customer_id"
    assert result["target_column_name"] == "id"


def test_column_put_schema_without_id() -> None:
    """Test that id is optional in put schema."""
    schema = DatasetRelationshipColumnPutSchema()
    result = schema.load({
        "source_column_name": "customer_id",
        "target_column_name": "id",
    })
    assert "id" not in result or result.get("id") is None


# =============================================================================
# DatasetRelationshipPostSchema tests
# =============================================================================


def test_post_schema_all_fields() -> None:
    """Test loading all fields in relationship post schema."""
    schema = DatasetRelationshipPostSchema()
    result = schema.load({
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
    })
    assert result["source_dataset_id"] == 10
    assert result["target_dataset_id"] == 20
    assert result["relationship_type"] == "many_to_one"
    assert result["join_type"] == "LEFT"
    assert result["is_active"] is True
    assert result["name"] == "orders_to_customers"
    assert len(result["columns"]) == 1


def test_post_schema_required_fields_only() -> None:
    """Test loading with only required fields."""
    schema = DatasetRelationshipPostSchema()
    result = schema.load({
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "columns": [
            {
                "source_column_name": "customer_id",
                "target_column_name": "id",
            }
        ],
    })
    assert result["source_dataset_id"] == 10
    assert result["target_dataset_id"] == 20
    assert result["relationship_type"] == "many_to_one"
    assert result["join_type"] == "LEFT"  # Default
    assert result["is_active"] is True  # Default
    assert "name" not in result


def test_post_schema_missing_source_dataset_id() -> None:
    """Test that missing source_dataset_id raises ValidationError."""
    schema = DatasetRelationshipPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "target_dataset_id": 20,
            "relationship_type": "many_to_one",
            "columns": [{"source_column_name": "x", "target_column_name": "y"}],
        })
    assert "source_dataset_id" in exc_info.value.messages


def test_post_schema_missing_target_dataset_id() -> None:
    """Test that missing target_dataset_id raises ValidationError."""
    schema = DatasetRelationshipPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "source_dataset_id": 10,
            "relationship_type": "many_to_one",
            "columns": [{"source_column_name": "x", "target_column_name": "y"}],
        })
    assert "target_dataset_id" in exc_info.value.messages


def test_post_schema_missing_relationship_type() -> None:
    """Test that missing relationship_type raises ValidationError."""
    schema = DatasetRelationshipPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "source_dataset_id": 10,
            "target_dataset_id": 20,
            "columns": [{"source_column_name": "x", "target_column_name": "y"}],
        })
    assert "relationship_type" in exc_info.value.messages


def test_post_schema_missing_columns() -> None:
    """Test that missing columns raises ValidationError."""
    schema = DatasetRelationshipPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "source_dataset_id": 10,
            "target_dataset_id": 20,
            "relationship_type": "many_to_one",
        })
    assert "columns" in exc_info.value.messages


def test_post_schema_empty_columns() -> None:
    """Test that empty columns list raises ValidationError."""
    schema = DatasetRelationshipPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "source_dataset_id": 10,
            "target_dataset_id": 20,
            "relationship_type": "many_to_one",
            "columns": [],
        })
    assert "columns" in exc_info.value.messages


def test_post_schema_self_reference_validation() -> None:
    """Test that self-reference raises ValidationError."""
    schema = DatasetRelationshipPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "source_dataset_id": 10,
            "target_dataset_id": 10,  # Same as source
            "relationship_type": "many_to_one",
            "columns": [{"source_column_name": "x", "target_column_name": "y"}],
        })
    assert "target_dataset_id" in exc_info.value.messages


def test_post_schema_invalid_relationship_type() -> None:
    """Test that invalid relationship_type raises ValidationError."""
    schema = DatasetRelationshipPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "source_dataset_id": 10,
            "target_dataset_id": 20,
            "relationship_type": "invalid_type",
            "columns": [{"source_column_name": "x", "target_column_name": "y"}],
        })
    assert "relationship_type" in exc_info.value.messages


def test_post_schema_valid_relationship_types() -> None:
    """Test that all valid relationship types are accepted."""
    schema = DatasetRelationshipPostSchema()
    for rel_type in ["one_to_one", "one_to_many", "many_to_one", "many_to_many"]:
        result = schema.load({
            "source_dataset_id": 10,
            "target_dataset_id": 20,
            "relationship_type": rel_type,
            "columns": [{"source_column_name": "x", "target_column_name": "y"}],
        })
        assert result["relationship_type"] == rel_type


def test_post_schema_invalid_join_type() -> None:
    """Test that invalid join_type raises ValidationError."""
    schema = DatasetRelationshipPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "source_dataset_id": 10,
            "target_dataset_id": 20,
            "relationship_type": "many_to_one",
            "join_type": "NATURAL",  # Invalid
            "columns": [{"source_column_name": "x", "target_column_name": "y"}],
        })
    assert "join_type" in exc_info.value.messages


def test_post_schema_valid_join_types() -> None:
    """Test that all valid join types are accepted."""
    schema = DatasetRelationshipPostSchema()
    for join_type in ["INNER", "LEFT", "RIGHT", "FULL"]:
        result = schema.load({
            "source_dataset_id": 10,
            "target_dataset_id": 20,
            "relationship_type": "many_to_one",
            "join_type": join_type,
            "columns": [{"source_column_name": "x", "target_column_name": "y"}],
        })
        assert result["join_type"] == join_type


def test_post_schema_nullable_name() -> None:
    """Test that name accepts None."""
    schema = DatasetRelationshipPostSchema()
    result = schema.load({
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "name": None,
        "columns": [{"source_column_name": "x", "target_column_name": "y"}],
    })
    assert result["name"] is None


def test_post_schema_nullable_description() -> None:
    """Test that description accepts None."""
    schema = DatasetRelationshipPostSchema()
    result = schema.load({
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "description": None,
        "columns": [{"source_column_name": "x", "target_column_name": "y"}],
    })
    assert result["description"] is None


# =============================================================================
# DatasetRelationshipPutSchema tests
# =============================================================================


def test_put_schema_all_fields() -> None:
    """Test loading all fields in relationship put schema."""
    schema = DatasetRelationshipPutSchema()
    result = schema.load({
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "is_active": False,
        "name": "updated_name",
        "description": "Updated description",
        "columns": [
            {
                "source_column_name": "customer_id",
                "target_column_name": "id",
                "operator": "=",
            }
        ],
    })
    assert result["source_dataset_id"] == 10
    assert result["is_active"] is False
    assert result["name"] == "updated_name"


def test_put_schema_empty() -> None:
    """Test loading empty payload (all fields optional)."""
    schema = DatasetRelationshipPutSchema()
    result = schema.load({})
    assert result == {}


def test_put_schema_partial_update_is_active() -> None:
    """Test partial update with only is_active."""
    schema = DatasetRelationshipPutSchema()
    result = schema.load({"is_active": False})
    assert result == {"is_active": False}


def test_put_schema_partial_update_name() -> None:
    """Test partial update with only name."""
    schema = DatasetRelationshipPutSchema()
    result = schema.load({"name": "new_name"})
    assert result == {"name": "new_name"}


def test_put_schema_partial_update_columns() -> None:
    """Test partial update with only columns."""
    schema = DatasetRelationshipPutSchema()
    result = schema.load({
        "columns": [
            {"source_column_name": "id", "target_column_name": "ref_id"}
        ]
    })
    assert "columns" in result
    assert len(result["columns"]) == 1


def test_put_schema_empty_columns_raises_error() -> None:
    """Test that empty columns list raises ValidationError."""
    schema = DatasetRelationshipPutSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({"columns": []})
    assert "columns" in exc_info.value.messages


def test_put_schema_invalid_relationship_type() -> None:
    """Test that invalid relationship_type raises ValidationError."""
    schema = DatasetRelationshipPutSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({"relationship_type": "invalid_type"})
    assert "relationship_type" in exc_info.value.messages


def test_put_schema_invalid_join_type() -> None:
    """Test that invalid join_type raises ValidationError."""
    schema = DatasetRelationshipPutSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({"join_type": "NATURAL"})
    assert "join_type" in exc_info.value.messages


def test_put_schema_nullable_name() -> None:
    """Test that name accepts None."""
    schema = DatasetRelationshipPutSchema()
    result = schema.load({"name": None})
    assert result["name"] is None


def test_put_schema_nullable_description() -> None:
    """Test that description accepts None."""
    schema = DatasetRelationshipPutSchema()
    result = schema.load({"description": None})
    assert result["description"] is None


def test_put_schema_all_optional_fields() -> None:
    """Test that all fields are optional in PUT schema."""
    schema = DatasetRelationshipPutSchema()
    # Should not raise ValidationError
    result = schema.load({})
    assert result == {}


# =============================================================================
# Edge cases and comprehensive tests
# =============================================================================


def test_post_schema_multiple_columns() -> None:
    """Test loading multiple column mappings."""
    schema = DatasetRelationshipPostSchema()
    result = schema.load({
        "source_dataset_id": 10,
        "target_dataset_id": 20,
        "relationship_type": "many_to_one",
        "columns": [
            {
                "source_column_name": "customer_id",
                "target_column_name": "id",
                "operator": "=",
                "ordinal": 0,
            },
            {
                "source_column_name": "region_id",
                "target_column_name": "region_id",
                "operator": "=",
                "ordinal": 1,
            },
        ],
    })
    assert len(result["columns"]) == 2


def test_post_schema_name_too_long() -> None:
    """Test that name exceeding max length raises ValidationError."""
    schema = DatasetRelationshipPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "source_dataset_id": 10,
            "target_dataset_id": 20,
            "relationship_type": "many_to_one",
            "name": "x" * 256,  # Exceeds max 255
            "columns": [{"source_column_name": "x", "target_column_name": "y"}],
        })
    assert "name" in exc_info.value.messages


def test_column_post_schema_column_name_too_long() -> None:
    """Test that column names exceeding max length raise ValidationError."""
    schema = DatasetRelationshipColumnPostSchema()
    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "source_column_name": "x" * 256,
            "target_column_name": "y",
        })
    assert "source_column_name" in exc_info.value.messages
