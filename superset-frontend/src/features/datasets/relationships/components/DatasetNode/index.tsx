/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import type { DatasetNode as DatasetNodeType } from '../../types';

function DatasetNodeComponent({ data, selected }: NodeProps<DatasetNodeType>) {
  const { dataset, label } = data;
  const columns = dataset.columns ?? [];

  return (
    <div
      style={{
        background: selected ? '#e0f0f5' : '#fff',
        border: `2px solid ${selected ? '#2893B3' : '#ddd'}`,
        borderRadius: 6,
        minWidth: 200,
        maxWidth: 300,
        fontSize: '13px',
        fontFamily: 'inherit',
        boxShadow: selected
          ? '0 0 0 1px #2893B3, 0 2px 8px rgba(40,147,179,0.15)'
          : '0 1px 4px rgba(0,0,0,0.08)',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '10px 12px',
          borderBottom: '1px solid #e8e8e8',
          background: selected ? '#d4eaf0' : '#f7f7f7',
          cursor: 'grab',
        }}
      >
        <div style={{ fontWeight: 'bold', fontSize: '14px', color: '#333', marginBottom: 2 }}>
          {label || dataset.table_name}
        </div>
        <div style={{ fontSize: '11px', color: '#999', display: 'flex', alignItems: 'center', gap: 4 }}>
          <span
            style={{
              background: '#e0f0f5',
              color: '#1a6d85',
              padding: '1px 6px',
              borderRadius: 4,
              fontSize: '11px',
            }}
          >
            {dataset.database?.database_name ?? 'DB'}
          </span>
          {dataset.schema && <span style={{ color: '#888' }}>· {dataset.schema}</span>}
        </div>
      </div>

      {/* Column list */}
      <div style={{ maxHeight: 300, overflowY: 'auto' }}>
        {columns.length === 0 && (
          <div style={{ padding: '8px 12px', color: '#999', fontSize: '12px' }}>
            No columns loaded
          </div>
        )}
        {columns.map((col: { column_name: string; type: string }) => {
          const handleBase = `${dataset.id}-${col.column_name}`;
          return (
            <div
              key={col.column_name}
              style={{
                position: 'relative',
                padding: '4px 20px',
                fontSize: '12px',
                lineHeight: '20px',
                color: '#444',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderBottom: '1px solid #f5f5f5',
              }}
            >
              {/* Target handle (left) */}
              <Handle
                type="target"
                position={Position.Left}
                id={`target-${handleBase}`}
                style={{
                  width: 8,
                  height: 8,
                  background: '#2893B3',
                  border: '2px solid #fff',
                }}
              />

              <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {col.column_name}
              </span>
              <span style={{ fontSize: '10px', color: '#aaa', marginLeft: 8, flexShrink: 0 }}>
                {col.type}
              </span>

              {/* Source handle (right) */}
              <Handle
                type="source"
                position={Position.Right}
                id={`source-${handleBase}`}
                style={{
                  width: 8,
                  height: 8,
                  background: '#2893B3',
                  border: '2px solid #fff',
                }}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}

export const DatasetNode = memo(DatasetNodeComponent);
