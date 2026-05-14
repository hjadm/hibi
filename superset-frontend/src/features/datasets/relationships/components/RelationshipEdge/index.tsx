/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file that was agreed to
 * by you in writing, software distributed under the License
 * is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
 * CONDITIONS OF ANY KIND, either express or implied.  See
 * the License for the specific language governing permissions
 * and limitations under the License.
 */

import { memo } from 'react';
import {
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath,
  type EdgeProps,
} from '@xyflow/react';
import { useTheme } from '@apache-superset/core/theme';
import type { RelationshipEdgeData } from '../types';

/**
 * Relationship type → human-readable label.
 */
const CARDINALITY_LABEL: Record<string, string> = {
  one_to_one: '1:1',
  one_to_many: '1:N',
  many_to_one: 'N:1',
  many_to_many: 'N:N',
};

/**
 * Custom React Flow edge representing a dataset relationship.
 * Displays cardinality, join type, and cross-DB indicator.
 */
function RelationshipEdgeComponent({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
  style,
  markerEnd,
}: EdgeProps<RelationshipEdgeData>) {
  const theme = useTheme();
  const rel = data?.relationship;

  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    borderRadius: 16,
  });

  const isCrossDb = rel?.is_cross_database ?? false;
  const color = isCrossDb
    ? theme.colors.warning.base
    : selected
      ? theme.colors.primary.base
      : theme.colors.grayscale.light2;

  const cardinality = rel
    ? CARDINALITY_LABEL[rel.relationship_type] ?? '?'
    : '';
  const joinLabel = rel?.join_type ?? '';

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          ...style,
          stroke: color,
          strokeWidth: selected ? 2.5 : 1.5,
        }}
        markerEnd={markerEnd}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: 'all',
            fontSize: theme.typography.sizes.xs,
            fontFamily: theme.typography.families.sansSerif,
            background: theme.colors.grayscale.light5,
            border: `1px solid ${color}`,
            borderRadius: theme.borderRadius,
            padding: `2px ${theme.gridUnit * 2}px`,
            color: theme.colors.grayscale.dark1,
            whiteSpace: 'nowrap',
          }}
          className="nodrag nopan"
        >
          {cardinality}
          {joinLabel && (
            <span
              style={{
                marginLeft: 4,
                color: theme.colors.grayscale.light1,
                fontSize: theme.typography.sizes.xxxs,
              }}
            >
              {joinLabel}
            </span>
          )}
          {isCrossDb && (
            <span
              style={{
                marginLeft: 4,
                color: theme.colors.warning.dark1,
              }}
              title="Cross-database"
            >
              ⚡
            </span>
          )}
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

export const RelationshipEdge = memo(RelationshipEdgeComponent);
