/**
 * M2 - Totals Highlight
 * Destaque visual nas linhas/colunas de total e subtotal.
 */
import { PivotModule } from './index';

const totalsHighlight: PivotModule = {
  id: 'totalsHighlight',
  name: 'Totals Highlight',
  description: 'Destaque visual em totais e subtotais',
  css: (theme) => `
    table.pvtTable tbody tr.pvtRowTotals {
      border-top: 2px solid ${theme.colorPrimary};
    }

    table.pvtTable tbody tr.pvtRowTotals td,
    table.pvtTable tbody tr.pvtRowTotals th {
      background-color: ${theme.colorPrimaryBg} !important;
      font-weight: ${theme.fontWeightStrong};
    }

    table.pvtTable .pvtTotal,
    table.pvtTable .pvtGrandTotal {
      background-color: ${theme.colorPrimaryBgHover} !important;
      font-weight: ${theme.fontWeightStrong};
      border-top: 2px solid ${theme.colorPrimary};
    }

    table.pvtTable .pvtSubtotalLabel,
    table.pvtTable .pvtTotalLabel {
      font-weight: ${theme.fontWeightStrong};
      color: ${theme.colorPrimaryText};
    }

    /* Subtotais com borda superior sutil */
    table.pvtTable tbody tr td.pvtSubtotal,
    table.pvtTable tbody tr th.pvtSubtotal {
      border-top: 1px dashed ${theme.colorBorderSecondary};
    }
  `,
};

export default totalsHighlight;
