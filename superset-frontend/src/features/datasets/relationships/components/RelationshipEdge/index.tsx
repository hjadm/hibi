/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  This ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except be agreed to
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
import type { RelationshipEdge as RelationshipEdgeType } from '../../types';

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
}: EdgeProps<RelationshipEdgeType>) {
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
    ? '#fcc700'
    : selected
      ? '#2893B3'
      : '#bbb';

  const cardinality = rel
    ? CARDINALITY_LABEL[rel.relationship_type] ?? '?'
    : '';
  const joinLabel = rel?.join_type ?? '';

  // Build column pair labels
  const columnLabels = rel?.columns
    ?.map(c => `${c.source_column_name} = ${c.target_column_name}`)
    ?.join(', ') ?? '';
  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          ...(style as React.CSSProperties),
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
            fontSize: '12px',
            fontFamily: 'inherit',
            background: '#fafafa',
            border: `1px solid ${color}`,
            borderRadius: 4,
            padding: '2px 8px',
            color: '#333',
            whiteSpace: 'nowrap',
          }}
          className="nodrag nopan"
        >
          {cardinality}
          {joinLabel && (
            <span
              style={{
                marginLeft: 4,
                color: '#999',
                fontSize: '10px',
              }}
            >
              {joinLabel}
            </span>
          )}
          {columnLabels && (
            <div style={{ fontSize: '10px', color: '#2893B3', marginTop: 2 }}>
              {columnLabels}
            </div>
          )}
          {isCrossDb && (
            <span
              style={{
                marginLeft: 4,
                color: '#b38f00',
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
