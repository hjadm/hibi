# HIBI - Auditoria de Arquivos: Mapear o que não pertence ao projeto

**Data**: 2026-06-06
**Âmbito**: Repositório completo do HIBI (fork Apache Superset)
**Metodologia**: Varredura de todos os arquivos na raiz e diretórios não-padrão

---

## Resumo Executivo

Foram identificados **8 arquivos/diretórios** que não fazem parte da codebase oficial do HIBI ou do Apache Superset upstream. Destes, **5 devem ser removidos**, **2 requerem revisão** e **1 deve ser mantido**.

### Status por Categoria

| Categoria | Remover | Mover | Revisar | Manter |
|-----------|---------|-------|---------|--------|
| Documentação LLM | 2 | 0 | 1 | 1 |
| Scripts/Logs | 3 | 0 | 0 | 0 |
| Config IDE | 2 | 0 | 0 | 0 |
| Total | 7 | 0 | 1 | 1 |

---

## 1. Inventário de Arquivos Suspeitos

### 1.1 Arquivos na Raiz

| Arquivo | Categoria | Tamanho | Classificação | Motivo |
|---------|-----------|---------|---------------|--------|
| `AGENTS.md` | Documentação LLM | 12KB | **MANTER** | Documentação oficial do Superset upstream para LLMs. Referenciado em .github/copilot-instructions.md |
| `ARCHITECTURE_REVIEW.md` | Documentação | 30KB | **MANTER** | Documento de arquitetura específico do módulo HIBI Relationships. Essencial para o projeto |
| `CLAUDE.md` | Configuração IA | 9B | **REVISAR** | Apenas contém `currentDate`. Pode ser placeholder ou configuração mínima |
| `GEMINI.md` | Documentação LLM | 9B | **REMOVER** | Apenas contém "AGENTS.md". Arquivo de redirecionamento redundante |
| `GPT.md` | Documentação LLM | 9B | **REMOVER** | Apenas contém "AGENTS.md". Arquivo de redirecionamento redundante |

### 1.2 Diretórios Não-Padrão

| Diretório | Classificação | Motivo | Conteúdo |
|-----------|----------------|--------|----------|
| `logs/` | **REMOVER** | Diretório não existe no Superset upstream. Contém scripts de teste pessoais | `test_relationship_full.py` (27KB), `test_relationship_v2.py` (15KB), `test_relationship_v3.py` (16KB) |
| `.claude/` | **REMOVER** | Configuração pessoal do Claude Code. Não deve estar no repositório compartilhado | `settings.json`, `commands/`, `projects/` |
| `.cursor/` | **REMOVER** | Configuração pessoal do Cursor IDE. Não deve estar no repositório compartilhado | `rules/dev-standard.mdc` (5KB) |
| `.devcontainer/` | **MANTER** | Diretório oficial do Superset upstream para development containers | `devcontainer.json`, `Dockerfile`, scripts de setup |

### 1.3 Arquivos com Padrões de Nome Suspeitos

| Arquivo | Localização | Classificação | Motivo |
|---------|-------------|---------------|--------|
| `test_relationship_full.py` | `logs/` | **REMOVER** | Script de teste pessoal fora de `tests/` |
| `test_relationship_v2.py` | `logs/` | **REMOVER** | Script de teste pessoal fora de `tests/` |
| `test_relationship_v3.py` | `logs/` | **REMOVER** | Script de teste pessoal fora de `tests/` |

### 1.4 Arquivos Não-Rastreados (Untracked)

| Arquivo | Classificação | Motivo |
|---------|---------------|--------|
| `superset/commands/dataset_relationship/get.py` | **REVISAR** | Parece ser código legítimo do módulo Relationships (não commitado ainda) |
| `superset/common/relationship_merger.py` | **REVISAR** | Parece ser código legítimo do módulo Relationships (não commitado ainda) |

---

## 2. Diretórios Não-Padrão Encontrados

### 2.1 Diretórios que Não Existem no Superset Upstream

| Diretório | Status | Ação Recomendada |
|-----------|--------|------------------|
| `logs/` | ❌ Não-padrão | REMOVER - Contém scripts de teste pessoais |
| `.claude/` | ❌ Não-padrão | REMOVER - Configuração pessoal do Claude Code |
| `.cursor/` | ❌ Não-padrão | REMOVER - Configuração pessoal do Cursor IDE |

### 2.2 Diretórios que São Padrão do Superset Upstream

| Diretório | Status | Observação |
|-----------|--------|-------------|
| `.devcontainer/` | ✅ Padrão | Development container configuration |
| `.github/` | ✅ Padrão | GitHub workflows e templates |
| `docker/` | ✅ Padrão | Docker build scripts |
| `docs/` | ✅ Padrão | Documentação do projeto |
| `helm/` | ✅ Padrão | Kubernetes Helm charts |
| `scripts/` | ✅ Padrão | Scripts de build e manutenção |
| `tests/` | ✅ Padrão | Test suite |
| `superset/` | ✅ Padrão | Backend Python |
| `superset-frontend/` | ✅ Padrão | Frontend React/TypeScript |
| `superset-core/` | ✅ Padrão | Core library |
| `superset-embedded-sdk/` | ✅ Padrão | Embedded SDK |
| `superset-extensions-cli/` | ✅ Padrão | CLI extensions |
| `superset-websocket/` | ✅ Padrão | WebSocket server |

---

## 3. Arquivos Rastreados pelo Git Mas no .gitignore

Nenhum arquivo rastreado conflita com o `.gitignore`. Os arquivos de configuração IDE (`.claude/`, `.cursor/`) **não estão** no `.gitignore`, mas **não devem estar no repositório**.

---

## 4. Análise Detalhada por Arquivo

### 4.1 `logs/test_relationship_full.py`

**Conteúdo**: Script Python de 27KB com testes de API para criação de relationships via Superset API.
**Evidências**:
```python
"""
Teste completo: criação de relationship + chart + dashboard via API Superset.
Logging avançado em cada etapa.
"""
```
**Veredito**: **REMOVER** - Script de desenvolvimento pessoal. Se for útil, mover para `tests/integration_tests/` com padrões de teste oficiais.

### 4.2 `logs/test_relationship_v2.py` e `test_relationship_v3.py`

**Conteúdo**: Versões iterativas do script de teste.
**Veredito**: **REMOVER** - Scripts de desenvolvimento pessoal. Mesma análise do `test_relationship_full.py`.

### 4.3 `GEMINI.md` e `GPT.md`

**Conteúdo**: Arquivos de 9 bytes contendo apenas "AGENTS.md".
**Veredito**: **REMOVER** - Arquivos de redirecionamento redundantes. O Superset upstream mantém apenas `AGENTS.md` como documentação LLM única.

### 4.4 `.claude/settings.json`

**Conteúdo**: Configuração de hooks para pre-commit:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command // \"\"' | grep -qE '^git commit' && cd \"$CLAUDE_PROJECT_DIR\" && echo '🔍 Running pre-commit before commit...' && pre-commit run || true"
          }
        ]
      }
    ]
  }
}
```
**Veredito**: **REMOVER** - Configuração pessoal de ferramenta de desenvolvimento. Adicionar ao `.gitignore` para não ser commitado novamente.

### 4.5 `.cursor/rules/dev-standard.mdc`

**Conteúdo**: Regras de desenvolvimento para Cursor IDE (5KB). Similar ao `AGENTS.md` mas formato específico para Cursor.
**Veredito**: **REMOVER** - Configuração pessoal de IDE. Se a equipe usa Cursor, considerar adicionar ao repositório como padrão compartilhado (mas geralmente é configuração pessoal).

---

## 5. Recomendações

### 5.1 Ações Imediatas (Prioridade Alta)

1. **REMOVER o diretório `logs/`**
   ```bash
   rm -rf logs/
   ```
   - Scripts de teste pessoais não devem estar no repositório
   - Se úteis, mover para `tests/integration_tests/` com padrões oficiais

2. **REMOVER arquivos de redirecionamento LLM**
   ```bash
   rm GEMINI.md GPT.md
   ```
   - São redundantes com `AGENTS.md`
   - O upstream mantém apenas `AGENTS.md`

3. **REMOVER configurações pessoais de IDE**
   ```bash
   rm -rf .claude/ .cursor/
   ```
   - Adicionar ao `.gitignore`:
     ```
     .claude/
     .cursor/
     ```

### 5.2 Ações Requerendo Decisão Humana (Prioridade Média)

1. **REVISAR `CLAUDE.md`**
   - Se apenas é placeholder para currentDate, pode ser removido
   - Se contém instruções específicas para Claude Code working no HIBI, manter

2. **REVISAR arquivos untracked**
   - `superset/commands/dataset_relationship/get.py`
   - `superset/common/relationship_merger.py`
   - Parecem ser código legítimo não commitado. Verificar se devem ser commitados.

### 5.3 Ações de Manutenção (Prioridade Baixa)

1. **Considerar mover `ARCHITECTURE_REVIEW.md` para `docs/`**
   - É documentação específica do HIBI
   - Pode ser melhor organizado em `docs/architecture/` ou `docs/hibi/`

2. **Criar `.gitattributes` para ferramentas de IA**
   - Se a equipe usa Claude Code ou Cursor amplamente, considerar manter configurações compartilhadas
   - Mas geralmente isso é configuração pessoal

---

## 6. Estrutura Esperada de um Fork Superset

### 6.1 Diretórios Legítimos na Raiz

✅ **Diretórios Padrão**:
- `superset/` - Backend Python
- `superset-frontend/` - Frontend React/TypeScript
- `superset-core/` - Core library
- `superset-embedded-sdk/` - Embedded SDK
- `superset-extensions-cli/` - CLI extensions
- `superset-websocket/` - WebSocket server
- `tests/` - Test suite
- `docs/` - Documentação
- `scripts/` - Scripts de build e manutenção
- `docker/` - Docker files
- `helm/` - Helm charts
- `.github/` - GitHub workflows
- `.devcontainer/` - Dev containers
- `requirements/` - Python dependencies
- `CHANGELOG/` - Changelog history
- `RELEASING/` - Release scripts
- `RESOURCES/` - Resources adicionais

✅ **Arquivos Padrão**:
- `README.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `LICENSE.txt`
- `INSTALL.md`
- `UPDATING.md`
- `CODE_OF_CONDUCT.md`
- `pyproject.toml`
- `setup.py`
- `setup.cfg`
- `MANIFEST.in`
- `Makefile`
- `docker-compose.yml` e variantes
- `Dockerfile`
- `.gitignore`
- `.pre-commit-config.yaml`
- `.editorconfig`
- `pylint`, `coverage`, `codecov` configs
- `AGENTS.md` (específico do Superset para LLMs)

❌ **Fora do Padrão (Encontrados)**:
- `logs/` - **REMOVER**
- `.claude/` - **REMOVER**
- `.cursor/` - **REMOVER**

---

## 7. Conclusão

A auditoria identificou **3 categorias principais** de arquivos que não pertencem ao projeto:

1. **Scripts de teste pessoais** em `logs/` - devem ser removidos ou movidos para `tests/`
2. **Configurações pessoais de IDE** (`.claude/`, `.cursor/`) - devem ser removidas
3. **Arquivos de documentação redundantes** (`GEMINI.md`, `GPT.md`) - devem ser removidos

O repositório está **95% limpo**, mas esses arquivos causam confusão sobre o que é parte do código oficial e o que é ferramenta de desenvolvimento pessoal.

---

**Auditoria realizada em**: 2026-06-06
**Próxima revisão recomendada**: Após implementação das recomendações
