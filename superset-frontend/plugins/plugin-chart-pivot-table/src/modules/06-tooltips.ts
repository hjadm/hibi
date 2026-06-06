/**
 * M6 - Tooltips
 * Tooltips com breakdown nas células de valor.
 * O título do tooltip mostra o valor formatado completo.
 * 
 * Nota: O HTML nativo title é o fallback universal. Para tooltips
 * mais ricos (React), seria necessário modificar o TableRenderers
 * para usar Ant Design Tooltip ou Popover.
 */
import { PivotModule } from './index';

const tooltips: PivotModule = {
  id: 'tooltips',
  name: 'Cell Tooltips',
  description: 'Tooltips com breakdown nas células',
  css: (_theme) => `
    /* Tooltips mais visíveis no HTML nativo */
    table.pvtTable tbody tr td[title] {
      cursor: help;
    }

    /* Fallback para tooltips personalizados com data-attribute */
    table.pvtTable tbody tr td[data-tooltip]:hover::after {
      content: attr(data-tooltip);
      position: absolute;
      background: #1f2937;
      color: #f9fafb;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      white-space: nowrap;
      z-index: 1000;
      pointer-events: none;
      bottom: 100%;
      left: 50%;
      transform: translateX(-50%);
      margin-bottom: 4px;
    }
  `,
};

export default tooltips;
