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
"""Cross-database merge engine for dataset relationships.

When two related datasets reside in different databases, we cannot use
SQL JOINs.  Instead, we pull both result sets into Pandas and perform
an application-level merge.

:func:`merge` provides a cached merge operation that respects the
relationship's join type and column mappings.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, TYPE_CHECKING

import pandas as pd
from flask import current_app

from superset.common.relationship_query_cache import RelationshipQueryCache

if TYPE_CHECKING:
    from superset.models.dataset_relationships import DatasetRelationship

logger = logging.getLogger(__name__)

# Default limits from config
RELATIONSHIP_CROSS_DB_MAX_ROWS = 100_000
RELATIONSHIP_MAX_ACTIVE = 5


class RelationshipMerger:
    """Handles cross-database dataset merges using Pandas.

    This class is stateless — all information it needs is passed explicitly
    through method parameters.
    """

    @staticmethod
    def _build_merge_key(
        source_df_hash: str,
        target_df_hash: str,
        relationship_id: int,
        join_type: str,
        selected_columns: list[str],
    ) -> str:
        """Build a cache key for the merge operation.

        Parameters
        ----------
        source_df_hash : str
            Hash of the source DataFrame content.
        target_df_hash : str
            Hash of the target DataFrame content.
        relationship_id : int
            ID of the relationship being used.
        join_type : str
            SQL join type (LEFT, INNER, RIGHT, FULL).
        selected_columns : list[str]
            Target columns to include in the result.

        Returns
        -------
        str
            A deterministic cache key.
        """
        payload = json.dumps(
            {
                "source_hash": source_df_hash,
                "target_hash": target_df_hash,
                "relationship_id": relationship_id,
                "join": join_type,
                "columns": sorted(selected_columns),
            },
            sort_keys=True,
        )
        digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
        return f"hibi_merge:{digest}"

    @staticmethod
    def _hash_dataframe(df: pd.DataFrame) -> str:
        """Create a hash of DataFrame content for cache keys.

        Uses the first 1000 rows to create a representative hash without
        reading the entire DataFrame into memory for hashing.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to hash.

        Returns
        -------
        str
            Hexadecimal hash digest.
        """
        sample = df.head(min(1000, len(df)))
        # Convert to string representation for hashing
        sample_str = sample.to_json()
        return hashlib.sha256(sample_str.encode()).hexdigest()[:16]

    @staticmethod
    def _apply_row_limit(df: pd.DataFrame, max_rows: int) -> pd.DataFrame:
        """Apply row limit with warning if exceeded.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to limit.
        max_rows : int
            Maximum number of rows.

        Returns
        -------
        pd.DataFrame
            Truncated DataFrame.
        """
        if len(df) > max_rows:
            logger.warning(
                "Cross-database merge: DataFrame exceeds limit of %d rows "
                "(has %d rows). Truncating.",
                max_rows,
                len(df),
            )
            return df.head(max_rows)
        return df

    @staticmethod
    def _sanitize_column_name(name: str) -> str:
        """Sanitize column name for Pandas merge.

        Parameters
        ----------
        name : str
            Original column name.

        Returns
        -------
        str
            Sanitized column name.
        """
        # Replace special characters that might cause issues
        return name.replace(".", "_").replace(" ", "_").replace("-", "_")

    @staticmethod
    def merge(
        source_df: pd.DataFrame,
        target_df: pd.DataFrame,
        relationship: DatasetRelationship,
        selected_columns: list[str] | None = None,
        force_fresh: bool = False,
    ) -> pd.DataFrame:
        """Merge two DataFrames according to a relationship definition.

        Parameters
        ----------
        source_df : pd.DataFrame
            Source dataset DataFrame.
        target_df : pd.DataFrame
            Target dataset DataFrame.
        relationship : DatasetRelationship
            Relationship definition with column mappings.
        selected_columns : list[str], optional
            Target columns to include in the result. If None, includes
            all target columns.
        force_fresh : bool, default False
            Bypass cache and force fresh merge.

        Returns
        -------
        pd.DataFrame
            Merged DataFrame.

        Raises
        ------
        ValueError
            If relationship has no column mappings or if DataFrames
            don't contain required columns.
        """
        if not relationship.columns:
            raise ValueError("Relationship has no column mappings defined.")

        # Get max rows limit from config
        max_rows = current_app.config.get(
            "RELATIONSHIP_CROSS_DB_MAX_ROWS", RELATIONSHIP_CROSS_DB_MAX_ROWS
        )

        # Apply row limits
        source_df = RelationshipMerger._apply_row_limit(source_df, max_rows)
        target_df = RelationshipMerger._apply_row_limit(target_df, max_rows)

        # Build cache key
        source_hash = RelationshipMerger._hash_dataframe(source_df)
        target_hash = RelationshipMerger._hash_dataframe(target_df)
        cache_key = RelationshipMerger._build_merge_key(
            source_hash=source_hash,
            target_df_hash=target_hash,
            relationship_id=relationship.id,
            join_type=relationship.join_type,
            selected_columns=selected_columns or [],
        )

        # Check cache unless forcing fresh merge
        if not force_fresh:
            cached = RelationshipQueryCache.get(
                source_dataset_id=relationship.source_dataset_id,
                target_dataset_id=relationship.target_dataset_id,
                column_pairs=[
                    (c.source_column_name, c.target_column_name)
                    for c in relationship.columns
                ],
                join_type=relationship.join_type,
            )
            if cached:
                logger.info("Using cached merge result for relationship %s", relationship.id)
                return pd.DataFrame(cached["result"])

        # Build left_on and right_on from relationship columns
        left_on = []
        right_on = []

        for col in sorted(relationship.columns, key=lambda c: c.ordinal):
            src_col = col.source_column_name
            tgt_col = col.target_column_name

            if src_col not in source_df.columns:
                raise ValueError(
                    f"Source column '{src_col}' not found in source DataFrame. "
                    f"Available columns: {list(source_df.columns)}"
                )

            if tgt_col not in target_df.columns:
                raise ValueError(
                    f"Target column '{tgt_col}' not found in target DataFrame. "
                    f"Available columns: {list(target_df.columns)}"
                )

            left_on.append(src_col)
            right_on.append(tgt_col)

        # Determine which columns to select from target
        if selected_columns:
            # Use only selected columns (excluding join keys to avoid duplicates)
            target_cols_to_include = [
                col for col in selected_columns if col in target_df.columns
            ]
        else:
            # Include all non-join columns
            target_cols_to_include = [
                col for col in target_df.columns if col not in right_on
            ]

        # Map join type to pandas how parameter
        join_type_map = {
            "INNER": "inner",
            "LEFT": "left",
            "RIGHT": "right",
            "FULL": "outer",
            "LEFT OUTER": "left",
            "RIGHT OUTER": "right",
            "FULL OUTER": "outer",
        }
        how = join_type_map.get(
            relationship.join_type.upper(), relationship.join_type.lower()
        )

        # Perform the merge
        logger.info(
            "Merging DataFrames: how=%s, left_on=%s, right_on=%s, "
            "target_cols=%s",
            how,
            left_on,
            right_on,
            target_cols_to_include,
        )

        merged = pd.merge(
            left=source_df,
            right=target_df[right_on + target_cols_to_include],
            left_on=left_on,
            right_on=right_on,
            how=how,
        )

        # Cache the result
        try:
            RelationshipQueryCache.set(
                source_dataset_id=relationship.source_dataset_id,
                target_dataset_id=relationship.target_dataset_id,
                column_pairs=[
                    (c.source_column_name, c.target_column_name)
                    for c in relationship.columns
                ],
                join_type=relationship.join_type,
                result=merged.to_dict(orient="records"),
                ttl=current_app.config.get("CACHE_CACHE_TIMEOUT", 300),
            )
            logger.debug("Cached merge result for relationship %s", relationship.id)
        except Exception as ex:
            logger.warning("Failed to cache merge result: %s", ex)

        return merged

    @staticmethod
    def merge_multiple(
        source_df: pd.DataFrame,
        target_dfs: dict[int, pd.DataFrame],
        relationships: list[DatasetRelationship],
        selected_columns_map: dict[int, list[str]] | None = None,
        force_fresh: bool = False,
    ) -> pd.DataFrame:
        """Merge source DataFrame with multiple target DataFrames.

        Parameters
        ----------
        source_df : pd.DataFrame
            Source dataset DataFrame.
        target_dfs : dict[int, pd.DataFrame]
            Map of target dataset ID to DataFrame.
        relationships : list[DatasetRelationship]
            List of relationships to apply (ordered by priority).
        selected_columns_map : dict[int, list[str]], optional
            Map of relationship ID to selected target columns.
        force_fresh : bool, default False
            Bypass cache.

        Returns
        -------
        pd.DataFrame
            Merged DataFrame with all relationships applied.

        Raises
        ------
        ValueError
            If relationships exceed maximum allowed or if a target
            DataFrame is missing.
        """
        max_relationships = current_app.config.get(
            "RELATIONSHIP_MAX_ACTIVE", RELATIONSHIP_MAX_ACTIVE
        )

        if len(relationships) > max_relationships:
            raise ValueError(
                f"Cannot merge more than {max_relationships} relationships "
                f"at once (got {len(relationships)})."
            )

        result_df = source_df

        for rel in relationships:
            target_id = rel.target_dataset_id

            if target_id not in target_dfs:
                raise ValueError(
                    f"Target DataFrame for dataset ID {target_id} not provided."
                )

            target_df = target_dfs[target_id]
            selected_cols = (
                selected_columns_map.get(rel.id) if selected_columns_map else None
            )

            result_df = RelationshipMerger.merge(
                source_df=result_df,
                target_df=target_df,
                relationship=rel,
                selected_columns=selected_cols,
                force_fresh=force_fresh,
            )

        return result_df
