{{ config(
    materialized='table',
    cluster_by=['account_id']
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
)

select * from final