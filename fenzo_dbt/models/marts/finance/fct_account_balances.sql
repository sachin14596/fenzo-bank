{{ config(
    materialized='incremental',
    partition_by={
        'field': 'balance_date',
        'data_type': 'date',
        'granularity': 'day'
    },
    cluster_by=['account_id'],
    incremental_strategy='merge',
    unique_key=['account_id', 'balance_date']
) }}

with source as (
    select * from {{ ref('fct_daily_account_movements') }}
),

final as (
    select
        account_id,
        movement_date as balance_date,
        sum(net_movement) over (
            partition by account_id
            order by movement_date
            rows between unbounded preceding and current row
        ) as balance
    from source
),

incremental_filter as (
    select * from final

    {% if is_incremental() %}
    where balance_date >= coalesce(
        (select date_sub(max(balance_date), interval 30 day) 
         from {{ this }}),
        '2024-06-01'
    )
    {% endif %}
)

select * from incremental_filter