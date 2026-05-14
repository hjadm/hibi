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

import { useCallback } from 'react';
import { useHistory } from 'react-router-dom';
import { styled, useTheme } from '@apache-superset/core/theme';
import { t } from '@apache-superset/core/translation';
import { Button, Icons } from '@superset-ui/core/components';
import { RelationshipCanvas } from 'src/features/datasets/relationships';

const StyledPage = styled.div`
  display: flex;
  flex-direction: column;
  height: calc(100vh - ${({ theme }) => theme.sizeUnit * 12}px);
  padding: ${({ theme }) => theme.sizeUnit * 4}px;
`;

const StyledHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${({ theme }) => theme.sizeUnit * 4}px;
`;

const StyledTitle = styled.h2`
  margin: 0;
  font-size: ${({ theme }) => theme.typography.sizes.xl}px;
  font-weight: ${({ theme }) => theme.typography.weights.bold};
  color: ${({ theme }) => theme.colors.grayscale.dark1};
`;

export default function DatasetRelationshipsPage() {
  const theme = useTheme();
  const history = useHistory();

  const handleBack = useCallback(() => {
    history.push('/dataset/list/');
  }, [history]);

  return (
    <StyledPage>
      <StyledHeader>
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.gridUnit * 2 }}>
          <Button buttonSize="sm" buttonStyle="secondary" onClick={handleBack}>
            <Icons.Back iconSize="s" /> {t('Back to Datasets')}
          </Button>
          <StyledTitle>{t('Dataset Relationships')}</StyledTitle>
        </div>
      </StyledHeader>
      <div style={{ flex: 1 }}>
        <RelationshipCanvas />
      </div>
    </StyledPage>
  );
}
