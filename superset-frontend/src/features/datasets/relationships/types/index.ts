/* eslint-disable camelcase */
/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain the copy of the License at
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

import type { Node, Edge } from '@xyflow/react';

// ---------------------------------------------------------------------------
// Enums & constants
// ---------------------------------------------------------------------------

export const RELATIONSHIP_TYPES = [
  'one_to_one',
  'one_to_many',
  'many_to_one',
  'many_to_many',
] as const;

export type RelationshipType = (typeof RELATIONSHIP_TYPES)[number];

export const JOIN_TYPES = ['INNER', 'LEFT', 'RIGHT', 'FULL'] as const;
export type JoinType = (typeof JOIN_TYPES)[number];

export const COLUMN_OPERATORS = [
  '=',
  '!=',
  '>',
  '<',
  '>=',
  '<=',
] as const;
export type ColumnOperator = (typeof COLUMN_OPERATORS)[number];

// ---------------------------------------------------------------------------
// API models (mirror backend schemas)
// ---------------------------------------------------------------------------

export interface RelationshipColumn {
  id?: number;
  source_column_name: string;
  target_column_name: string;
  operator: ColumnOperator;
  ordinal: number;
}

export interface DatasetRelationship {
  id: number;
  uuid: string;
  source_dataset_id: number;
  target_dataset_id: number;
  relationship_type: RelationshipType;
  join_type: JoinType;
  is_cross_database: boolean;
  is_active: boolean;
  name: string | null;
  description: string | null;
  columns: RelationshipColumn[];
  created_on?: string;
  changed_on?: string;
  created_by_fk?: number;
  changed_by_fk?: number;
}

export interface DatasetRelationshipCreate {
  source_dataset_id: number;
  target_dataset_id: number;
  relationship_type: RelationshipType;
  join_type?: JoinType;
  is_active?: boolean;
  name?: string | null;
  description?: string | null;
  columns: Omit<RelationshipColumn, 'id'>[];
}

export interface DatasetRelationshipUpdate {
  source_dataset_id?: number;
  target_dataset_id?: number;
  relationship_type?: RelationshipType;
  join_type?: JoinType;
  is_active?: boolean;
  name?: string | null;
  description?: string | null;
  columns?: Omit<RelationshipColumn, 'id'>[];
}

// ---------------------------------------------------------------------------
// Dataset summary (lightweight, for graph nodes)
// ---------------------------------------------------------------------------

export interface DatasetSummary {
  id: number;
  table_name: string;
  schema: string | null;
  database: {
    id: number;
    database_name: string;
  };
  columns: {
    column_name: string;
    type: string;
  }[];
}

// ---------------------------------------------------------------------------
// React Flow custom node/edge data
// ---------------------------------------------------------------------------

export interface DatasetNodeData extends Record<string, unknown> {
  dataset: DatasetSummary;
  label: string;
}

export type DatasetNode = Node<DatasetNodeData, 'dataset'>;

export interface RelationshipEdgeData extends Record<string, unknown> {
  relationship: DatasetRelationship;
  label: string;
}

export type RelationshipEdge = Edge<RelationshipEdgeData>;

// ---------------------------------------------------------------------------
// API responses
// ---------------------------------------------------------------------------

export interface RelationshipListResponse {
  count: number;
  result: DatasetRelationship[];
}

export interface RelationshipCreateResponse {
  id: number;
  result: DatasetRelationshipCreate;
}

export interface RelationshipGraphResponse {
  datasets: DatasetSummary[];
  relationships: DatasetRelationship[];
}
