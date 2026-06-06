#!/usr/bin/env python3
"""
TESTE v3: Dataset Relationship Engine via API (full flow)
- Bug #1: CSRF token obrigatório só em dataset_relationship (outros endpoints não precisam)
- Bug #2: F-string/escaping em scripts injetados no container
- Bug #3: python3 import direto falha (precisa de Flask app context)
- Bug #4: docker exec python3 sem init_app
- Bug #5: GET /dataset_relationship/dataset/{id} retorna 403 Forbidden
- Bug #6: explore endpoint NÃO inclui relationships no response (ou inclui?)

Logging avançado. Cada passo documentado.
"""
import logging, sys, json, time, requests, urllib.parse

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/root/hibi/logs/relationship_v3_test.log", mode="w"),
    ],
)
log = logging.getLogger("rel_v3")
requests.packages.urllib3.disable_warnings()

BASE = "http://localhost:8088/api/v1"

class Tester:
    def __init__(self):
        self.s = requests.Session()
        self.token = None
        self.csrf = None
        self.step = 0
        self.bugs = []
        self.findings = []

    def step_log(self, desc):
        self.step += 1
        log.info(f"\n{'='*70}")
        log.info(f"STEP {self.step}: {desc}")
        log.info(f"{'='*70}")

    def report_bug(self, code, title, detail, severity="MEDIUM"):
        self.bugs.append({"code": code, "title": title, "detail": detail, "severity": severity})
        log.warning(f"\n*** BUG [{severity}] #{code}: {title}")
        log.warning(f"    {detail[:300]}")

    def report_finding(self, code, title, detail):
        self.findings.append({"code": code, "title": title, "detail": detail})
        log.info(f"\n  >> FINDING #{code}: {title}")
        log.info(f"     {detail[:300]}")

    def login(self):
        self.step_log("Login admin/admin")
        r = self.s.post(f"{BASE}/security/login",
                        json={"username": "admin", "password": "admin", "provider": "db"}, timeout=10)
        log.info(f"Status: {r.status_code}")
        assert r.status_code == 200, f"Login failed: {r.text}"
        self.token = r.json()["access_token"]
        self.s.headers.update({"Authorization": f"Bearer {self.token}"})
        log.info(f"Token: len={len(self.token)}")
        self._csrf()
        log.info(f"CSRF inicial: len={len(self.csrf)}")

    def _csrf(self):
        r = self.s.get(f"{BASE}/security/csrf_token/", timeout=10)
        if r.status_code == 200:
            self.csrf = r.json().get("result", "")
            self.s.headers.update({"X-CSRFToken": self.csrf, "Referer": "http://localhost:8088"})

    def get(self, path, label=""):
        log.info(f">> GET {BASE}{path}  [{label}]")
        r = self.s.get(f"{BASE}{path}", timeout=15)
        log.info(f"   Status: {r.status_code}")
        try:
            j = r.json()
            log.debug(f"   Body: {json.dumps(j, default=str)[:2000]}")
            return r.status_code, j
        except:
            log.warning(f"   Raw: {r.text[:300]}")
            return r.status_code, r.text

    def post(self, path, payload, label=""):
        self._csrf()
        log.info(f">> POST {BASE}{path}  [{label}]")
        log.debug(f"   Payload: {json.dumps(payload, default=str)[:2000]}")
        r = self.s.post(f"{BASE}{path}", json=payload, timeout=15)
        log.info(f"   Status: {r.status_code}")
        try:
            j = r.json()
            log.debug(f"   Response: {json.dumps(j, default=str)[:2000]}")
            return r.status_code, j
        except:
            log.warning(f"   Raw: {r.text[:500]}")
            return r.status_code, r.text

    def put(self, path, payload, label=""):
        self._csrf()
        log.info(f">> PUT {BASE}{path}  [{label}]")
        r = self.s.put(f"{BASE}{path}", json=payload, timeout=15)
        log.info(f"   Status: {r.status_code}")
        try:
            j = r.json()
            log.debug(f"   Response: {json.dumps(j, default=str)[:2000]}")
            return r.status_code, j
        except:
            return r.status_code, r.text

    def delete(self, path, label=""):
        self._csrf()
        log.info(f">> DELETE {BASE}{path}  [{label}]")
        r = self.s.delete(f"{BASE}{path}", timeout=15)
        log.info(f"   Status: {r.status_code}")
        return r.status_code, r.text if r.text else ""


def main():
    t = Tester()
    t.login()

    # ─────────────────────────────────────────────────
    # FASE 1: MA PEAGEM COMPLETA
    # ─────────────────────────────────────────────────
    t.step_log("FASE 1: MAPEAR ESTADO ATUAL")

    # 1A - Listar todos os datasets (nome + id + colunas principais)
    t.step_log("1A: Listar datasets com schema")
    st, datasets = t.get("/dataset/?q=(page:0,page_size:50)", "List datasets")
    ds_by_id = {}
    for ds in datasets.get("result", []):
        ds_by_id[ds["id"]] = ds
    
    log.info("Datasets encontrados:")
    for d in datasets.get("ids", []):
        log.info(f"  ID={d}: {ds_by_id.get(d,{}).get('table_name','?')} (db={ds_by_id.get(d,{}).get('database.id','?')})")

    # 1B - Listar relationships existentes
    t.step_log("1B: Listar relationships")
    st, rels = t.get("/dataset_relationship/", "List relationships")
    existing = {}
    for r in rels.get("result", []):
        existing[(r["source_dataset_id"], r["target_dataset_id"])] = r
        log.info(f"  ID={r['id']}: src={r['source_dataset_id']}->tgt={r['target_dataset_id']} [{r['join_type']}] \"{r.get('name','')}\"")

    # 1C - Testar bug #5: endpoint /dataset/{id}/relationships
    t.step_log("1C: Testar GET /dataset/{id}/relationships (bug #5)")
    for ds_id in [17, 22, 23]:
        st, body = t.get(f"/dataset/{ds_id}/relationships", f"Get relationships for dataset {ds_id}")
        if st == 200:
            self = t  # TODO: check
        else:
            st2, body2 = t.get(f"/dataset_relationship/dataset/{ds_id}", f"Alt endpoint rels for ds {ds_id}")

    # 1D - Buscar detalhes de datasets com relationships
    t.step_log("1D: Detalhes dos datasets envolvidos")
    for ds_id in [17, 8, 22, 23]:
        st, det = t.get(f"/dataset/{ds_id}", f"Detail ds {ds_id}")
        if st == 200:
            res = det.get("result", {})
            cols = [c["column_name"] for c in res.get("columns", [])]
            log.info(f"  Dataset {ds_id}: {res.get('table_name','?')} ({len(cols)} cols)")
            log.info(f"    Cols: {cols[:10]}{'...' if len(cols)>10 else ''}")

    # ─────────────────────────────────────────────────
    # FASE 2: CRIAR NOVO RELATIONSHIP (CRUD test)
    # ─────────────────────────────────────────────────
    t.step_log("FASE 2: TESTAR CRUD DE RELATIONSHIP")

    # 2A - CREATE: nova relationship entre birth_names(17) -> long_lat(8)
    # (já existe ID=1, mas vamos criar outra com join diferente pra testar)
    if (17, 8) in existing:
        rel_id_1 = existing[(17, 8)]["id"]
        log.info(f"  Relationship (17->8) já existe: ID={rel_id_1}")
    else:
        t.step_log("2A: Criar relationship birth_names(17)->long_lat(8)")
        payload = {
            "source_dataset_id": 17, "target_dataset_id": 8,
            "relationship_type": "one_to_many", "join_type": "LEFT",
            "name": "birth_names->long_lat (state=REGION)",
            "columns": [{"source_column_name": "state", "target_column_name": "REGION", "operator": "=", "ordinal": 0}],
        }
        st, r = t.post("/dataset_relationship/", payload)
        rel_id_1 = r.get("id")
        log.info(f"  CREATE: {'OK ID='+str(rel_id_1) if rel_id_1 else 'FALHOU: '+str(r)}")

    # 2B - Criar outra relationship entre contasareceber_faturas(23) -> contasareceber_eventos(22)
    # (já existe ID=5 com src=23->tgt=22, vamos criar uma nova src=22->tgt=23 se ID=6 já existe)
    pair_rev = (22, 23)
    if pair_rev in existing:
        rel_id_2 = existing[pair_rev]["id"]
        log.info(f"  Relationship (22->23) já existe: ID={rel_id_2}")
    else:
        t.step_log("2B: Criar relationship eventos(22)->faturas(23)")
        payload = {
            "source_dataset_id": 22, "target_dataset_id": 23,
            "relationship_type": "many_to_one", "join_type": "LEFT",
            "name": "eventos->faturas (fatura_dominio=fatura_dominio)",
            "columns": [{"source_column_name": "fatura_dominio", "target_column_name": "fatura_dominio", "operator": "=", "ordinal": 0}],
        }
        st, r = t.post("/dataset_relationship/", payload)
        rel_id_2 = r.get("id")
        log.info(f"  CREATE: {'OK ID='+str(rel_id_2) if rel_id_2 else 'FALHOU: '+str(r)}")

    # 2C - GET individual
    t.step_log("2C: GET relationship individual")
    for rid in [rel_id_1, rel_id_2]:
        st, det = t.get(f"/dataset_relationship/{rid}", f"Get rel {rid}")
        if st == 200:
            cols = det.get("result", {}).get("columns", [])
            log.info(f"  Relationship {rid}: {len(cols)} column(s)")
            for c in cols:
                log.info(f"    {c['source_column_name']} {c.get('operator','=')} {c['target_column_name']} (ord={c['ordinal']})")

    # 2D - UPDATE: PUT test
    t.step_log("2D: UPDATE relationship (PUT)")
    new_name = f"Updated via API v3 at {time.strftime('%H:%M:%S')}"
    st, up = t.put(f"/dataset_relationship/{rel_id_1}", {"name": new_name}, "Update name")
    log.info(f"  UPDATE: {'OK' if st==200 else 'FALHOU: '+str(up)}")

    # 2E - DELETE & RECREATE test (se permitido)
    t.step_log("2E: DELETE test (se idempotente)")
    st, _ = t.delete(f"/dataset_relationship/{rel_id_1}", "Delete relationship")
    if st in (200, 204):
        log.info(f"  DELETE OK: recreando...")
        payload = {
            "source_dataset_id": 17, "target_dataset_id": 8,
            "relationship_type": "one_to_many", "join_type": "LEFT",
            "name": "recreated birth_names->long_lat",
            "columns": [{"source_column_name": "state", "target_column_name": "REGION", "operator": "=", "ordinal": 0}],
        }
        st2, r2 = t.post("/dataset_relationship/", payload, "Recreate after delete")
        if st2 in (200, 201):
            rel_id_1 = r2.get("id")
            log.info(f"  RECREATED: ID={rel_id_1}")
    else:
        log.warning(f"  DELETE FALHOU (esperado se sem permissao): {st}")

    # ─────────────────────────────────────────────────
    # FASE 3: CRIAR CHART + DASHBOARD
    # ─────────────────────────────────────────────────
    t.step_log("FASE 3: CRIAR CHART COM RELATIONSHIP E DASHBOARD")

    # 3A - Criar chart usando dataset com relationship
    t.step_log("3A: Chart com birth_names (que tem relationship #1)")
    chart_payload = {
        "datasource_id": 17,
        "datasource_type": "table",
        "slice_name": f"Chart with Rel (ds=17)",
        "viz_type": "table",
        "params": json.dumps({
            "datasource": "17__table",
            "viz_type": "table",
            "metrics": [{"expressionType": "SIMPLE", "column": {"column_name": "num"}, "aggregate": "SUM", "label": "SUM(num)"}],
            "groupby": [{"column_name": "state"}],
            "adhoc_filters": [],
            "row_limit": 10,
            "include_time": False,
        }),
    }
    st, cr = t.post("/chart/", chart_payload, "Create chart")
    chart_id = cr.get("id") if st in (200, 201) else None
    log.info(f"  Chart: {'OK ID='+str(chart_id) if chart_id else 'FALHOU'}")
    if chart_id:
        self = t  # HACK: fix reference

    # 3B - Buscar dados do chart (explore) - ver se relationships aparecem
    t.step_log("3B: Verificar explore data do chart")
    st, exp = t.get(f"/explore/?datasource_type=table&datasource_id=17", "Explore with relationships")
    if st == 200:
        res = exp.get("result", {})
        ds_info = res.get("dataset", {})
        has_rels = "relationships" in ds_info
        t.report_finding("EXP-001", "Explore dataset relationships", 
                        f"Campo 'relationships' no explore: {has_rels}")
        if has_rels:
            rels_data = ds_info.get("relationships", [])
            log.info(f"  Relationships no explore: {json.dumps(rels_data, default=str)[:500]}")

    # 3C - Dashboard
    t.step_log("3C: Dashboard com chart")
    if chart_id:
        dash_payload = {
            "dashboard_title": f"Test Relationship Dashboard v3 (rels #{rel_id_1}, #{rel_id_2})",
            "slug": f"test-rels-v3-{int(time.time())}",
            "published": True,
            "position_json": json.dumps({
                "DASHBOARD_VERSION_KEY": "v2",
                "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
                "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": ["CHART-1"]},
                "CHART-1": {"type": "CHART", "id": "CHART-1", "children": [],
                            "meta": {"chartId": chart_id, "width": 6, "height": 20}},
            }),
        }
        st, dr = t.post("/dashboard/", dash_payload, "Create dashboard")
        dash_id = dr.get("id") if st in (200, 201) else None
        log.info(f"  Dashboard: {'OK ID='+str(dash_id) if dash_id else 'FALHOU'}")
    
    # 3D - Executar query via SQL Lab API (testar o JOIN implicitamente)
    t.step_log("3D: Testar execution do chart (GET chart data)")
    if chart_id:
        st, cd = t.get(f"/chart/{chart_id}/data/", "Get chart data")
        if st == 200:
            log.info(f"  Chart data OK: {json.dumps(cd, default=str)[:500]}")
        else:
            # Tenta via explore warmup
            st2, cd2 = t.get(f"/explore/?datasource_type=table&datasource_id=17&viz_type=table",
                            "Explore warmup")

    # ─────────────────────────────────────────────────
    # FASE 4: TESTAR ENDPOINTS RELACIONADOS
    # ─────────────────────────────────────────────────
    t.step_log("FASE 4: TESTAR ENDPOINTS DE DESCOBERTA")

    # 4A - Testar se existe endpoint de contextual database
    for endpoint in [
        "/dataset_relationship/",
        "/dataset_relationship/_info",
        "/dataset_relationship/related/",
    ]:
        t.get(endpoint, f"Test endpoint {endpoint}")

    # 4B - Buscar dados de um dataset que tem relationships
    t.get(f"/dataset/17?q=(columns:!(id,table_name,columns,relationships))",
          "Dataset 17 com relationships")

    # 4C - Verificar se as colunas aparecem com join hint
    t.get(f"/dataset/22?q=(columns:!(columns.column_name,columns.expression,columns.verbose_name,columns.filterable))",
          "Dataset 22 columns")

    # ─────────────────────────────────────────────────
    # RESUMO
    # ─────────────────────────────────────────────────
    log.info(f"\n{'#'*70}")
    log.info(f"# RESUMO FINAL v3")
    log.info(f"{'#'*70}")
    log.info(f"Relationships usadas: ID={rel_id_1} (17->8, birth_names->long_lat)")
    log.info(f"                      ID={rel_id_2} (22->23, eventos->faturas)")
    log.info(f"Chart ID: {chart_id or 'N/A'}")
    log.info(f"Dashboard ID: {dash_id if chart_id else 'N/A'}")
    
    if t.bugs:
        log.info(f"\n--- BUGS ENCONTRADOS ({len(t.bugs)}) ---")
        for b in t.bugs:
            log.info(f"  [{b['severity']}] #{b['code']}: {b['title']}")
    
    if t.findings:
        log.info(f"\n--- FINDINGS ({len(t.findings)}) ---")
        for f in t.findings:
            log.info(f"  #{f['code']}: {f['title']}")

    log.info(f"\nLog completo: /root/hibi/logs/relationship_v3_test.log")
    log.info(f"{'#'*70}")


if __name__ == "__main__":
    main()
