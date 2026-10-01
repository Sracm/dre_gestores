# DRE Gestores — MQ Hair

Painel gerencial do Demonstrativo de Resultado do Exercício (DRE) para Gestores e Diretoria da MQ Hair. Desenvolvido em Flask, com suporte a cache em memória e sincronização com banco de dados MariaDB / Oracle (Sankhya).

---

## 🔗 Links e Visões de Acesso aos Dashboards (Porta 5100)

| Visão / Gestor | Link Local (Sua Máquina) | Link de Rede (Equipe MQ) | Centros de Custo |
| :--- | :--- | :--- | :--- |
| **DRE Gestores — Geral (Diretoria)** | [http://localhost:5100/](http://localhost:5100/) | [http://10.11.1.120:5100/](http://10.11.1.120:5100/) | Todos os centros |
| **DRE Gestores — Regional FSP** | [http://localhost:5100/regional-fsp](http://localhost:5100/regional-fsp) | [http://10.11.1.120:5100/regional-fsp](http://10.11.1.120:5100/regional-fsp) | `1020000, 1010200, 1010300, 1010400` |
| **DRE Gestores — Regional SP** | [http://localhost:5100/regional-sp](http://localhost:5100/regional-sp) | [http://10.11.1.120:5100/regional-sp](http://10.11.1.120:5100/regional-sp) | `1010100` |
| **DRE Gestores — RH** | [http://localhost:5100/rh](http://localhost:5100/rh) | [http://10.11.1.120:5100/rh](http://10.11.1.120:5100/rh) | `9010000` |
| **DRE Gestores — Assistência Técnica & SAC** | [http://localhost:5100/assistencia](http://localhost:5100/assistencia) | [http://10.11.1.120:5100/assistencia](http://10.11.1.120:5100/assistencia) | `3000000, 3010000, 2010000` |
| **DRE Gestores — Logística** | [http://localhost:5100/logistica](http://localhost:5100/logistica) | [http://10.11.1.120:5100/logistica](http://10.11.1.120:5100/logistica) | `4010500, 4010600, 4010700, 4010800` |
| **DRE Gestores — Comex** | [http://localhost:5100/comex](http://localhost:5100/comex) | [http://10.11.1.120:5100/comex](http://10.11.1.120:5100/comex) | `1050000, 23000000, 23010000, 23020000, 24000000, 24010101` |
| **DRE Gestores — Desenvolvimento de Produtos** | [http://localhost:5100/produto](http://localhost:5100/produto) | [http://10.11.1.120:5100/produto](http://10.11.1.120:5100/produto) | `10020000` |
| **DRE Gestores — Marketing** | [http://localhost:5100/mkt](http://localhost:5100/mkt) | [http://10.11.1.120:5100/mkt](http://10.11.1.120:5100/mkt) | `10010000, 10011001, 10011002, 10011003, 10011005, 11010100, 11010200, 11010300, 11010400, 11010500, 20090000` |

---

## 🚀 Como Iniciar o Servidor

```bash
# Executar servidor Flask na porta 5100
python app.py
```

Ou pelo arquivo batch:
```cmd
iniciar_servidor_dre.bat
```

---

## 🔄 Atualização Automática de Dados (ETL)

O pipeline de extração e atualização (`etl/atualizar_dados.py`) é executado diariamente às **21:00** pelo Agendador de Tarefas do Windows:
- Atualiza a base incremental dos últimos **2 meses**.
- Sincroniza os dados com o banco MariaDB e invalida o cache em memória automaticamente no Flask.
