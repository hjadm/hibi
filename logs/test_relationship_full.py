#!/usr/bin/env python3
"""
Teste completo: criação de relationship + chart + dashboard via API Superset.
Logging avançado em cada etapa.
"""

import logging
import sys
import json
import time
import requests

# ── Config logging ──────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/root/hibi/logs/relationship_test.log", mode="w"),
    ],
)
log = logging.getLogger("relationship_test")
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.WARNING)

# ── Config ──────────────────────────────────────────────
BASE_URL = "http://localhost:8088/api/v1"
VERIFY_SSL = False
requests.packages.urllib3.disable_warnings()

class SupersetAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.headers = {}
        self.step = 0

    def step_log(self, step_name, data=None):
        self.step += 1
        log.info(f"\n{'='*70}")
        log.info(f"STEP {self.step}: {step_name}")
        log.info(f"{'='*70}")
        if data:
            log.info(f"  Input: {json.dumps(data, indent=2, default=str)[:2000]}")

    def login(self, username="admin", password="admin"):
        self.step_log("LOGIN")
        url = f"{self.base_url}/security/login"
        payload = {"username": username, "password": password, "provider": "db"}
        log.info(f"  POST {url}")
        resp = requests.post(url, json=payload, verify=VERIFY_SSL, timeout=10)
        log.info(f"  Response status: {resp.status_code}")
        log.info(f"  Response body: {resp.text[:500]}")
        if resp.status_code == 200:
            self.token = resp.json().get("access_token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            log.info(f"  Token obtido (len={len(self.token)})")
            return True
        log.error(f"  ❌ LOGIN FALHOU: {resp.text}")
        return False

    def get(self, path, desc=""):
        url = f"{self.base_url}{path}"
        log.info(f"  GET {url}  |  desc={desc}")
        resp = requests.get(url, headers=self.headers, verify=VERIFY_SSL, timeout=10)
        log.info(f"  Status: {resp.status_code}")
        try:
            data = resp.json()
            log.info(f"  Body (truncated): {json.dumps(data, default=str)[:1500]}")
            return resp.status_code, data
        except Exception as e:
            log.warning(f"  JSON parse error: {e} | Raw: {resp.text[:500]}")
            return resp.status_code, resp.text

    def post(self, path, payload, desc=""):
        url = f"{self.base_url}{path}"
        log.info(f"  POST {url}  |  desc={desc}")
        log.info(f"  Payload: {json.dumps(payload, default=str)[:2000]}")
        resp = requests.post(url, json=payload, headers=self.headers, verify=VERIFY_SSL, timeout=10)
        log.info(f"  Status: {resp.status_code}")
        try:
            data = resp.json()
            log.info(f"  Response: {json.dumps(data, default=str)[:2000]}")
            return resp.status_code, data
        except Exception as e:
            log.warning(f"  JSON parse error: {e} | Raw: {resp.text[:500]}")
            return resp.status_code, resp.text

    def put(self, path, payload, desc=""):
        url = f"{self.base_url}{path}"
        log.info(f"  PUT {url}  |  desc={desc}")
        log.info(f"  Payload: {json.dumps(payload, default=str)[:2000]}")
        resp = requests.put(url, json=payload, headers=self.headers, verify=VERIFY_SSL, timeout=10)
        log.info(f"  Status: {resp.status_code}")
        try:
            data = resp.json()
            log.info(f"  Response: {json.dumps(data, default=str)[:2000]}")
            return resp.status_code, data
        except Exception as e:
            log.warning(f"  JSON parse error: {e} | Raw: {resp.text[:500]}")
            return resp.status_code, resp.text

    def delete(self, path, desc=""):
        url = f"{self.base_url}{path}"
        log.info(f"  DELETE {url}  |  desc={desc}")
        resp = requests.delete(url, headers=self.headers, verify=VERIFY_SSL, timeout=10)
        log.info(f"  Status: {resp.status_code}")
        try:
            data = resp.json()
            log.info(f"  Response: {json.dumps(data, default=str)[:500]}")
            return resp.status_code, data
        except:
            return resp.status_code, resp.text


def main():
    log.info(f"{'#'*70}")
    log.info(f"# TESTE COMPLETO: DATASET RELATIONSHIP ENGINE")
    log.info(f"# Início: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"{'#'*70}\n")

    api = SupersetAPI(BASE_URL)

    # ───────────────────────────────────────────────────
    # STEP 1: LOGIN
    # ───────────────────────────────────────────────────
    if not api.login():
        log.critical("❌ Abortando: login falhou")
        return

    # ───────────────────────────────────────────────────
    # STEP 2: LISTAR DATASETS DISPONÍVEIS
    # ───────────────────────────────────────────────────
    api.step_log("Listar todos os datasets disponíveis")
    status, datasets = api.get("/dataset?q=(page:0,page_size:100)", desc="Lista completa de datasets")
    if status != 200:
        log.error(f"❌ Falha ao listar datasets: {datasets}")
        return

    log.info(f"\n  Datasets encontrados: {datasets.get('count', '?')}")
    for ds in datasets.get("result", []):
        log.info(f"    ID={ds['id']:>4} | {ds.get('table_name','?'):30s} | "
                 f"db={ds.get('database',{}).get('database_name','?'):15s} | "
                 f"schema={ds.get('schema','?')}")

    # ───────────────────────────────────────────────────
    # STEP 3: VERIFICAR O FEATURE FLAG
    # ───────────────────────────────────────────────────
    api.step_log("Verificar feature flag DATASET_RELATIONSHIPS")
    try:
        from superset import is_feature_enabled
        enabled = is_feature_enabled("DATASET_RELATIONSHIPS")
        log.info(f"  DATASET_RELATIONSHIPS = {enabled}")
        if not enabled:
            log.warning("  ⚠️ Feature flag desligada! Relationships API pode não funcionar")
    except Exception as e:
        log.warning(f"  Não foi possível verificar feature flag (pode ser OK): {e}")

    # ───────────────────────────────────────────────────
    # STEP 4: VERIFICAR SE RELATIONSHIP API ESTÁ REGISTRADA
    # ───────────────────────────────────────────────────
    api.step_log("Verificar se endpoint /dataset_relationship/ existe")
    status_rels, rel_data = api.get("/dataset_relationship/", desc="List relationships")
    if status_rels == 404:
        log.error("❌ Endpoint /dataset_relationship/ não encontrado! API não registrada.")
        log.error("   Verificar if is_feature_enabled('DATASET_RELATIONSHIPS') no initialization")
        return
    elif status_rels >= 200 and status_rels < 300:
        log.info(f"  ✅ Relationship API ativa. {rel_data.get('count', '?')} relationships existentes")
    else:
        log.warning(f"  Status inesperado: {status_rels}")

    # ───────────────────────────────────────────────────
    # STEP 5: ESCOLHER 2 DATASETS PARA CRIAR RELATIONSHIP
    # ───────────────────────────────────────────────────
    api.step_log("Selecionar datasets de exemplo para criar relationship")
    ds_list = datasets.get("result", [])

    # Filtra datasets físicos (não virtuais) com colunas
    # A lista padrão não inclui colunas, precisamos buscar cada dataset individualmente
    valid_ds = []
    for ds in ds_list:
        # Buscar detalhes do dataset para pegar as colunas
        ds_id = ds["id"]
        _, ds_detail = api.get(f"/dataset/{ds_id}", desc=f"Detalhes dataset {ds_id}")
        if isinstance(ds_detail, dict):
            cols = ds_detail.get("result", {}).get("columns", [])
            if len(cols) >= 2:
                ds["columns"] = cols
                valid_ds.append(ds)
        log.info(f"    Dataset {ds_id}: {ds.get('table_name','?')} - colunas={len(ds_detail.get('result',{}).get('columns',[])) if isinstance(ds_detail, dict) else '?'}")

    log.info(f"  Datasets com 2+ colunas: {len(valid_ds)}")

    # Usar os primeiros dois datasets válidos
    if len(valid_ds) < 2:
        log.error(f"❌ Precisamos de pelo menos 2 datasets com colunas. Temos {len(valid_ds)}")
        return

    ds_source = valid_ds[0]
    ds_target = valid_ds[1]
    log.info(f"\n  Source dataset: ID={ds_source['id']} {ds_source.get('table_name','?')}")
    log.info(f"  Target dataset: ID={ds_target['id']} {ds_target.get('table_name','?')}")

    source_cols = [(c.get("column_name",""), c.get("type","")) for c in ds_source.get("columns",[])]
    target_cols = [(c.get("column_name",""), c.get("type","")) for c in ds_target.get("columns",[])]
    log.info(f"\n  Colunas source ({len(source_cols)}):")
    for c,t in source_cols[:10]:
        log.info(f"    - {c} ({t})")
    log.info(f"\n  Colunas target ({len(target_cols)}):")
    for c,t in target_cols[:10]:
        log.info(f"    - {c} ({t})")

    # Procurar colunas com mesmo nome pra fazer join
    source_names = {c[0] for c in source_cols}
    target_names = {c[0] for c in target_cols}
    common_cols = source_names & target_names
    log.info(f"\n  Colunas comuns: {common_cols}")

    if not common_cols:
        # Tentar encontrar colunas de tipo compatível
        log.warning("  ⚠️ Nenhuma coluna com nome igual. Usaremos a primeira do source e primeira do target")
        src_col = source_cols[0][0]
        tgt_col = target_cols[0][0]
    else:
        src_col = list(common_cols)[0]
        tgt_col = src_col

    log.info(f"  Coluna join: {src_col} = {tgt_col}")

    # ───────────────────────────────────────────────────
    # STEP 6: CRIAR RELATIONSHIP
    # ───────────────────────────────────────────────────
    api.step_log("Criar relationship entre os datasets via API")

    relationship_payload = {
        "source_dataset_id": ds_source["id"],
        "target_dataset_id": ds_target["id"],
        "relationship_type": "many_to_one",
        "join_type": "LEFT",
        "name": f"test: {ds_source.get('table_name','?')} → {ds_target.get('table_name','?')}",
        "description": "Relationship criada via teste automatizado",
        "columns": [
            {
                "source_column_name": src_col,
                "target_column_name": tgt_col,
                "operator": "=",
                "ordinal": 0,
            }
        ],
    }

    status_create, create_resp = api.post(
        "/dataset_relationship/",
        relationship_payload,
        desc="Create relationship"
    )

    if status_create == 201 or status_create == 200:
        rel_id = create_resp.get("id")
        log.info(f"  ✅ Relationship criada com ID={rel_id}")
    elif status_create == 422:
        log.warning("  ⚠️ Relationship 422 — provavelmente já existe. Buscando existente...")
        # Tentar listar de novo e pegar o ID
        _, rels = api.get("/dataset_relationship/", desc="Re-list relationships")
        for r in rels.get("result", []):
            if r["source_dataset_id"] == ds_source["id"] and r["target_dataset_id"] == ds_target["id"]:
                rel_id = r["id"]
                log.info(f"  Usando relationship existente ID={rel_id}")
                break
        else:
            log.error("  ❌ Não foi possível criar nem encontrar a relationship")
            return
        api.step_log("Continuando com relationship existente (processo normal, erro esperado se já existia)")
    else:
        log.error(f"  ❌ Falha ao criar relationship: {create_resp}")
        return

    # ───────────────────────────────────────────────────
    # STEP 7: BUSCAR DETAILHES DA RELATIONSHIP
    # ───────────────────────────────────────────────────
    api.step_log(f"Buscar detalhes da relationship ID={rel_id}")
    status_get, rel_detail = api.get(f"/dataset_relationship/{rel_id}", desc="Get relationship detail")
    if status_get == 200:
        log.info(f"  ✅ Relationship detail obtido")
        log.info(f"  uuid: {rel_detail.get('result',{}).get('uuid','?')}")
        log.info(f"  columns: {json.dumps(rel_detail.get('result',{}).get('columns',[]), default=str)}")
    else:
        log.warning(f"  ⚠️ Não foi possível obter detalhes: {rel_detail}")

    # ───────────────────────────────────────────────────
    # STEP 8: TENTAR USAR O QUERY INJECTOR (TESTE DIRETO)
    # ───────────────────────────────────────────────────
    api.step_log("Testar injector de JOIN na query")
    try:
        log.info("  Tentando importar e usar RelationshipQueryInjector...")
        # Isso precisa rodar dentro do contexto do Flask
        import subprocess
        test_cmd = f"""
cd /root/hibi && python3 -c "
import sys, json, logging
logging.basicConfig(level=logging.INFO)

# Setup Flask context
from superset import app, db
from superset.models.dataset_relationships import DatasetRelationship
from superset.common.relationship_query_injector import RelationshipQueryInjector
from superset.connectors.sqla.models import SqlaTable
import sqlalchemy as sa

with app.app_context():
    # 1. Buscar a relationship
    rel = db.session.get(DatasetRelationship, {rel_id})
    if rel is None:
        print('RELATIONSHIP_NOT_FOUND')
        sys.exit(1)
    
    print(f'Relationship found: id={{rel.id}} src={{rel.source_dataset_id}} -> tgt={{rel.target_dataset_id}}')
    print(f'  type={{rel.relationship_type}} join={{rel.join_type}} cross_db={{rel.is_cross_database}}')
    print(f'  columns: {{\", \".join(f\"{{c.source_column_name}}={{c.operator}}{{c.target_column_name}}\" for c in rel.columns)}}')
    
    # 2. Verificar os datasets
    src_tbl = db.session.get(SqlaTable, rel.source_dataset_id)
    tgt_tbl = db.session.get(SqlaTable, rel.target_dataset_id)
    
    if src_tbl is None or tgt_tbl is None:
        print(f'DATASET_LOAD_ERROR src={{src_tbl}} tgt={{tgt_tbl}}')
        sys.exit(1)
    
    print(f'Source dataset: {{src_tbl.table_name}} (db_id={{src_tbl.database_id}})')
    print(f'Target dataset: {{tgt_tbl.table_name}} (db_id={{tgt_tbl.database_id}})')
    print(f'Same DB: {{src_tbl.database_id == tgt_tbl.database_id}}')
    
    # 3. Build SQLAlchemy table references
    src_schema = src_tbl.schema or None
    tgt_schema = tgt_tbl.schema or None
    
    src_table = sa.table(src_tbl.table_name, schema=src_schema)
    tgt_table = sa.table(tgt_tbl.table_name, schema=tgt_schema)
    
    # 4. Create a simple SELECT * FROM source
    query = sa.select(sa.text('*')).select_from(src_table)
    
    # 5. Try to inject JOIN
    injector = RelationshipQueryInjector()
    relationships = [rel]
    
    try:
        new_query = injector.inject_joins(
            sqla_query=query,
            source_table=src_table,
            relationships=relationships,
        )
        compiled = str(new_query.compile(compile_kwargs={{'literal_binds': True}}))
        print(f'Injected SQL: {{compiled[:2000]}}')
    except Exception as e:
        print(f'JOIN_INJECTION_ERROR: {{e}}')
        import traceback
        traceback.print_exc()
"
" 2>&1
"""
        log.info(f"  Executando comando de teste...")
        result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=30)
        log.info(f"  stdout:\n{result.stdout}")
        if result.stderr:
            log.warning(f"  stderr:\n{result.stderr[:2000]}")
        
        if "JOIN_INJECTION_ERROR" in result.stdout:
            log.error("  ❌ JOIN injection falhou!")
        elif "Injected SQL" in result.stdout:
            log.info("  ✅ JOIN injection funcionou!")
            # Extrair SQL
            for line in result.stdout.split('\n'):
                if 'Injected SQL' in line or 'SELECT' in line.upper():
                    log.info(f"  SQL: {line}")
        elif "RELATIONSHIP_NOT_FOUND" in result.stdout:
            log.error("  ❌ Relationship não encontrada no banco!")
        else:
            log.warning("  ⚠️ Resultado inesperado - ver logs")
            
    except Exception as e:
        log.error(f"  ❌ Erro ao executar teste do injector: {e}")
        import traceback
        log.error(traceback.format_exc())

    # ───────────────────────────────────────────────────
    # STEP 9: CRIAR UM CHART QUE USA A RELATIONSHIP
    # ───────────────────────────────────────────────────
    api.step_log(f"Criar chart (explore) usando datasets com relationship")

    # Vamos criar um chart simples no dataset SOURCE
    log.info("  Criando chart no dataset source...")
    
    chart_payload = {
        "datasource_id": ds_source["id"],
        "datasource_type": "table",
        "slice_name": f"Test Relationship: {ds_source.get('table_name','?')} -> {ds_target.get('table_name','?')}",
        "viz_type": "table",
        "params": json.dumps({
            "datasource": f"{ds_source['id']}__table",
            "viz_type": "table",
            "metrics": [],
            "groupby": [source_cols[0][0]] if source_cols else [],
            "adhoc_filters": [],
            "order_desc": True,
            "page_length": 10,
            "include_search": False,
            "table_timestamp_format": "smart",
            "show_cell_bars": True,
            "align_pn": False,
            "color_pn": True,
            "allow_reorder": True,
            "timeseries_limit_metric": None,
            "column_config": {},
            "url_params": {},
            "customize_label": {},
        }),
        "query_context": json.dumps({
            "datasource": {"id": ds_source["id"], "type": "table"},
            "force": False,
            "queries": [
                {
                    "columns": [source_cols[0][0]] if source_cols else [],
                    "metrics": [],
                    "orderby": [],
                    "row_limit": 10,
                }
            ],
            "result_format": "json",
            "result_type": "full",
        }),
    }

    status_chart, chart_resp = api.post(
        "/chart/",
        chart_payload,
        desc="Create chart"
    )
    
    if status_chart in (200, 201):
        chart_id = chart_resp.get("id")
        log.info(f"  ✅ Chart criado: ID={chart_id}")
    else:
        log.warning(f"  ⚠️ Falha ao criar chart: {chart_resp}")
        log.warning("  Tentando criar chart mais simples...")
        
        # Tenta sem query_context
        chart_payload.pop("query_context", None)
        status_chart, chart_resp = api.post(
            "/chart/",
            chart_payload,
            desc="Create chart (simplificado)"
        )
        if status_chart in (200, 201):
            chart_id = chart_resp.get("id")
            log.info(f"  ✅ Chart criado (attempt 2): ID={chart_id}")
        else:
            log.error(f"  ❌ Falha ao criar chart: {chart_resp}")
            # Continuamos mesmo sem chart para testar o dashboard
            chart_id = None

    # ───────────────────────────────────────────────────
    # STEP 10: CRIAR UM DASHBOARD
    # ───────────────────────────────────────────────────
    api.step_log("Criar um dashboard")

    if chart_id:
        dashboard_payload = {
            "dashboard_title": f"Test Dashboard - Relationships",
            "slug": f"test-relationships-{int(time.time())}",
            "position_json": json.dumps({
                "DASHBOARD_VERSION_KEY": "v2",
                "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
                "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": ["CHART-1"]},
                "CHART-1": {
                    "type": "CHART",
                    "id": "CHART-1",
                    "children": [],
                    "meta": {
                        "chartId": chart_id,
                        "width": 6,
                        "height": 20,
                    },
                },
            }),
            "published": True,
            "certified_by": "Teste",
            "certification_details": "Dashboard de teste para relationships",
        }
    else:
        dashboard_payload = {
            "dashboard_title": f"Test Dashboard - Relationships (sem chart)",
            "slug": f"test-relationships-{int(time.time())}",
            "published": True,
        }

    status_dash, dash_resp = api.post(
        "/dashboard/",
        dashboard_payload,
        desc="Create dashboard"
    )

    if status_dash in (200, 201):
        dash_id = dash_resp.get("id")
        log.info(f"  ✅ Dashboard criado: ID={dash_id}")
    else:
        log.warning(f"  ⚠️ Falha ao criar dashboard: {dash_resp}")
        dash_id = None

    # ───────────────────────────────────────────────────
    # STEP 11: TESTAR QUERY REAL USANDO A RELATIONSHIP
    # ───────────────────────────────────────────────────
    api.step_log("Testar query com JOIN (via SQL Lab)")
    
    # Fazer uma query SQL direta testando a relação
    # Mas primeiro tenta ver se o explore/lab interpreta o JOIN
    try:
        import subprocess
        test_sql = f"""
cd /root/hibi && python3 -c "
import sys, json, logging
logging.basicConfig(level=logging.INFO)

from superset import app, db
from superset.models.dataset_relationships import DatasetRelationship
from superset.common.relationship_query_injector import RelationshipQueryInjector
from superset.connectors.sqla.models import SqlaTable
from superset.sql_lab import execute_sql
import sqlalchemy as sa

with app.app_context():
    rel = db.session.get(DatasetRelationship, {rel_id})
    if rel is None:
        print('REL_NOT_FOUND')
        sys.exit(1)
    
    src_tbl = db.session.get(SqlaTable, rel.source_dataset_id)
    tgt_tbl = db.session.get(SqlaTable, rel.target_dataset_id)
    
    # 1. Build the query with JOIN injection
    src_schema = src_tbl.schema or None
    tgt_schema = tgt_tbl.schema or None
    
    src_table = sa.table(src_tbl.table_name, schema=src_schema)
    tgt_table = sa.table(tgt_tbl.table_name, schema=tgt_schema)
    
    # Get column names for SELECT
    src_cols = [c.column_name for c in src_tbl.columns]
    tgt_cols = [c.column_name for c in tgt_tbl.columns]
    
    # Select some columns from both
    selected_cols = [sa.column(c, _selectable=src_table) for c in src_cols[:3]]
    selected_cols += [sa.column(c, _selectable=tgt_table) for c in tgt_cols[:3]]
    
    query = sa.select(*selected_cols).select_from(src_table)
    
    injector = RelationshipQueryInjector()
    relationships = [rel]
    
    try:
        new_query = injector.inject_joins(query, src_table, relationships)
        compiled = str(new_query.compile(compile_kwargs={{'literal_binds': True}}))
        print(f'=== COMPILED SQL ===')
        print(compiled)
        
        # 2. Try to get the database and execute
        database = src_tbl.database
        if database:
            # Use db_engine_spec to run the query
            engine = database.get_sqla_engine()
            with engine.connect() as conn:
                result = conn.execute(new_query)
                rows = result.fetchmany(5)
                print(f'=== QUERY RESULT ({len(rows)} rows) ===')
                for row in rows:
                    print(dict(row._mapping))
    except Exception as e:
        print(f'ERROR: {{e}}')
        import traceback
        traceback.print_exc()
"
" 2>&1
"""
        log.info(f"  Executando query de teste com JOIN...")
        result = subprocess.run(test_sql, shell=True, capture_output=True, text=True, timeout=30)
        log.info(f"  stdout:\n{result.stdout[:3000]}")
        if result.stderr:
            log.warning(f"  stderr:\n{result.stderr[:1000]}")
        
        if "=== QUERY RESULT" in result.stdout:
            log.info("  ✅ Query com JOIN executou com sucesso!")
        elif "ERROR" in result.stdout:
            log.error(f"  ❌ Query falhou: {result.stdout[:500]}")
        else:
            log.info("  Resultado misto - ver logs completos")
            
    except Exception as e:
        log.error(f"  ❌ Erro na query: {e}")

    # ───────────────────────────────────────────────────
    # STEP 12: CLEANUP (opcional)
    # ───────────────────────────────────────────────────
    api.step_log("Cleanup - deletar relationship (opcional, comentado)")
    log.info("  Skiping cleanup para análise futura")

    log.info(f"\n{'#'*70}")
    log.info(f"# TESTE CONCLUÍDO")
    log.info(f"# Fim: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"# Log completo em: /root/hibi/logs/relationship_test.log")
    log.info(f"{'#'*70}")


if __name__ == "__main__":
    main()
