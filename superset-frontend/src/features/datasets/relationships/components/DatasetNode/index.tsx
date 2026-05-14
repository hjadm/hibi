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

import { memo, useMemo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { useTheme } from '@superset-ui/core';
import type { DatasetNodeData } from '../types';

/**
 * Custom React Flow node that represents a dataset on the canvas.
 * Shows dataset name, database name, and a condensed column list.
 */
function DatasetNodeComponent({ data, selected }: NodeProps<DatasetNodeData>) {
  const theme = useTheme();
  const { dataset, label } = data;

  const columnList = useMemo(
    () =>
      dataset.columns
        .slice(0, 8)
        .map(c => c.column_name)
        .join(', ') + (dataset.columns.length > 8 ? ' …' : ''),
    [dataset.columns],
  );

  return (
    <div
      style={{
        background: selected ? theme.colors.primary.light4 : theme.colors.grayscale.light5,
        border: `2px solid ${selected ? theme.colors.primary.base : theme.colors.grayscale.light3}`,
        borderRadius: theme.borderRadius,
        padding: theme.gridUnit * 3,
        minWidth: 180,
        maxWidth: 280,
        fontSize: theme.typography.sizes.s,
        fontFamily: theme.typography.families.sansSerif,
        boxShadow: selected
          ? `0 0 0 1px ${theme.colors.primary.base}`
          : theme.shadows.sm,
      }}
    >
      {/* Connection handles */}
      <Handle
        type="target"
        position={Position.Left}
        style={{ background: theme.colors.primary.base, width: 8, height: 8 }}
      />
      <Handle
        type="source"
        position={Position.Right}
        style={{ background: theme.colors.primary.base, width: 8, height: 8 }}
      />

      {/* Header */}
      <div
        style={{
          fontWeight: theme.typography.weights.bold,
          fontSize: theme.typography.sizes.m,
          marginBottom: theme.gridUnit,
          color: theme.colors.grayscale.dark1,
        }}
      >
        {label || dataset.table_name}
      </div>

      {/* Database badge */}
      <div
        style={{
          fontSize: theme.typography.sizes.xs,
          color: theme.colors.grayscale.light1,
          marginBottom: theme.gridUnit * 2,
          display: 'flex',
          alignItems: 'center',
          gap: 4,
        }}
      >
        <span
          style={{
            background: theme.colors.primary.light4,
            color: theme.colors.primary.dark1,
            padding: '1px 6px',
            borderRadius: 4,
          }}
        >
          {dataset.database?.database_name ?? 'DB'}
        </span>
        {dataset.schema && <span>· {dataset.schema}</span>}
      </div>

      {/* Columns preview */}
      <div
        style={{
          fontSize: theme.typography.sizes.xs,
          color: theme.colors.grayscale.base,
          lineHeight: 1.4,
          maxHeight: 60,
          overflow: 'hidden',
        }}
      >
        {columnList}
      </div>
    </div>
  );
}

export const DatasetNode = memo(DatasetNodeComponent);
