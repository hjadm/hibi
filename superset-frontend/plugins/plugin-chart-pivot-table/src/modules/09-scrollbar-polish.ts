/**
 * M9 - Scrollbar Polish
 * Scrollbars mais refinadas e consistentes entre browsers.
 * Reforça o que já existe no PivotTableChart.tsx.
 */
import { PivotModule } from './index';

const scrollbarPolish: PivotModule = {
  id: 'scrollbarPolish',
  name: 'Scrollbar Polish',
  description: 'Scrollbars mais refinadas',
  css: (theme) => `
    .pivot-table-wrapper {
      scrollbar-width: thin;
      scrollbar-color: ${theme.colorFillSecondary} ${theme.colorFillQuaternary};
    }

    .pivot-table-wrapper::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }

    .pivot-table-wrapper::-webkit-scrollbar-track {
      background: ${theme.colorFillQuaternary};
      border-radius: 3px;
    }

    .pivot-table-wrapper::-webkit-scrollbar-thumb {
      background: ${theme.colorFillSecondary};
      border-radius: 3px;
    }

    .pivot-table-wrapper::-webkit-scrollbar-thumb:hover {
      background: ${theme.colorFillTertiary};
    }

    .pivot-table-wrapper::-webkit-scrollbar-corner {
      background: ${theme.colorFillQuaternary};
    }

    /* Smooth scrolling para uma experiência mais fluida */
    .pivot-table-wrapper {
      scroll-behavior: smooth;
    }
  `,
};

export default scrollbarPolish;
