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

import { useState, useMemo, useCallback } from 'react';
import { useTheme } from '@superset-ui/core';
import { Select, Input, Button } from 'src/components';
import Modal from 'src/components/Modal';
import type {
  RelationshipColumn,
  ColumnOperator,
  DatasetSummary,
} from '../types';

interface ColumnPickerModalProps {
  show: boolean;
  sourceDataset: DatasetSummary | null;
  targetDataset: DatasetSummary | null;
  initialColumns?: RelationshipColumn[];
  onSave: (columns: RelationshipColumn[]) => void;
  onHide: () => void;
}

interface ColumnPair {
  id: string;
  source_column_name: string;
  target_column_name: string;
  operator: ColumnOperator;
  ordinal: number;
}

const OPERATOR_OPTIONS = [
  { value: '=', label: '= (equals)' },
  { value: '!=', label: '!= (not equals)' },
  { value: '>', label: '> (greater than)' },
  { value: '<', label: '< (less than)' },
  { value: '>=', label: '>= (greater or equal)' },
  { value: '<=', label: '<= (less or equal)' },
];

export default function ColumnPickerModal({
  show,
  sourceDataset,
  targetDataset,
  initialColumns,
  onSave,
  onHide,
}: ColumnPickerModalProps) {
  const theme = useTheme();

  const sourceColumnOptions = useMemo(
    () =>
      sourceDataset?.columns.map(c => ({
        value: c.column_name,
        label: `${c.column_name} (${c.type})`,
      })) ?? [],
    [sourceDataset],
  );

  const targetColumnOptions = useMemo(
    () =>
      targetDataset?.columns.map(c => ({
        value: c.column_name,
        label: `${c.column_name} (${c.type})`,
      })) ?? [],
    [targetDataset],
  );

  const [pairs, setPairs] = useState<ColumnPair[]>(() =>
    (initialColumns ?? [{ source_column_name: '', target_column_name: '', operator: '=' as ColumnOperator, ordinal: 0 }]).map(
      (col, i) => ({
        id: `pair-${i}-${Date.now()}`,
        ...col,
        ordinal: i,
      }),
    ),
  );

  const updatePair = useCallback(
    (pairId: string, field: keyof ColumnPair, value: string) => {
      setPairs(prev =>
        prev.map(p => (p.id === pairId ? { ...p, [field]: value } : p)),
      );
    },
    [],
  );

  const addPair = useCallback(() => {
    setPairs(prev => [
      ...prev,
      {
        id: `pair-${prev.length}-${Date.now()}`,
        source_column_name: '',
        target_column_name: '',
        operator: '=' as ColumnOperator,
        ordinal: prev.length,
      },
    ]);
  }, []);

  const removePair = useCallback((pairId: string) => {
    setPairs(prev => prev.filter(p => p.id !== pairId));
  }, []);

  const handleSave = useCallback(() => {
    const cleaned = pairs
      .filter(p => p.source_column_name && p.target_column_name)
      .map((p, i) => ({
        source_column_name: p.source_column_name,
        target_column_name: p.target_column_name,
        operator: p.operator,
        ordinal: i,
      }));
    if (cleaned.length > 0) {
      onSave(cleaned);
    }
  }, [pairs, onSave]);

  const isValid = pairs.some(
    p => p.source_column_name && p.target_column_name,
  );

  return (
    <Modal
      show={show}
      onHide={onHide}
      title="Configure Column Mappings"
      footer={
        <>
          <Button buttonSize="sm" buttonStyle="secondary" onClick={onHide}>
            Cancel
          </Button>
          <Button
            buttonSize="sm"
            buttonStyle="primary"
            onClick={handleSave}
            disabled={!isValid}
          >
            Save Mappings
          </Button>
        </>
      }
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: theme.gridUnit * 3,
        }}
      >
        {pairs.map(pair => (
          <div
            key={pair.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: theme.gridUnit * 2,
              padding: theme.gridUnit * 2,
              background: theme.colors.grayscale.light5,
              borderRadius: theme.borderRadius,
            }}
          >
            <div style={{ flex: 1 }}>
              <div
                style={{
                  fontSize: theme.typography.sizes.xs,
                  color: theme.colors.grayscale.light1,
                  marginBottom: 4,
                }}
              >
                Source Column
              </div>
              <Select
                value={pair.source_column_name || undefined}
                options={sourceColumnOptions}
                onChange={(v: unknown) =>
                  updatePair(pair.id, 'source_column_name', v as string)
                }
                placeholder="Select column…"
              />
            </div>

            <div style={{ width: 100, flexShrink: 0 }}>
              <div
                style={{
                  fontSize: theme.typography.sizes.xs,
                  color: theme.colors.grayscale.light1,
                  marginBottom: 4,
                }}
              >
                Operator
              </div>
              <Select
                value={pair.operator}
                options={OPERATOR_OPTIONS}
                onChange={(v: unknown) =>
                  updatePair(pair.id, 'operator', v as string)
                }
              />
            </div>

            <div style={{ flex: 1 }}>
              <div
                style={{
                  fontSize: theme.typography.sizes.xs,
                  color: theme.colors.grayscale.light1,
                  marginBottom: 4,
                }}
              >
                Target Column
              </div>
              <Select
                value={pair.target_column_name || undefined}
                options={targetColumnOptions}
                onChange={(v: unknown) =>
                  updatePair(pair.id, 'target_column_name', v as string)
                }
                placeholder="Select column…"
              />
            </div>

            {pairs.length > 1 && (
              <Button
                buttonSize="xs"
                buttonStyle="danger"
                onClick={() => removePair(pair.id)}
                style={{ marginTop: 16 }}
              >
                ✕
              </Button>
            )}
          </div>
        ))}

        <Button
          buttonSize="sm"
          buttonStyle="tertiary"
          onClick={addPair}
          style={{ alignSelf: 'flex-start' }}
        >
          + Add Column Pair
        </Button>
      </div>
    </Modal>
  );
}
