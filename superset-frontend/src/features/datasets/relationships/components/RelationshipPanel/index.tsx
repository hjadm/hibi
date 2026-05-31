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
import { useState, useCallback } from 'react';
import { t, styled, css, useTheme } from '@superset-ui/core';
import type {
  DatasetRelationship,
  ActiveJoin,
} from '../../hooks/useExploreRelationships';

const PanelContainer = styled.div`
  ${({ theme }) => css`
    padding: ${theme.sizeUnit * 4}px;
    border-bottom: 1px solid ${theme.colorSplit};
  `}
`;

const PanelHeader = styled.div`
  ${({ theme }) => css`
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: ${theme.sizeUnit * 2}px;

    h4 {
      margin: 0;
      font-size: ${theme.fontSize}px;
      font-weight: ${theme.fontWeightStrong};
    }
  `}
`;

const RelationshipRow = styled.div<{ $enabled: boolean }>`
  ${({ theme, $enabled }) => css`
    display: flex;
    align-items: center;
    gap: ${theme.sizeUnit * 2}px;
    padding: ${theme.sizeUnit * 2}px ${theme.sizeUnit * 3}px;
    margin-bottom: ${theme.sizeUnit}px;
    border-radius: ${theme.borderRadius}px;
    background: ${$enabled
      ? 'rgba(5, 150, 105, 0.06)'
      : theme.colors.grayscale.light3};
    border: 1px solid
      ${$enabled ? 'rgba(5, 150, 105, 0.2)' : theme.colorSplit};
    transition: all 0.15s ease;

    &:hover {
      background: ${$enabled
        ? 'rgba(5, 150, 105, 0.1)'
        : theme.colors.grayscale.light2};
    }
  `}
`;

const ToggleSwitch = styled.button<{ $active: boolean }>`
  ${({ theme, $active }) => css`
    width: 28px;
    height: 16px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    padding: 2px;
    transition: all 0.15s ease;
    flex-shrink: 0;
    background-color: ${$active ? '#059669' : theme.colors.grayscale.light2};
    position: relative;

    &::after {
      content: '';
      display: block;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: white;
      transition: transform 0.15s ease;
      transform: translateX(${$active ? '12px' : '0'});
    }

    &:hover {
      opacity: 0.85;
    }

    &:focus-visible {
      outline: 2px solid ${theme.colorPrimary};
      outline-offset: 2px;
    }
  `}
`;

const RelationshipInfo = styled.div`
  ${({ theme }) => css`
    flex: 1;
    min-width: 0;
    font-size: ${theme.fontSizeSM}px;

    .rel-name {
      font-weight: ${theme.fontWeightStrong};
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .rel-detail {
      color: ${theme.colors.grayscale.base};
      font-size: ${theme.fontSizeXS}px;
      margin-top: 1px;
    }
  `}
`;

const ColumnList = styled.div`
  ${({ theme }) => css`
    margin-top: ${theme.sizeUnit}px;

    label {
      display: inline-flex;
      align-items: center;
      gap: ${theme.sizeUnit}px;
      font-size: ${theme.fontSizeXS}px;
      padding: 1px ${theme.sizeUnit}px;
      margin: 1px ${theme.sizeUnit}px 1px 0;
      border-radius: 2px;
      background: ${theme.colors.grayscale.light2};
      cursor: pointer;

      input {
        margin: 0;
        cursor: pointer;
      }

      &:hover {
        background: ${theme.colors.grayscale.light1};
      }
    }
  `}
`;

interface RelationshipPanelProps {
  relationships: DatasetRelationship[];
  activeJoins: Map<number, ActiveJoin>;
  availableTargetColumns: Map<number, string[]>;
  onToggleJoin: (relationshipId: number) => void;
  onUpdateSelectedColumns: (relationshipId: number, columns: string[]) => void;
}

/**
 * Panel section in the Explore datasource sidebar showing
 * available relationships and their JOIN status.
 *
 * Users can:
 * - Toggle JOIN on/off
 * - See which columns map to which target
 * - Select which target columns to include
 */
export function RelationshipPanel({
  relationships,
  activeJoins,
  availableTargetColumns,
  onToggleJoin,
  onUpdateSelectedColumns,
}: RelationshipPanelProps) {
  const [expanded, setExpanded] = useState(false);
  const theme = useTheme();

  if (relationships.length === 0) return null;

  return (
    <PanelContainer>
      <PanelHeader>
        <h4>{t('Relationships')}</h4>
        {relationships.length > 1 && (
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            css={css`
              border: none;
              background: none;
              font-size: ${theme.fontSizeSM}px;
              color: ${theme.colorPrimary};
              cursor: pointer;
              padding: 0;
              &:hover {
                text-decoration: underline;
              }
            `}
          >
            {expanded ? t('Collapse') : t('Show all')}
          </button>
        )}
      </PanelHeader>

      {(expanded ? relationships : relationships.slice(0, 1)).map(rel => {
        const join = activeJoins.get(rel.id);
        const enabled = join?.enabled ?? false;
        const selectedCols = join?.selectedColumns ?? [];
        const targetCols = availableTargetColumns.get(rel.id) ?? [];

        return (
          <RelationshipRow key={rel.id} $enabled={enabled}>
            <ToggleSwitch
              $active={enabled}
              onClick={() => onToggleJoin(rel.id)}
              aria-label={
                enabled
                  ? t('Disable relationship %s', rel.id)
                  : t('Enable relationship %s', rel.id)
              }
            />
            <RelationshipInfo>
              <div className="rel-name">
                {rel.name ?? t('Relationship #%s', rel.id)}
              </div>
              <div className="rel-detail">
                {rel.relationship_type.replace(/_/g, ' → ')} &middot;{' '}
                {rel.join_type} JOIN &middot;{' '}
                {rel.columns
                  .map(
                    col =>
                      `${col.source_column_name} → ${col.target_column_name}`,
                  )
                  .join(', ')}
              </div>
              {enabled && targetCols.length > 0 && (
                <ColumnList>
                  {targetCols.map(colName => (
                    <label key={colName}>
                      <input
                        type="checkbox"
                        checked={selectedCols.includes(colName)}
                        onChange={e => {
                          if (e.target.checked) {
                            onUpdateSelectedColumns(rel.id, [
                              ...selectedCols,
                              colName,
                            ]);
                          } else {
                            onUpdateSelectedColumns(
                              rel.id,
                              selectedCols.filter(c => c !== colName),
                            );
                          }
                        }}
                      />
                      {colName}
                    </label>
                  ))}
                </ColumnList>
              )}
            </RelationshipInfo>
          </RelationshipRow>
        );
      })}
    </PanelContainer>
  );
}
