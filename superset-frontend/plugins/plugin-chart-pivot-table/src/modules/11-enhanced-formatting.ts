/**
 * M11 - Enhanced Formatting Rules
 * 
 * Módulo que ativa regras visuais configuráveis na tabela pivot:
 * - Cor de fundo condicional (BACKGROUND_COLOR)
 * - Cor do texto condicional (TEXT_COLOR)
 * - Barra horizontal na célula (CELL_BAR)
 * - Ícones nos valores (positive/negative/trend)
 * - Texto legível automático sobre fundo colorido
 * 
 * Funciona em conjunto com o sistema ConditionalFormattingControl
 * existente no Superset e o CSS dos módulos M1-M10.
 */
import { PivotModule } from './index';

const enhancedFormatting: PivotModule = {
  id: 'enhancedFormatting',
  name: 'Enhanced Formatting Rules',
  description: 'Ativa coloração condicional, cell bars e ícones configuráveis',
  css: (theme) => `
    /* ============ CELL BARS ============ */
    table.pvtTable tbody tr td.cell-bar {
      position: relative;
      z-index: 0;
    }

    table.pvtTable tbody tr td.cell-bar::before {
      content: '';
      position: absolute;
      top: 1px;
      left: 0;
      height: calc(100% - 2px);
      z-index: -1;
      border-radius: 0 2px 2px 0;
      opacity: 0.15;
      transition: opacity 0.15s ease;
      background-color: ${theme.colorPrimary};
      min-width: 2px;
    }

    table.pvtTable tbody tr td.cell-bar:hover::before {
      opacity: 0.25;
    }

    /* Cell bar em células de total com mais destaque */
    table.pvtTable tbody tr.pvtRowTotals td.cell-bar::before {
      opacity: 0.2;
    }

    /* ============ BACKGROUND COLOR - Texto legível ============ */
    table.pvtTable tbody tr td[style*="background-color"] {
      font-weight: 500;
    }

    /* ============ ÍCONES NOS VALORES ============ */
    /* Indicador de tendência positiva (seta verde para cima) */
    table.pvtTable tbody tr td.trend-up::after {
      content: ' ▲';
      color: #16a34a;
      font-size: 10px;
      vertical-align: middle;
    }

    /* Indicador de tendência negativa (seta vermelha para baixo) */
    table.pvtTable tbody tr td.trend-down::after {
      content: ' ▼';
      color: #dc2626;
      font-size: 10px;
      vertical-align: middle;
    }

    /* Indicador neutro */
    table.pvtTable tbody tr td.trend-flat::after {
      content: ' ―';
      color: #9ca3af;
      font-size: 10px;
      vertical-align: middle;
    }

    /* ============ FORMATAÇÃO PORCENTAGEM ============ */
    table.pvtTable tbody tr td.pct-high {
      color: #15803d;
      font-weight: 600;
    }

    table.pvtTable tbody tr td.pct-low {
      color: #dc2626;
      font-weight: 600;
    }

    /* ============ VALORES DESTACADOS ============ */
    /* Top 3 valores ganham destaque especial */
    table.pvtTable tbody tr td.rank-1 {
      font-weight: 700;
      position: relative;
    }

    table.pvtTable tbody tr td.rank-1::after {
      content: ' 🏆';
      font-size: 11px;
      position: absolute;
      right: 2px;
      top: 50%;
      transform: translateY(-50%);
    }

    /* ============ VALORES NULOS/ZERO ============ */
    table.pvtTable tbody tr td.value-zero {
      color: ${theme.colorTextQuaternary};
      font-style: italic;
    }

    table.pvtTable tbody tr td.value-null {
      color: ${theme.colorTextQuaternary};
      font-style: italic;
    }

    table.pvtTable tbody tr td.value-null::before {
      content: '—';
    }
  `,
};

export default enhancedFormatting;
