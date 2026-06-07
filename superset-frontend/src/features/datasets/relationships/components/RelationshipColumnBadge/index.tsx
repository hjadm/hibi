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

import { Tooltip } from '@superset-ui/core/components';
import { styled, css, useTheme } from '@apache-superset/core/theme';
import { t } from '@apache-superset/core/translation';

export interface RelationshipColumnBadgeProps {
  /** Name of the target dataset this column comes from */
  targetDatasetName?: string;
  /** Whether this is a compact version (smaller icon) */
  compact?: boolean;
}

const BadgeContainer = styled.span<{ compact?: boolean }>`
  ${({ theme, compact }) => css`
    display: inline-flex;
    align-items: center;
    gap: ${theme.sizeUnit}px;
    font-size: ${theme.fontSizeXS}px;
    font-weight: ${theme.fontWeightStrong};
    padding: ${compact ? '1px 4px' : '2px 6px'};
    border-radius: ${theme.borderRadius}px;
    margin-left: ${compact ? theme.sizeUnit : theme.sizeUnit * 1.5}px;
    white-space: nowrap;
    background-color: ${theme.colorPrimaryBg};
    color: ${theme.colorPrimary};
    border: 1px solid ${theme.colorPrimaryBorder};
    vertical-align: middle;
    line-height: 1;

    svg {
      width: ${compact ? '10px' : '12px'};
      height: ${compact ? '10px' : '12px'};
    }
  `}
`;

/**
 * Visual badge shown next to a column name to indicate it comes from
 * a target dataset via an active relationship JOIN.
 *
 * This badge is purely informational and decorative — it doesn't affect
 * the column's behavior or selection state.
 */
export function RelationshipColumnBadge({
  targetDatasetName,
  compact = false,
}: RelationshipColumnBadgeProps) {
  const theme = useTheme();
  const label = targetDatasetName || t('related');

  return (
    <Tooltip
      title={t(
        'This column comes from the "%s" dataset via an active relationship',
        label,
      )}
    >
      <BadgeContainer compact={compact}>
        {/* Link/join icon */}
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
        </svg>
        {!compact && <span>{label}</span>}
      </BadgeContainer>
    </Tooltip>
  );
}

export default RelationshipColumnBadge;
