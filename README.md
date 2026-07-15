# 🏦 Fenzo Bank - Analytics Engineering Project

[![dbt](https://img.shields.io/badge/dbt-1.8.2-orange?logo=dbt)](https://www.getdbt.com/)
[![BigQuery](https://img.shields.io/badge/BigQuery-Google_Cloud-blue?logo=google-cloud)](https://cloud.google.com/bigquery)
[![Python](https://img.shields.io/badge/Python-3.13-green?logo=python)](https://www.python.org/)
[![CI/CD](https://github.com/sachin14596/fenzo-bank/actions/workflows/dbt_deploy.yml/badge.svg)](https://github.com/sachin14596/fenzo-bank/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A production-grade Analytics Engineering project simulating a UK neobank data warehouse - built with **dbt Core**, **Google BigQuery**, and **Looker Studio**. Demonstrates financial reconciliation, incremental modelling, and self-serve analytics at scale.

**[📊 Live Dashboard](https://datastudio.google.com/reporting/0fc8b2ec-3896-414f-816d-a5f2467f70c3)** | **[📖 dbt Docs](https://sachin14596.github.io/fenzo-bank/)** | **[🔍 Key Results](#key-results)**

---

## Architecture

```mermaid
flowchart LR
    subgraph Generation["🐍 Data Generation"]
        PY[Python\nFaker + NumPy]
    end

    subgraph Raw["📥 Raw Layer - BigQuery"]
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

---

## Business Problem

UK neobanks process millions of financial events daily - card payments, transfers, FX conversions. The core challenge is ensuring that **computed account balances** (derived from event streams) match **stated balances** (from the core banking ledger). Discrepancies indicate data quality issues, system bugs, or potential fraud.

This project simulates that exact problem:
- **14.7M synthetic events** across 18,000 customers, 12 months of activity
- A **reconciliation mart** that compares event-derived balances against ledger snapshots
- Automated **data quality tests** that fail the build if break rate exceeds threshold

> Fenzo Bank processes millions of financial events daily across 18,000+ customers. Ensuring data integrity between event-derived balances and the core banking ledger is critical for financial reporting and regulatory compliance.

---

## Key Results

| Metric | Value |
|--------|-------|
| Events processed | 14,737,596 |
| Accounts tracked | 20,696 |
| dbt models | 13 (staging → intermediate → marts) |
| Data tests | 59 (58 PASS, 1 WARN, 0 ERROR) |
| Reconciliation accuracy | **98.9%** genuine mismatch detection |
| Break rate | **4.04%** (threshold: 5%) |
| BigQuery optimisation | `cluster_by account_id` on fact tables |
| CI/CD | GitHub Actions - PR + deploy workflows |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Warehouse | Google BigQuery (`europe-west2`) |
| Transformation | dbt Core 1.8.2 + dbt-bigquery |
| Data Generation | Python 3.13 (Faker, NumPy, Pandas) |
| BI / Dashboard | Looker Studio |
| CI/CD | GitHub Actions |
| Version Control | Git + GitHub |
| dbt Packages | dbt_utils 1.3.0 |
| Credentials | GCP Service Account (encrypted GitHub Secret) |

---

## Data Model

```mermaid
erDiagram
    dim_customers {
        string customer_id PK
        string full_name
        string email
        date date_of_birth
        date signup_date
        string country
    }

    dim_accounts {
        string account_id PK
        string customer_id FK
        string account_type
        string currency
        timestamp opened_at
        date opened_date
        string status
        string tier
    }

    fct_daily_account_movements {
        string account_id FK
        date movement_date
        int total_credit
        int total_debit
        int net_movement
    }

    fct_account_balances {
        string account_id FK
        date balance_date
        int balance
    }

    fct_reconciliation_breaks {
        string account_id FK
        date snapshot_date
        int stated_movement
        int computed_movement
        int difference
        int is_break
        float break_percentage
    }

    fct_daily_transactions_summary {
        date transaction_date
        string category
        int transaction_count
        int total_spend_gbp_minor_units
    }

    dim_customers ||--o{ dim_accounts : "has"
    dim_accounts ||--o{ fct_daily_account_movements : "tracks"
    fct_daily_account_movements ||--o{ fct_account_balances : "aggregates to"
    fct_account_balances ||--o{ fct_reconciliation_breaks : "compared in"
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Medallion + Kimball** | Staging (Silver) → Intermediate → Dimensional Marts (Gold). Star schema with `fct_` fact tables and `dim_` dimensions |
| **Month-over-month reconciliation** | Avoids opening balance issues - compares monthly movements, not absolute balances |
| **`insert_overwrite` incremental strategy** | Designed for append-only event data - replaces partitions, cheaper than `merge` at scale |
| **`europe-west2` region** | UK data residency - mirrors FCA regulatory requirements for UK financial data |
| **Auth balance reservation** | Card authorisations immediately reserve balance - prevents impossible negative balances |
| **Ground truth labelling** | ~2% deliberate ledger mismatches injected at generation - pipeline detects breaks independently, accuracy validated post-hoc |
| **Service account over OAuth** | Production standard - works in CI/CD without browser interaction |

---

## How to Run

### Prerequisites
- Python 3.10+
- Google Cloud account with BigQuery enabled
- GCP Service Account with BigQuery Admin role

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/sachin14596/fenzo-bank.git
cd fenzo-bank

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate synthetic data
python generate_data.py        # generates raw CSVs (~15 min)
python generate_data_seeds.py  # generates seed CSVs

# 5. Load to BigQuery
bq load --source_format=CSV --autodetect --skip_leading_rows=1 \
    your-project:raw.events data/events.csv
# Load other tables via BigQuery Console

# 6. Configure dbt
# Create ~/.dbt/profiles.yml (see profiles.yml.example)
cd fenzo_dbt
dbt deps
dbt debug  # verify connection

# 7. Run the pipeline
dbt build --exclude resource_type:snapshot

# 8. View docs
dbt docs generate
dbt docs serve
```

### CI/CD
Every PR to `main` triggers `dbt build` automatically via GitHub Actions.
Every merge to `main` triggers full deploy + `manifest.json` artifact upload.

---

## Project Structure

```
fenzo-bank/
├── generate_data.py          # Synthetic event data generator
├── generate_data_seeds.py    # Reference data generator
├── requirements.txt
├── .github/workflows/        # CI/CD pipelines
│   ├── dbt_ci.yml           # PR checks
│   └── dbt_deploy.yml       # Production deploy
└── fenzo_dbt/               # dbt project
    ├── models/
    │   ├── staging/          # Cleaned source data (views)
    │   ├── intermediate/     # Joined/aggregated (views)
    │   └── marts/
    │       ├── finance/      # Reconciliation, balances
    │       └── analytics/    # Spending, customers
    ├── seeds/                # Reference data (fx_rates, merchants)
    ├── snapshots/            # SCD2 account history
    ├── macros/               # Reusable SQL (cents_to_pounds)
    └── tests/                # Singular business assertions
```

---

## Dashboard

**[📊 Live Dashboard - Looker Studio](https://datastudio.google.com/reporting/0fc8b2ec-3896-414f-816d-a5f2467f70c3)**

3 pages:
- **Spending Overview** - monthly spending by category
- **Account Balances** - average daily balance trends
- **Reconciliation Health** - 4.04% break rate, monthly trend

---

## License

MIT