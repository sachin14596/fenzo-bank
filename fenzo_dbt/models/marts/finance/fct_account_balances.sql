with source as(
    select * from {{ref('fct_daily_account_movements')}}
),

final as(

    select
        account_id,
        movement_date as balance_date,
        sum(net_movement) over (
        partition by account_id
        order by movement_date
        rows between unbounded preceding and current row
        ) as balance
    from source
)
select * from final