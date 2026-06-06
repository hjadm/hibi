/**
 * M4 - Cell Bar
 * Barras horizontais inline nas células de valor, proporcionais ao
 * maior valor da linha/coluna (tipo Excel "Data Bar").
 *
 * A barra é renderizada como um pseudo-elemento ::before com largura
 * proporcional. A classe "cell-bar" deve ser aplicada nas células <td>
 * via TableRenderers.
 *
 * A cor da barra pode ser:
 * - Azul para valores positivos
 * - Vermelho para negativos (se M3 ativo)
 */
import { PivotModule } from './index';

const cellBar: PivotModule = {
  id: 'cellBar',
  name: 'Cell Bar',
  description: 'Barras horizontais inline nas células',
  css: (theme) => `
    table.pvtTable tbody tr td.cell-bar {
      position: relative;
      z-index: 0;
    }

    table.pvtTable tbody tr td.cell-bar::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      height: 100%;
      z-index: -1;
      border-radius: 0 2px 2px 0;
      opacity: 0.12;
      transition: opacity 0.15s ease;
      background-color: ${theme.colorPrimary};
    }

    table.pvtTable tbody tr td.cell-bar.negative::before {
      background-color: #dc2626;
      left: auto;
      right: 0;
      border-radius: 2px 0 0 2px;
    }

    table.pvtTable tbody tr td.cell-bar:hover::before {
      opacity: 0.2;
    }

    /* Células de total com barra mais escura */
    table.pvtTable tbody tr.pvtRowTotals td.cell-bar::before {
      opacity: 0.18;
    }

    table.pvtTable tbody tr.pvtRowTotals td.cell-bar:hover::before {
      opacity: 0.28;
    }
  `,
};

export default cellBar;
