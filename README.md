# 🏦 Fenzo Bank — Analytics Engineering Portfolio Project

[![dbt](https://img.shields.io/badge/dbt-1.8.2-orange?logo=dbt)](https://www.getdbt.com/)
[![BigQuery](https://img.shields.io/badge/BigQuery-Google_Cloud-blue?logo=google-cloud)](https://cloud.google.com/bigquery)
[![Python](https://img.shields.io/badge/Python-3.13-green?logo=python)](https://www.python.org/)
[![CI/CD](https://github.com/sachin14596/fenzo-bank/actions/workflows/dbt_deploy.yml/badge.svg)](https://github.com/sachin14596/fenzo-bank/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A production-grade Analytics Engineering project simulating a UK neobank data warehouse — built with **dbt Core**, **Google BigQuery**, and **Looker Studio**. Demonstrates financial reconciliation, incremental modelling, and self-serve analytics at scale.

**[📊 Live Dashboard](https://datastudio.google.com/reporting/0fc8b2ec-3896-414f-816d-a5f2467f70c3)** | **[📖 dbt Docs](#)** | **[🔍 Key Results](#key-results)**

---

## Architecture

```mermaid
flowchart LR
    subgraph Generation["🐍 Data Generation"]
        PY[Python\nFaker + NumPy]
    end

    subgraph Raw["📥 Raw Layer — BigQuery"]
        R1[raw.events\n14.7M rows]
        R2[raw.accounts\n20.7k rows]
        R3[raw.customers\n18k rows]
        R4[raw.ledger_snapshots\n19k rows]
    end

    subgraph dbt["⚙️ dbt Transformation"]
        subgraph Staging["Staging Layer"]
            S1[stg_events\ndeduplicated]
            S2[stg_accounts]
            S3[stg_customers]
            S4[stg_ledger_snapshots]
        end

        subgraph Intermediate["Intermediate Layer"]
            I1[int_events\nfx_normalised]
            I2[int_account\ndaily_movements]
        end

        subgraph Marts["Mart Layer"]
            M1[dim_accounts]
            M2[dim_customers]
            M3[fct_daily_account\nmovements]
            M4[fct_account\nbalances]
            M5[fct_reconciliation\nbreaks ⭐]
            M6[fct_daily_transactions\nsummary]
        end
    end

    subgraph Seeds["🌱 Seeds"]
        SE1[fx_rates\n730 rows]
        SE2[merchants\n200 rows]
    end

    subgraph BI["📊 Looker Studio"]
        L1[Spending Overview]
        L2[Account Balances]
        L3[Reconciliation Health]
    end

    subgraph CI["🔄 GitHub Actions"]
        CI1[dbt CI\non PR]
        CI2[dbt Deploy\non merge]
    end

    PY --> R1 & R2 & R3 & R4
    R1 --> S1
    R2 --> S2
    R3 --> S3
    R4 --> S4
    SE1 --> I1
    SE2 --> M6
    S1 --> I1
    S1 --> I2
    I1 --> I2
    I2 --> M3
    M3 --> M4
    M4 --> M5
    S4 --> M5
    S2 --> M1
    S3 --> M2
    M6 --> L1
    M4 --> L2
    M5 --> L3
    CI1 -.->|tests on PR| dbt
    CI2 -.->|deploys on merge| dbt
```