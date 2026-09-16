from app import app
import json

client = app.test_client()

print("--- Teste 1: GET /api/filtros ---")
res = client.get("/api/filtros")
print(f"Status: {res.status_code}")
data = res.get_json()
print("Anos:", data.get("anos"))
print("Empresas:", len(data.get("empresas", [])), [e["NOME"] for e in data.get("empresas", [])][:5])
print("Centros:", len(data.get("centros", [])), [c["NOME"] for c in data.get("centros", [])][:5])

print("\n--- Teste 2: GET /api/dre?ano=2026&mes=8&emp=ALL&cenc=ALL ---")
res = client.get("/api/dre?ano=2026&mes=8&emp=ALL&cenc=ALL")
print(f"Status: {res.status_code}")
data = res.get_json()
dre = data.get("dre", [])
print(f"Blocos retornados ({len(dre)}):")
for b in dre:
    print(f"  {b['bloco']:<40} Real: R$ {b['realizado']:>12,.2f} | Orc: R$ {b['orcado']:>12,.2f} | % VB Real: {b.get('pct_real')}%")

print("\n--- Teste 3: GET /api/dre/mensal?ano=2026&emp=ALL&cenc=ALL ---")
res = client.get("/api/dre/mensal?ano=2026&emp=ALL&cenc=ALL")
print(f"Status: {res.status_code}")
data = res.get_json()
print(f"Registros mensais: {len(data.get('mensal', []))}")

print("\n--- Teste 4: GET /api/dre/por-empresa?ano=2026&mes=8&cenc=ALL ---")
res = client.get("/api/dre/por-empresa?ano=2026&mes=8&cenc=ALL")
print(f"Status: {res.status_code}")
data = res.get_json()
print(f"Registros por empresa: {len(data.get('por_empresa', []))}")

print("\n--- Teste 5: GET / (HTML) ---")
res = client.get("/")
print(f"Status: {res.status_code}, HTML Length: {len(res.get_data(as_text=True))}")
