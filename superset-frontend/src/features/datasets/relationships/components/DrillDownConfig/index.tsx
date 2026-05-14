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

import { useState, useCallback, useMemo } from 'react';
import { useTheme } from '@superset-ui/core';
import { Select, Input, Button } from 'src/components';
import Modal from 'src/components/Modal';
import { useDatasetList } from '../hooks';
import type { DatasetSummary } from '../types';

export interface DrillDownLevel {
  dataset_id: number;
  column_name: string;
  label: string;
}

export interface DrillDownHierarchy {
  id: string;
  name: string;
  levels: DrillDownLevel[];
}

interface DrillDownConfigProps {
  show: boolean;
  hierarchies: DrillDownHierarchy[];
  onSave: (hierarchies: DrillDownHierarchy[]) => void;
  onHide: () => void;
}

export default function DrillDownConfigModal({
  show,
  hierarchies: initialHierarchies,
  onSave,
  onHide,
}: DrillDownConfigProps) {
  const theme = useTheme();
  const { datasets } = useDatasetList();

  const [hierarchies, setHierarchies] =
    useState<DrillDownHierarchy[]>(initialHierarchies);

  const addHierarchy = useCallback(() => {
    setHierarchies(prev => [
      ...prev,
      {
        id: `hierarchy-${Date.now()}`,
        name: '',
        levels: [],
      },
    ]);
  }, []);

  const removeHierarchy = useCallback((hId: string) => {
    setHierarchies(prev => prev.filter(h => h.id !== hId));
  }, []);

  const updateHierarchyName = useCallback(
    (hId: string, name: string) => {
      setHierarchies(prev =>
        prev.map(h => (h.id === hId ? { ...h, name } : h)),
      );
    },
    [],
  );

  const addLevel = useCallback((hId: string) => {
    setHierarchies(prev =>
      prev.map(h =>
        h.id === hId
          ? {
              ...h,
              levels: [
                ...h.levels,
                {
                  dataset_id: 0,
                  column_name: '',
                  label: `Level ${h.levels.length + 1}`,
                },
              ],
            }
          : h,
      ),
    );
  }, []);

  const removeLevel = useCallback((hId: string, levelIdx: number) => {
    setHierarchies(prev =>
      prev.map(h =>
        h.id === hId
          ? { ...h, levels: h.levels.filter((_, i) => i !== levelIdx) }
          : h,
      ),
    );
  }, []);

  const updateLevel = useCallback(
    (
      hId: string,
      levelIdx: number,
      field: keyof DrillDownLevel,
      value: string | number,
    ) => {
      setHierarchies(prev =>
        prev.map(h =>
          h.id === hId
            ? {
                ...h,
                levels: h.levels.map((l, i) =>
                  i === levelIdx ? { ...l, [field]: value } : l,
                ),
              }
            : h,
        ),
      );
    },
    [],
  );

  const getColumnsForDataset = useCallback(
    (datasetId: number) =>
      datasets
        .find(d => d.id === datasetId)
        ?.columns.map(c => ({
          value: c.column_name,
          label: `${c.column_name} (${c.type})`,
        })) ?? [],
    [datasets],
  );

  const datasetOptions = useMemo(
    () =>
      datasets.map(d => ({
        value: d.id,
        label: `${d.table_name} (${d.database?.database_name ?? 'DB'})`,
      })),
    [datasets],
  );

  const handleSave = useCallback(() => {
    const valid = hierarchies.filter(
      h => h.name && h.levels.length >= 2 && h.levels.every(l => l.dataset_id && l.column_name),
    );
    onSave(valid);
  }, [hierarchies, onSave]);

  return (
    <Modal
      show={show}
      onHide={onHide}
      title="Configure Drill-Down Hierarchies"
      footer={
        <>
          <Button buttonSize="sm" buttonStyle="secondary" onClick={onHide}>
            Cancel
          </Button>
          <Button buttonSize="sm" buttonStyle="primary" onClick={handleSave}>
            Save
          </Button>
        </>
      }
      style={{ width: 700 }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: theme.gridUnit * 4,
          maxHeight: '60vh',
          overflowY: 'auto',
        }}
      >
        {hierarchies.map(hierarchy => (
          <div
            key={hierarchy.id}
            style={{
              border: `1px solid ${theme.colors.grayscale.light4}`,
              borderRadius: theme.borderRadius,
              padding: theme.gridUnit * 3,
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: theme.gridUnit * 2,
                marginBottom: theme.gridUnit * 2,
              }}
            >
              <Input
                value={hierarchy.name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  updateHierarchyName(hierarchy.id, e.target.value)
                }
                placeholder="Hierarchy name (e.g., Geography)"
                style={{ flex: 1 }}
              />
              <Button
                buttonSize="xs"
                buttonStyle="danger"
                onClick={() => removeHierarchy(hierarchy.id)}
              >
                Remove
              </Button>
            </div>

            {hierarchy.levels.map((level, levelIdx) => (
              <div
                key={levelIdx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: theme.gridUnit * 2,
                  marginBottom: theme.gridUnit * 2,
                  paddingLeft: theme.gridUnit * 4,
                }}
              >
                <span
                  style={{
                    color: theme.colors.grayscale.light1,
                    fontSize: theme.typography.sizes.xs,
                    width: 20,
                  }}
                >
                  {levelIdx + 1}.
                </span>

                <Select
                  value={level.dataset_id || undefined}
                  options={datasetOptions}
                  onChange={(v: unknown) =>
                    updateLevel(
                      hierarchy.id,
                      levelIdx,
                      'dataset_id',
                      v as number,
                    )
                  }
                  placeholder="Dataset"
                  style={{ width: 180 }}
                />

                <Select
                  value={level.column_name || undefined}
                  options={
                    level.dataset_id
                      ? getColumnsForDataset(level.dataset_id)
                      : []
                  }
                  onChange={(v: unknown) =>
                    updateLevel(
                      hierarchy.id,
                      levelIdx,
                      'column_name',
                      v as string,
                    )
                  }
                  placeholder="Column"
                  style={{ width: 160 }}
                />

                <Input
                  value={level.label}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    updateLevel(
                      hierarchy.id,
                      levelIdx,
                      'label',
                      e.target.value,
                    )
                  }
                  placeholder="Label"
                  style={{ width: 120 }}
                />

                <Button
                  buttonSize="xs"
                  buttonStyle="danger"
                  onClick={() => removeLevel(hierarchy.id, levelIdx)}
                >
                  ✕
                </Button>
              </div>
            ))}

            <Button
              buttonSize="xs"
              buttonStyle="tertiary"
              onClick={() => addLevel(hierarchy.id)}
              style={{ marginLeft: theme.gridUnit * 4 }}
            >
              + Add Level
            </Button>
          </div>
        ))}

        <Button
          buttonSize="sm"
          buttonStyle="primary"
          onClick={addHierarchy}
        >
          + Add Hierarchy
        </Button>
      </div>
    </Modal>
  );
}
