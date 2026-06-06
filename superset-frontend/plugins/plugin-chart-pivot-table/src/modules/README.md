# Módulos de Customização da Tabela Pivot

Estrutura modular para customizações da tabela Pivot do Super Sete (Safira).
Cada módulo é independente e pode ser ativado/desativado individualmente.

## Módulos

| Módulo | Arquivo | Descrição | Status |
|--------|---------|-----------|--------|
| M1 | `01-zebra-striping.ts` | Alternância de cor entre linhas | ✅ |
| M2 | `02-totals-highlight.ts` | Destaque visual em totais/subtotais | ✅ |
| M3 | `03-negative-red.ts` | Números negativos em vermelho | ✅ |
| M4 | `04-cell-bar.ts` | Barras horizontais inline nas células | ✅ |
| M5 | `05-conditional-color.ts` | Cor condicional automática por valor | ✅ |
| M6 | `06-tooltips.ts` | Tooltips com breakdown nas células | ✅ |
| M7 | `07-sort-visual.ts` | Ícones de ordenação mais visíveis | ✅ |
| M8 | `08-header-truncate.ts` | Truncamento de headers com ellipsis | ✅ |
| M9 | `09-scrollbar-polish.ts` | Scrollbars mais refinadas | ✅ |
| M10 | `10-padding-spacing.ts` | Padding e spacing otimizados | ✅ |
| M11 | `11-enhanced-formatting.ts` | Coloração condicional + cell bars + ícones integrados | ✅ |
| M12 | `12-value-icons.ts` | Ícones por valor (setas, medalhas, alertas, check/cross) | ✅ |
| — | `rule-engine.ts` | Motor de regras configurável para aplicar condicionais nas células | ✅ |

## Como usar

```ts
// No PivotTableChart.tsx ou TableRenderers.tsx
import { applyModule } from './modules';

// Aplica módulos específicos
applyModule('zebraStriping', tableElement);
applyModule('negativeRed', tableElement);
```

## Ordem de implementação

1. **Fase 1 - Visual base** (M1, M2, M3, M8, M9, M10) — risco baixo
2. **Fase 2 - Células enriquecidas** (M4, M5, M6) — risco médio
3. **Fase 3 - UX** (M7) — risco médio
