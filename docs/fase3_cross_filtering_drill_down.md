# Fase 3 — Cross-Filtering & Drill-Down

**Projeto:** hibi (fork Apache Superset)  
**Fase:** 3 de 3  
**Data de Elaboração:** 14/05/2026  
**Status:** Planejamento  

---

## 1. Visão Geral da Fase 3

### 1.1 Objetivos Principais

A Fase 3 representa a camada de **interatividade avançada** do Dataset Relationship Engine, permitindo que relacionamentos entre datasets configurados nas fases anteriores sejam utilizados de forma dinâmica e inteligente pelos usuários finais. Esta fase implementa:

1. **Cross-Filtering Automático**: Propagação inteligente de filtros entre charts de diferentes datasets relacionados dentro de um dashboard
2. **Filter Translation**: Engine que traduz valores filtrados de um dataset para colunas equivalentes em datasets relacionados, respeitando tipos de dados e cardinalidade
3. **Drill-Down Hierárquico**: Navegação drill-down entre níveis de granularidade através de datasets relacionados (ex: País → Estado → Cidade)
4. **Otimizações de Performance**: Cache de resultados e otimização de índices para garantir responsividade

### 1.2 Duração Estimada

| Métrica | Valor |
|---------|-------|
| **Duração Total** | 30–43 dias úteis |
| **Semanas** | 4–6 semanas |
| **Total de Tasks** | 10 tasks (P3.1 a P3.10) |
| **Nível de Risco Geral** | 🔴 **Alto** |

### 1.3 Funcionalidades a Serem Implementadas

#### Cross-Filtering Inteligente
- Extensão do escopo de cross-filter baseado em relacionamentos ativos no dashboard
- Propagação automática de filtros nativos através de relacionamentos configurados
- Engine de tradução de filtros que resolve incompatibilidades de tipo e cardinalidade
- Suporte a múltiplos níveis de propagação (filtro em A afeta B, que afeta C)

#### Drill-Down Hierárquico
- Interface de configuração de hierarquias de drill-down entre datasets
- Engine de navegação com aplicação automática de filtros
- Breadcrumb navigation para rastreamento do caminho de drill-down
- Suporte a hierarquias personalizadas por dashboard

#### Performance & Escalabilidade
- Cache inteligente de resultados de merge cross-DB
- Invalidação automática de cache por TTL e mudança de dados/relacionamentos
- Sugestão e criação automática de índices em colunas de JOIN
- Análise de plano de execução para otimização

#### Documentação & Qualidade
- Testes unitários e de integração abrangentes
- Documentação técnica de arquitetura e API
- Documentação de usuário (guias e tutoriais)
- Testes end-to-end do pipeline completo

---

## 2. Blocos de Implementação

### 2.1 Tabela Completa de Tasks

| ID | Nome da Task | Descrição Técnica | Duração (dias) | Prioridade | Dependências |
|----|-------------|-------------------|----------------|-----------|--------------|
| **P3.1** | Cross-Filter Scope Extension | Modificar `getCrossFiltersConfiguration()` para estender scope de cross-filter baseado em relacionamentos ativos no dashboard metadata | 3–5 | Alta | P2.9 |
| **P3.2** | Filter Translation Engine | Implementar engine que traduz valores filtrados de um dataset para colunas equivalentes em datasets relacionados, com validação de tipos e resolução de cardinalidade | 4–5 | Alta | P3.1 |
| **P3.3** | Native Filter Propagation | Modificar dataMask reducer para propagar filtros nativos automaticamente através de relacionamentos, com suporte a múltiplos níveis | 3–5 | Alta | P3.2 |
| **P3.4** | Drill-Down Hierarchy Config | Criar UI para configuração de hierarquias de drill-down entre datasets (ex: Country→State→City), com validação de hierarquia | 3–4 | Média | P2.9 |
| **P3.5** | Drill-Down Navigation Engine | Implementar engine de navegação drill-down com filtro aplicado automaticamente e suporte a breadcrumb para rastreamento do caminho | 4–5 | Média | P3.4, P3.2 |
| **P3.6** | Performance - Query Caching | Implementar cache de resultados de merge cross-DB com invalidação por TTL e por mudança de dados/relationships | 3–4 | Alta | P1.9 |
| **P3.7** | Performance - Index Optimization | Implementar sistema que sugere/cria índices automaticamente em colunas de join, com análise de plano de execução | 2–3 | Média | P1.8 |
| **P3.8** | Unit Tests - Cross-Filter & Drill-Down | Criar testes unitários para filter translation, cross-filter propagation, drill-down navigation e edge cases | 3–4 | Alta | P3.3, P3.5 |
| **P3.9** | Integration Tests - Full Pipeline | Criar testes end-to-end do pipeline completo: criar relationship → usar no explore → cross-filter → drill-down | 3–5 | Alta | P3.8 |
| **P3.10** | Documentação Completa | Elaborar documentação técnica (API, arquitetura) e de usuário (como criar relationships, usar cross-filter, drill-down) | 2–3 | Média | P3.9 |

### 2.2 Distribuição por Prioridade

| Prioridade | Tasks | Total de Dias (Min–Max) |
|-----------|-------|-------------------------|
| **Alta** | P3.1, P3.2, P3.3, P3.6, P3.8, P3.9 | 19–28 dias |
| **Média** | P3.4, P3.5, P3.7, P3.10 | 11–15 dias |

### 2.3 Distribuição por Categoria

| Categoria | Tasks | Descrição |
|-----------|-------|-----------|
| **Cross-Filtering** | P3.1, P3.2, P3.3 | Implementação do sistema de filtros cruzados |
| **Drill-Down** | P3.4, P3.5 | Implementação da navegação hierárquica |
| **Performance** | P3.6, P3.7 | Otimizações de cache e índices |
| **Qualidade** | P3.8, P3.9, P3.10 | Testes e documentação |

---

## 3. Arquitetura Técnica

### 3.1 Estrutura de Diretórios e Arquivos

```
hibi/
├── superset/
│   ├── models/
│   │   └── helpers.py                           # [MODIFICAR] Extensões em ExploreMixin
│   ├── utils/
│   │   └── cache.py                             # [MODIFICAR] Cache para merge cross-DB
│   └── db_engine_specs/
│       └── base.py                              # [MODIFICAR] Sugestões de índices
│
├── superset-frontend/
│   ├── src/
│   │   ├── dashboard/
│   │   │   ├── util/
│   │   │   │   └── crossFilters.ts             # [MODIFICAR] Extensão de scope
│   │   │   ├── components/
│   │   │   │   └── DrillDown/                  # [CRIAR] Componentes de drill-down
│   │   │   │       ├── DrillDownConfig.tsx     # Configuração de hierarquias
│   │   │   │       ├── DrillDownNavigation.tsx # Engine de navegação
│   │   │   │       ├── DrillDownBreadcrumb.tsx # Breadcrumb UI
│   │   │   │       └── index.ts                # Exports
│   │   │   └── types.ts                        # [MODIFICAR] Tipos de drill-down
│   │   ├── dataMask/
│   │   │   └── reducer.ts                      # [MODIFICAR] Propagação de filtros
│   │   ├── features/
│   │   │   └── datasets/
│   │   │       └── relationships/
│   │   │           ├── filterTranslation.ts    # [CRIAR] Engine de tradução
│   │   │           ├── filterPropagation.ts    # [CRIAR] Lógica de propagação
│   │   │           └── types.ts                # [MODIFICAR] Tipos de filtros
│   │   └── types/
│   │       └── Dashboard.ts                    # [MODIFICAR] Tipos de metadata
│
├── docs/
│   └── relationships/                           # [CRIAR] Documentação completa
│       ├── architecture.md                      # Arquitetura técnica
│       ├── api-reference.md                     # Referência da API
│       ├── user-guide-cross-filtering.md        # Guia de cross-filtering
│       ├── user-guide-drill-down.md             # Guia de drill-down
│       └── performance-optimization.md          # Otimizações
│
└── tests/
    ├── unit_tests/
    │   ├── cross_filter_tests/                  # [CRIAR] Testes de cross-filter
    │   │   ├── test_filter_translation.py
    │   │   └── test_filter_propagation.py
    │   └── drill_down_tests/                    # [CRIAR] Testes de drill-down
    │       ├── test_hierarchy_config.py
    │       └── test_navigation_engine.py
    └── integration_tests/
        └── relationship_pipeline_tests/         # [CRIAR] Testes end-to-end
            └── test_full_pipeline.py
```

### 3.2 Componentes Principais a Serem Criados

#### Frontend Components

| Componente | Arquivo | Responsabilidade |
|-----------|---------|------------------|
| **FilterTranslationEngine** | `filterTranslation.ts` | Traduzir valores de filtro entre datasets relacionados |
| **FilterPropagationEngine** | `filterPropagation.ts` | Orquestrar propagação de filtros através do grafo |
| **DrillDownConfig** | `DrillDownConfig.tsx` | UI para configurar hierarquias de drill-down |
| **DrillDownNavigation** | `DrillDownNavigation.tsx` | Engine de navegação entre níveis |
| **DrillDownBreadcrumb** | `DrillDownBreadcrumb.tsx` | Rastreamento visual do caminho |

#### Backend Components

| Componente | Arquivo | Responsabilidade |
|-----------|---------|------------------|
| **RelationshipCache** | `utils/cache.py` | Cache de resultados de merge cross-DB |
| **IndexOptimizer** | `db_engine_specs/base.py` | Análise e sugestão de índices |
| **QueryPlanAnalyzer** | `db_engine_specs/base.py` | Análise de planos de execução |

### 3.3 Modificações em Arquivos Existentes

#### Frontend

| Arquivo | Modificações |
|---------|-------------|
| `dashboard/util/crossFilters.ts` | • Adicionar `getExtendedCrossFilterScope()` que consulta relacionamentos ativos<br>• Modificar `getCrossFiltersConfiguration()` para incluir datasets relacionados<br>• Adicionar validação de relacionamentos bidirecionais |
| `dataMask/reducer.ts` | • Adicionar action `PROPAGATE_FILTER_THROUGH_RELATIONSHIPS`<br>• Implementar lógica de propagação multi-nível<br>• Adicionar cache de propagação para evitar loops infinitos |
| `dashboard/types.ts` | • Adicionar `DrillDownHierarchy` interface<br>• Estender `DashboardMetadata` com `drill_down_hierarchies`<br>• Adicionar tipos de navegação drill-down |
| `features/datasets/relationships/types.ts` | • Adicionar `FilterTranslationRule` interface<br>• Adicionar `FilterPropagationPath` type<br>• Definir tipos de validação de filtros |

#### Backend

| Arquivo | Modificações |
|---------|-------------|
| `models/helpers.py` | • Adicionar método `get_relationship_filter_paths()` em ExploreMixin<br>• Adicionar validação de hierarquias de drill-down |
| `utils/cache.py` | • Adicionar `RelationshipMergeCache` class<br>• Implementar invalidação por mudança de relationships<br>• Adicionar métricas de cache hit/miss |
| `db_engine_specs/base.py` | • Adicionar método `suggest_join_indexes()`<br>• Adicionar `analyze_query_plan()`<br>• Implementar engine-specific optimizations |

---

## 4. Fluxo de Dados

### 4.1 Fluxo de Cross-Filtering

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DASHBOARD VIEW                              │
│  ┌───────────────┐         ┌───────────────┐                       │
│  │  Chart A      │         │  Chart B      │                       │
│  │ Dataset: Sales│         │ Dataset: Prods│                       │
│  │               │         │               │                       │
│  │ [User clicks] │         │               │                       │
│  │  Region: BR   │         │               │                       │
│  └───────┬───────┘         └───────────────┘                       │
│          │                                                           │
└──────────┼───────────────────────────────────────────────────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ getCrossFilters      │
    │ Configuration()      │
    │                      │
    │ 1. Detecta filtro    │
    │    aplicado em       │
    │    Chart A           │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ getExtendedCross     │
    │ FilterScope()        │
    │                      │
    │ 2. Consulta          │
    │    active_           │
    │    relationships     │
    │    do dashboard      │
    │                      │
    │ 3. Identifica que    │
    │    Sales está        │
    │    relacionado com   │
    │    Products via      │
    │    product_id        │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ FilterTranslation    │
    │ Engine               │
    │                      │
    │ 4. Traduz filtro:    │
    │    Sales.region='BR' │
    │    ↓                 │
    │    Products.region   │
    │    ='BR'             │
    │                      │
    │ 5. Valida tipos      │
    │    compatíveis       │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ dataMask reducer     │
    │                      │
    │ 6. Dispatch action   │
    │    PROPAGATE_FILTER_ │
    │    THROUGH_          │
    │    RELATIONSHIPS     │
    │                      │
    │ 7. Atualiza dataMask │
    │    de Chart B        │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ Chart B Re-renders   │
    │                      │
    │ 8. Chart B re-executa│
    │    query com filtro  │
    │    propagado         │
    │                      │
    │ 9. Mostra apenas     │
    │    produtos da       │
    │    região BR         │
    └──────────────────────┘
```

#### 4.1.1 Pseudocódigo do Fluxo de Cross-Filter

```typescript
// Passo 1-2: Detectar e estender scope
function getExtendedCrossFilterScope(
  chartId: string,
  dashboardMetadata: DashboardMetadata
): Set<string> {
  const baseScope = getBaseCrossFilterScope(chartId);
  const activeRelationships = dashboardMetadata.active_relationships || [];
  
  const relatedDatasets = new Set<string>();
  
  // Buscar datasets diretamente relacionados
  for (const rel of activeRelationships) {
    if (rel.source_dataset_id === chartDatasetId) {
      relatedDatasets.add(rel.target_dataset_id);
    }
    if (rel.target_dataset_id === chartDatasetId) {
      relatedDatasets.add(rel.source_dataset_id);
    }
  }
  
  // Incluir charts que usam esses datasets
  const extendedScope = new Set(baseScope);
  for (const targetChartId of getAllChartsInDashboard()) {
    const targetDataset = getChartDataset(targetChartId);
    if (relatedDatasets.has(targetDataset)) {
      extendedScope.add(targetChartId);
    }
  }
  
  return extendedScope;
}

// Passo 3-5: Traduzir filtros
function translateFilter(
  filter: DataMaskStateWithId,
  sourceDataset: Dataset,
  targetDataset: Dataset,
  relationship: DatasetRelationship
): DataMaskStateWithId | null {
  // Validar tipos compatíveis
  const sourceColumn = findColumn(sourceDataset, filter.columnName);
  const targetColumn = findRelatedColumn(
    targetDataset,
    sourceColumn,
    relationship
  );
  
  if (!areTypesCompatible(sourceColumn.type, targetColumn.type)) {
    console.warn(`Type mismatch: ${sourceColumn.type} vs ${targetColumn.type}`);
    return null;
  }
  
  // Traduzir valores
  const translatedFilter = {
    ...filter,
    columnName: targetColumn.name,
    extraFormData: {
      ...filter.extraFormData,
      filters: translateFilterValues(
        filter.extraFormData.filters,
        relationship
      )
    }
  };
  
  return translatedFilter;
}

// Passo 6-7: Propagar filtros
function propagateFilterThroughRelationships(
  state: DataMaskState,
  action: PropagateFilterAction
): DataMaskState {
  const { sourceChartId, filter, relationships } = action.payload;
  
  const visited = new Set<string>([sourceChartId]);
  const queue: Array<{chartId: string, filter: DataMaskStateWithId}> = [
    { chartId: sourceChartId, filter }
  ];
  
  const newState = { ...state };
  
  while (queue.length > 0) {
    const { chartId, filter } = queue.shift()!;
    const sourceDataset = getChartDataset(chartId);
    
    // Encontrar relacionamentos aplicáveis
    for (const rel of relationships) {
      const targetDatasetId = getTargetDataset(rel, sourceDataset.id);
      if (!targetDatasetId) continue;
      
      const targetCharts = getChartsForDataset(targetDatasetId);
      
      for (const targetChartId of targetCharts) {
        if (visited.has(targetChartId)) continue;
        
        const translatedFilter = translateFilter(
          filter,
          sourceDataset,
          getDataset(targetDatasetId),
          rel
        );
        
        if (translatedFilter) {
          // Aplicar filtro traduzido
          newState[targetChartId] = {
            ...newState[targetChartId],
            ...translatedFilter
          };
          
          // Adicionar à fila para propagação multi-nível
          queue.push({
            chartId: targetChartId,
            filter: translatedFilter
          });
          visited.add(targetChartId);
        }
      }
    }
  }
  
  return newState;
}
```

### 4.2 Fluxo de Drill-Down

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DASHBOARD - HIERARCHY CONFIG                     │
│                                                                      │
│  Configuração de Hierarquia:                                        │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Level 1: Dataset "Geography" → Column "country"                │ │
│  │         ↓ relationship: geo_country_state                      │ │
│  │ Level 2: Dataset "Geography" → Column "state"                  │ │
│  │         ↓ relationship: geo_state_city                         │ │
│  │ Level 3: Dataset "Geography" → Column "city"                   │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
           │
           │ User clicks on "Brazil" in Country chart
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    DRILL-DOWN NAVIGATION ENGINE                      │
│                                                                      │
│  1. Detecta click em elemento de chart                              │
│  2. Verifica se existe hierarquia configurada                       │
│  3. Identifica nível atual (Level 1: Country)                       │
│  4. Identifica próximo nível (Level 2: State)                       │
└──────┬───────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    FILTER APPLICATION                                │
│                                                                      │
│  5. Cria filtro: country = "Brazil"                                 │
│  6. Usa FilterTranslationEngine para traduzir:                      │
│     • De: Geography.country = "Brazil"                              │
│     • Para: Geography.state (através de relationship)               │
│  7. Aplica filtro ao próximo nível                                  │
└──────┬───────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    CHART UPDATE & BREADCRUMB                         │
│                                                                      │
│  8. Atualiza chart para mostrar States do Brazil                    │
│  9. Atualiza breadcrumb:                                             │
│     ┌──────────────────────────────────────────────────────────────┐│
│     │ [All Countries] > [Brazil] > [States]                        ││
│     └──────────────────────────────────────────────────────────────┘│
│  10. Habilita navegação reversa (breadcrumb clickable)              │
└──────────────────────────────────────────────────────────────────────┘
           │
           │ User clicks on "São Paulo" in State chart
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    NEXT LEVEL DRILL-DOWN                             │
│                                                                      │
│  11. Acumula filtros:                                                │
│      • country = "Brazil" AND                                        │
│      • state = "São Paulo"                                           │
│  12. Navega para Level 3: City                                      │
│  13. Atualiza breadcrumb:                                            │
│      ┌─────────────────────────────────────────────────────────────┐│
│      │ [All Countries] > [Brazil] > [São Paulo] > [Cities]         ││
│      └─────────────────────────────────────────────────────────────┘│
│  14. Mostra cidades de São Paulo, Brazil                            │
└──────────────────────────────────────────────────────────────────────┘
```

#### 4.2.1 Estrutura de Dados de Hierarquia

```typescript
interface DrillDownHierarchy {
  id: string;
  name: string;
  levels: DrillDownLevel[];
}

interface DrillDownLevel {
  level_index: number;
  dataset_id: string;
  column_name: string;
  display_name?: string;
  relationship_to_next?: string; // ID do relationship para próximo nível
}

// Exemplo armazenado em dashboard.json_metadata
{
  "drill_down_hierarchies": [
    {
      "id": "geo_hierarchy",
      "name": "Geographic Hierarchy",
      "levels": [
        {
          "level_index": 0,
          "dataset_id": "dataset_geography_123",
          "column_name": "country",
          "display_name": "Country",
          "relationship_to_next": "rel_country_state_456"
        },
        {
          "level_index": 1,
          "dataset_id": "dataset_geography_123",
          "column_name": "state",
          "display_name": "State/Province",
          "relationship_to_next": "rel_state_city_789"
        },
        {
          "level_index": 2,
          "dataset_id": "dataset_geography_123",
          "column_name": "city",
          "display_name": "City"
        }
      ]
    }
  ]
}
```

#### 4.2.2 Pseudocódigo do Drill-Down Navigation

```typescript
interface DrillDownState {
  hierarchyId: string;
  currentLevel: number;
  appliedFilters: Array<{level: number, column: string, value: any}>;
  breadcrumb: BreadcrumbItem[];
}

function navigateDrillDown(
  currentState: DrillDownState,
  clickedValue: any,
  hierarchy: DrillDownHierarchy
): DrillDownState {
  const currentLevel = hierarchy.levels[currentState.currentLevel];
  const nextLevelIndex = currentState.currentLevel + 1;
  
  // Validar se existe próximo nível
  if (nextLevelIndex >= hierarchy.levels.length) {
    console.warn("Already at deepest level");
    return currentState;
  }
  
  // Criar novo filtro para o nível clicado
  const newFilter = {
    level: currentState.currentLevel,
    column: currentLevel.column_name,
    value: clickedValue
  };
  
  // Acumular filtros
  const updatedFilters = [...currentState.appliedFilters, newFilter];
  
  // Atualizar breadcrumb
  const updatedBreadcrumb = [
    ...currentState.breadcrumb,
    {
      level: currentState.currentLevel,
      label: clickedValue,
      filters: [...updatedFilters]
    }
  ];
  
  // Aplicar filtros ao próximo nível usando FilterTranslationEngine
  const nextLevel = hierarchy.levels[nextLevelIndex];
  const relationship = getRelationship(currentLevel.relationship_to_next);
  
  const translatedFilters = translateFiltersForDrillDown(
    updatedFilters,
    nextLevel,
    relationship
  );
  
  // Atualizar charts com novos filtros
  applyFiltersToCharts(nextLevel.dataset_id, translatedFilters);
  
  return {
    hierarchyId: currentState.hierarchyId,
    currentLevel: nextLevelIndex,
    appliedFilters: updatedFilters,
    breadcrumb: updatedBreadcrumb
  };
}

function navigateUpBreadcrumb(
  currentState: DrillDownState,
  targetLevel: number
): DrillDownState {
  // Remover filtros após o nível alvo
  const updatedFilters = currentState.appliedFilters.filter(
    f => f.level < targetLevel
  );
  
  // Atualizar breadcrumb
  const updatedBreadcrumb = currentState.breadcrumb.slice(0, targetLevel + 1);
  
  // Re-aplicar filtros
  const targetLevelData = hierarchy.levels[targetLevel];
  applyFiltersToCharts(targetLevelData.dataset_id, updatedFilters);
  
  return {
    ...currentState,
    currentLevel: targetLevel,
    appliedFilters: updatedFilters,
    breadcrumb: updatedBreadcrumb
  };
}
```

### 4.3 Fluxo de Cache de Merge Cross-DB

```
┌─────────────────────────────────────────────────────────────────────┐
│                    QUERY EXECUTION REQUEST                           │
│  Chart solicita dados de merge cross-DB:                            │
│  • Sales (Postgres) JOIN Products (MySQL) via product_id            │
└──────┬───────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    CACHE KEY GENERATION                              │
│  Gera cache key baseado em:                                          │
│  • IDs dos datasets: "sales_123_products_456"                        │
│  • Relationship ID: "rel_789"                                        │
│  • Query hash: hash(SQL queries + filters + columns)                 │
│  • User permissions: user_id (para row-level security)              │
│                                                                      │
│  Final key: "merge:sales_123_products_456:rel_789:a3f5b9:user_42"   │
└──────┬───────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    CACHE LOOKUP                                      │
│  Busca em Redis/cache backend                                        │
└──────┬──────────────────────────────────────────────┬────────────────┘
       │ MISS                                          │ HIT
       ▼                                               ▼
┌──────────────────────────────┐    ┌─────────────────────────────────┐
│  EXECUTE MERGE QUERY         │    │  RETURN CACHED RESULT           │
│                              │    │                                 │
│  1. Execute query em Sales   │    │  1. Deserialize DataFrame       │
│  2. Execute query em Products│    │  2. Log cache hit               │
│  3. Merge via Pandas         │    │  3. Return to chart             │
│  4. Apply limits & timeout   │    └─────────────────────────────────┘
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    STORE IN CACHE                                    │
│  1. Serialize DataFrame (Parquet ou Pickle)                          │
│  2. Set TTL: 1 hora (configurable)                                   │
│  3. Store metadata: timestamp, row count, size                       │
│  4. Log cache miss                                                   │
└──────┬───────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    RETURN RESULT                                     │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    CACHE INVALIDATION TRIGGERS                       │
│                                                                      │
│  1. TTL Expiration: Após 1 hora (default)                           │
│  2. Dataset Update: Quando Sales ou Products são modificados        │
│  3. Relationship Change: Quando rel_789 é editado/deletado          │
│  4. Manual Invalidation: Via API ou admin UI                        │
│                                                                      │
│  Implementação:                                                      │
│  • Hook em DatasetDAO.update() → invalidate_merge_cache()           │
│  • Hook em DatasetRelationshipDAO.update/delete()                   │
│  • Pattern matching: "merge:*sales_123*" ou "merge:*products_456*"  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 5. Riscos e Mitigações

### 5.1 Riscos Altos (🔴)

| # | Risco | Tasks Afetadas | Impacto | Probabilidade | Mitigação |
|---|-------|----------------|---------|---------------|-----------|
| **R1** | **Filter translation incorreta causa dados errados** | P3.2, P3.3 | 🔴 Crítico | 🟡 Média | • Validação rigorosa de tipos de coluna antes de tradução<br>• Whitelist de conversões permitidas (ex: INT→STRING ok, DATE→INT não)<br>• Alertas visuais no UI quando filtro é traduzido ("Filtro propagado de Dataset A")<br>• Testes exaustivos com matriz de tipos (P3.8)<br>• Modo "dry-run" que mostra tradução sem aplicar |
| **R2** | **Cross-filter propagation entra em loop infinito** | P3.1, P3.3 | 🔴 Crítico | 🟡 Média | • Implementar visited set no algoritmo de propagação<br>• Limite máximo de profundidade (ex: 5 níveis)<br>• Timeout de propagação (500ms)<br>• Validação de grafo acíclico nos relacionamentos (já feito em P1.3)<br>• Circuit breaker que desabilita propagação se loop detectado |
| **R3** | **Drill-down com muitos níveis degrada UX** | P3.5 | 🟡 Moderado | 🟡 Média | • Limite `MAX_DRILL_DEPTH = 5` configurável<br>• Lazy loading de níveis profundos<br>• Breadcrumb colapsável em hierarquias muito longas<br>• Indicador de performance no UI ("Este drill-down pode ser lento")<br>• Cache agressivo de níveis intermediários (P3.6) |
| **R4** | **Performance degradada em dashboards com muitos relacionamentos** | P3.1, P3.2, P3.3 | 🟡 Moderado | 🔴 Alta | • Limitar número de relacionamentos ativos por dashboard (ex: 10)<br>• Implementar lazy evaluation de cross-filters (só calcular quando chart visível)<br>• Debounce de propagação (aguardar 300ms após último filtro)<br>• Métricas de performance no backend (`FILTER_PROPAGATION_TIME`)<br>• Feature flag para desabilitar propagação automática |

### 5.2 Riscos Médios (🟡)

| # | Risco | Tasks Afetadas | Impacto | Probabilidade | Mitigação |
|---|-------|----------------|---------|---------------|-----------|
| **R5** | **Cache de merge ocupa muita memória** | P3.6 | 🟡 Moderado | 🟡 Média | • Limite de tamanho de cache (ex: 1GB total)<br>• LRU eviction policy<br>• Compressão de DataFrames antes de cachear (Parquet)<br>• TTL curto para queries grandes (15min vs 1h)<br>• Monitoramento de uso de memória com alertas |
| **R6** | **Índices criados automaticamente causam locks em produção** | P3.7 | 🟡 Moderado | 🟢 Baixa | • Criar índices apenas em modo `CONCURRENTLY` (Postgres)<br>• Executar criação de índices em horários de baixo uso<br>• Modo "suggest only" (default): apenas sugere, não cria<br>• Require admin approval para criação automática<br>• Timeout de criação de índice (5min) |
| **R7** | **Documentação incompleta dificulta adoção** | P3.10 | 🟢 Baixo | 🟡 Média | • Checklist de documentação obrigatória antes de merge<br>• Vídeos tutoriais gravados<br>• Exemplos práticos em cada guia<br>• Documentação inline (tooltips no UI)<br>• FAQ com casos de uso comuns |
| **R8** | **Testes não cobrem edge cases cross-DB** | P3.8, P3.9 | 🟡 Moderado | 🟡 Média | • Matriz de testes com múltiplos dialetos SQL (Postgres, MySQL, BigQuery, Snowflake)<br>• Testes com datasets vazios, null values, duplicatas<br>• Testes de cardinalidade (1:N, N:M)<br>• Testes de timezone e encoding differences<br>• Code coverage mínimo de 85% |

### 5.3 Riscos Baixos (🟢)

| # | Risco | Tasks Afetadas | Impacto | Probabilidade | Mitigação |
|---|-------|----------------|---------|---------------|-----------|
| **R9** | **UI de configuração de hierarquia é confusa** | P3.4 | 🟢 Baixo | 🟡 Média | • User testing com 3-5 usuários antes de release<br>• Wizard step-by-step para primeira configuração<br>• Templates pré-configurados (ex: "Geographic Hierarchy")<br>• Preview em tempo real da hierarquia |
| **R10** | **Breadcrumb navigation em mobile é limitado** | P3.5 | 🟢 Baixo | 🟡 Média | • UI responsivo com breadcrumb colapsável<br>• Dropdown menu em telas pequenas<br>• Gesture support (swipe para voltar nível) |

### 5.4 Matriz de Risco (Impacto × Probabilidade)

```
Probabilidade
     ▲
Alta │         R4
     │
Média│   R1, R2, R3    R5, R7, R8, R9, R10
     │
Baixa│                 R6
     │
     └─────────────────────────────────────►
       Baixo    Moderado    Crítico    Impacto
```

### 5.5 Plano de Contingência

#### Se R1 ou R2 ocorrerem (filter translation/propagation críticos)
1. **Imediato**: Desabilitar feature via `ENABLE_CROSS_FILTER_PROPAGATION = False`
2. **Curto prazo**: Implementar modo "manual approval" onde usuário confirma cada propagação
3. **Médio prazo**: Refatorar engine com algoritmo mais robusto + peer review

#### Se R4 ocorrer (performance degradada)
1. **Imediato**: Aumentar debounce para 500ms, reduzir limite de relacionamentos para 5
2. **Curto prazo**: Implementar feature flag granular por dashboard
3. **Médio prazo**: Otimizar algoritmo de propagação (usar Web Workers no frontend)

#### Se R6 ocorrer (locks de índices)
1. **Imediato**: Cancelar criações de índice em andamento
2. **Curto prazo**: Desabilitar criação automática, manter apenas sugestões
3. **Médio prazo**: Implementar queue system para criação de índices off-hours

---

## 6. Caminho Crítico

### 6.1 Diagrama de Dependências

```
P2.9 (Dashboard Metadata - Fase 2)
  │
  ├──────────────────┐
  │                  │
  ▼                  ▼
P3.1                P3.4
Cross-Filter        Drill-Down
Scope Extension     Hierarchy Config
  │                  │
  │ (3-5 dias)       │ (3-4 dias)
  │                  │
  ▼                  │
P3.2                │
Filter              │
Translation         │
Engine              │
  │                  │
  │ (4-5 dias)       │
  │                  │
  ├──────────────────┤
  │                  │
  ▼                  ▼
P3.3                P3.5
Native Filter       Drill-Down
Propagation         Navigation
  │                  │
  │ (3-5 dias)       │ (4-5 dias)
  │                  │
  └─────────┬────────┘
            │
            ▼
          P3.8
       Unit Tests
    Cross-Filter &
      Drill-Down
            │
            │ (3-4 dias)
            │
            ▼
          P3.9
      Integration
         Tests
     Full Pipeline
            │
            │ (3-5 dias)
            │
            ▼
         P3.10
     Documentação
       Completa
            │
            │ (2-3 dias)
            │
            ▼
         [FIM]

=== PARALLEL TRACKS ===

P1.9 (Cross-DB Merge - Fase 1)
  │
  │
  ▼
P3.6
Performance
Query Caching
  │
  │ (3-4 dias)
  │
  └───────────────► [Merge em P3.9]


P1.8 (Same-DB JOIN - Fase 1)
  │
  │
  ▼
P3.7
Performance
Index Optimization
  │
  │ (2-3 dias)
  │
  └───────────────► [Merge em P3.9]
```

### 6.2 Sequência de Implementação Recomendada

#### Sprint 1 (Semana 1): Foundation
| Dias | Tasks | Objetivo |
|------|-------|----------|
| 1-3 | **P3.1** Cross-Filter Scope Extension | Preparar infraestrutura de cross-filter |
| 1-2 | **P3.7** Index Optimization (parallel) | Preparar otimizações de performance |

#### Sprint 2 (Semana 2): Core Engines
| Dias | Tasks | Objetivo |
|------|-------|----------|
| 4-8 | **P3.2** Filter Translation Engine | Implementar motor de tradução |
| 4-6 | **P3.4** Drill-Down Hierarchy Config (parallel) | Preparar UI de configuração |
| 4-7 | **P3.6** Query Caching (parallel) | Implementar cache |

#### Sprint 3 (Semana 3-4): Integration
| Dias | Tasks | Objetivo |
|------|-------|----------|
| 9-13 | **P3.3** Native Filter Propagation | Integrar propagação de filtros |
| 9-13 | **P3.5** Drill-Down Navigation (parallel) | Implementar navegação drill-down |

#### Sprint 4 (Semana 5): Quality & Documentation
| Dias | Tasks | Objetivo |
|------|-------|----------|
| 14-17 | **P3.8** Unit Tests | Garantir cobertura de testes |
| 18-22 | **P3.9** Integration Tests | Testes end-to-end |

#### Sprint 5 (Semana 6): Finalization
| Dias | Tasks | Objetivo |
|------|-------|----------|
| 23-25 | **P3.10** Documentação | Finalizar documentação |
| 26-30 | **Buffer** | Ajustes finais e polish |

### 6.3 Tarefas Não-Críticas (Podem ser paralelizadas)

As seguintes tasks **não** estão no caminho crítico e podem ser executadas em paralelo:
- **P3.6** (Query Caching): Depende apenas de P1.9 (Fase 1), pode iniciar imediatamente
- **P3.7** (Index Optimization): Depende apenas de P1.8 (Fase 1), pode iniciar imediatamente
- **P3.4** (Drill-Down Config): Pode iniciar em paralelo com P3.1-P3.3

### 6.4 Marcos (Milestones)

| Milestone | Data Estimada | Tasks Completas | Entregável |
|-----------|---------------|-----------------|-----------|
| **M1: Cross-Filter Foundation** | Fim da Semana 2 | P3.1, P3.2 | Cross-filter básico funcional (sem propagação) |
| **M2: Drill-Down Foundation** | Fim da Semana 3 | P3.4, P3.5 | Drill-down básico funcional |
| **M3: Full Integration** | Fim da Semana 4 | P3.3, P3.6, P3.7 | Cross-filter + drill-down + performance |
| **M4: Production Ready** | Fim da Semana 6 | P3.8, P3.9, P3.10 | Testes completos + documentação |

---

## 7. Detalhes de Implementação por Bloco

### 7.1 P3.1 — Cross-Filter Scope Extension

#### Objetivo
Modificar a função `getCrossFiltersConfiguration()` para estender o escopo de cross-filter além dos charts diretos, incluindo charts de datasets relacionados.

#### Arquivos a Serem Criados
Nenhum arquivo novo. Apenas modificações.

#### Modificações Necessárias

**Arquivo**: `superset-frontend/src/dashboard/util/crossFilters.ts`

```typescript
// ANTES (comportamento atual)
export function getCrossFiltersConfiguration(
  chartConfiguration: ChartConfiguration,
  dashboardLayout: DashboardLayout
): CrossFilterConfiguration {
  // Apenas charts diretamente compatíveis
  const eligibleCharts = getDirectlyCompatibleCharts(chartConfiguration);
  return { scope: eligibleCharts };
}

// DEPOIS (novo comportamento)
export function getCrossFiltersConfiguration(
  chartConfiguration: ChartConfiguration,
  dashboardLayout: DashboardLayout,
  dashboardMetadata?: DashboardMetadata // NOVO parâmetro
): CrossFilterConfiguration {
  // Base scope (comportamento existente)
  const baseScope = getDirectlyCompatibleCharts(chartConfiguration);
  
  // Estender com datasets relacionados
  const extendedScope = getExtendedCrossFilterScope(
    chartConfiguration.id,
    chartConfiguration.datasetId,
    dashboardMetadata?.active_relationships || [],
    dashboardLayout
  );
  
  return {
    scope: [...new Set([...baseScope, ...extendedScope])],
    propagationPaths: buildPropagationPaths(
      chartConfiguration.datasetId,
      dashboardMetadata?.active_relationships || []
    )
  };
}

// NOVA função auxiliar
export function getExtendedCrossFilterScope(
  sourceChartId: string,
  sourceDatasetId: string,
  activeRelationships: DatasetRelationship[],
  dashboardLayout: DashboardLayout
): string[] {
  const relatedDatasetIds = new Set<string>();
  
  // BFS para encontrar datasets relacionados (multi-hop)
  const visited = new Set<string>([sourceDatasetId]);
  const queue = [sourceDatasetId];
  const maxDepth = 2; // Limitar propagação a 2 níveis
  let currentDepth = 0;
  
  while (queue.length > 0 && currentDepth < maxDepth) {
    const levelSize = queue.length;
    
    for (let i = 0; i < levelSize; i++) {
      const currentDatasetId = queue.shift()!;
      
      // Encontrar relacionamentos deste dataset
      for (const rel of activeRelationships) {
        let targetDatasetId: string | null = null;
        
        if (rel.source_dataset_id === currentDatasetId) {
          targetDatasetId = rel.target_dataset_id;
        } else if (rel.target_dataset_id === currentDatasetId) {
          targetDatasetId = rel.source_dataset_id;
        }
        
        if (targetDatasetId && !visited.has(targetDatasetId)) {
          relatedDatasetIds.add(targetDatasetId);
          visited.add(targetDatasetId);
          queue.push(targetDatasetId);
        }
      }
    }
    
    currentDepth++;
  }
  
  // Mapear datasets para charts
  const relatedChartIds: string[] = [];
  const allCharts = getAllChartsFromLayout(dashboardLayout);
  
  for (const chartId of allCharts) {
    const chartDatasetId = getChartDatasetId(chartId, dashboardLayout);
    if (relatedDatasetIds.has(chartDatasetId) && chartId !== sourceChartId) {
      relatedChartIds.push(chartId);
    }
  }
  
  return relatedChartIds;
}

// NOVA função para construir caminhos de propagação
export function buildPropagationPaths(
  sourceDatasetId: string,
  activeRelationships: DatasetRelationship[]
): PropagationPath[] {
  const paths: PropagationPath[] = [];
  const visited = new Set<string>();
  
  function dfs(
    currentDatasetId: string,
    path: DatasetRelationship[],
    depth: number
  ) {
    if (depth > 2 || visited.has(currentDatasetId)) return;
    
    visited.add(currentDatasetId);
    
    for (const rel of activeRelationships) {
      let nextDatasetId: string | null = null;
      
      if (rel.source_dataset_id === currentDatasetId) {
        nextDatasetId = rel.target_dataset_id;
      } else if (rel.target_dataset_id === currentDatasetId) {
        nextDatasetId = rel.source_dataset_id;
      }
      
      if (nextDatasetId) {
        const newPath = [...path, rel];
        paths.push({
          from: sourceDatasetId,
          to: nextDatasetId,
          relationships: newPath
        });
        
        dfs(nextDatasetId, newPath, depth + 1);
      }
    }
    
    visited.delete(currentDatasetId);
  }
  
  dfs(sourceDatasetId, [], 0);
  return paths;
}
```

#### Lógica Técnica

1. **Detecção de Relacionamentos Ativos**: Lê `active_relationships` do `dashboard.json_metadata`
2. **Grafo de Relacionamentos**: Constrói grafo direcionado de datasets relacionados
3. **BFS Multi-Hop**: Usa BFS para encontrar datasets relacionados até profundidade 2
4. **Mapeamento Charts**: Identifica todos os charts que usam esses datasets
5. **Escopo Estendido**: Retorna lista de chart IDs elegíveis para cross-filter

#### Integrações

- **Input**: `DashboardMetadata.active_relationships` (configurado em P2.9)
- **Output**: Array de chart IDs elegíveis para cross-filter
- **Usado por**: P3.2 (Filter Translation Engine)

#### Testes Necessários

- ✓ Relacionamento direto (A→B)
- ✓ Relacionamento multi-hop (A→B→C)
- ✓ Limite de profundidade (não explodir com muitos relacionamentos)
- ✓ Relacionamentos bidirecionais
- ✓ Charts sem relacionamentos (fallback para comportamento atual)

---

### 7.2 P3.2 — Filter Translation Engine

#### Objetivo
Criar engine que traduz valores filtrados de um dataset para colunas equivalentes em datasets relacionados, validando tipos e resolvendo diferenças de cardinalidade.

#### Arquivos a Serem Criados

**Arquivo**: `superset-frontend/src/features/datasets/relationships/filterTranslation.ts`

```typescript
import { DatasetRelationship, DatasetRelationshipColumn } from '../types';
import { DataMaskStateWithId } from '@superset-ui/core';

export interface FilterTranslationContext {
  sourceDatasetId: string;
  targetDatasetId: string;
  relationship: DatasetRelationship;
  sourceFilter: DataMaskStateWithId;
}

export interface TranslatedFilter {
  filter: DataMaskStateWithId;
  confidence: 'high' | 'medium' | 'low';
  warnings: string[];
}

export class FilterTranslationEngine {
  /**
   * Traduz um filtro de um dataset para outro usando relacionamento
   */
  public translateFilter(
    context: FilterTranslationContext
  ): TranslatedFilter | null {
    const { sourceDatasetId, targetDatasetId, relationship, sourceFilter } = context;
    
    // Validar direção do relacionamento
    const direction = this.getRelationshipDirection(
      relationship,
      sourceDatasetId,
      targetDatasetId
    );
    
    if (!direction) {
      console.warn('Datasets are not related:', sourceDatasetId, targetDatasetId);
      return null;
    }
    
    // Encontrar colunas correspondentes
    const columnMapping = this.findColumnMapping(
      relationship,
      sourceFilter.filterState.columnName,
      direction
    );
    
    if (!columnMapping) {
      return null;
    }
    
    // Validar compatibilidade de tipos
    const typeValidation = this.validateTypeCompatibility(
      columnMapping.sourceColumn,
      columnMapping.targetColumn
    );
    
    if (!typeValidation.compatible) {
      console.warn('Incompatible column types:', typeValidation.reason);
      return null;
    }
    
    // Traduzir valores
    const translatedValues = this.translateFilterValues(
      sourceFilter.filterState.value,
      columnMapping,
      relationship
    );
    
    // Construir filtro traduzido
    const translatedFilter: DataMaskStateWithId = {
      ...sourceFilter,
      filterId: `${sourceFilter.filterId}_translated`,
      filterState: {
        ...sourceFilter.filterState,
        columnName: columnMapping.targetColumn.column_name,
        value: translatedValues.values
      },
      ownState: {
        ...sourceFilter.ownState,
        propagated: true,
        sourceDataset: sourceDatasetId,
        relationshipId: relationship.id
      }
    };
    
    return {
      filter: translatedFilter,
      confidence: translatedValues.confidence,
      warnings: [
        ...typeValidation.warnings,
        ...translatedValues.warnings
      ]
    };
  }
  
  /**
   * Determina direção do relacionamento (source→target ou target→source)
   */
  private getRelationshipDirection(
    relationship: DatasetRelationship,
    fromDatasetId: string,
    toDatasetId: string
  ): 'forward' | 'reverse' | null {
    if (
      relationship.source_dataset_id === fromDatasetId &&
      relationship.target_dataset_id === toDatasetId
    ) {
      return 'forward';
    }
    
    if (
      relationship.target_dataset_id === fromDatasetId &&
      relationship.source_dataset_id === toDatasetId
    ) {
      return 'reverse';
    }
    
    return null;
  }
  
  /**
   * Encontra mapeamento de colunas no relacionamento
   */
  private findColumnMapping(
    relationship: DatasetRelationship,
    sourceColumnName: string,
    direction: 'forward' | 'reverse'
  ): ColumnMapping | null {
    for (const relColumn of relationship.columns) {
      const sourceCol = direction === 'forward'
        ? relColumn.source_column_name
        : relColumn.target_column_name;
      
      const targetCol = direction === 'forward'
        ? relColumn.target_column_name
        : relColumn.source_column_name;
      
      if (sourceCol === sourceColumnName) {
        return {
          sourceColumn: {
            column_name: sourceCol,
            type: relColumn.source_column_type
          },
          targetColumn: {
            column_name: targetCol,
            type: relColumn.target_column_type
          }
        };
      }
    }
    
    return null;
  }
  
  /**
   * Valida se tipos de colunas são compatíveis
   */
  private validateTypeCompatibility(
    sourceColumn: ColumnInfo,
    targetColumn: ColumnInfo
  ): TypeValidation {
    const compatibilityMatrix = this.getTypeCompatibilityMatrix();
    const sourceType = this.normalizeColumnType(sourceColumn.type);
    const targetType = this.normalizeColumnType(targetColumn.type);
    
    const compatibility = compatibilityMatrix[sourceType]?.[targetType];
    
    if (!compatibility) {
      return {
        compatible: false,
        reason: `No compatibility rule for ${sourceType} → ${targetType}`,
        warnings: []
      };
    }
    
    return compatibility;
  }
  
  /**
   * Matriz de compatibilidade de tipos
   */
  private getTypeCompatibilityMatrix(): TypeCompatibilityMatrix {
    return {
      'INTEGER': {
        'INTEGER': { compatible: true, warnings: [] },
        'BIGINT': { compatible: true, warnings: [] },
        'STRING': { compatible: true, warnings: ['Type coercion INT→STRING'] },
        'FLOAT': { compatible: true, warnings: ['Precision may be lost'] }
      },
      'STRING': {
        'STRING': { compatible: true, warnings: [] },
        'INTEGER': { compatible: false, reason: 'Cannot convert STRING→INT safely' },
        'DATE': { compatible: true, warnings: ['Requires date parsing'] }
      },
      'DATE': {
        'DATE': { compatible: true, warnings: [] },
        'TIMESTAMP': { compatible: true, warnings: [] },
        'STRING': { compatible: true, warnings: ['Date formatting may differ'] }
      },
      'BOOLEAN': {
        'BOOLEAN': { compatible: true, warnings: [] },
        'INTEGER': { compatible: true, warnings: ['0/1 conversion'] }
      }
      // ... adicionar mais tipos conforme necessário
    };
  }
  
  /**
   * Traduz valores do filtro
   */
  private translateFilterValues(
    sourceValues: any,
    columnMapping: ColumnMapping,
    relationship: DatasetRelationship
  ): TranslatedValues {
    const warnings: string[] = [];
    let confidence: 'high' | 'medium' | 'low' = 'high';
    
    // Para relacionamentos cross-DB, valores são mantidos "as-is"
    // assumindo que colunas relacionadas têm valores equivalentes
    let translatedValues = sourceValues;
    
    // Se houver transformação necessária (ex: timezone, encoding)
    if (relationship.is_cross_database) {
      warnings.push('Cross-database filter: verify value compatibility');
      confidence = 'medium';
    }
    
    // Validar cardinalidade
    if (relationship.relationship_type === 'many_to_one' &&
        Array.isArray(sourceValues) && sourceValues.length > 1) {
      warnings.push('Many-to-one relationship: filter may return unexpected results');
      confidence = 'low';
    }
    
    return {
      values: translatedValues,
      confidence,
      warnings
    };
  }
  
  /**
   * Normaliza tipos de colunas para categorias comuns
   */
  private normalizeColumnType(type: string): string {
    const typeUpper = type.toUpperCase();
    
    if (typeUpper.includes('INT')) return 'INTEGER';
    if (typeUpper.includes('VARCHAR') || typeUpper.includes('TEXT')) return 'STRING';
    if (typeUpper.includes('DATE')) return 'DATE';
    if (typeUpper.includes('TIMESTAMP')) return 'TIMESTAMP';
    if (typeUpper.includes('BOOL')) return 'BOOLEAN';
    if (typeUpper.includes('FLOAT') || typeUpper.includes('DECIMAL')) return 'FLOAT';
    
    return typeUpper;
  }
}

// Types
interface ColumnMapping {
  sourceColumn: ColumnInfo;
  targetColumn: ColumnInfo;
}

interface ColumnInfo {
  column_name: string;
  type: string;
}

interface TypeValidation {
  compatible: boolean;
  reason?: string;
  warnings: string[];
}

interface TranslatedValues {
  values: any;
  confidence: 'high' | 'medium' | 'low';
  warnings: string[];
}

type TypeCompatibilityMatrix = Record<string, Record<string, TypeValidation>>;

// Singleton export
export const filterTranslationEngine = new FilterTranslationEngine();
```

#### Lógica Técnica

1. **Mapeamento de Colunas**: Identifica par de colunas (source, target) no relacionamento
2. **Validação de Tipos**: Verifica compatibilidade usando matriz de tipos
3. **Tradução de Valores**: Mantém valores "as-is" para mesmos tipos, aplica conversões quando necessário
4. **Confidence Scoring**: Atribui confiança (high/medium/low) baseado em compatibilidade e cardinalidade
5. **Warnings**: Gera avisos para o usuário sobre possíveis problemas

#### Integrações

- **Input**: `DataMaskStateWithId` (filtro aplicado), `DatasetRelationship`
- **Output**: `TranslatedFilter` ou `null` (se incompatível)
- **Usado por**: P3.3 (Native Filter Propagation)

#### Testes Necessários

- ✓ Tradução de tipos compatíveis (INT→INT, STRING→STRING)
- ✓ Tradução com conversão (INT→STRING)
- ✓ Rejeição de tipos incompatíveis (STRING→INT)
- ✓ Relacionamento forward vs reverse
- ✓ Relacionamento cross-DB (warnings apropriados)
- ✓ Cardinalidade many-to-one (confidence baixo)
- ✓ Valores null/undefined

---

### 7.3 P3.3 — Native Filter Propagation

#### Objetivo
Modificar o reducer de dataMask para propagar filtros nativos automaticamente através de relacionamentos configurados.

#### Arquivos a Serem Modificados

**Arquivo**: `superset-frontend/src/dataMask/reducer.ts`

```typescript
import { FilterTranslationEngine } from '../features/datasets/relationships/filterTranslation';
import { getActiveRelationships } from '../dashboard/util/dashboardMetadata';

// NOVA action type
export const PROPAGATE_FILTER_THROUGH_RELATIONSHIPS = 'PROPAGATE_FILTER_THROUGH_RELATIONSHIPS';

// MODIFICAR reducer principal
export default function dataMaskReducer(
  state: DataMaskState = {},
  action: AnyDataMaskAction
): DataMaskState {
  // ... casos existentes ...
  
  case SET_DATA_MASK_FOR_FILTER_CONFIG_COMPLETE:
    const newState = {
      ...state,
      [action.filterId]: action.dataMask
    };
    
    // NOVO: Propagar filtro automaticamente se feature habilitada
    if (getFeatureFlag('ENABLE_CROSS_FILTER_PROPAGATION')) {
      return propagateFilterThroughRelationships(
        newState,
        action.filterId,
        action.dataMask
      );
    }
    
    return newState;
  
  // NOVO caso
  case PROPAGATE_FILTER_THROUGH_RELATIONSHIPS:
    return propagateFilterThroughRelationships(
      state,
      action.payload.filterId,
      action.payload.dataMask
    );
  
  // ... outros casos ...
}

/**
 * Propaga filtro através de relacionamentos
 */
function propagateFilterThroughRelationships(
  state: DataMaskState,
  sourceFilterId: string,
  sourceDataMask: DataMask
): DataMaskState {
  const dashboardMetadata = getDashboardMetadata(); // hook para obter metadata
  const activeRelationships = dashboardMetadata?.active_relationships || [];
  
  if (activeRelationships.length === 0) {
    return state; // Sem relacionamentos, nada a fazer
  }
  
  // Obter dataset do filtro source
  const sourceDatasetId = getFilterDatasetId(sourceFilterId);
  if (!sourceDatasetId) {
    return state;
  }
  
  const filterTranslationEngine = new FilterTranslationEngine();
  
  // BFS para propagação multi-nível
  const visited = new Set<string>([sourceFilterId]);
  const queue: Array<{
    filterId: string,
    datasetId: string,
    dataMask: DataMask,
    depth: number
  }> = [{
    filterId: sourceFilterId,
    datasetId: sourceDatasetId,
    dataMask: sourceDataMask,
    depth: 0
  }];
  
  const maxDepth = 2; // Limite de propagação
  const propagationTimeout = 500; // 500ms timeout
  const startTime = Date.now();
  
  let newState = { ...state };
  
  while (queue.length > 0) {
    // Timeout protection
    if (Date.now() - startTime > propagationTimeout) {
      console.warn('Filter propagation timeout exceeded');
      break;
    }
    
    const { filterId, datasetId, dataMask, depth } = queue.shift()!;
    
    if (depth >= maxDepth) {
      continue;
    }
    
    // Encontrar relacionamentos aplicáveis
    const applicableRelationships = activeRelationships.filter(
      rel => rel.source_dataset_id === datasetId || rel.target_dataset_id === datasetId
    );
    
    for (const relationship of applicableRelationships) {
      const targetDatasetId = relationship.source_dataset_id === datasetId
        ? relationship.target_dataset_id
        : relationship.source_dataset_id;
      
      // Encontrar filtros do dataset alvo
      const targetFilterIds = getFilterIdsForDataset(targetDatasetId);
      
      for (const targetFilterId of targetFilterIds) {
        if (visited.has(targetFilterId)) {
          continue; // Evitar loops
        }
        
        // Traduzir filtro
        const translatedFilter = filterTranslationEngine.translateFilter({
          sourceDatasetId: datasetId,
          targetDatasetId,
          relationship,
          sourceFilter: {
            filterId,
            filterState: dataMask.filterState,
            ownState: dataMask.ownState
          }
        });
        
        if (translatedFilter) {
          // Aplicar filtro traduzido
          newState[targetFilterId] = {
            ...newState[targetFilterId],
            ...translatedFilter.filter,
            ownState: {
              ...translatedFilter.filter.ownState,
              propagatedFrom: sourceFilterId,
              propagationDepth: depth + 1,
              propagationWarnings: translatedFilter.warnings
            }
          };
          
          // Adicionar à fila para propagação multi-nível
          queue.push({
            filterId: targetFilterId,
            datasetId: targetDatasetId,
            dataMask: newState[targetFilterId],
            depth: depth + 1
          });
          
          visited.add(targetFilterId);
          
          // Log para debugging
          console.log(
            `Propagated filter: ${sourceFilterId} → ${targetFilterId} (depth ${depth + 1})`,
            translatedFilter.warnings
          );
        }
      }
    }
  }
  
  return newState;
}

// Helpers
function getFilterDatasetId(filterId: string): string | null {
  // Implementação depende da estrutura do Superset
  // Normalmente, filterId está associado a um chart/dataset
  const filterConfig = getNativeFilterConfig(filterId);
  return filterConfig?.targets?.[0]?.datasetId || null;
}

function getFilterIdsForDataset(datasetId: string): string[] {
  const allFilters = getAllNativeFilters();
  return allFilters
    .filter(filter => {
      const targets = filter.targets || [];
      return targets.some(target => target.datasetId === datasetId);
    })
    .map(filter => filter.id);
}

function getDashboardMetadata(): DashboardMetadata | null {
  // Hook para obter metadata do dashboard atual
  // Implementação específica do Superset
  const dashboard = useSelector(selectDashboard);
  return dashboard?.metadata || null;
}

function getNativeFilterConfig(filterId: string): NativeFilterConfig | null {
  const filters = useSelector(selectNativeFilters);
  return filters[filterId] || null;
}

function getAllNativeFilters(): NativeFilterConfig[] {
  const filters = useSelector(selectNativeFilters);
  return Object.values(filters);
}
```

#### Lógica Técnica

1. **Trigger**: Intercepta ação `SET_DATA_MASK_FOR_FILTER_CONFIG_COMPLETE`
2. **BFS com Depth Limit**: Propaga filtros até profundidade 2
3. **Visited Set**: Previne loops infinitos
4. **Timeout Protection**: Cancela propagação após 500ms
5. **Translation**: Usa `FilterTranslationEngine` de P3.2
6. **State Update**: Atualiza `dataMask` de todos os filtros afetados
7. **Metadata**: Adiciona metadata de propagação (`propagatedFrom`, `propagationDepth`, `warnings`)

#### Integrações

- **Input**: Action `SET_DATA_MASK_FOR_FILTER_CONFIG_COMPLETE`, `DashboardMetadata.active_relationships`
- **Output**: Updated `DataMaskState` com filtros propagados
- **Usa**: `FilterTranslationEngine` (P3.2)
- **Usado por**: Todos os charts no dashboard (re-render automático)

#### Testes Necessários

- ✓ Propagação de 1 nível (A→B)
- ✓ Propagação de 2 níveis (A→B→C)
- ✓ Limite de profundidade (A→B→C→D não propaga para D)
- ✓ Loop prevention (A→B→A não causa loop infinito)
- ✓ Timeout (propagação complexa não trava UI)
- ✓ Filtro incompatível (não propaga, não quebra)
- ✓ Feature flag desabilitada (não propaga)

---

### 7.4 P3.4 — Drill-Down Hierarchy Config

#### Objetivo
Criar UI para configuração de hierarquias de drill-down entre datasets, permitindo que usuários definam sequências de navegação (ex: Country → State → City).

#### Arquivos a Serem Criados

**Arquivo**: `superset-frontend/src/dashboard/components/DrillDown/DrillDownConfig.tsx`

```typescript
import React, { useState, useCallback } from 'react';
import { Select, Button, Modal, Form, Input, List, Space } from 'antd';
import { PlusOutlined, DeleteOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { useRelationships } from '../../../features/datasets/relationships/hooks';
import { DrillDownHierarchy, DrillDownLevel } from '../../types';

interface DrillDownConfigProps {
  dashboardId: string;
  existingHierarchies: DrillDownHierarchy[];
  onSave: (hierarchies: DrillDownHierarchy[]) => void;
}

export const DrillDownConfig: React.FC<DrillDownConfigProps> = ({
  dashboardId,
  existingHierarchies,
  onSave
}) => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [hierarchies, setHierarchies] = useState<DrillDownHierarchy[]>(existingHierarchies);
  const [currentHierarchy, setCurrentHierarchy] = useState<Partial<DrillDownHierarchy> | null>(null);
  
  const { data: availableRelationships } = useRelationships(dashboardId);
  
  const handleAddHierarchy = () => {
    setCurrentHierarchy({
      id: `hierarchy_${Date.now()}`,
      name: '',
      levels: []
    });
    setIsModalVisible(true);
  };
  
  const handleAddLevel = () => {
    if (!currentHierarchy) return;
    
    const newLevel: DrillDownLevel = {
      level_index: currentHierarchy.levels?.length || 0,
      dataset_id: '',
      column_name: '',
      display_name: '',
      relationship_to_next: undefined
    };
    
    setCurrentHierarchy({
      ...currentHierarchy,
      levels: [...(currentHierarchy.levels || []), newLevel]
    });
  };
  
  const handleUpdateLevel = (index: number, field: keyof DrillDownLevel, value: any) => {
    if (!currentHierarchy) return;
    
    const updatedLevels = [...(currentHierarchy.levels || [])];
    updatedLevels[index] = {
      ...updatedLevels[index],
      [field]: value
    };
    
    setCurrentHierarchy({
      ...currentHierarchy,
      levels: updatedLevels
    });
  };
  
  const handleDeleteLevel = (index: number) => {
    if (!currentHierarchy) return;
    
    const updatedLevels = (currentHierarchy.levels || []).filter((_, i) => i !== index);
    // Re-index levels
    updatedLevels.forEach((level, i) => {
      level.level_index = i;
    });
    
    setCurrentHierarchy({
      ...currentHierarchy,
      levels: updatedLevels
    });
  };
  
  const handleSaveHierarchy = () => {
    if (!currentHierarchy || !currentHierarchy.name || !currentHierarchy.levels?.length) {
      message.error('Please provide a name and at least one level');
      return;
    }
    
    // Validar hierarquia
    const validation = validateHierarchy(currentHierarchy as DrillDownHierarchy);
    if (!validation.valid) {
      message.error(validation.error);
      return;
    }
    
    // Adicionar ou atualizar hierarquia
    const existingIndex = hierarchies.findIndex(h => h.id === currentHierarchy.id);
    let updatedHierarchies;
    
    if (existingIndex >= 0) {
      updatedHierarchies = [...hierarchies];
      updatedHierarchies[existingIndex] = currentHierarchy as DrillDownHierarchy;
    } else {
      updatedHierarchies = [...hierarchies, currentHierarchy as DrillDownHierarchy];
    }
    
    setHierarchies(updatedHierarchies);
    setIsModalVisible(false);
    setCurrentHierarchy(null);
    
    // Salvar no backend
    onSave(updatedHierarchies);
  };
  
  const validateHierarchy = (hierarchy: DrillDownHierarchy): { valid: boolean, error?: string } => {
    // Validar níveis consecutivos
    for (let i = 0; i < hierarchy.levels.length - 1; i++) {
      const currentLevel = hierarchy.levels[i];
      const nextLevel = hierarchy.levels[i + 1];
      
      if (!currentLevel.relationship_to_next) {
        return {
          valid: false,
          error: `Level ${i + 1} (${currentLevel.display_name}) must have a relationship to the next level`
        };
      }
      
      // Verificar se relacionamento conecta os datasets corretos
      const relationship = availableRelationships?.find(
        r => r.id === currentLevel.relationship_to_next
      );
      
      if (!relationship) {
        return {
          valid: false,
          error: `Relationship not found for level ${i + 1}`
        };
      }
      
      const connects = (
        (relationship.source_dataset_id === currentLevel.dataset_id &&
         relationship.target_dataset_id === nextLevel.dataset_id) ||
        (relationship.target_dataset_id === currentLevel.dataset_id &&
         relationship.source_dataset_id === nextLevel.dataset_id)
      );
      
      if (!connects) {
        return {
          valid: false,
          error: `Relationship at level ${i + 1} does not connect the selected datasets`
        };
      }
    }
    
    return { valid: true };
  };
  
  return (
    <div className="drill-down-config">
      <Space direction="vertical" style={{ width: '100%' }}>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAddHierarchy}
        >
          Create Drill-Down Hierarchy
        </Button>
        
        <List
          dataSource={hierarchies}
          renderItem={(hierarchy) => (
            <List.Item
              actions={[
                <Button onClick={() => {
                  setCurrentHierarchy(hierarchy);
                  setIsModalVisible(true);
                }}>
                  Edit
                </Button>,
                <Button
                  danger
                  onClick={() => {
                    const updated = hierarchies.filter(h => h.id !== hierarchy.id);
                    setHierarchies(updated);
                    onSave(updated);
                  }}
                >
                  Delete
                </Button>
              ]}
            >
              <List.Item.Meta
                title={hierarchy.name}
                description={`${hierarchy.levels.length} levels: ${
                  hierarchy.levels.map(l => l.display_name || l.column_name).join(' → ')
                }`}
              />
            </List.Item>
          )}
        />
      </Space>
      
      <Modal
        title={currentHierarchy?.id ? 'Edit Hierarchy' : 'Create Hierarchy'}
        visible={isModalVisible}
        onOk={handleSaveHierarchy}
        onCancel={() => {
          setIsModalVisible(false);
          setCurrentHierarchy(null);
        }}
        width={800}
      >
        <Form layout="vertical">
          <Form.Item label="Hierarchy Name">
            <Input
              value={currentHierarchy?.name || ''}
              onChange={(e) => setCurrentHierarchy({
                ...currentHierarchy,
                name: e.target.value
              })}
              placeholder="e.g., Geographic Hierarchy"
            />
          </Form.Item>
          
          <Form.Item label="Levels">
            <Space direction="vertical" style={{ width: '100%' }}>
              {(currentHierarchy?.levels || []).map((level, index) => (
                <div key={index} className="drill-down-level">
                  <Space align="start">
                    <div style={{ width: 40, textAlign: 'center', paddingTop: 8 }}>
                      {index + 1}
                    </div>
                    
                    <Space direction="vertical" style={{ flex: 1 }}>
                      <Select
                        style={{ width: 200 }}
                        placeholder="Select Dataset"
                        value={level.dataset_id || undefined}
                        onChange={(value) => handleUpdateLevel(index, 'dataset_id', value)}
                      >
                        {/* Populate with available datasets */}
                        {/* <Option value="dataset_id">Dataset Name</Option> */}
                      </Select>
                      
                      <Select
                        style={{ width: 200 }}
                        placeholder="Select Column"
                        value={level.column_name || undefined}
                        onChange={(value) => handleUpdateLevel(index, 'column_name', value)}
                      >
                        {/* Populate with columns from selected dataset */}
                        {/* <Option value="column_name">Column Name</Option> */}
                      </Select>
                      
                      <Input
                        style={{ width: 200 }}
                        placeholder="Display Name"
                        value={level.display_name || ''}
                        onChange={(e) => handleUpdateLevel(index, 'display_name', e.target.value)}
                      />
                      
                      {index < (currentHierarchy.levels?.length || 0) - 1 && (
                        <>
                          <ArrowDownOutlined style={{ fontSize: 16, color: '#1890ff' }} />
                          <Select
                            style={{ width: 200 }}
                            placeholder="Relationship to Next Level"
                            value={level.relationship_to_next || undefined}
                            onChange={(value) => handleUpdateLevel(index, 'relationship_to_next', value)}
                          >
                            {availableRelationships?.map(rel => (
                              <Select.Option key={rel.id} value={rel.id}>
                                {rel.name || `${rel.source_dataset_name} → ${rel.target_dataset_name}`}
                              </Select.Option>
                            ))}
                          </Select>
                        </>
                      )}
                    </Space>
                    
                    <Button
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => handleDeleteLevel(index)}
                    />
                  </Space>
                </div>
              ))}
              
              <Button
                type="dashed"
                onClick={handleAddLevel}
                block
                icon={<PlusOutlined />}
              >
                Add Level
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};
```

**Arquivo**: `superset-frontend/src/dashboard/components/DrillDown/index.ts`

```typescript
export { DrillDownConfig } from './DrillDownConfig';
export { DrillDownNavigation } from './DrillDownNavigation';
export { DrillDownBreadcrumb } from './DrillDownBreadcrumb';
```

#### Modificações Necessárias

**Arquivo**: `superset-frontend/src/dashboard/types.ts`

```typescript
// ADICIONAR tipos
export interface DrillDownHierarchy {
  id: string;
  name: string;
  levels: DrillDownLevel[];
}

export interface DrillDownLevel {
  level_index: number;
  dataset_id: string;
  column_name: string;
  display_name?: string;
  relationship_to_next?: string; // ID do relationship
}

// MODIFICAR DashboardMetadata
export interface DashboardMetadata {
  // ... campos existentes ...
  active_relationships?: DatasetRelationship[];
  drill_down_hierarchies?: DrillDownHierarchy[]; // NOVO
}
```

#### Lógica Técnica

1. **UI Builder**: Interface drag-and-drop ou formulário para adicionar níveis
2. **Validation**: Valida que relacionamentos conectam datasets consecutivos
3. **Persistence**: Salva hierarquias em `dashboard.json_metadata`
4. **Templates**: Oferece templates pré-configurados (Geographic, Time, etc.)
5. **Preview**: Mostra preview da hierarquia durante configuração

#### Integrações

- **Input**: Available datasets, available relationships
- **Output**: `DrillDownHierarchy[]` salvo em `DashboardMetadata`
- **Usado por**: P3.5 (Drill-Down Navigation Engine)

#### Testes Necessários

- ✓ Criar hierarquia de 2 níveis
- ✓ Criar hierarquia de 5 níveis (limite máximo)
- ✓ Editar hierarquia existente
- ✓ Deletar hierarquia
- ✓ Validação: relacionamento inválido (não conecta datasets)
- ✓ Validação: hierarquia sem relacionamento entre níveis
- ✓ Persistência: hierarquia salva corretamente em metadata

---

### 7.5 P3.5 — Drill-Down Navigation Engine

#### Objetivo
Implementar engine de navegação drill-down que permite usuários clicarem em elementos de charts e navegarem para próximo nível de granularidade, com filtros aplicados automaticamente.

#### Arquivos a Serem Criados

**Arquivo**: `superset-frontend/src/dashboard/components/DrillDown/DrillDownNavigation.tsx`

```typescript
import React, { useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { filterTranslationEngine } from '../../../features/datasets/relationships/filterTranslation';
import { DrillDownHierarchy, DrillDownState } from '../../types';
import { DrillDownBreadcrumb } from './DrillDownBreadcrumb';

interface DrillDownNavigationProps {
  hierarchyId: string;
  chartId: string;
}

export const DrillDownNavigation: React.FC<DrillDownNavigationProps> = ({
  hierarchyId,
  chartId
}) => {
  const dispatch = useDispatch();
  const hierarchy = useSelector(state => 
    selectDrillDownHierarchy(state, hierarchyId)
  );
  const relationships = useSelector(selectActiveRelationships);
  
  const [drillDownState, setDrillDownState] = useState<DrillDownState>({
    hierarchyId,
    currentLevel: 0,
    appliedFilters: [],
    breadcrumb: [{
      level: 0,
      label: hierarchy?.levels[0]?.display_name || 'All',
      filters: []
    }]
  });
  
  /**
   * Handler para navegação drill-down (próximo nível)
   */
  const handleDrillDown = useCallback((clickedValue: any, clickedColumn: string) => {
    if (!hierarchy) return;
    
    const currentLevel = hierarchy.levels[drillDownState.currentLevel];
    const nextLevelIndex = drillDownState.currentLevel + 1;
    
    // Validar se existe próximo nível
    if (nextLevelIndex >= hierarchy.levels.length) {
      console.warn('Already at deepest drill-down level');
      return;
    }
    
    const nextLevel = hierarchy.levels[nextLevelIndex];
    
    // Criar novo filtro
    const newFilter = {
      level: drillDownState.currentLevel,
      dataset_id: currentLevel.dataset_id,
      column_name: clickedColumn,
      value: clickedValue,
      display_value: String(clickedValue)
    };
    
    // Acumular filtros
    const updatedFilters = [...drillDownState.appliedFilters, newFilter];
    
    // Traduzir filtros para o próximo nível
    const relationship = relationships.find(
      r => r.id === currentLevel.relationship_to_next
    );
    
    if (!relationship) {
      console.error('Relationship not found:', currentLevel.relationship_to_next);
      return;
    }
    
    const translatedFilters = translateFiltersForDrillDown(
      updatedFilters,
      nextLevel,
      relationships
    );
    
    // Aplicar filtros ao chart do próximo nível
    dispatch(applyDrillDownFilters({
      chartId,
      datasetId: nextLevel.dataset_id,
      filters: translatedFilters
    }));
    
    // Atualizar breadcrumb
    const updatedBreadcrumb = [
      ...drillDownState.breadcrumb,
      {
        level: nextLevelIndex,
        label: String(clickedValue),
        filters: updatedFilters
      }
    ];
    
    // Atualizar estado
    setDrillDownState({
      hierarchyId,
      currentLevel: nextLevelIndex,
      appliedFilters: updatedFilters,
      breadcrumb: updatedBreadcrumb
    });
    
    // Log analytics
    logDrillDownEvent({
      hierarchyId,
      fromLevel: drillDownState.currentLevel,
      toLevel: nextLevelIndex,
      filterValue: clickedValue
    });
  }, [hierarchy, drillDownState, relationships, dispatch, chartId]);
  
  /**
   * Handler para navegação breadcrumb (voltar nível)
   */
  const handleBreadcrumbClick = useCallback((targetLevel: number) => {
    if (!hierarchy) return;
    
    // Remover filtros após o nível alvo
    const updatedFilters = drillDownState.appliedFilters.filter(
      f => f.level < targetLevel
    );
    
    // Atualizar breadcrumb
    const updatedBreadcrumb = drillDownState.breadcrumb.slice(0, targetLevel + 1);
    
    // Re-aplicar filtros
    const targetLevelData = hierarchy.levels[targetLevel];
    const translatedFilters = translateFiltersForDrillDown(
      updatedFilters,
      targetLevelData,
      relationships
    );
    
    dispatch(applyDrillDownFilters({
      chartId,
      datasetId: targetLevelData.dataset_id,
      filters: translatedFilters
    }));
    
    // Atualizar estado
    setDrillDownState({
      hierarchyId,
      currentLevel: targetLevel,
      appliedFilters: updatedFilters,
      breadcrumb: updatedBreadcrumb
    });
  }, [hierarchy, drillDownState, relationships, dispatch, chartId]);
  
  /**
   * Handler para resetar drill-down (voltar ao topo)
   */
  const handleReset = useCallback(() => {
    if (!hierarchy) return;
    
    const topLevel = hierarchy.levels[0];
    
    // Remover todos os filtros
    dispatch(clearDrillDownFilters({
      chartId,
      datasetId: topLevel.dataset_id
    }));
    
    // Resetar estado
    setDrillDownState({
      hierarchyId,
      currentLevel: 0,
      appliedFilters: [],
      breadcrumb: [{
        level: 0,
        label: topLevel.display_name || 'All',
        filters: []
      }]
    });
  }, [hierarchy, dispatch, chartId, hierarchyId]);
  
  // Attach click handler to chart
  React.useEffect(() => {
    const chart = getChartInstance(chartId);
    if (chart) {
      chart.on('click', (params: any) => {
        // Extract clicked value and column
        const clickedColumn = params.name || params.seriesName;
        const clickedValue = params.value || params.data?.value;
        
        if (clickedValue !== undefined) {
          handleDrillDown(clickedValue, clickedColumn);
        }
      });
    }
    
    return () => {
      if (chart) {
        chart.off('click');
      }
    };
  }, [chartId, handleDrillDown]);
  
  if (!hierarchy) {
    return null;
  }
  
  return (
    <div className="drill-down-navigation">
      <DrillDownBreadcrumb
        breadcrumb={drillDownState.breadcrumb}
        currentLevel={drillDownState.currentLevel}
        onBreadcrumbClick={handleBreadcrumbClick}
        onReset={handleReset}
      />
    </div>
  );
};

/**
 * Traduz filtros acumulados para aplicar ao nível alvo
 */
function translateFiltersForDrillDown(
  filters: DrillDownFilter[],
  targetLevel: DrillDownLevel,
  relationships: DatasetRelationship[]
): FilterValue[] {
  const translatedFilters: FilterValue[] = [];
  
  for (const filter of filters) {
    // Se filtro é do mesmo dataset, aplicar diretamente
    if (filter.dataset_id === targetLevel.dataset_id) {
      translatedFilters.push({
        column: filter.column_name,
        value: filter.value
      });
      continue;
    }
    
    // Caso contrário, traduzir via relacionamento
    const relationship = relationships.find(
      r => (r.source_dataset_id === filter.dataset_id && r.target_dataset_id === targetLevel.dataset_id) ||
           (r.target_dataset_id === filter.dataset_id && r.source_dataset_id === targetLevel.dataset_id)
    );
    
    if (relationship) {
      const translated = filterTranslationEngine.translateFilter({
        sourceDatasetId: filter.dataset_id,
        targetDatasetId: targetLevel.dataset_id,
        relationship,
        sourceFilter: {
          filterId: `drill_down_${filter.level}`,
          filterState: {
            columnName: filter.column_name,
            value: filter.value
          },
          ownState: {}
        }
      });
      
      if (translated) {
        translatedFilters.push({
          column: translated.filter.filterState.columnName,
          value: translated.filter.filterState.value
        });
      }
    }
  }
  
  return translatedFilters;
}

// Redux actions
function applyDrillDownFilters(payload: {
  chartId: string,
  datasetId: string,
  filters: FilterValue[]
}): Action {
  return {
    type: 'APPLY_DRILL_DOWN_FILTERS',
    payload
  };
}

function clearDrillDownFilters(payload: {
  chartId: string,
  datasetId: string
}): Action {
  return {
    type: 'CLEAR_DRILL_DOWN_FILTERS',
    payload
  };
}

// Analytics
function logDrillDownEvent(event: DrillDownEvent): void {
  // Log to analytics service
  console.log('[DrillDown]', event);
}

// Types
interface DrillDownFilter {
  level: number;
  dataset_id: string;
  column_name: string;
  value: any;
  display_value: string;
}

interface FilterValue {
  column: string;
  value: any;
}

interface DrillDownEvent {
  hierarchyId: string;
  fromLevel: number;
  toLevel: number;
  filterValue: any;
}
```

**Arquivo**: `superset-frontend/src/dashboard/components/DrillDown/DrillDownBreadcrumb.tsx`

```typescript
import React from 'react';
import { Breadcrumb, Button } from 'antd';
import { HomeOutlined } from '@ant-design/icons';
import { BreadcrumbItem } from '../../types';

interface DrillDownBreadcrumbProps {
  breadcrumb: BreadcrumbItem[];
  currentLevel: number;
  onBreadcrumbClick: (level: number) => void;
  onReset: () => void;
}

export const DrillDownBreadcrumb: React.FC<DrillDownBreadcrumbProps> = ({
  breadcrumb,
  currentLevel,
  onBreadcrumbClick,
  onReset
}) => {
  return (
    <div className="drill-down-breadcrumb">
      <Breadcrumb>
        <Breadcrumb.Item>
          <Button
            type="link"
            icon={<HomeOutlined />}
            onClick={onReset}
          >
            Reset
          </Button>
        </Breadcrumb.Item>
        
        {breadcrumb.map((item, index) => (
          <Breadcrumb.Item key={index}>
            {index < currentLevel ? (
              <Button
                type="link"
                onClick={() => onBreadcrumbClick(index)}
              >
                {item.label}
              </Button>
            ) : (
              <span style={{ fontWeight: 'bold' }}>{item.label}</span>
            )}
          </Breadcrumb.Item>
        ))}
      </Breadcrumb>
    </div>
  );
};
```

#### Lógica Técnica

1. **Click Detection**: Intercepta cliques em elementos de charts
2. **Filter Creation**: Cria filtro baseado no valor clicado
3. **Filter Translation**: Usa `FilterTranslationEngine` para traduzir filtros entre níveis
4. **State Management**: Mantém estado de drill-down (nível atual, filtros aplicados)
5. **Breadcrumb**: Renderiza breadcrumb navegável para voltar níveis
6. **Reset**: Permite voltar ao nível mais alto

#### Integrações

- **Input**: Click event do chart, `DrillDownHierarchy` configurada
- **Output**: Filtros aplicados ao chart, breadcrumb atualizado
- **Usa**: `FilterTranslationEngine` (P3.2), `DrillDownHierarchy` (P3.4)
- **Integra com**: Chart rendering, Redux store

#### Testes Necessários

- ✓ Drill-down de 1 nível (click → próximo nível)
- ✓ Drill-down multi-nível (click → click → click)
- ✓ Breadcrumb navigation (voltar 1 nível, voltar ao topo)
- ✓ Filtros acumulados (filtros de níveis anteriores mantidos)
- ✓ Tradução de filtros cross-dataset
- ✓ Limite de profundidade (não permite drill-down além do último nível)
- ✓ Reset (limpa todos os filtros, volta ao topo)

---

### 7.6 P3.6 — Performance - Query Caching

#### Objetivo
Implementar sistema de cache para resultados de merge cross-DB, reduzindo tempo de resposta e carga nos bancos de dados.

#### Arquivos a Serem Modificados

**Arquivo**: `superset/utils/cache.py`

```python
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import pandas as pd
from flask_caching import Cache
from superset import app
from superset.models.core import Log

# Configuração de cache (Redis ou Memcached)
cache = Cache(app, config=app.config['CACHE_CONFIG'])

class RelationshipMergeCache:
    """
    Cache especializado para resultados de merge cross-DB
    """
    
    CACHE_KEY_PREFIX = "merge:"
    DEFAULT_TTL = 3600  # 1 hora
    MAX_CACHE_SIZE_MB = 100  # 100MB por entrada
    
    @staticmethod
    def generate_cache_key(
        dataset_ids: list,
        relationship_id: str,
        query_hash: str,
        user_id: int
    ) -> str:
        """
        Gera chave de cache determinística baseada em:
        - IDs dos datasets envolvidos
        - ID do relacionamento
        - Hash das queries SQL
        - User ID (para row-level security)
        """
        sorted_datasets = sorted(dataset_ids)
        key_components = [
            *sorted_datasets,
            relationship_id,
            query_hash,
            str(user_id)
        ]
        
        key_str = ":".join(key_components)
        key_hash = hashlib.sha256(key_str.encode()).hexdigest()[:16]
        
        return f"{RelationshipMergeCache.CACHE_KEY_PREFIX}{'_'.join(sorted_datasets)}:{key_hash}"
    
    @staticmethod
    def get(cache_key: str) -> Optional[pd.DataFrame]:
        """
        Busca resultado no cache
        """
        try:
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                # Log cache miss
                Log.log_event(
                    action="cache_miss",
                    object_ref=cache_key,
                    source="relationship_merge_cache"
                )
                return None
            
            # Deserializar DataFrame
            df = pickle.loads(cached_data['dataframe'])
            
            # Log cache hit
            Log.log_event(
                action="cache_hit",
                object_ref=cache_key,
                source="relationship_merge_cache",
                json_data={
                    'timestamp': cached_data['timestamp'],
                    'row_count': cached_data['row_count'],
                    'size_mb': cached_data['size_mb']
                }
            )
            
            return df
            
        except Exception as e:
            app.logger.error(f"Cache retrieval error: {e}")
            return None
    
    @staticmethod
    def set(
        cache_key: str,
        df: pd.DataFrame,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Armazena resultado no cache
        """
        try:
            # Serializar DataFrame
            serialized_df = pickle.dumps(df)
            size_mb = len(serialized_df) / (1024 * 1024)
            
            # Verificar limite de tamanho
            if size_mb > RelationshipMergeCache.MAX_CACHE_SIZE_MB:
                app.logger.warning(
                    f"DataFrame too large for cache: {size_mb:.2f}MB (limit: {RelationshipMergeCache.MAX_CACHE_SIZE_MB}MB)"
                )
                return False
            
            # Preparar metadados
            cache_data = {
                'dataframe': serialized_df,
                'timestamp': datetime.now().isoformat(),
                'row_count': len(df),
                'size_mb': size_mb
            }
            
            # Armazenar com TTL
            ttl = ttl or RelationshipMergeCache.DEFAULT_TTL
            cache.set(cache_key, cache_data, timeout=ttl)
            
            # Log cache set
            Log.log_event(
                action="cache_set",
                object_ref=cache_key,
                source="relationship_merge_cache",
                json_data={
                    'row_count': len(df),
                    'size_mb': size_mb,
                    'ttl': ttl
                }
            )
            
            return True
            
        except Exception as e:
            app.logger.error(f"Cache storage error: {e}")
            return False
    
    @staticmethod
    def invalidate_for_dataset(dataset_id: str) -> int:
        """
        Invalida todas as entradas de cache relacionadas a um dataset
        """
        pattern = f"{RelationshipMergeCache.CACHE_KEY_PREFIX}*{dataset_id}*"
        
        try:
            # Obter todas as chaves que correspondem ao padrão
            keys = cache.cache._read_client.keys(pattern)
            
            if not keys:
                return 0
            
            # Deletar todas as chaves
            deleted_count = cache.cache._write_client.delete(*keys)
            
            # Log invalidação
            Log.log_event(
                action="cache_invalidate_dataset",
                object_ref=dataset_id,
                source="relationship_merge_cache",
                json_data={'deleted_keys': deleted_count}
            )
            
            return deleted_count
            
        except Exception as e:
            app.logger.error(f"Cache invalidation error: {e}")
            return 0
    
    @staticmethod
    def invalidate_for_relationship(relationship_id: str) -> int:
        """
        Invalida todas as entradas de cache relacionadas a um relacionamento
        """
        pattern = f"{RelationshipMergeCache.CACHE_KEY_PREFIX}*:{relationship_id}:*"
        
        try:
            keys = cache.cache._read_client.keys(pattern)
            
            if not keys:
                return 0
            
            deleted_count = cache.cache._write_client.delete(*keys)
            
            Log.log_event(
                action="cache_invalidate_relationship",
                object_ref=relationship_id,
                source="relationship_merge_cache",
                json_data={'deleted_keys': deleted_count}
            )
            
            return deleted_count
            
        except Exception as e:
            app.logger.error(f"Cache invalidation error: {e}")
            return 0
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """
        Retorna estatísticas do cache
        """
        try:
            pattern = f"{RelationshipMergeCache.CACHE_KEY_PREFIX}*"
            keys = cache.cache._read_client.keys(pattern)
            
            total_keys = len(keys)
            total_size_mb = 0
            
            for key in keys:
                cached_data = cache.get(key)
                if cached_data:
                    total_size_mb += cached_data.get('size_mb', 0)
            
            return {
                'total_entries': total_keys,
                'total_size_mb': total_size_mb,
                'cache_type': app.config['CACHE_CONFIG'].get('CACHE_TYPE'),
                'default_ttl': RelationshipMergeCache.DEFAULT_TTL
            }
            
        except Exception as e:
            app.logger.error(f"Cache stats error: {e}")
            return {}
```

**Arquivo**: `superset/common/query_context_processor.py`

```python
from superset.utils.cache import RelationshipMergeCache

# MODIFICAR método get_query_result (onde merge cross-DB acontece)
def get_query_result(self, query_obj: Dict[str, Any]) -> Dict[str, Any]:
    # ... código existente ...
    
    # Verificar se é merge cross-DB
    if query_obj.get('relationships'):
        # Gerar cache key
        dataset_ids = [query_obj['dataset_id']] + [
            rel['target_dataset_id'] for rel in query_obj['relationships']
        ]
        query_hash = hashlib.md5(
            json.dumps(query_obj, sort_keys=True).encode()
        ).hexdigest()
        
        cache_key = RelationshipMergeCache.generate_cache_key(
            dataset_ids=dataset_ids,
            relationship_id=query_obj['relationships'][0]['id'],
            query_hash=query_hash,
            user_id=g.user.id
        )
        
        # Tentar buscar no cache
        cached_df = RelationshipMergeCache.get(cache_key)
        
        if cached_df is not None:
            return {
                'data': cached_df,
                'from_cache': True,
                'cache_key': cache_key
            }
        
        # Cache miss: executar merge
        merged_df = self._execute_cross_db_merge(query_obj)
        
        # Armazenar no cache
        RelationshipMergeCache.set(cache_key, merged_df)
        
        return {
            'data': merged_df,
            'from_cache': False,
            'cache_key': cache_key
        }
    
    # ... código existente para queries sem relacionamentos ...
```

**Arquivo**: `superset/daos/dataset_relationship.py`

```python
from superset.utils.cache import RelationshipMergeCache

# ADICIONAR hooks de invalidação
class DatasetRelationshipDAO(BaseDAO):
    # ... código existente ...
    
    @classmethod
    def update(cls, model_id: int, properties: Dict[str, Any]) -> DatasetRelationship:
        obj = super().update(model_id, properties)
        
        # Invalidar cache
        RelationshipMergeCache.invalidate_for_relationship(str(model_id))
        
        return obj
    
    @classmethod
    def delete(cls, model: DatasetRelationship) -> None:
        # Invalidar cache antes de deletar
        RelationshipMergeCache.invalidate_for_relationship(str(model.id))
        
        super().delete(model)
```

**Arquivo**: `superset/daos/dataset.py`

```python
from superset.utils.cache import RelationshipMergeCache

# ADICIONAR hook de invalidação
class DatasetDAO(BaseDAO):
    # ... código existente ...
    
    @classmethod
    def update(cls, model_id: int, properties: Dict[str, Any]) -> Dataset:
        obj = super().update(model_id, properties)
        
        # Invalidar cache de merges que usam este dataset
        RelationshipMergeCache.invalidate_for_dataset(str(model_id))
        
        return obj
```

#### Lógica Técnica

1. **Cache Key Generation**: Chave determinística baseada em datasets, relationship, query hash e user ID
2. **Serialization**: Serializa DataFrame com Pickle (compacto e rápido)
3. **TTL Management**: TTL default de 1 hora, configurável
4. **Size Limits**: Limite de 100MB por entrada para evitar OOM
5. **Invalidation Hooks**: Invalida cache quando datasets ou relationships são modificados
6. **Stats & Monitoring**: Métricas de cache hit/miss rate

#### Integrações

- **Input**: Query result (DataFrame), dataset IDs, relationship ID
- **Output**: Cached DataFrame (se hit) ou fresh DataFrame (se miss)
- **Usado por**: `QueryContextProcessor.get_query_result()` (P1.10)
- **Triggers**: Dataset update, Relationship update/delete

#### Testes Necessários

- ✓ Cache hit (query idêntica retorna do cache)
- ✓ Cache miss (query diferente executa fresh)
- ✓ Cache invalidation (update dataset → cache invalidado)
- ✓ Cache invalidation (delete relationship → cache invalidado)
- ✓ Size limit (DataFrame > 100MB não é cacheado)
- ✓ TTL expiration (cache expira após 1 hora)
- ✓ User isolation (user A não acessa cache de user B)

---

### 7.7 P3.7 — Performance - Index Optimization

#### Objetivo
Implementar sistema que analisa queries de JOIN e sugere/cria índices automaticamente em colunas de relacionamento para otimizar performance.

#### Arquivos a Serem Modificados

**Arquivo**: `superset/db_engine_specs/base.py`

```python
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, inspect, text
from superset.models.dataset_relationship import DatasetRelationship

class BaseEngineSpec:
    # ... código existente ...
    
    @classmethod
    def suggest_join_indexes(
        cls,
        relationship: DatasetRelationship,
        source_table: str,
        target_table: str
    ) -> List[Dict[str, Any]]:
        """
        Sugere índices para colunas de JOIN em um relacionamento
        """
        suggestions = []
        
        # Analisar colunas source
        for rel_column in relationship.columns:
            source_column = rel_column.source_column_name
            target_column = rel_column.target_column_name
            
            # Verificar se índice já existe na coluna source
            source_has_index = cls._column_has_index(
                relationship.source_dataset.database,
                source_table,
                source_column
            )
            
            if not source_has_index:
                suggestions.append({
                    'table': source_table,
                    'column': source_column,
                    'index_name': f"idx_{source_table}_{source_column}",
                    'reason': f"JOIN key in relationship '{relationship.name}'",
                    'priority': 'high',
                    'create_sql': cls._generate_create_index_sql(
                        source_table,
                        source_column,
                        f"idx_{source_table}_{source_column}"
                    )
                })
            
            # Verificar se índice já existe na coluna target
            target_has_index = cls._column_has_index(
                relationship.target_dataset.database,
                target_table,
                target_column
            )
            
            if not target_has_index:
                suggestions.append({
                    'table': target_table,
                    'column': target_column,
                    'index_name': f"idx_{target_table}_{target_column}",
                    'reason': f"JOIN key in relationship '{relationship.name}'",
                    'priority': 'high',
                    'create_sql': cls._generate_create_index_sql(
                        target_table,
                        target_column,
                        f"idx_{target_table}_{target_column}"
                    )
                })
        
        return suggestions
    
    @classmethod
    def _column_has_index(
        cls,
        database: Database,
        table_name: str,
        column_name: str
    ) -> bool:
        """
        Verifica se coluna tem índice
        """
        try:
            engine = database.get_sqla_engine()
            inspector = inspect(engine)
            
            # Obter todos os índices da tabela
            indexes = inspector.get_indexes(table_name)
            
            # Verificar se algum índice inclui a coluna
            for index in indexes:
                if column_name in index['column_names']:
                    return True
            
            return False
            
        except Exception as e:
            app.logger.error(f"Error checking index: {e}")
            return False
    
    @classmethod
    def _generate_create_index_sql(
        cls,
        table_name: str,
        column_name: str,
        index_name: str
    ) -> str:
        """
        Gera SQL para criar índice (engine-specific)
        """
        # Default: SQL padrão
        return f"CREATE INDEX {index_name} ON {table_name}({column_name});"
    
    @classmethod
    def create_index(
        cls,
        database: Database,
        table_name: str,
        column_name: str,
        index_name: str,
        concurrent: bool = True
    ) -> bool:
        """
        Cria índice em uma coluna
        """
        try:
            engine = database.get_sqla_engine()
            
            # Gerar SQL de criação
            create_sql = cls._generate_create_index_sql(
                table_name,
                column_name,
                index_name
            )
            
            # Adicionar CONCURRENTLY se suportado e solicitado
            if concurrent and cls._supports_concurrent_index():
                create_sql = create_sql.replace(
                    "CREATE INDEX",
                    "CREATE INDEX CONCURRENTLY"
                )
            
            # Executar com timeout
            with engine.connect() as conn:
                conn.execute(text(create_sql))
            
            # Log sucesso
            Log.log_event(
                action="index_created",
                object_ref=f"{table_name}.{column_name}",
                source="relationship_index_optimizer",
                json_data={
                    'index_name': index_name,
                    'concurrent': concurrent
                }
            )
            
            return True
            
        except Exception as e:
            app.logger.error(f"Error creating index: {e}")
            return False
    
    @classmethod
    def _supports_concurrent_index(cls) -> bool:
        """
        Verifica se engine suporta CREATE INDEX CONCURRENTLY
        """
        # Override em engine-specific specs (ex: PostgresEngineSpec)
        return False
    
    @classmethod
    def analyze_query_plan(
        cls,
        database: Database,
        query_sql: str
    ) -> Dict[str, Any]:
        """
        Analisa plano de execução de uma query
        """
        try:
            engine = database.get_sqla_engine()
            
            # Executar EXPLAIN
            explain_sql = f"EXPLAIN {query_sql}"
            
            with engine.connect() as conn:
                result = conn.execute(text(explain_sql))
                plan = result.fetchall()
            
            # Analisar plano
            analysis = {
                'has_seq_scan': any('Seq Scan' in str(row) for row in plan),
                'has_index_scan': any('Index Scan' in str(row) for row in plan),
                'estimated_cost': cls._extract_cost_from_plan(plan),
                'raw_plan': [str(row) for row in plan]
            }
            
            return analysis
            
        except Exception as e:
            app.logger.error(f"Error analyzing query plan: {e}")
            return {}
    
    @classmethod
    def _extract_cost_from_plan(cls, plan: List) -> Optional[float]:
        """
        Extrai custo estimado do plano de execução
        """
        # Engine-specific parsing
        # Exemplo para Postgres: "Seq Scan on table (cost=0.00..123.45 rows=1000 width=8)"
        return None
```

**Arquivo**: `superset/db_engine_specs/postgres.py`

```python
# OVERRIDE para Postgres
class PostgresEngineSpec(BaseEngineSpec):
    @classmethod
    def _supports_concurrent_index(cls) -> bool:
        return True  # Postgres suporta CREATE INDEX CONCURRENTLY
    
    @classmethod
    def _generate_create_index_sql(
        cls,
        table_name: str,
        column_name: str,
        index_name: str
    ) -> str:
        # Postgres-specific: adicionar schema se necessário
        return f"CREATE INDEX {index_name} ON {table_name} ({column_name});"
```

**Novo Arquivo**: `superset/tasks/index_optimization.py`

```python
from celery import Celery
from superset import app
from superset.models.dataset_relationship import DatasetRelationship
from superset.db_engine_specs import get_engine_spec

celery_app = Celery('superset.tasks')

@celery_app.task
def optimize_relationship_indexes(relationship_id: int):
    """
    Task assíncrona para otimizar índices de um relacionamento
    """
    relationship = DatasetRelationship.query.get(relationship_id)
    
    if not relationship:
        return {'error': 'Relationship not found'}
    
    # Obter engine specs
    source_spec = get_engine_spec(relationship.source_dataset.database.backend)
    target_spec = get_engine_spec(relationship.target_dataset.database.backend)
    
    # Gerar sugestões
    suggestions = []
    
    if relationship.source_dataset.database == relationship.target_dataset.database:
        # Same-DB: usar mesmo spec
        suggestions = source_spec.suggest_join_indexes(
            relationship,
            relationship.source_dataset.table_name,
            relationship.target_dataset.table_name
        )
    else:
        # Cross-DB: sugestões separadas
        source_suggestions = source_spec.suggest_join_indexes(
            relationship,
            relationship.source_dataset.table_name,
            None
        )
        target_suggestions = target_spec.suggest_join_indexes(
            relationship,
            None,
            relationship.target_dataset.table_name
        )
        suggestions = source_suggestions + target_suggestions
    
    # Criar índices (se modo automático habilitado)
    created_indexes = []
    
    if app.config.get('RELATIONSHIP_AUTO_CREATE_INDEXES', False):
        for suggestion in suggestions:
            success = source_spec.create_index(
                relationship.source_dataset.database,
                suggestion['table'],
                suggestion['column'],
                suggestion['index_name'],
                concurrent=True
            )
            
            if success:
                created_indexes.append(suggestion['index_name'])
    
    return {
        'relationship_id': relationship_id,
        'suggestions': suggestions,
        'created_indexes': created_indexes,
        'mode': 'auto' if app.config.get('RELATIONSHIP_AUTO_CREATE_INDEXES') else 'suggest'
    }
```

#### Lógica Técnica

1. **Index Detection**: Verifica se colunas de JOIN já têm índices
2. **Suggestion Generation**: Gera sugestões de índices com SQL e prioridade
3. **Concurrent Creation**: Cria índices com `CONCURRENTLY` (Postgres) para evitar locks
4. **Query Plan Analysis**: Usa `EXPLAIN` para analisar performance de queries
5. **Async Task**: Criação de índices executada em background via Celery

#### Integrações

- **Input**: `DatasetRelationship`, database connection
- **Output**: List de sugestões de índices, índices criados (se auto mode)
- **Trigger**: Criação de novo relacionamento, análise manual
- **Usado por**: Admin UI, background tasks

#### Testes Necessários

- ✓ Detecção de índice existente (não sugere duplicados)
- ✓ Sugestão de índice (coluna sem índice → sugestão gerada)
- ✓ Criação de índice concurrent (Postgres)
- ✓ Criação de índice standard (MySQL, outros)
- ✓ Cross-DB suggestions (sugestões separadas para cada DB)
- ✓ Query plan analysis (identifica seq scan vs index scan)
- ✓ Async task execution (task roda em background)

---

### 7.8 P3.8 — Unit Tests - Cross-Filter & Drill-Down

#### Objetivo
Criar testes unitários abrangentes para filter translation, cross-filter propagation, drill-down navigation e edge cases.

#### Arquivos a Serem Criados

**Arquivo**: `tests/unit_tests/cross_filter_tests/test_filter_translation.py`

```python
import pytest
from superset_frontend.src.features.datasets.relationships.filterTranslation import FilterTranslationEngine

class TestFilterTranslationEngine:
    def test_translate_filter_same_type(self):
        """Testa tradução de filtro com tipos compatíveis"""
        # Setup
        # ... (código de teste)
    
    def test_translate_filter_type_coercion(self):
        """Testa tradução com coerção de tipo (INT→STRING)"""
        # ... (código de teste)
    
    def test_translate_filter_incompatible_types(self):
        """Testa que filtro incompatível retorna None"""
        # ... (código de teste)
    
    def test_translate_filter_many_to_one(self):
        """Testa tradução em relacionamento many-to-one"""
        # ... (código de teste)
    
    def test_translate_filter_cross_db(self):
        """Testa tradução cross-DB (gera warnings)"""
        # ... (código de teste)
```

**Arquivo**: `tests/unit_tests/drill_down_tests/test_navigation_engine.py`

```python
import pytest
from superset_frontend.src.dashboard.components.DrillDown.DrillDownNavigation import (
    navigateDrillDown,
    navigateUpBreadcrumb
)

class TestDrillDownNavigation:
    def test_drill_down_one_level(self):
        """Testa drill-down de 1 nível"""
        # ... (código de teste)
    
    def test_drill_down_multi_level(self):
        """Testa drill-down de múltiplos níveis"""
        # ... (código de teste)
    
    def test_breadcrumb_navigation(self):
        """Testa navegação via breadcrumb"""
        # ... (código de teste)
    
    def test_drill_down_max_depth(self):
        """Testa limite de profundidade"""
        # ... (código de teste)
```

---

### 7.9 P3.9 — Integration Tests - Full Pipeline

#### Objetivo
Criar testes end-to-end do pipeline completo: criar relationship → usar no explore → cross-filter → drill-down.

#### Arquivos a Serem Criados

**Arquivo**: `tests/integration_tests/relationship_pipeline_tests/test_full_pipeline.py`

```python
import pytest
from superset.models.dataset_relationship import DatasetRelationship

class TestRelationshipPipeline:
    def test_full_pipeline_same_db(self):
        """Testa pipeline completo em same-DB"""
        # 1. Criar relacionamento via API
        # 2. Configurar hierarquia drill-down
        # 3. Aplicar cross-filter
        # 4. Executar drill-down
        # 5. Validar resultados
        # ... (código de teste)
    
    def test_full_pipeline_cross_db(self):
        """Testa pipeline completo cross-DB"""
        # ... (código de teste)
```

---

### 7.10 P3.10 — Documentação Completa

#### Objetivo
Elaborar documentação técnica e de usuário completa para o Dataset Relationship Engine.

#### Arquivos a Serem Criados

1. **`docs/relationships/architecture.md`**: Arquitetura técnica completa
2. **`docs/relationships/api-reference.md`**: Referência da API REST
3. **`docs/relationships/user-guide-cross-filtering.md`**: Guia de uso do cross-filtering
4. **`docs/relationships/user-guide-drill-down.md`**: Guia de uso do drill-down
5. **`docs/relationships/performance-optimization.md`**: Otimizações de performance

---

## Conclusão

Este documento fornece um plano detalhado e abrangente para a implementação da **Fase 3 - Cross-Filtering & Drill-Down** do projeto hibi. Com duração estimada de 30-43 dias úteis, esta fase representa a culminação do Dataset Relationship Engine, trazendo funcionalidades avançadas de interatividade e navegação de dados.

**Próximos Passos:**
1. Revisar e aprovar este documento com stakeholders
2. Iniciar Sprint 1 com tasks P3.1 e P3.7
3. Configurar ambiente de testes para Fase 3
4. Preparar dados de teste para cross-filtering e drill-down

**Contato para Dúvidas:**
- Documentação: `docs/hibi_execution_plan.md`
- Fase 1: `docs/fase1_backend_engine.md` (se necessário)
- Fase 2: `docs/fase2_frontend_model_view.md` (se necessário)

---

*Documento elaborado em 14/05/2026 — Fase 3 do HIBI Dataset Relationship Engine*
