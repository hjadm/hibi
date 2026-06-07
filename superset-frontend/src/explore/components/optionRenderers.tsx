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

import { styled } from '@apache-superset/core/theme';
import {
  MetricOption,
  ColumnOption,
  MetricOptionProps,
  ColumnOptionProps,
} from '@superset-ui/chart-controls';
import { isFeatureEnabled, FeatureFlag } from '@superset-ui/core';
import { RelationshipColumnBadge } from 'src/features/datasets/relationships/components/RelationshipColumnBadge';

const OptionContainer = styled.div`
  width: 100%;
  > span {
    display: flex;
    align-items: center;
  }

  .option-label {
    display: inline-block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    & ~ i {
      margin-left: ${({ theme }) => theme.sizeUnit}px;
    }
  }
  .type-label {
    margin-right: ${({ theme }) => theme.sizeUnit * 3}px;
    width: ${({ theme }) => theme.sizeUnit * 7}px;
    display: inline-block;
    text-align: center;
    font-weight: ${({ theme }) => theme.fontWeightStrong};
  }
`;

export const StyledMetricOption = (props: MetricOptionProps) => (
  <OptionContainer>
    <MetricOption {...props} />
  </OptionContainer>
);

export const StyledColumnOption = (props: ColumnOptionProps) => {
  // Check if this column has relationship metadata
  const targetDatasetName =
    isFeatureEnabled(FeatureFlag.DatasetRelationships) &&
    props.column?.relationship_target_dataset
      ? props.column.relationship_target_dataset
      : undefined;

  return (
    <OptionContainer>
      <ColumnOption {...props} />
      {targetDatasetName && (
        <RelationshipColumnBadge
          targetDatasetName={targetDatasetName}
          compact
        />
      )}
    </OptionContainer>
  );
};
