/**
 * M3 - Negative Red
 * Números negativos exibidos em vermelho automaticamente.
 * Depende de uma classe CSS aplicada via formatação condicional no TableRenderers.
 */
import { PivotModule } from './index';

const negativeRed: PivotModule = {
  id: 'negativeRed',
  name: 'Negative Numbers in Red',
  description: 'Números negativos em vermelho',
  css: (_theme) => `
    table.pvtTable tbody tr td.negative,
    table.pvtTable tbody tr td .negative {
      color: #dc2626 !important;
      font-weight: 500;
    }

    table.pvtTable tbody tr td.positive {
      color: #16a34a;
    }

    /* Variação com fundo sutil para destaque extra */
    table.pvtTable tbody tr td.negative-bg {
      background-color: #fef2f2;
      color: #dc2626 !important;
      font-weight: 500;
    }
  `,
};

export default negativeRed;
