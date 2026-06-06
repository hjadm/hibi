/**
 * Módulos de Customização da Tabela Pivot
 * 
 * Cada módulo exporta uma função apply() que recebe o theme do Superset
 * e retorna um objeto CSS ou um callback de pós-renderização.
 * 
 * Uso: import { modules } from './modules';
 * modules.zebraStriping.apply(theme) => CSS string
 */

// Tipos compartilhados
export type ModuleCSS = (theme: Record<string, any>) => string;

export interface PivotModule {
  id: string;
  name: string;
  description: string;
  css: ModuleCSS;
}

import _zebraStriping from './01-zebra-striping';
import _totalsHighlight from './02-totals-highlight';
import _negativeRed from './03-negative-red';
import _cellBar from './04-cell-bar';
import _conditionalColor from './05-conditional-color';
import _tooltips from './06-tooltips';
import _sortVisual from './07-sort-visual';
import _headerTruncate from './08-header-truncate';
import _scrollbarPolish from './09-scrollbar-polish';
import _paddingSpacing from './10-padding-spacing';
import _enhancedFormatting from './11-enhanced-formatting';
import _valueIcons from './12-value-icons';

export const zebraStriping = _zebraStriping;
export const totalsHighlight = _totalsHighlight;
export const negativeRed = _negativeRed;
export const cellBar = _cellBar;
export const conditionalColor = _conditionalColor;
export const tooltips = _tooltips;
export const sortVisual = _sortVisual;
export const headerTruncate = _headerTruncate;
export const scrollbarPolish = _scrollbarPolish;
export const paddingSpacing = _paddingSpacing;
export const enhancedFormatting = _enhancedFormatting;
export const valueIcons = _valueIcons;

export const modules: Record<string, PivotModule> = {
  zebraStriping: _zebraStriping,
  totalsHighlight: _totalsHighlight,
  negativeRed: _negativeRed,
  cellBar: _cellBar,
  conditionalColor: _conditionalColor,
  tooltips: _tooltips,
  sortVisual: _sortVisual,
  headerTruncate: _headerTruncate,
  scrollbarPolish: _scrollbarPolish,
  paddingSpacing: _paddingSpacing,
  enhancedFormatting: _enhancedFormatting,
  valueIcons: _valueIcons,
};

/**
 * Aplica múltiplos módulos e retorna CSS concatenado
 */
export function applyModules(
  moduleIds: string[],
  theme: Record<string, any>,
): string {
  return moduleIds
    .filter(id => modules[id])
    .map(id => modules[id].css(theme))
    .join('\n');
}

/**
 * Retorna CSS de todos os módulos ativos
 */
export function allModulesCSS(theme: Record<string, any>): string {
  return Object.values(modules)
    .map(m => m.css(theme))
    .join('\n');
}

export * from './rule-engine';
