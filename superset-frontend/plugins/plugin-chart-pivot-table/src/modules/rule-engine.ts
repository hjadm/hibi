/**
 * Rule Engine — Sistema de Regras Visuais para a Tabela Pivot
 * 
 * Permite definir regras JSON que são aplicadas célula a célula.
 * As regras podem ser carregadas via props do chart ou de um arquivo.
 * 
 * Exemplo de regra:
 * {
 *   name: 'Negativo em vermelho',
 *   field: '*',           // aplica a todas as colunas numéricas
 *   condition: { type: 'lt', value: 0 },
 *   style: { color: '#dc2626', fontWeight: 'bold' },
 *   icon: 'trend-down',
 * }
 * 
 * {
 *   name: 'Top 3 com medalha',
 *   field: 'receita',
 *   condition: { type: 'top', value: 3 },
 *   icon: 'gold',
 *   className: 'rank-1',
 * }
 */

export type RuleCondition =
  | { type: 'gt'; value: number }
  | { type: 'gte'; value: number }
  | { type: 'lt'; value: number }
  | { type: 'lte'; value: number }
  | { type: 'eq'; value: number | string | boolean }
  | { type: 'neq'; value: number | string | boolean }
  | { type: 'between'; min: number; max: number }
  | { type: 'top'; value: number }        // Top N valores
  | { type: 'bottom'; value: number }     // Bottom N valores
  | { type: 'pct_above'; value: number }  // % acima da média da coluna
  | { type: 'pct_below'; value: number }  // % abaixo da média da coluna
  | { type: 'threshold'; value: number }  // Acima de threshold (OK/WARN/CRITICAL)
  | { type: 'is_null' }
  | { type: 'is_zero' }
  | { type: 'is_true' }
  | { type: 'is_false' };

export type RuleIcon = 
  | 'trend-up'
  | 'trend-down' 
  | 'trend-flat'
  | 'gold'
  | 'silver'
  | 'bronze'
  | 'alert'
  | 'check'
  | 'cross'
  | 'pct-bar';

export interface VisualRule {
  name: string;
  field: string | '*';     // '*' = aplica a todas as colunas métricas
  condition: RuleCondition;
  style?: Partial<CSSStyleDeclaration>;
  className?: string;
  icon?: RuleIcon;
  cellBar?: {
    color: string;
    relativeTo: 'max' | 'sum' | 'column_max';
  };
}

export interface RuleSet {
  name: string;
  description?: string;
  rules: VisualRule[];
}

export interface RuleResult {
  className?: string;
  style?: Record<string, string>;
  icon?: RuleIcon;
  cellBar?: {
    width: number;  // 0-100
    color: string;
  };
}

/**
 * Avalia se um valor atende a uma condição
 */
function evaluateCondition(
  value: unknown,
  condition: RuleCondition,
  allValues?: number[],
): boolean {
  if (value === null || value === undefined) {
    return condition.type === 'is_null';
  }

  const numValue = typeof value === 'number' ? value : Number(value);

  switch (condition.type) {
    case 'gt': return numValue > condition.value;
    case 'gte': return numValue >= condition.value;
    case 'lt': return numValue < condition.value;
    case 'lte': return numValue <= condition.value;
    case 'eq': return value === condition.value;
    case 'neq': return value !== condition.value;
    case 'between': return numValue >= condition.min && numValue <= condition.max;
    case 'is_zero': return numValue === 0;
    case 'is_true': return value === true || value === 1;
    case 'is_false': return value === false || value === 0;
    case 'is_null': return value === null || value === undefined;
    case 'top': {
      if (!allValues || allValues.length === 0) return false;
      const sorted = [...allValues].sort((a, b) => b - a);
      const topValues = sorted.slice(0, condition.value);
      return topValues.includes(numValue);
    }
    case 'bottom': {
      if (!allValues || allValues.length === 0) return false;
      const sorted = [...allValues].sort((a, b) => a - b);
      const bottomValues = sorted.slice(0, condition.value);
      return bottomValues.includes(numValue);
    }
    case 'pct_above': {
      if (!allValues || allValues.length === 0) return false;
      const avg = allValues.reduce((s, v) => s + v, 0) / allValues.length;
      return numValue > avg * (1 + condition.value / 100);
    }
    case 'pct_below': {
      if (!allValues || allValues.length === 0) return false;
      const avg = allValues.reduce((s, v) => s + v, 0) / allValues.length;
      return numValue < avg * (1 - condition.value / 100);
    }
    case 'threshold': {
      // Multi-level: ok > value, warn = value * 0.8, critical = abaixo
      return numValue <= condition.value;
    }
    default: return false;
  }
}

/**
 * Avalia uma célula contra todas as regras e retorna o resultado
 */
export function evaluateRules(
  value: unknown,
  fieldName: string,
  rules: VisualRule[],
  allColumnValues?: Record<string, number[]>,
): RuleResult | null {
  for (const rule of rules) {
    // Verifica se a regra se aplica a este campo
    if (rule.field !== '*' && rule.field !== fieldName) continue;

    const allValues = allColumnValues?.[fieldName];
    const matches = evaluateCondition(value, rule.condition, allValues);

    if (matches) {
      const result: RuleResult = {};

      if (rule.className) result.className = rule.className;
      if (rule.icon) result.icon = rule.icon;

      if (rule.style) {
        result.style = Object.fromEntries(
          Object.entries(rule.style).map(([k, v]) => [k, String(v)]),
        );
      }

      if (rule.cellBar && typeof value === 'number') {
        const colValues = allColumnValues?.[rule.field || fieldName] || [value];
        const maxVal = Math.max(...colValues, Math.abs(value));
        result.cellBar = {
          width: maxVal > 0 ? (Math.abs(value) / maxVal) * 100 : 0,
          color: rule.cellBar.color,
        };
      }

      // Retorna a PRIMEIRA regra que match (prioridade)
      return result;
    }
  }

  return null;
}

/**
 * Aplica regras a um dataset inteiro, retornando um mapa
 * de (rowKey_colKey) => RuleResult
 */
export function applyRulesToData(
  data: Record<string, any>[],
  metricNames: string[],
  rules: VisualRule[],
): Map<string, RuleResult> {
  const results = new Map<string, RuleResult>();

  // Pré-calcula valores por coluna para condições que precisam (top, bottom, pct)
  const allColumnValues: Record<string, number[]> = {};
  metricNames.forEach(metric => {
    allColumnValues[metric] = data
      .map(row => row[metric])
      .filter((v): v is number => typeof v === 'number' && !isNaN(v));
  });

  data.forEach((row, rowIdx) => {
    metricNames.forEach(metric => {
      const value = row[metric];
      const result = evaluateRules(value, metric, rules, allColumnValues);
      if (result) {
        results.set(`${rowIdx}_${metric}`, result);
      }
    });
  });

  return results;
}

/**
 * Regras pré-definidas para ativação rápida
 */
export const defaultRuleSets: Record<string, RuleSet> = {
  financial: {
    name: 'Financeiro',
    description: 'Regras para tabelas financeiras',
    rules: [
      {
        name: 'Negativo',
        field: '*',
        condition: { type: 'lt', value: 0 },
        style: { color: '#dc2626' },
        icon: 'trend-down',
      },
      {
        name: 'Positivo alto',
        field: '*',
        condition: { type: 'pct_above', value: 50 },
        style: { color: '#15803d' },
        icon: 'trend-up',
      },
      {
        name: 'Zero',
        field: '*',
        condition: { type: 'is_zero' },
        className: 'value-zero',
      },
    ],
  },
  ranking: {
    name: 'Ranking',
    description: 'Destaca top 3 valores',
    rules: [
      {
        name: 'Ouro',
        field: '*',
        condition: { type: 'top', value: 1 },
        icon: 'gold',
        className: 'rank-1',
      },
      {
        name: 'Prata',
        field: '*',
        condition: { type: 'bottom', value: 1 },
        icon: 'bronze',
      },
    ],
  },
  threshold: {
    name: 'Threshold',
    description: 'Indicadores de OK/WARN/CRITICAL',
    rules: [
      {
        name: 'Crítico',
        field: '*',
        condition: { type: 'threshold', value: 0 },
        className: 'threshold-critical',
        icon: 'alert',
      },
    ],
  },
};
