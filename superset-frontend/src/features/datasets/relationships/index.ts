/**
 * Dataset Relationships feature module.
 *
 * Exposes the main canvas component and all hooks/types for external use.
 */
export { default as RelationshipCanvas } from './components/RelationshipCanvas';
export { DatasetNode } from './components/DatasetNode';
export { RelationshipEdge } from './components/RelationshipEdge';
export { default as ColumnPickerModal } from './components/ColumnPickerModal';
export { default as RelationshipSidebar } from './components/RelationshipSidebar';

export * from './hooks';
export * from './types';
