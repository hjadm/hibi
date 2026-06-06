/**
 * M8 - Header Truncate
 * Truncamento automático de headers longos com ellipsis + tooltip.
 */
import { PivotModule } from './index';

const headerTruncate: PivotModule = {
  id: 'headerTruncate',
  name: 'Header Truncate',
  description: 'Truncamento de headers com ellipsis',
  css: (_theme) => `
    table.pvtTable thead tr th {
      max-width: 200px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    table.pvtTable thead tr th.pvtColLabel {
      max-width: 150px;
    }

    table.pvtTable tbody tr th.pvtRowLabel {
      max-width: 250px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    /* Para headers que explicitamente não devem truncar */
    table.pvtTable thead tr th.pvtTotalLabel,
    table.pvtTable thead tr th.pvtSubtotalLabel {
      max-width: none;
      white-space: normal;
    }
  `,
};

export default headerTruncate;
