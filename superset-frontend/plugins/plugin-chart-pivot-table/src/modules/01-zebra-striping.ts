/**
 * M1 - Zebra Striping
 * Alternância de cor entre linhas para melhor legibilidade.
 */
import { PivotModule } from './index';

const zebraStriping: PivotModule = {
  id: 'zebraStriping',
  name: 'Zebra Striping',
  description: 'Alternância de cor entre linhas da tabela',
  css: (theme) => `
    table.pvtTable tbody tr:nth-child(even) td,
    table.pvtTable tbody tr:nth-child(even) th {
      background-color: ${theme.colorFillQuaternary};
    }

    table.pvtTable tbody tr:hover td,
    table.pvtTable tbody tr:hover th {
      background-color: ${theme.colorFillContentHover};
    }

    table.pvtTable tbody tr.pvtRowTotals:nth-child(even) td,
    table.pvtTable tbody tr.pvtRowTotals:nth-child(even) th {
      background-color: ${theme.colorBgBase};
    }
  `,
};

export default zebraStriping;
