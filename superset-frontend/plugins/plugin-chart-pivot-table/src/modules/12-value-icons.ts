/**
 * M12 - Value Icons
 * 
 * Ícones visuais nas células baseados no valor:
 * - Seta ▲/▼ para variação positiva/negativa
 * - Medalha 🏆 para top 3 valores
 * - Indicador de alerta ⚠️ para valores críticos
 * - Check/cross ✅/❌ para booleanos
 * 
 * NOTA: Este módulo requer modificações no TableRenderers.tsx
 * para aplicar as classes CSS dinamicamente com base nos dados.
 * Por enquanto, só fornece o CSS para quando as classes forem aplicadas.
 */
import { PivotModule } from './index';

const valueIcons: PivotModule = {
  id: 'valueIcons',
  name: 'Value Icons',
  description: 
    'Ícones visuais nas células: setas de tendência, medalhas, alertas',
  css: (theme) => `
    /* ============ SETAS DE TENDÊNCIA ============ */
    /* Aplicar classe 'icon-trend-up' quando valor > meta/media */
    table.pvtTable tbody tr td .icon-trend-up,
    table.pvtTable tbody tr td.icon-trend-up {
      position: relative;
    }

    table.pvtTable tbody tr td .icon-trend-up::after {
      content: '';
      display: inline-block;
      width: 0;
      height: 0;
      border-left: 5px solid transparent;
      border-right: 5px solid transparent;
      border-bottom: 7px solid #16a34a;
      margin-left: 4px;
      vertical-align: middle;
    }

    /* Aplicar classe 'icon-trend-down' quando valor < meta/media */
    table.pvtTable tbody tr td .icon-trend-down::after {
      content: '';
      display: inline-block;
      width: 0;
      height: 0;
      border-left: 5px solid transparent;
      border-right: 5px solid transparent;
      border-top: 7px solid #dc2626;
      margin-left: 4px;
      vertical-align: middle;
    }

    /* ============ MEDALHAS (TOP N) ============ */
    table.pvtTable tbody tr td.icon-gold::before {
      content: '🥇';
      font-size: 11px;
      margin-right: 2px;
    }

    table.pvtTable tbody tr td.icon-silver::before {
      content: '🥈';
      font-size: 11px;
      margin-right: 2px;
    }

    table.pvtTable tbody tr td.icon-bronze::before {
      content: '🥉';
      font-size: 11px;
      margin-right: 2px;
    }

    /* ============ ALERTAS ============ */
    table.pvtTable tbody tr td.icon-alert::after {
      content: ' ⚠️';
      font-size: 11px;
      vertical-align: middle;
    }

    /* ============ BOOLEANOS ============ */
    table.pvtTable tbody tr td.icon-true {
      color: #16a34a;
      font-weight: 600;
    }

    table.pvtTable tbody tr td.icon-true::before {
      content: '✓ ';
    }

    table.pvtTable tbody tr td.icon-false {
      color: #dc2626;
    }

    table.pvtTable tbody tr td.icon-false::before {
      content: '✗ ';
    }

    /* ============ PORCENTAGEM COM BARRA ============ */
    table.pvtTable tbody tr td.pct-bar {
      position: relative;
      z-index: 0;
    }

    table.pvtTable tbody tr td.pct-bar::before {
      content: '';
      position: absolute;
      top: 1px;
      left: 0;
      height: calc(100% - 2px);
      z-index: -1;
      border-radius: 2px;
      background: linear-gradient(
        90deg,
        ${theme.colorPrimaryBg} 0%,
        ${theme.colorPrimaryBorder} 100%
      );
      opacity: 0.3;
    }

    table.pvtTable tbody tr td.pct-bar.pct-high::before {
      background: linear-gradient(
        90deg,
        #dcfce7 0%,
        #16a34a 100%
      );
    }

    table.pvtTable tbody tr td.pct-bar.pct-low::before {
      background: linear-gradient(
        90deg,
        #fef2f2 0%,
        #dc2626 100%
      );
    }

    /* ============ THRESHOLD INDICATORS ============ */
    table.pvtTable tbody tr td.threshold-ok {
      border-left: 3px solid #16a34a;
    }

    table.pvtTable tbody tr td.threshold-warn {
      border-left: 3px solid #f59e0b;
    }

    table.pvtTable tbody tr td.threshold-critical {
      border-left: 3px solid #dc2626;
      font-weight: 600;
    }
  `,
};

export default valueIcons;
