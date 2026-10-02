# 📜 Histórico e Contexto da Sessão — DRE Gestores

> **Data de Fechamento da Sessão:** 02/10/2026  
> **Repositório GitHub:** `git@github.com:Sracm/dre_gestores.git` (Branch `main`)  
> **Servidor / Porta:** Flask porta `5100`  
> **IP da Máquina na Rede MQ:** `10.11.1.120`  

Este documento resume em detalhes todas as atividades, configurações e validações realizadas nesta sessão para rápida leitura e retomada.

---

## 1. ⏱️ Cronograma e Fluxo de Atualização Automática

- **Pipeline ETL:** [`etl/atualizar_dados.py`](file:///c:/Users/amello/OneDrive%20-%20MQHAIR/T.I/PROJETOS%20BI/ANTIGRAVITY/PROJETOS/Dre_Gestores/etl/atualizar_dados.py)
- **Agendamento no Windows:** [`etl/agendar_tarefa.ps1`](file:///c:/Users/amello/OneDrive%20-%20MQHAIR/T.I/PROJETOS%20BI/ANTIGRAVITY/PROJETOS/Dre_Gestores/etl/agendar_tarefa.ps1)
  - **Horário Principal:** Diariamente às **21:00** (após o fechamento das operações comerciais e financeiras no Sankhya).
  - **Modo Incremental:** Atualiza automaticamente os últimos **2 meses** (mês anterior + mês corrente) em ~5 minutos.
  - **Invalidação Dinâmica de Cache:** O Flask monitora a tabela `etl_status` a cada 5 segundos. Assim que o ETL grava um novo lote, todo o cache em memória é invalidado automaticamente, refletindo os dados novos no próximo acesso/refresh.

---

## 2. 🎯 Criação e Integração do DRE Marketing (MKT)

- **Rotas Adicionadas no [`app.py`](file:///c:/Users/amello/OneDrive%20-%20MQHAIR/T.I/PROJETOS%20BI/ANTIGRAVITY/PROJETOS/Dre_Gestores/app.py):** `/mkt` e `/marketing`.
- **Interface Web ([`templates/index.html`](file:///c:/Users/amello/OneDrive%20-%20MQHAIR/T.I/PROJETOS%20BI/ANTIGRAVITY/PROJETOS/Dre_Gestores/templates/index.html)):** Adicionada a opção **Marketing (MKT)** ao seletor de áreas/regionais.
- **Centros de Custo de Marketing Configurados:**
  - `10010000` — MARKETING
  - `10011001` — MARKETING - NACIONAL - MQ
  - `10011002` — MARKETING - NACIONAL - FORCE BARBER
  - `10011003` — MARKETING - NACIONAL - ACESSORIOS
  - `10011005` — MARKETING - DIGITAL
  - `11010100` — TRADEMARKETING - SP
  - `11010200` — TRADEMARKETING - RJ
  - `11010300` — TRADEMARKETING - ND
  - `11010400` — TRADEMARKETING - SUL
  - `11010500` — TRADEMARKETING GERAL - BUDGET
  - `20090000` — MERCADORIA - MARKETING

---

## 3. 🗄️ Migração e Apontamento para o MariaDB Central

- **Servidor:** `192.168.1.22:3306`
- **Usuário:** `antonio`
- **Banco de Dados:** `dre_gestores`
- **Configuração via [.env](file:///c:/Users/amello/OneDrive%20-%20MQHAIR/T.I/PROJETOS%20BI/ANTIGRAVITY/PROJETOS/Dre_Gestores/.env):**
  - O [`db.py`](file:///c:/Users/amello/OneDrive%20-%20MQHAIR/T.I/PROJETOS%20BI/ANTIGRAVITY/PROJETOS/Dre_Gestores/db.py) lê as credenciais automaticamente via `python-dotenv`.
  - Criado o arquivo modelo [`.env.example`](file:///c:/Users/amello/OneDrive%20-%20MQHAIR/T.I/PROJETOS%20BI/ANTIGRAVITY/PROJETOS/Dre_Gestores/.env.example).
- **Validação de Sincronização (100% Idêntico ao SQLite):**
  - `dre_data`: **45.033 linhas** (Orçado: R$ 114.431.514,82 | Realizado: R$ 109.720.833,61)
  - `dre_detalhe_fsp`: **711.212 linhas** (Orçado: R$ 15.372.466,08 | Realizado: R$ 19.249.257,06)
  - `dre_detalhe_rh`: **1.838 linhas** (Orçado: -R$ 2.521.962,82 | Realizado: -R$ 2.036.918,48)
  - `dre_resumo_mensal`: **7.838 linhas**
  - `dre_filtros_anos`: 3 linhas | `dre_filtros_centros`: 124 linhas | `dre_filtros_empresas`: 14 linhas
  - `etl_status`: 17 execuções registradas
- **Ajustes de Código:**
  - Removido `import sqlite3` obsoleto do [`app.py`](file:///c:/Users/amello/OneDrive%20-%20MQHAIR/T.I/PROJETOS%20BI/ANTIGRAVITY/PROJETOS/Dre_Gestores/app.py).
  - Corrigido o filtro de RH na API para não buscar `codcencus` inexistente em `dre_detalhe_rh`.
  - **Todas as rotas testadas retornando HTTP 200 OK.**

---

## 4. 🌐 Tabela de Links Atualizada

| Visão / Área | Link Local | Link Rede MQ (IP 10.11.1.120) | Centros de Custo |
| :--- | :--- | :--- | :--- |
| **Geral (Diretoria)** | [http://localhost:5100/](http://localhost:5100/) | [http://10.11.1.120:5100/](http://10.11.1.120:5100/) | Todos |
| **Regional FSP** | [http://localhost:5100/regional-fsp](http://localhost:5100/regional-fsp) | [http://10.11.1.120:5100/regional-fsp](http://10.11.1.120:5100/regional-fsp) | `1020000, 1010200, 1010300, 1010400` |
| **Regional SP (Varejo)** | [http://localhost:5100/regional-sp](http://localhost:5100/regional-sp) | [http://10.11.1.120:5100/regional-sp](http://10.11.1.120:5100/regional-sp) | `1010100` |
| **RH** | [http://localhost:5100/rh](http://localhost:5100/rh) | [http://10.11.1.120:5100/rh](http://10.11.1.120:5100/rh) | `9010000` |
| **Marketing** | [http://localhost:5100/mkt](http://localhost:5100/mkt) | [http://10.11.1.120:5100/mkt](http://10.11.1.120:5100/mkt) | Ver lista de 11 centros acima |
| **Assistência Técnica & SAC** | [http://localhost:5100/assistencia](http://localhost:5100/assistencia) | [http://10.11.1.120:5100/assistencia](http://10.11.1.120:5100/assistencia) | `3000000, 3010000, 2010000` |
| **Logística** | [http://localhost:5100/logistica](http://localhost:5100/logistica) | [http://10.11.1.120:5100/logistica](http://10.11.1.120:5100/logistica) | `4010500, 4010600, 4010700, 4010800` |
| **Comex** | [http://localhost:5100/comex](http://localhost:5100/comex) | [http://10.11.1.120:5100/comex](http://10.11.1.120:5100/comex) | `1050000, 23000000, ...` |
| **Desenvolvimento de Produtos** | [http://localhost:5100/produto](http://localhost:5100/produto) | [http://10.11.1.120:5100/produto](http://10.11.1.120:5100/produto) | `10020000` |
| **DRE Empresa Consolidado** | [http://localhost:5150/](http://localhost:5150/) | [http://10.11.1.120:5150/](http://10.11.1.120:5150/) | Multiempresa |

---

## 5. 🛠️ Regra Obrigatória Permanente

- **Dependências:** Sempre que uma nova biblioteca, pacote ou dependência for utilizada ou adicionada ao projeto, salvá-la imediatamente no [`requirements.txt`](file:///c:/Users/amello/OneDrive%20-%20MQHAIR/T.I/PROJETOS%20BI/ANTIGRAVITY/PROJETOS/Dre_Gestores/requirements.txt) (registrado no [`GEMINI.md`](file:///c:/Users/amello/OneDrive%20-%20MQHAIR/T.I/PROJETOS%20BI/ANTIGRAVITY/PROJETOS/Dre_Gestores/GEMINI.md)).

---

## 6. 🚀 Comandos Rápidos Globais

- `\dre`: Inicia automaticamente os servidores do DRE Gestores (5100) e DRE Empresa (5150).
- `\projetos`: Inicia simultaneamente todos os dashboards (Portal 5080, DRE Empresa 5150, DRE Gestores 5100, Dashboard TV 5050 e Painel 5000).
