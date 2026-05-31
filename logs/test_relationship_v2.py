#!/usr/bin/env python3
"""
Teste completo: criação de relationship + chart + dashboard via API Superset.
Logging avançado em cada etapa. Com CSRF fix.
"""
import logging, sys, json, time, requests, base64, urllib.parse, subprocess

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler("/root/hibi/logs/relationship_test.log", mode="w")],
)
log = logging.getLogger("relationship_test")
requests.packages.urllib3.disable_warnings()

BASE_URL = "http://localhost:8088/api/v1"

class SupersetAPI:
    def __init__(self):
        self.token = None
        self.csrf = None
        self.cookies = {}
        self.session = requests.Session()
        self.step = 0

    def step_log(self, name, data=None):
        self.step += 1
        log.info(f"\n{'='*70}")
        log.info(f"STEP {self.step}: {name}")
        log.info(f"{'='*70}")
        if data:
            log.info(f"  Data: {json.dumps(data, indent=2, default=str)[:2000]}")

    def login(self):
        self.step_log("LOGIN")
        resp = self.session.post(f"{BASE_URL}/security/login",
            json={"username": "admin", "password": "admin", "provider": "db"}, timeout=10)
        log.info(f"  Status: {resp.status_code}")
        if resp.status_code == 200:
            self.token = resp.json()["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            log.info(f"  Token OK (len={len(self.token)})")
            self._refresh_csrf()
            return True
        log.error(f"  LOGIN FAILED: {resp.text}")
        return False

    def _refresh_csrf(self):
        resp = self.session.get(f"{BASE_URL}/security/csrf_token/", timeout=10)
        if resp.status_code == 200:
            self.csrf = resp.json().get("result", "")
            self.session.headers.update({
                "X-CSRFToken": self.csrf,
                "Referer": "http://localhost:8088",
            })

    def get(self, path, desc=""):
        log.info(f"  GET {BASE_URL}{path}  [{desc}]")
        resp = self.session.get(f"{BASE_URL}{path}", timeout=15)
        log.info(f"  Status: {resp.status_code}")
        try:
            data = resp.json()
            log.info(f"  Body: {json.dumps(data, default=str)[:1500]}")
            return resp.status_code, data
        except Exception as e:
            log.warning(f"  JSON err: {e} | Raw: {resp.text[:300]}")
            return resp.status_code, resp.text

    def post(self, path, payload, desc=""):
        self._refresh_csrf()
        log.info(f"  POST {BASE_URL}{path}  [{desc}]")
        log.info(f"  Payload: {json.dumps(payload, default=str)[:2000]}")
        resp = self.session.post(f"{BASE_URL}{path}", json=payload, timeout=15)
        log.info(f"  Status: {resp.status_code}")
        try:
            data = resp.json()
            log.info(f"  Response: {json.dumps(data, default=str)[:2000]}")
            return resp.status_code, data
        except Exception as e:
            log.warning(f"  JSON err: {e} | Raw: {resp.text[:500]}")
            return resp.status_code, resp.text


def run_python_in_container(code):
    """Run Python code inside the Docker container and return output."""
    safe_code = code.replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
    cmd = f"docker exec hibi-superset-1 python3 -c \"{safe_code}\""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        out = result.stdout.strip()
        err = result.stderr.strip()
        return out, err
    except Exception as e:
        return None, str(e)


def exec_injector_test(rel_id, src_id, tgt_id):
    code = r'''
import sys, json, logging
logging.basicConfig(level=logging.INFO)
from superset import app, db
from superset.models.dataset_relationships import DatasetRelationship
from superset.common.relationship_query_injector import RelationshipQueryInjector
from superset.connectors.sqla.models import SqlaTable
import sqlalchemy as sa

with app.app_context():
    rel = db.session.get(DatasetRelationship, ''' + str(rel_id) + r''')
    src_tbl = db.session.get(SqlaTable, ''' + str(src_id) + r''')
    tgt_tbl = db.session.get(SqlaTable, ''' + str(tgt_id) + r''')
    if not rel or not src_tbl or not tgt_tbl:
        print(f'MISSING: rel={rel} src={src_tbl} tgt={tgt_tbl}')
        sys.exit(1)
    
    print(f'Loaded: {rel.name or "unnamed"}')
    print(f'Type: {rel.relationship_type} / Join: {rel.join_type}')
    print(f'Cross-DB: {rel.is_cross_database}')
    print(f'Source: {src_tbl.table_name} (db={src_tbl.database_id})')
    print(f'Target: {tgt_tbl.table_name} (db={tgt_tbl.database_id})')
    
    for c in rel.columns:
        print(f'  Col: {c.source_column_name} {c.operator} {c.target_column_name}')
    
    src_table = sa.table(src_tbl.table_name, schema=src_tbl.schema or None)
    tgt_table = sa.table(tgt_tbl.table_name, schema=tgt_tbl.schema or None)
    
    query = sa.select(sa.text('*')).select_from(src_table)
    injector = RelationshipQueryInjector()
    new_query = injector.inject_joins(query, src_table, [rel])
    compiled = str(new_query.compile(compile_kwargs={'literal_binds': True}))
    print('=== INJECTED SQL ===')
    print(compiled)
    print('=== END ===')
'''
    out, err = run_python_in_container(code)
    if err:
        log.warning(f"  stderr: {err[:500]}")
    if out:
        for line in out.split('\n'):
            log.info(f"  | {line}")
    return out or err


def exec_real_query(rel_id):
    code = r'''
import sys, json, logging
logging.basicConfig(level=logging.INFO)
from superset import app, db
from superset.models.dataset_relationships import DatasetRelationship
from superset.common.relationship_query_injector import RelationshipQueryInjector
from superset.connectors.sqla.models import SqlaTable
import sqlalchemy as sa

with app.app_context():
    rel = db.session.get(DatasetRelationship, ''' + str(rel_id) + r''')
    src_tbl = db.session.get(SqlaTable, rel.source_dataset_id)
    tgt_tbl = db.session.get(SqlaTable, rel.target_dataset_id)
    
    src_table = sa.table(src_tbl.table_name, schema=src_tbl.schema or None)
    
    src_cols = [c.column_name for c in src_tbl.columns][:5]
    tgt_cols = [c.column_name for c in tgt_tbl.columns][:3]
    
    selected = [sa.column(c, _selectable=src_table) for c in src_cols]
    selected += [sa.column(c, _selectable=sa.table(tgt_tbl.table_name, schema=tgt_tbl.schema or None)) for c in tgt_cols]
    
    query = sa.select(*selected).select_from(src_table)
    injector = RelationshipQueryInjector()
    new_query = injector.inject_joins(query, src_table, [rel])
    
    compiled = str(new_query.compile(compile_kwargs={'literal_binds': True}))
    print('=== COMPILED SQL ===')
    print(compiled)
    
    database = src_tbl.database
    engine = database.get_sqla_engine()
    with engine.connect() as conn:
        result = conn.execute(new_query)
        rows = result.fetchmany(5)
        print(f'=== RESULT ({len(rows)} rows) ===')
        for row in rows:
            print(dict(row._mapping))
    print('=== END ===')
'''
    out, err = run_python_in_container(code)
    if err:
        log.warning(f"  stderr: {err[:500]}")
    if out:
        for line in out.split('\n'):
            log.info(f"  | {line}")
    return out or err


def main():
    log.info(f"{'#'*70}\n# TESTE COMPLETO: DATASET RELATIONSHIP ENGINE (v2)\n# {time.strftime('%Y-%m-%d %H:%M:%S')}\n{'#'*70}")
    api = SupersetAPI()
    if not api.login():
        return

    # ─── STEP 2: LIST DATASETS ──────────────────────────
    api.step_log("Listar datasets")
    status, datasets = api.get("/dataset?q=(page:0,page_size:50)")
    if status != 200:
        log.error("Falha ao listar datasets")
        return
    log.info(f"  Total: {datasets.get('count', 0)}")

    # ─── STEP 3: VERIFY RELATIONSHIP API ────────────────
    api.step_log("Verificar Relationship API existentes")
    status_r, rels = api.get("/dataset_relationship/")
    log.info(f"  Relationships: {rels.get('count', 0)}")
    for r in rels.get("result", []):
        log.info(f"    ID={r['id']} {r.get('name','?')} | src={r['source_dataset_id']}->tgt={r['target_dataset_id']} [{r['join_type']}]")

    # ─── STEP 4: DADOS DOS DATASETS 17 e 8 (relationship #1) ──
    api.step_log("Buscar detalhes dos datasets birth_names(17) e long_lat(8)")
    for did in [17, 8]:
        s, d = api.get(f"/dataset/{did}")
        if s == 200:
            res = d.get("result", {})
            cols = res.get("columns", [])
            col_names = [c["column_name"] for c in cols]
            log.info(f"  Dataset {did}: {res.get('table_name','?')} cols={len(cols)}: {col_names[:8]}...")

    # ─── STEP 5: CRIAR NOVA RELATIONSHIP (birth_names -> long_lat já existe = ID1)
    # Vamos criar uma entre birth_names(17) e long_lat(8) mas com nome diferente
    # Primeiro ver se já existe
    existing_pairs = {(r['source_dataset_id'], r['target_dataset_id']): r for r in rels.get("result", [])}
    
    pair_key = (17, 8)
    if pair_key in existing_pairs:
        rel_id = existing_pairs[pair_key]["id"]
        log.info(f"  Relationship (17->8) ja existe: ID={rel_id}, reutilizando")
    else:
        api.step_log("Criar nova relationship birth_names(17) -> long_lat(8)")
        payload = {
            "source_dataset_id": 17,
            "target_dataset_id": 8,
            "relationship_type": "one_to_many",
            "join_type": "INNER",
            "name": "birth_names -> long_lat (state=REGION)",
            "columns": [{"source_column_name": "state", "target_column_name": "REGION", "operator": "=", "ordinal": 0}],
        }
        s, r = api.post("/dataset_relationship/", payload)
        if s in (200, 201):
            rel_id = r.get("id")
            log.info(f"  Relationship criada: ID={rel_id}")
        else:
            log.error(f"  Falha: {r}")
            rel_id = 1
            log.warning(f"  Usando relationship ID=1 como fallback")

    # ─── STEP 6: DETALHES ──────────────────────────────
    api.step_log(f"Detalhes da relationship ID={rel_id}")
    s, rd = api.get(f"/dataset_relationship/{rel_id}")
    if s == 200:
        rel_detail = rd.get("result", {})
        log.info(f"  uuid={rel_detail.get('uuid','?')}")
        log.info(f"  cols={json.dumps(rel_detail.get('columns',[]), default=str)}")
        src_ds_id = rel_detail["source_dataset_id"]
        tgt_ds_id = rel_detail["target_dataset_id"]
    else:
        src_ds_id, tgt_ds_id = 17, 8

    # ─── STEP 7: TESTAR QUERY INJECTOR ─────────────────
    api.step_log("Testar RelationshipQueryInjector (JOIN injection)")
    injector_out = exec_injector_test(rel_id, src_ds_id, tgt_ds_id)
    
    has_sql = injector_out and "INJECTED SQL" in injector_out
    log.info(f"  Injector: {'OK' if has_sql else 'FALHOU'}")

    # ─── STEP 8: CRIAR CHART ────────────────────────────
    api.step_log("Criar chart com dataset birth_names(17)")
    chart_payload = {
        "datasource_id": src_ds_id,
        "datasource_type": "table",
        "slice_name": f"Test Rel {src_ds_id}->{tgt_ds_id}",
        "viz_type": "table",
        "params": json.dumps({
            "datasource": f"{src_ds_id}__table",
            "viz_type": "table",
            "metrics": [],
            "groupby": [],
            "adhoc_filters": [],
            "row_limit": 10,
        }),
    }
    s, cr = api.post("/chart/", chart_payload)
    chart_id = cr.get("id") if s in (200, 201) else None
    log.info(f"  Chart: {'OK ID='+str(chart_id) if chart_id else 'FALHOU '+str(cr)}")

    # ─── STEP 9: CRIAR DASHBOARD ────────────────────────
    api.step_log("Criar dashboard com o chart")
    dash_payload = {
        "dashboard_title": f"Test Relationships Dashboard (rels={rel_id})",
        "slug": f"test-rels-{int(time.time())}",
        "published": True,
    }
    if chart_id:
        dash_payload["position_json"] = json.dumps({
            "DASHBOARD_VERSION_KEY": "v2",
            "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
            "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": ["CHART-1"]},
            "CHART-1": {"type": "CHART", "id": "CHART-1", "children": [],
                        "meta": {"chartId": chart_id, "width": 6, "height": 20}},
        })
    s, dr = api.post("/dashboard/", dash_payload)
    dash_id = dr.get("id") if s in (200, 201) else None
    log.info(f"  Dashboard: {'OK ID='+str(dash_id) if dash_id else 'FALHOU '+str(dr)}")

    # ─── STEP 10: TESTAR QUERY REAL ─────────────────────
    api.step_log("Testar query SQL real com JOIN (executar no banco)")
    query_out = exec_real_query(rel_id)
    has_result = query_out and "RESULT" in query_out
    log.info(f"  Query real: {'OK' if has_result else 'FALHOU'}")

    # ─── STEP 11: LISTAR RELATIONSHIPS DO DATASET ──────
    api.step_log(f"Listar relationships do dataset {src_ds_id}")
    s, rd = api.get(f"/dataset_relationship/dataset/{src_ds_id}")

    # ─── STEP 12: EXPLORE O CHART ──────────────────────
    if chart_id:
        api.step_log("Explorar o chart criado (GET /explore/)")
        log.info(f"  Explore URL: http://localhost:8088/superset/explore/?datasource_id={src_ds_id}&datasource_type=table&datasource_key={src_ds_id}__table")
        # Tentar GET na explore API
        s, ed = api.get(f"/explore/?datasource_type=table&datasource_id={src_ds_id}",
                        desc="Get explore data (tentativa de ver se JOIN aparece)")

    # ─── RESUMO ─────────────────────────────────────────
    log.info(f"\n{'#'*70}")
    log.info(f"# RESUMO FINAL")
    log.info(f"# Relationship: ID={rel_id} ({'birth_names -> long_lat' if rel_id==1 else 'other'})")
    log.info(f"# Injector:     {'OK' if has_sql else 'FALHOU'}")
    log.info(f"# Chart:        ID={chart_id or 'N/A'}")
    log.info(f"# Dashboard:    ID={dash_id or 'N/A'}")
    log.info(f"# Query real:   {'OK' if has_result else 'FALHOU'}")
    log.info(f"# Log: /root/hibi/logs/relationship_test.log")
    log.info(f"{'#'*70}")


if __name__ == "__main__":
    main()
