{{ config(
    materialized='incremental',
    partition_by={
        'field': 'movement_date',
        'data_type': 'date',
        'granularity': 'day'
    },
    cluster_by=['account_id'],
    incremental_strategy='insert_overwrite'
) }}

with source as (
    select * from {{ ref('int_account_daily_movements') }}
),

final as (
    select
        account_id,
        movement_date,
        total_credit,
        total_debit,
        net_movement
    from source

    {% if is_incremental() %}
    where movement_date >= coalesce(
        date_sub(date(_dbt_max_partition), interval 7 day),
        '2024-06-01'
    )
    {% endif %}
)

select * from final