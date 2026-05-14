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

import { useState, useEffect, useCallback } from 'react';
import { SupersetClient } from '@superset-ui/core';
import { addDangerToast } from 'src/components/MessageToasts/actions';
import type { DatasetSummary } from '../types';

/**
 * Fetch a lightweight list of datasets (id, name, database, columns)
 * for use in the relationship graph canvas.
 */
export function useDatasetList() {
  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [loading, setLoading] = useState(false);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const { json } = await SupersetClient.get({
        endpoint: '/api/v1/dataset/?q=(keys:none,columns:!(id,table_name,schema,database,columns),page_size:500)',
      });
      // The dataset list API returns { result: [...] }
      const result = (json as { result: DatasetSummary[] }).result;
      setDatasets(result);
    } catch (err) {
      addDangerToast('Error fetching datasets.');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { datasets, loading, refresh: fetch };
}

/**
 * Fetch a single dataset with full column info.
 */
export function useDataset(datasetId: number | null) {
  const [dataset, setDataset] = useState<DatasetSummary | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (datasetId === null) {
      setDataset(null);
      return;
    }
    setLoading(true);
    SupersetClient.get({
      endpoint: `/api/v1/dataset/${datasetId}`,
    })
      .then(({ json }) => {
        setDataset(json as DatasetSummary);
      })
      .catch(() => {
        addDangerToast('Error fetching dataset.');
      })
      .finally(() => setLoading(false));
  }, [datasetId]);

  return { dataset, loading };
}
