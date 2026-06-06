/**
 * M5 - Conditional Color
 * Cor condicional automática baseada no valor da célula relativo
 * à média da linha/coluna (acima = verde, abaixo = vermelho).
 * 
 * Funciona em conjunto com o sistema existente de cellColorFormatters
 * no Superset, mas adiciona um fallback automático.
 */
import { PivotModule } from './index';

const conditionalColor: PivotModule = {
  id: 'conditionalColor',
  name: 'Conditional Color',
  description: 'Cor condicional automática por valor',
  css: (_theme) => `
    /* Valores muito acima da média - verde forte */
    table.pvtTable tbody tr td.cond-high {
      color: #15803d;
      font-weight: 500;
    }

    /* Valores acima da média - verde claro */
    table.pvtTable tbody tr td.cond-medium-high {
      color: #22c55e;
    }

    /* Valores na média - cor padrão (herdada) */
    table.pvtTable tbody tr td.cond-average {
      color: inherit;
    }

    /* Valores abaixo da média - laranja */
    table.pvtTable tbody tr td.cond-medium-low {
      color: #f97316;
    }

    /* Valores muito abaixo da média - vermelho */
    table.pvtTable tbody tr td.cond-low {
      color: #dc2626;
      font-weight: 500;
    }

    /* Células de total não recebem cor condicional (herdam destaque) */
    table.pvtTable tbody tr.pvtRowTotals td[class*="cond-"] {
      color: inherit;
      font-weight: ${({ theme }: any) => theme?.fontWeightStrong || 700};
    }
  `,
};

export default conditionalColor;
