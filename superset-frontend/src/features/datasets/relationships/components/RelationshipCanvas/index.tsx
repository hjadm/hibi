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
  addEdge,
  useNodesState,
  useEdgesState,
  type Connection,
  type OnNodesChange,
  type OnEdgesChange,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useTheme } from '@apache-superset/core/theme';
import { Button } from '@superset-ui/core/components';
import { DatasetNode } from '../components/DatasetNode';
import { RelationshipEdge } from '../components/RelationshipEdge';
import RelationshipSidebar from '../components/RelationshipSidebar';
import ColumnPickerModal from '../components/ColumnPickerModal';
import {
  useRelationships,
  useCreateRelationship,
  useUpdateRelationship,
  useDeleteRelationship,
  useDatasetList,
} from '../hooks';
import type {
  DatasetRelationship,
  DatasetNode as DatasetNodeType,
  RelationshipEdge as RelationshipEdgeType,
  DatasetSummary,
  RelationshipColumn,
} from '../types';

// ---------------------------------------------------------------------------
// Helpers: convert API data → React Flow nodes/edges
// ---------------------------------------------------------------------------

const nodeTypes = { dataset: DatasetNode };
const edgeTypes = { relationship: RelationshipEdge };

function datasetsToNodes(
  datasets: DatasetSummary[],
  relationships: DatasetRelationship[],
): DatasetNodeType[] {
  // Only include datasets that appear in at least one relationship
  const usedIds = new Set<number>();
  relationships.forEach(r => {
    usedIds.add(r.source_dataset_id);
    usedIds.add(r.target_dataset_id);
  });

  const filtered = datasets.filter(d => usedIds.has(d.id));

  // Simple auto-layout: spread in a grid
  const cols = Math.ceil(Math.sqrt(filtered.length));
  return filtered.map((ds, i) => ({
    id: `dataset-${ds.id}`,
    type: 'dataset',
    position: { x: (i % cols) * 300 + 50, y: Math.floor(i / cols) * 180 + 50 },
    data: {
      dataset: ds,
      label: ds.table_name,
    },
  }));
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
// Main component
// ---------------------------------------------------------------------------

interface RelationshipCanvasProps {
  /** If provided, only show relationships for this dataset */
  datasetId?: number;
  /** Called when the user navigates away */
  onClose?: () => void;
}

export default function RelationshipCanvas({
  datasetId,
  onClose,
}: RelationshipCanvasProps) {
  const theme = useTheme();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  // Data hooks
  const { relationships, loading: relLoading, refresh: refreshRelationships } =
    useRelationships(datasetId);
  const { datasets, loading: dsLoading, refresh: refreshDatasets } =
    useDatasetList();
  const { create } = useCreateRelationship();
  const { update } = useUpdateRelationship();
  const { remove } = useDeleteRelationship();

  const loading = relLoading || dsLoading;

  // React Flow state — initialize from API data
  const initialNodes = useMemo(
    () => datasetsToNodes(datasets, relationships),
    [datasets, relationships],
  );
  const initialEdges = useMemo(
    () => relationshipsToEdges(relationships),
    [relationships],
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Sync when API data changes
  useEffect(() => {
    setNodes(datasetsToNodes(datasets, relationships));
    setEdges(relationshipsToEdges(relationships));
  }, [datasets, relationships, setNodes, setEdges]);

  // Selection state
  const [selectedRelationship, setSelectedRelationship] =
    useState<DatasetRelationship | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);

  // New relationship flow
  const [connecting, setConnecting] = useState(false);
  const [pendingConnection, setPendingConnection] = useState<{
    sourceId: number;
    targetId: number;
  } | null>(null);
  const [showNewRelPicker, setShowNewRelPicker] = useState(false);

  // Find dataset by node ID
  const getDatasetByNodeId = useCallback(
    (nodeId: string): DatasetSummary | null => {
      const dsId = parseInt(nodeId.replace('dataset-', ''), 10);
      return datasets.find(d => d.id === dsId) ?? null;
    },
    [datasets],
  );

  // Find relationship by edge ID
  const getRelationshipByEdgeId = useCallback(
    (edgeId: string): DatasetRelationship | null => {
      const relId = parseInt(edgeId.replace('relationship-', ''), 10);
      return relationships.find(r => r.id === relId) ?? null;
    },
    [relationships],
  );

  // Handle edge click → open sidebar
  const onEdgeClick = useCallback(
    (_event: React.MouseEvent, edge: { id: string }) => {
      const rel = getRelationshipByEdgeId(edge.id);
      setSelectedRelationship(rel);
      setSelectedEdgeId(edge.id);
    },
    [getRelationshipByEdgeId],
  );

  // Handle new connection (drag from handle)
  const onConnect = useCallback(
    (connection: Connection) => {
      if (!connection.source || !connection.target) return;
      const sourceId = parseInt(connection.source.replace('dataset-', ''), 10);
      const targetId = parseInt(connection.target.replace('dataset-', ''), 10);
      setPendingConnection({ sourceId, targetId });
      setShowNewRelPicker(true);
    },
    [],
  );

  // Create new relationship after column picker
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

  // Update relationship
  const handleUpdateRelationship = useCallback(
    async (id: number, data: Partial<DatasetRelationship>) => {
      try {
        await update(id, data);
        refreshRelationships();
        // Re-select updated relationship
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

  // Delete relationship
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

  // Click on canvas background → deselect
  const onPaneClick = useCallback(() => {
    setSelectedRelationship(null);
    setSelectedEdgeId(null);
  }, []);

  const sourceDs = selectedRelationship
    ? datasets.find(d => d.id === selectedRelationship.source_dataset_id) ?? null
    : pendingConnection
      ? datasets.find(d => d.id === pendingConnection.sourceId) ?? null
      : null;

  const targetDs = selectedRelationship
    ? datasets.find(d => d.id === selectedRelationship.target_dataset_id) ?? null
    : pendingConnection
      ? datasets.find(d => d.id === pendingConnection.targetId) ?? null
      : null;

  if (loading) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: 400,
          color: theme.colors.grayscale.light1,
          fontFamily: theme.typography.families.sansSerif,
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
        fontFamily: theme.typography.families.sansSerif,
        border: `1px solid ${theme.colors.grayscale.light4}`,
        borderRadius: theme.borderRadius,
        overflow: 'hidden',
      }}
    >
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
          fitView
          fitViewOptions={{ padding: 0.2 }}
          style={{ background: theme.colors.grayscale.light5 }}
        >
          <Controls />
          <MiniMap
            nodeColor={n =>
              n.selected
                ? theme.colors.primary.base
                : theme.colors.grayscale.light3
            }
            style={{
              background: theme.colors.grayscale.light5,
              border: `1px solid ${theme.colors.grayscale.light3}`,
            }}
          />
          <Background
            variant={BackgroundVariant.Dots}
            gap={20}
            size={1}
            color={theme.colors.grayscale.light3}
          />
        </ReactFlow>
      </div>

      {/* Sidebar */}
      {(selectedRelationship || !selectedEdgeId) && (
        <div
          style={{
            width: 320,
            borderLeft: `1px solid ${theme.colors.grayscale.light4}`,
            background: theme.colors.grayscale.light5,
            overflowY: 'auto',
          }}
        >
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

      {/* New Relationship Column Picker */}
      <ColumnPickerModal
        show={showNewRelPicker}
        sourceDataset={
          pendingConnection
            ? datasets.find(d => d.id === pendingConnection.sourceId) ?? null
            : null
        }
        targetDataset={
          pendingConnection
            ? datasets.find(d => d.id === pendingConnection.targetId) ?? null
            : null
        }
        onSave={handleCreateRelationship}
        onHide={() => {
          setShowNewRelPicker(false);
          setPendingConnection(null);
        }}
      />
    </div>
  );
}
