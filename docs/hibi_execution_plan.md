# HIBI — Plano de Execução: Dataset Relationship Engine

**Projeto:** hibi (fork Apache Superset)  
**Data:** 14/05/2026  
**Estimativa Total:** 11–17 semanas (~79–121 dias úteis)  
**Total de Tasks:** 33

---

## Visão Geral das Fases

| Fase | Descrição | Semanas | Dias (Min–Max) | Tasks | Risco Geral |
|------|-----------|---------|----------------|-------|-------------|
| **Fase 1** | Backend & Engine | 4–6 | 27–43 | 13 | Médio-Alto |
| **Fase 2** | Frontend & Model View | 3–4 | 22–35 | 10 | Médio |
| **Fase 3** | Cross-Filtering & Drill-Down | 4–6 | 30–43 | 10 | Alto |
| **TOTAL** | — | **11–17** | **79–121** | **33** | — |

---

## Fase 1 — Backend & Engine (27–43 dias)

| ID | Bloco/Task | Descrição | Est. (dias) | Deps | Prioridade | Risco |
|----|-----------|-----------|-------------|------|-----------|-------|
| P1.1 | Alembic Migration | Criar migration com tabelas `dataset_relationships` e `dataset_relationship_columns`, incluindo constraints, indices e downgrade | 1–2 | — | Alta | 🟢 Baixo |
| P1.2 | SQLAlchemy Models | Implementar `DatasetRelationship` e `DatasetRelationshipColumn` com relationships, back_populates, validações e uuid generation | 2–3 | P1.1 | Alta | 🟢 Baixo |
| P1.3 | DAO Layer | Implementar `DatasetRelationshipDAO` com find_by_dataset, compute_is_cross_database, get_relationship_graph, validação de grafo acíclico | 2–4 | P1.2 | Alta | 🟡 Médio |
| P1.4 | Schemas & Validation | Criar Marshmallow schemas para serialização/deserialização, validação de payloads da API e error handling | 1–2 | P1.2 | Alta | 🟢 Baixo |
| P1.5 | REST API CRUD | Implementar endpoints: list, create, get, update, delete relationships com permissões e rate limiting | 3–5 | P1.3, P1.4 | Alta | 🟡 Médio |
| P1.6 | API Discovery Endpoints | Implementar endpoints `related/<dataset_id>/` e `graph/` para descoberta de relacionamentos | 1–2 | P1.5 | Média | 🟢 Baixo |
| P1.7 | Feature Flags & Config | Adicionar feature flags e limites de segurança (`MAX_MERGE_ROWS`, `TIMEOUT`, etc.) | 1–1 | — | Alta | 🟢 Baixo |
| P1.8 | Same-DB JOIN Engine | Modificar `get_sqla_query()` para injetar cláusulas JOIN quando datasets estão no mesmo banco. Suportar LEFT, INNER, RIGHT, FULL | 3–5 | P1.3, P1.7 | Alta | 🔴 Alto |
| P1.9 | Cross-DB Merge Engine | Modificar `get_query_result()` para execução paralela de queries e merge via Pandas com proteção de memória e timeout | 4–5 | P1.3, P1.7 | Alta | 🔴 Alto |
| P1.10 | Query Context Integration | Modificar `QueryContextProcessor.get_df_payload()` para orquestrar merges cross-DB e passar relationships no query_obj | 2–3 | P1.8, P1.9 | Alta | 🔴 Alto |
| P1.11 | Unit Tests - Models & DAO | Testes para models, DAO methods, validação de grafo acíclico, compute_is_cross_database | 2–3 | P1.3 | Alta | 🟢 Baixo |
| P1.12 | Unit Tests - API | Testes CRUD da API, validação de payloads, permissões, error responses | 2–3 | P1.5, P1.6 | Alta | 🟢 Baixo |
| P1.13 | Integration Tests - JOIN Engine | Testes end-to-end do same-DB JOIN e cross-DB merge com datasets reais, edge cases e limites de segurança | 3–5 | P1.10 | Alta | 🟡 Médio |

#### Arquivos Principais Afetados — Fase 1
- `superset/migrations/versions/xxxx_add_dataset_relationships.py`
- `superset/models/dataset_relationship.py`
- `superset/connectors/sqla/models.py`
- `superset/daos/dataset_relationship.py`
- `superset/datasets/schemas.py`
- `superset/dataset_relationships/api.py`
- `superset/config.py`
- `superset/models/helpers.py` (ExploreMixin)
- `superset/common/query_context_processor.py`
- `tests/unit_tests/` e `tests/integration_tests/`

#### Caminho Crítico — Fase 1
```
P1.1 → P1.2 → P1.3 → P1.8 ─┐
                    └→ P1.9 ─┼→ P1.10 → P1.13
              P1.7 ──────────┘
```

---

## Fase 2 — Frontend & Model View (22–35 dias)

| ID | Bloco/Task | Descrição | Est. (dias) | Deps | Prioridade | Risco |
|----|-----------|-----------|-------------|------|-----------|-------|
| P2.1 | Setup React Flow | Instalar `@xyflow/react`, configurar estrutura de diretórios, setup de tipos TypeScript | 1–2 | — | Alta | 🟢 Baixo |
| P2.2 | DatasetNode Component | Componente de nó representando dataset: nome, ícone de banco, lista de colunas com tipos, handles para conexão | 2–3 | P2.1 | Alta | 🟢 Baixo |
| P2.3 | RelationshipEdge Component | Aresta customizada mostrando tipo de relação (1:N, N:1), join type, indicador cross-DB, label interativo | 2–3 | P2.1 | Alta | 🟡 Médio |
| P2.4 | ColumnPicker Modal | Modal/drawer para selecionar colunas source→target, suporte a múltiplos pares, auto-suggest | 2–4 | P2.2 | Alta | 🟡 Médio |
| P2.5 | RelationshipSidebar | Painel lateral com detalhes do relacionamento selecionado: edição de tipo, join type, validação, delete | 2–3 | P2.3 | Média | 🟢 Baixo |
| P2.6 | RelationshipCanvas Container | Container principal integrando todos os componentes, mini-map, controles de zoom, toolbar, save/load | 3–4 | P2.2, P2.3, P2.4, P2.5 | Alta | 🟡 Médio |
| P2.7 | API Hooks & Integration | Hooks `useRelationships` e `useRelationshipGraph`, integração com API REST, cache e optimistic updates | 2–3 | P1.5, P2.1 | Alta | 🟢 Baixo |
| P2.8 | Explore View - Column Picker | Estender column picker do Explore para mostrar colunas de datasets relacionados agrupadas por dataset de origem | 3–5 | P2.7, P1.8 | Alta | 🔴 Alto |
| P2.9 | Dashboard Metadata Integration | Estender `json_metadata` do dashboard para armazenar active_relationships e drill_down_hierarchies | 2–3 | P2.7 | Média | 🟡 Médio |
| P2.10 | E2E Tests - Playwright | Testes end-to-end: criar/editar/deletar relacionamentos no canvas, verificar column picker, dashboard integration | 3–5 | P2.6, P2.8, P2.9 | Alta | 🟡 Médio |

#### Arquivos Principais Afetados — Fase 2
- `superset-frontend/src/features/datasets/relationships/` (novo módulo)
- `superset-frontend/src/explore/` (múltiplos arquivos)
- `superset-frontend/src/dashboard/` (metadata handling)
- `superset-frontend/cypress/` ou `playwright/`

#### Caminho Crítico — Fase 2
```
P2.1 → P2.2 → P2.4 ─┐
  └→ P2.3 → P2.5 ────┼→ P2.6 ─┐
P1.5 → P2.7 → P2.8 ──┤        ├→ P2.10
              └→ P2.9 ─────────┘
```

---

## Fase 3 — Cross-Filtering & Drill-Down (30–43 dias)

| ID | Bloco/Task | Descrição | Est. (dias) | Deps | Prioridade | Risco |
|----|-----------|-----------|-------------|------|-----------|-------|
| P3.1 | Cross-Filter Scope Extension | Modificar `getCrossFiltersConfiguration()` para estender scope de cross-filter baseado em relacionamentos ativos | 3–5 | P2.9 | Alta | 🔴 Alto |
| P3.2 | Filter Translation Engine | Engine que traduz valores filtrados de um dataset para colunas equivalentes em datasets relacionados | 4–5 | P3.1 | Alta | 🔴 Alto |
| P3.3 | Native Filter Propagation | Modificar dataMask reducer para propagar filtros nativos automaticamente através de relacionamentos | 3–5 | P3.2 | Alta | 🔴 Alto |
| P3.4 | Drill-Down Hierarchy Config | UI para configuração de hierarquias de drill-down entre datasets (Country→State→City) | 3–4 | P2.9 | Média | 🟡 Médio |
| P3.5 | Drill-Down Navigation Engine | Engine de navegação drill-down com filtro aplicado e suporte a breadcrumb | 4–5 | P3.4, P3.2 | Média | 🔴 Alto |
| P3.6 | Performance - Query Caching | Cache de resultados de merge cross-DB, invalidação por TTL e por mudança de dados/relationships | 3–4 | P1.9 | Alta | 🟡 Médio |
| P3.7 | Performance - Index Optimization | Sugerir/criar índices automaticamente em colunas de join, análise de plano de execução | 2–3 | P1.8 | Média | 🟢 Baixo |
| P3.8 | Unit Tests - Cross-Filter & Drill-Down | Testes para filter translation, cross-filter propagation, drill-down navigation, edge cases | 3–4 | P3.3, P3.5 | Alta | 🟢 Baixo |
| P3.9 | Integration Tests - Full Pipeline | Testes end-to-end do pipeline completo: criar relationship → usar no explore → cross-filter → drill-down | 3–5 | P3.8 | Alta | 🟡 Médio |
| P3.10 | Documentação Completa | Documentação técnica (API, arquitetura) e de usuário (como criar relationships, usar cross-filter, drill-down) | 2–3 | P3.9 | Média | 🟢 Baixo |

#### Arquivos Principais Afetados — Fase 3
- `superset-frontend/src/dashboard/util/crossFilters.ts`
- `superset-frontend/src/dataMask/reducer.ts`
- `superset-frontend/src/features/datasets/relationships/filterTranslation.ts`
- `superset-frontend/src/dashboard/components/DrillDown/`
- `superset/models/helpers.py`, `superset/utils/cache.py`
- `docs/relationships/`

#### Caminho Crítico — Fase 3
```
P2.9 → P3.1 → P3.2 → P3.3 ─┐
              └→ P3.5 ───────┼→ P3.8 → P3.9 → P3.10
P2.9 → P3.4 ─────────────────┘
```

---

## Cronograma Estimado (Gantt Simplificado)

```
Semana:  S1   S2   S3   S4   S5   S6   S7   S8   S9   S10  S11  S12  S13  S14  S15  S16  S17

=== FASE 1 ===
P1.1     ██
P1.2     ░░██
P1.3         ████
P1.4       ██
P1.5           ████████
P1.6               ██
P1.7     ██
P1.8         ████████
P1.9         ██████████
P1.10                ████
P1.11        ████
P1.12              ████
P1.13                    ████████

=== FASE 2 ===
P2.1                         ██
P2.2                         ████
P2.3                         ████
P2.4                             ████
P2.5                             ████
P2.6                                 ██████
P2.7                         ████
P2.8                             ████████
P2.9                             ████
P2.10                                    ████████

=== FASE 3 ===
P3.1                                             ████████
P3.2                                                 ██████████
P3.3                                                     ████████
P3.4                                             ██████
P3.5                                                     ██████████
P3.6                                             ██████
P3.7                                             ████
P3.8                                                         ██████
P3.9                                                             ████████
P3.10                                                                ████
```

---

## Matriz de Dependências

### Dependências Cross-Fase (Críticas)

| De | Para | Tipo | Descrição |
|----|------|------|-----------|
| P1.5 | P2.7 | Backend → Frontend | API REST precisa estar pronta para hooks de integração |
| P1.8 | P2.8 | Engine → UI | JOIN engine precisa funcionar para column picker mostrar colunas relacionadas |
| P1.8 | P3.7 | Engine → Perf | Same-DB JOIN engine precisa existir para otimização de índices |
| P1.9 | P3.6 | Engine → Perf | Cross-DB merge engine precisa existir para implementar caching |
| P2.9 | P3.1 | Dashboard → Filter | Dashboard metadata precisa suportar active_relationships |
| P2.9 | P3.4 | Dashboard → Drill-Down | Dashboard metadata precisa suportar drill_down_hierarchies |

### Dependências Intra-Fase

**Fase 1:** Fluxo principal `P1.1 → P1.2 → P1.3 → P1.8/P1.9 → P1.10 → P1.13`  
**Fase 2:** Fluxo principal `P2.1 → P2.2/P2.3 → P2.6 → P2.10`  
**Fase 3:** Fluxo principal `P3.1 → P3.2 → P3.3 → P3.8 → P3.9 → P3.10`

---

## Análise de Riscos

### 🔴 Riscos Altos

| # | Risco | Fase(s) | Tasks Afetadas | Mitigação |
|---|-------|---------|----------------|----------|
| 1 | **OOM em merge cross-DB** com datasets grandes | 1, 3 | P1.9, P1.10, P3.6 | Limite `RELATIONSHIP_MAX_MERGE_ROWS` (100K), timeout de 30s, streaming parcial |
| 2 | **JOINs same-DB degradam performance** de queries existentes | 1 | P1.8, P1.10, P3.7 | Índices automáticos em colunas de JOIN, cache, feature flags para rollback |
| 3 | **Conflitos com funcionalidades existentes** do Superset | 1, 2 | P1.8, P1.10, P2.8 | Feature flags granulares, testes de regressão, rollout gradual |
| 4 | **Filter translation incorreta** causa dados errados | 3 | P3.2, P3.3 | Testes exaustivos, validação de tipos de coluna, alertas visuais |
| 5 | **Testes insuficientes** em cenários cross-DB edge cases | 1, 3 | P1.13, P3.9 | Matriz de testes com múltiplos dialetos SQL (Postgres, MySQL, BigQuery) |

### 🟡 Riscos Médios

| # | Risco | Fase(s) | Tasks Afetadas | Mitigação |
|---|-------|---------|----------------|----------|
| 6 | **Complexidade no frontend** com muitos datasets | 2 | P2.6, P2.8 | Canvas com lazy loading, virtualização de listas, paginação |
| 7 | **Drill-down com muitos níveis** degrada UX | 3 | P3.5 | Limite `MAX_DRILL_DEPTH` (5), breadcrumb navigation |
| 8 | **Compatibilidade com Superset upstream** | 1, 2, 3 | Todas | Minimizar patches em core, preferir extensões via hooks/plugins |

### 🟢 Riscos Baixos

| # | Risco | Fase(s) | Tasks Afetadas | Mitigação |
|---|-------|---------|----------------|----------|
| 9 | **Circular relationships** causam loops | 1, 3 | P1.3, P3.2 | Validação de grafo acíclico (DAG) no DAO |
| 10 | **React Flow performance** com grafos grandes | 2 | P2.6 | Limitar nós visíveis, viewport culling |

---

## Recomendações de Execução

1. **Comece pela Fase 1 em paralelo:** P1.1→P1.2→P1.3 (caminho de dados) pode rodar em paralelo com P1.7 (config)
2. **Teste cedo:** Inicie P1.11 (testes) assim que P1.3 estiver pronto, não espere o engine completo
3. **Fase 2 pode começar parcialmente antes de Fase 1 terminar:** P2.1–P2.5 (UI pura) podem iniciar quando P1.5 estiver pronto
4. **Fase 3 é a mais arriscada:** Planeje buffer extra de 1–2 semanas para filter translation e cross-filter
5. **Feature flags são críticos:** Implemente P1.7 no início para permitir rollback seguro a qualquer momento
6. **Priorize compatibilidade upstream:** Documente todos os patches em arquivos core do Superset para facilitar rebases futuros

---

*Documento gerado em 14/05/2026 — Plano de execução para o design document `superset_relationship_design.md`*
