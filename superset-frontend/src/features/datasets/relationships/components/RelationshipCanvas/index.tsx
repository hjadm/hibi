/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except be agreed to
 * by you writing, software distributed under the License
 * is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
 * CONDITIONS OF ANY KIND, either express or implied.  See
 * the License for the specific language governing permissions
 * and limitations under the License.
 */

import {
  useState,
  useCallback,
  useMemo,
  useRef,
  useEffect,
} from 'react';
import {
  ReactFlow,
  Controls,
  MiniMap,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  type Connection,
  type OnNodesChange,
  type OnEdgesChange,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Select } from '@superset-ui/core/components';
import { DatasetNode } from '../DatasetNode';
import { RelationshipEdge } from '../RelationshipEdge';
import RelationshipSidebar from '../RelationshipSidebar';
import ColumnPickerModal from '../ColumnPickerModal';
import {
  useRelationships,
  useCreateRelationship,
  useUpdateRelationship,
  useDeleteRelationship,
  useDatasetList,
  useDatasetColumnsEnricher,
} from '../../hooks';
import type {
  DatasetRelationship,
  DatasetNode as DatasetNodeType,
  RelationshipEdge as RelationshipEdgeType,
  DatasetSummary,
  RelationshipColumn,
} from '../../types';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const nodeTypes = { dataset: DatasetNode } as any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const edgeTypes = { relationship: RelationshipEdge } as any;

function datasetsToNodes(
  datasets: DatasetSummary[],
  relationships: DatasetRelationship[],
  manuallyAddedIds: Set<number>,
): DatasetNodeType[] {
  const relatedIds = new Set<number>();
  relationships.forEach(rel => {
    relatedIds.add(rel.source_dataset_id);
    relatedIds.add(rel.target_dataset_id);
  });
  manuallyAddedIds.forEach(id => relatedIds.add(id));

  const visible = datasets.filter(ds => relatedIds.has(ds.id));
  if (visible.length === 0) return [];

  const groupKey = (ds: DatasetSummary) =>
    `${ds.database?.database_name ?? 'unknown'}::${ds.schema ?? 'public'}`;

  const groups = new Map<string, DatasetSummary[]>();
  visible.forEach(ds => {
    const key = groupKey(ds);
    const arr = groups.get(key) ?? [];
    arr.push(ds);
    groups.set(key, arr);
  });

  const nodes: DatasetNodeType[] = [];
  let groupX = 0;
  const COLS_PER_GROUP = 4;
  const X_SPACING = 340;
  const Y_SPACING = 320;

  groups.forEach((groupDatasets) => {
    groupDatasets.forEach((ds, i) => {
      nodes.push({
        id: `dataset-${ds.id}`,
        type: 'dataset',
        position: {
          x: groupX + (i % COLS_PER_GROUP) * X_SPACING + 50,
          y: Math.floor(i / COLS_PER_GROUP) * Y_SPACING + 50,
        },
        data: {
          dataset: ds,
          label: ds.table_name,
        },
      });
    });
    groupX += COLS_PER_GROUP * X_SPACING + 100;
  });

  return nodes;
}

function relationshipsToEdges(
  relationships: DatasetRelationship[],
): RelationshipEdgeType[] {
  return relationships.map(rel => ({
    id: `relationship-${rel.id}`,
    source: `dataset-${rel.source_dataset_id}`,
    target: `dataset-${rel.target_dataset_id}`,
    type: 'relationship',
    data: {
      relationship: rel,
      label: rel.name ?? `${rel.relationship_type} (${rel.join_type})`,
    },
  }));
}

// ---------------------------------------------------------------------------
// Hierarchical Dataset Selector
// ---------------------------------------------------------------------------

interface HierarchicalSelectorProps {
  enrichedDatasets: DatasetSummary[];
  onAddDataset: (id: number) => void;
  relatedIds: Set<number>;
  onFilterChange: (database: string | undefined, schema: string | undefined) => void;
}

function HierarchicalDatasetSelector({
  enrichedDatasets,
  onAddDataset,
  relatedIds,
  onFilterChange,
}: HierarchicalSelectorProps) {
  const [selectedDb, setSelectedDb] = useState<string | undefined>(undefined);
  const [selectedSchema, setSelectedSchema] = useState<string | undefined>(undefined);

  // Extract unique databases
  const databases = useMemo(() => {
    const dbNames = new Set<string>();
    enrichedDatasets.forEach(ds => {
      const name = ds.database?.database_name;
      if (name) dbNames.add(name);
    });
    return Array.from(dbNames).sort().map(name => ({
      value: name,
      label: name,
    }));
  }, [enrichedDatasets]);

  // Extract unique schemas filtered by selected database
  const schemas = useMemo(() => {
    if (!selectedDb) return [];
    const schemaNames = new Set<string>();
    enrichedDatasets
      .filter(ds => ds.database?.database_name === selectedDb)
      .forEach(ds => {
        const s = ds.schema ?? 'public';
        schemaNames.add(s);
      });
    return Array.from(schemaNames).sort().map(name => ({
      value: name,
      label: name,
    }));
  }, [enrichedDatasets, selectedDb]);

  // Filter datasets by database + schema
  const filteredDatasets = useMemo(() => {
    if (!selectedDb || !selectedSchema) return [];
    return enrichedDatasets.filter(
      ds =>
        ds.database?.database_name === selectedDb &&
        (ds.schema ?? 'public') === selectedSchema,
    );
  }, [enrichedDatasets, selectedDb, selectedSchema]);

  // Reset schema when database changes
  const handleDbChange = useCallback((value: string) => {
    setSelectedDb(value || undefined);
    setSelectedSchema(undefined);
    onFilterChange(value || undefined, undefined);
  }, [onFilterChange]);

  const handleSchemaChange = useCallback((value: string) => {
    setSelectedSchema(value || undefined);
    onFilterChange(selectedDb, value || undefined);
  }, [onFilterChange, selectedDb]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ fontSize: 12, color: '#999', marginBottom: 2 }}>Add Dataset to Canvas</div>
      <Select
        value={selectedDb}
        options={databases}
        onChange={handleDbChange}
        placeholder="Select database…"
      />
      {selectedDb && (
        <Select
          value={selectedSchema}
          options={schemas}
          onChange={handleSchemaChange}
          placeholder="Select schema…"
        />
      )}
      {selectedDb && selectedSchema && filteredDatasets.length > 0 && (
        <div
          style={{
            maxHeight: 200,
            overflowY: 'auto',
            border: '1px solid #e8e8e8',
            borderRadius: 4,
            background: '#fff',
          }}
        >
          {filteredDatasets.map(ds => {
            const isAdded = relatedIds.has(ds.id);
            return (
              <div
                key={ds.id}
                onClick={() => {
                  if (!isAdded) onAddDataset(ds.id);
                }}
                style={{
                  padding: '6px 10px',
                  fontSize: '12px',
                  cursor: isAdded ? 'default' : 'pointer',
                  background: isAdded ? '#f5f5f5' : '#fff',
                  color: isAdded ? '#999' : '#333',
                  borderBottom: '1px solid #f0f0f0',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
                onMouseEnter={e => {
                  if (!isAdded) (e.currentTarget as HTMLDivElement).style.background = '#e0f0f5';
                }}
                onMouseLeave={e => {
                  if (!isAdded) (e.currentTarget as HTMLDivElement).style.background = '#fff';
                }}
              >
                <span>{ds.table_name}</span>
                {isAdded && <span style={{ color: '#2893B3', fontSize: '11px' }}>✓ added</span>}
              </div>
            );
          })}
        </div>
      )}
      {selectedDb && selectedSchema && filteredDatasets.length === 0 && (
        <div style={{ fontSize: '12px', color: '#999', padding: '4px 0' }}>
          No datasets in this schema.
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

interface RelationshipCanvasProps {
  datasetId?: number;
  onClose?: () => void;
}

export default function RelationshipCanvas({
  datasetId,
  onClose,
}: RelationshipCanvasProps) {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  // Data hooks
  const { relationships, loading: relLoading, refresh: refreshRelationships } =
    useRelationships(datasetId);
  const { datasets, loading: dsLoading } =
    useDatasetList();
  const { enrichDatasets } = useDatasetColumnsEnricher();
  const { create } = useCreateRelationship();
  const { update } = useUpdateRelationship();
  const { remove } = useDeleteRelationship();

  const [manuallyAddedIds, setManuallyAddedIds] = useState<Set<number>>(new Set());
  const [enrichedDatasets, setEnrichedDatasets] = useState<DatasetSummary[]>([]);
  const [filterDb, setFilterDb] = useState<string | undefined>(undefined);
  const [filterSchema, setFilterSchema] = useState<string | undefined>(undefined);

  // Enrich datasets with columns when they change
  useEffect(() => {
    if (dsLoading) return;
    enrichDatasets(datasets).then(setEnrichedDatasets);
  }, [datasets, dsLoading, enrichDatasets]);

  // Filter handler from hierarchical selector
  const handleFilterChange = useCallback((db: string | undefined, schema: string | undefined) => {
    setFilterDb(db);
    setFilterSchema(schema);
  }, []);

  // Filter datasets by selected database + schema
  const filteredDatasets = useMemo(() => {
    if (!filterDb || !filterSchema) return enrichedDatasets;
    return enrichedDatasets.filter(
      ds =>
        ds.database?.database_name === filterDb &&
        (ds.schema ?? 'public') === filterSchema,
    );
  }, [enrichedDatasets, filterDb, filterSchema]);

  // Filter relationships to only those involving visible datasets
  const filteredRelationships = useMemo(() => {
    if (!filterDb || !filterSchema) return relationships;
    const visibleIds = new Set(filteredDatasets.map(ds => ds.id));
    return relationships.filter(
      r => visibleIds.has(r.source_dataset_id) && visibleIds.has(r.target_dataset_id),
    );
  }, [relationships, filteredDatasets, filterDb, filterSchema]);

  const loading = relLoading || dsLoading || enrichedDatasets.length === 0;

  const initialNodes = useMemo(
    () => datasetsToNodes(filteredDatasets, filteredRelationships, manuallyAddedIds),
    [filteredDatasets, filteredRelationships, manuallyAddedIds],
  );
  const initialEdges = useMemo(
    () => relationshipsToEdges(filteredRelationships),
    [filteredRelationships],
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setNodes(datasetsToNodes(filteredDatasets, filteredRelationships, manuallyAddedIds));
    setEdges(relationshipsToEdges(relationships));
  }, [filteredDatasets, filteredRelationships, manuallyAddedIds, setNodes, setEdges]);

  // Dataset selector: compute related IDs for showing "added" state
  const relatedIds = useMemo(() => {
    const ids = new Set<number>();
    relationships.forEach(rel => {
      ids.add(rel.source_dataset_id);
      ids.add(rel.target_dataset_id);
    });
    manuallyAddedIds.forEach(id => ids.add(id));
    return ids;
  }, [relationships, manuallyAddedIds]);

  const handleAddDataset = useCallback(
    (id: number) => {
      setManuallyAddedIds(prev => new Set(prev).add(id));
    },
    [],
  );

  const [selectedRelationship, setSelectedRelationship] =
    useState<DatasetRelationship | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);

  // Pending connection - now includes optional pre-selected column names
  const [pendingConnection, setPendingConnection] = useState<{
    sourceId: number;
    targetId: number;
    sourceColumn?: string;
    targetColumn?: string;
  } | null>(null);
  const [showNewRelPicker, setShowNewRelPicker] = useState(false);

  const getRelationshipByEdgeId = useCallback(
    (edgeId: string): DatasetRelationship | null => {
      const relId = parseInt(edgeId.replace('relationship-', ''), 10);
      return relationships.find(r => r.id === relId) ?? null;
    },
    [relationships],
  );

  const onEdgeClick = useCallback(
    (_event: React.MouseEvent, edge: { id: string }) => {
      const rel = getRelationshipByEdgeId(edge.id);
      setSelectedRelationship(rel);
      setSelectedEdgeId(edge.id);
    },
    [getRelationshipByEdgeId],
  );

  /**
   * Handle column-level connections.
   * Handle IDs are formatted as:
   *   source-{datasetId}-{columnName}
   *   target-{datasetId}-{columnName}
   */
  const onConnect = useCallback(
    async (connection: Connection) => {
      if (!connection.source || !connection.target) return;
      const sourceId = parseInt(connection.source.replace('dataset-', ''), 10);
      const targetId = parseInt(connection.target.replace('dataset-', ''), 10);

      // Extract column names from handle IDs
      let sourceColumn: string | undefined;
      let targetColumn: string | undefined;

      if (connection.sourceHandle) {
        const parts = connection.sourceHandle.split('-');
        if (parts.length >= 3) {
          sourceColumn = parts.slice(2).join('-');
        }
      }

      if (connection.targetHandle) {
        const parts = connection.targetHandle.split('-');
        if (parts.length >= 3) {
          targetColumn = parts.slice(2).join('-');
        }
      }

      // If both columns identified, create relationship directly (no modal)
      if (sourceColumn && targetColumn) {
        try {
          await create({
            source_dataset_id: sourceId,
            target_dataset_id: targetId,
            relationship_type: 'many_to_one',
            join_type: 'LEFT',
            name: `${sourceColumn} → ${targetColumn}`,
            columns: [{
              source_column_name: sourceColumn,
              target_column_name: targetColumn,
              operator: '=',
              ordinal: 0,
            }],
          });
          refreshRelationships();
        } catch {
          // Error toast handled by hook
        }
        return;
      }

      // Fallback: if columns not identified from handles, show picker modal
      setPendingConnection({ sourceId, targetId, sourceColumn, targetColumn });
      setShowNewRelPicker(true);
    },
    [create, refreshRelationships],
  );

  const handleCreateRelationship = useCallback(
    async (columns: RelationshipColumn[]) => {
      if (!pendingConnection) return;
      try {
        await create({
          source_dataset_id: pendingConnection.sourceId,
          target_dataset_id: pendingConnection.targetId,
          relationship_type: 'many_to_one',
          join_type: 'LEFT',
          columns,
        });
        refreshRelationships();
        setShowNewRelPicker(false);
        setPendingConnection(null);
      } catch {
        // Error toast handled by hook
      }
    },
    [pendingConnection, create, refreshRelationships],
  );

  const handleUpdateRelationship = useCallback(
    async (id: number, data: Partial<DatasetRelationship>) => {
      try {
        await update(id, data);
        refreshRelationships();
        const updated = relationships.find(r => r.id === id);
        if (updated) {
          setSelectedRelationship({ ...updated, ...data } as DatasetRelationship);
        }
      } catch {
        // Error toast handled by hook
      }
    },
    [update, refreshRelationships, relationships],
  );

  const handleDeleteRelationship = useCallback(
    async (id: number) => {
      try {
        await remove(id);
        setSelectedRelationship(null);
        setSelectedEdgeId(null);
        refreshRelationships();
      } catch {
        // Error toast handled by hook
      }
    },
    [remove, refreshRelationships],
  );

  const onPaneClick = useCallback(() => {
    setSelectedRelationship(null);
    setSelectedEdgeId(null);
  }, []);

  const sourceDs = selectedRelationship
    ? enrichedDatasets.find(d => d.id === selectedRelationship.source_dataset_id) ?? null
    : pendingConnection
      ? enrichedDatasets.find(d => d.id === pendingConnection.sourceId) ?? null
      : null;

  const targetDs = selectedRelationship
    ? enrichedDatasets.find(d => d.id === selectedRelationship.target_dataset_id) ?? null
    : pendingConnection
      ? enrichedDatasets.find(d => d.id === pendingConnection.targetId) ?? null
      : null;

  // Build initial columns from column-level drag if present
  const pickerInitialColumns = useMemo(() => {
    if (!pendingConnection?.sourceColumn || !pendingConnection?.targetColumn) {
      return undefined;
    }
    return [{
      source_column_name: pendingConnection.sourceColumn,
      target_column_name: pendingConnection.targetColumn,
      operator: '=' as const,
      ordinal: 0,
    }];
  }, [pendingConnection]);

  if (loading) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: 400,
          color: '#999',
        }}
      >
        Loading relationships…
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        height: '100%',
        minHeight: 500,
        border: '1px solid #e8e8e8',
        borderRadius: 4,
        overflow: 'hidden',
      }}
    >
      {/* Sidebar LEFT */}
      {(selectedRelationship || !selectedEdgeId) && (
        <div
          style={{
            width: 320,
            borderRight: '1px solid #e8e8e8',
            background: '#fafafa',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Hierarchical Add Dataset selector */}
          <div style={{ padding: '12px 16px', borderBottom: '1px solid #e8e8e8' }}>
            <HierarchicalDatasetSelector
              enrichedDatasets={enrichedDatasets}
              onAddDataset={handleAddDataset}
              relatedIds={relatedIds}
              onFilterChange={handleFilterChange}
            />
          </div>
          <RelationshipSidebar
            relationship={selectedRelationship}
            sourceDataset={sourceDs}
            targetDataset={targetDs}
            onUpdate={handleUpdateRelationship}
            onDelete={handleDeleteRelationship}
            onClose={() => {
              setSelectedRelationship(null);
              setSelectedEdgeId(null);
            }}
          />
        </div>
      )}

      {/* Canvas area */}
      <div
        ref={reactFlowWrapper}
        style={{ flex: 1, height: '100%' }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange as OnNodesChange}
          onEdgesChange={onEdgesChange as OnEdgesChange}
          onConnect={onConnect}
          onEdgeClick={onEdgeClick as (event: React.MouseEvent, edge: { id: string }) => void}
          onPaneClick={onPaneClick}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          connectOnClick={false}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          style={{ background: '#fafafa' }}
        >
          <Controls />
          <MiniMap
            nodeColor={n =>
              n.selected ? '#2893B3' : '#ccc'
            }
            style={{
              background: '#fafafa',
              border: '1px solid #ddd',
            }}
          />
          <Background
            variant={BackgroundVariant.Dots}
            gap={20}
            size={1}
            color="#ddd"
          />
        </ReactFlow>
      </div>

      {/* New Relationship Column Picker */}
      <ColumnPickerModal
        show={showNewRelPicker}
        sourceDataset={
          pendingConnection
            ? enrichedDatasets.find(d => d.id === pendingConnection.sourceId) ?? null
            : null
        }
        targetDataset={
          pendingConnection
            ? enrichedDatasets.find(d => d.id === pendingConnection.targetId) ?? null
            : null
        }
        initialColumns={pickerInitialColumns}
        onSave={handleCreateRelationship}
        onHide={() => {
          setShowNewRelPicker(false);
          setPendingConnection(null);
        }}
      />
    </div>
  );
}
