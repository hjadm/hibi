/**
 * M7 - Sort Visual
 * Ícones de ordenação mais visíveis nos headers.
 * Substitui o ícone genérico ColumnHeightOutlined por setas
 * direcionais mais claras (CaretUp/Down nos headers clicáveis).
 */
import { PivotModule } from './index';

const sortVisual: PivotModule = {
  id: 'sortVisual',
  name: 'Sort Visual',
  description: 'Ícones de ordenação mais visíveis nos headers',
  css: (theme) => `
    /* Indicador de coluna ordenável mais visível */
    table.pvtTable thead tr th.sortable,
    table.pvtTable thead tr th.pvtColLabel.sortable {
      cursor: pointer;
      position: relative;
      padding-right: 20px !important;
    }

    table.pvtTable thead tr th.sortable::after {
      content: '';
      position: absolute;
      right: 6px;
      top: 50%;
      transform: translateY(-50%);
      border-left: 4px solid transparent;
      border-right: 4px solid transparent;
    }

    table.pvtTable thead tr th.sortable.sort-asc::after {
      border-bottom: 5px solid ${theme.colorPrimary};
      border-top: none;
    }

    table.pvtTable thead tr th.sortable.sort-desc::after {
      border-top: 5px solid ${theme.colorPrimary};
      border-bottom: none;
    }

    table.pvtTable thead tr th.sortable:not(.sort-asc):not(.sort-desc)::after {
      border-bottom: 5px solid ${theme.colorTextQuaternary};
      border-top: none;
      opacity: 0.4;
    }

    table.pvtTable thead tr th.sortable:hover::after {
      opacity: 1;
    }

    /* Destacar header da coluna ordenada */
    table.pvtTable thead tr th.sort-asc,
    table.pvtTable thead tr th.sort-desc {
      background-color: ${theme.colorPrimaryBg};
    }

    /* Botão de toggle nos subtotais mais visível */
    table.pvtTable .toggle-wrapper .toggle {
      color: ${theme.colorPrimary};
      opacity: 0.7;
    }

    table.pvtTable .toggle-wrapper .toggle:hover {
      opacity: 1;
    }
  `,
};

export default sortVisual;
