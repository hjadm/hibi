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

import { useState, useCallback } from 'react';
import { useTheme } from '@apache-superset/core/theme';
import { Select, Input, Button } from '@superset-ui/core/components';
import type {
  DatasetRelationship,
  RelationshipType,
  JoinType,
  RelationshipColumn,
} from '../types';
import ColumnPickerModal from '../ColumnPickerModal';
import type { DatasetSummary } from '../types';

interface RelationshipSidebarProps {
  relationship: DatasetRelationship | null;
  sourceDataset: DatasetSummary | null;
  targetDataset: DatasetSummary | null;
  onUpdate: (id: number, data: Partial<DatasetRelationship>) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  onClose: () => void;
}

const RELATIONSHIP_TYPE_OPTIONS = [
  { value: 'one_to_one', label: 'One to One (1:1)' },
  { value: 'one_to_many', label: 'One to Many (1:N)' },
  { value: 'many_to_one', label: 'Many to One (N:1)' },
  { value: 'many_to_many', label: 'Many to Many (N:N)' },
];

const JOIN_TYPE_OPTIONS = [
  { value: 'LEFT', label: 'LEFT JOIN' },
  { value: 'INNER', label: 'INNER JOIN' },
  { value: 'RIGHT', label: 'RIGHT JOIN' },
  { value: 'FULL', label: 'FULL JOIN' },
];

export default function RelationshipSidebar({
  relationship,
  sourceDataset,
  targetDataset,
  onUpdate,
  onDelete,
  onClose,
}: RelationshipSidebarProps) {
  const theme = useTheme();
  const [saving, setSaving] = useState(false);
  const [showColumnPicker, setShowColumnPicker] = useState(false);

  const [relType, setRelType] = useState<RelationshipType>(
    relationship?.relationship_type ?? 'many_to_one',
  );
  const [joinType, setJoinType] = useState<JoinType>(
    relationship?.join_type ?? 'LEFT',
  );
  const [name, setName] = useState(relationship?.name ?? '');
  const [description, setDescription] = useState(
    relationship?.description ?? '',
  );
  const [isActive, setIsActive] = useState(relationship?.is_active ?? true);
  const [columns, setColumns] = useState<RelationshipColumn[]>(
    relationship?.columns ?? [],
  );

  const handleSave = useCallback(async () => {
    if (!relationship) return;
    setSaving(true);
    try {
      await onUpdate(relationship.id, {
        relationship_type: relType,
        join_type: joinType,
        name: name || null,
        description: description || null,
        is_active: isActive,
        columns: columns.map((col, i) => ({
          source_column_name: col.source_column_name,
          target_column_name: col.target_column_name,
          operator: col.operator,
          ordinal: i,
        })),
      });
    } finally {
      setSaving(false);
    }
  }, [relationship, relType, joinType, name, description, isActive, columns, onUpdate]);

  const handleDelete = useCallback(async () => {
    if (!relationship) return;
    // eslint-disable-next-line no-alert
    if (window.confirm('Delete this relationship?')) {
      await onDelete(relationship.id);
    }
  }, [relationship, onDelete]);

  if (!relationship) {
    return (
      <div
        style={{
          padding: theme.gridUnit * 4,
          color: theme.colors.grayscale.light1,
          textAlign: 'center',
          fontSize: theme.typography.sizes.s,
        }}
      >
        Select a relationship on the canvas to view its details.
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: theme.gridUnit * 3,
        padding: theme.gridUnit * 4,
        height: '100%',
        overflowY: 'auto',
        fontFamily: theme.typography.families.sansSerif,
        fontSize: theme.typography.sizes.s,
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: `1px solid ${theme.colors.grayscale.light4}`,
          paddingBottom: theme.gridUnit * 2,
        }}
      >
        <h4 style={{ margin: 0, fontSize: theme.typography.sizes.l }}>
          Relationship #{relationship.id}
        </h4>
        <Button buttonSize="xs" buttonStyle="secondary" onClick={onClose}>
          ✕
        </Button>
      </div>

      {/* Datasets info */}
      <div
        style={{
          background: theme.colors.grayscale.light5,
          padding: theme.gridUnit * 3,
          borderRadius: theme.borderRadius,
        }}
      >
        <div style={{ marginBottom: theme.gridUnit }}>
          <strong>Source:</strong>{' '}
          {sourceDataset?.table_name ?? `Dataset #${relationship.source_dataset_id}`}
          {relationship.is_cross_database && (
            <span style={{ color: theme.colors.warning.dark1, marginLeft: 8 }}>
              ⚡ Cross-DB
            </span>
          )}
        </div>
        <div>
          <strong>Target:</strong>{' '}
          {targetDataset?.table_name ?? `Dataset #${relationship.target_dataset_id}`}
        </div>
      </div>

      {/* Name */}
      <div>
        <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>
          Name
        </label>
        <Input
          value={name}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setName(e.target.value)
          }
          placeholder="Optional name…"
        />
      </div>

      {/* Relationship type */}
      <div>
        <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>
          Cardinality
        </label>
        <Select
          value={relType}
          options={RELATIONSHIP_TYPE_OPTIONS}
          onChange={(v: unknown) => setRelType(v as RelationshipType)}
        />
      </div>

      {/* Join type */}
      <div>
        <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>
          Join Type
        </label>
        <Select
          value={joinType}
          options={JOIN_TYPE_OPTIONS}
          onChange={(v: unknown) => setJoinType(v as JoinType)}
        />
      </div>

      {/* Active toggle */}
      <div>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            type="checkbox"
            checked={isActive}
            onChange={e => setIsActive(e.target.checked)}
          />
          Active
        </label>
      </div>

      {/* Description */}
      <div>
        <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>
          Description
        </label>
        <Input
          value={description}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setDescription(e.target.value)
          }
          placeholder="Optional description…"
        />
      </div>

      {/* Column mappings */}
      <div>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: theme.gridUnit * 2,
          }}
        >
          <strong>Column Mappings ({columns.length})</strong>
          <Button
            buttonSize="xs"
            buttonStyle="primary"
            onClick={() => setShowColumnPicker(true)}
          >
            Edit
          </Button>
        </div>
        {columns.length > 0 ? (
          <div
            style={{
              background: theme.colors.grayscale.light5,
              borderRadius: theme.borderRadius,
              padding: theme.gridUnit * 2,
            }}
          >
            {columns.map((col, i) => (
              <div
                key={col.source_column_name + col.target_column_name + i}
                style={{ fontSize: theme.typography.sizes.xs, marginBottom: 4 }}
              >
                <span style={{ fontWeight: 'bold' }}>
                  {col.source_column_name}
                </span>{' '}
                {col.operator}{' '}
                <span style={{ fontWeight: 'bold' }}>
                  {col.target_column_name}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ color: theme.colors.grayscale.light1 }}>
            No column mappings configured.
          </div>
        )}
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: theme.gridUnit * 2, marginTop: 'auto' }}>
        <Button
          buttonSize="sm"
          buttonStyle="primary"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving…' : 'Save Changes'}
        </Button>
        <Button
          buttonSize="sm"
          buttonStyle="danger"
          onClick={handleDelete}
          disabled={saving}
        >
          Delete
        </Button>
      </div>

      {/* Column Picker Modal */}
      <ColumnPickerModal
        show={showColumnPicker}
        sourceDataset={sourceDataset}
        targetDataset={targetDataset}
        initialColumns={columns}
        onSave={setColumns}
        onHide={() => setShowColumnPicker(false)}
      />
    </div>
  );
}
