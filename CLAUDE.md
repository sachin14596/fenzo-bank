# Fenzo Bank — Project Context for Claude Code

## What is this project?
Fenzo Bank is a synthetic UK neobank analytics engineering portfolio project.
It simulates a digital bank's event stream (payments, transfers, FX conversions)
landing in BigQuery, transformed via dbt into a finance-grade data warehouse.
Primary goal: demonstrate AE skills aligned with Monzo's data stack.

## Tech Stack
- Warehouse: Google BigQuery
- Transformation: dbt Core (dbt-bigquery adapter)
- Data generation: Python (faker, numpy, pandas)
- BI: Looker Studio
- CI/CD: GitHub Actions
- dbt packages: dbt_utils, dbt_expectations

## dbt Standards (non-negotiable)
- Naming: stg_ / int_ / dim_ / fct_ prefixes strictly followed
- Staging models: materialized as view, use source() only
- Mart models: materialized as table, use ref() only
- Column names: snake_case always
- Money: always stored as amount_minor_units (pence) in raw/staging/intermediate
- Timestamps: _at suffix (created_at, settled_at). Date columns: _date suffix
- Every model must have: grain documented, all columns described in yml

## Folder Structure
- data/          → generated CSVs (raw data simulation)
- fenzo_dbt/     → dbt project (to be created)
- generate_data.py → Python data generator script

## Key Business Context
- Events table is the "firehose" — one row per event, append-only
- Ledger snapshots are generated independently — ~1-2% deliberate mismatches
- Reconciliation between computed balance vs stated balance is the centerpiece mart
- FX rates join on (event_date + currency) — NOT a simple FK join

## How to help me
- I write all code myself. Do NOT write code for me unless I explicitly ask.
- Review my code for best practice violations when I share it.
- Explain concepts when I ask "why" or "how does X work".
- Debug errors by explaining the cause — let me write the fix.
- Always refer to dbt standards section above before any suggestion.