/**
 * M10 - Padding & Spacing
 * Padding e spacing otimizados para melhor scan visual.
 * Reduz desperdício de espaço e melhora densidade de informação.
 */
import { PivotModule } from './index';

const paddingSpacing: PivotModule = {
  id: 'paddingSpacing',
  name: 'Padding & Spacing',
  description: 'Padding e spacing otimizados',
  css: (theme) => `
    table.pvtTable {
      line-height: 1.3;
      font-size: ${theme.fontSizeSM}px;
      margin: 0;
    }

    table.pvtTable thead tr th,
    table.pvtTable tbody tr th {
      padding: 6px 8px;
    }

    table.pvtTable tbody tr td {
      padding: 4px 8px;
      font-size: ${theme.fontSizeSM}px;
      vertical-align: middle;
    }

    /* Células numéricas com monospace para alinhamento */
    table.pvtTable tbody tr td:not(.pvtRowLabel) {
      font-feature-settings: 'tnum' 1;
      font-variant-numeric: tabular-nums;
    }

    /* Headers mais compactos */
    table.pvtTable thead tr th {
      font-size: ${theme.fontSizeSM}px;
      padding: 6px 8px;
    }

    /* Labels de linha com padding extra à esquerda para hierarquia */
    table.pvtTable tbody tr th.pvtRowLabel {
      padding-left: 10px;
    }
  `,
};

export default paddingSpacing;
