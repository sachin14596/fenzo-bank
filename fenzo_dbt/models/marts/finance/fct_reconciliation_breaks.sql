with stated as (

    select
        account_id,
        snapshot_date,
        stated_balance_minor_units,
        lag(stated_balance_minor_units) over (
            partition by account_id
            order by snapshot_date
        ) as prev_stated_balance
    from {{ ref('stg_fenzo_app__ledger_snapshots') }}

),

-- Calculate month-over-month movement from ledger snapshots
stated_movements as (

    select
        account_id,
        snapshot_date,
        stated_balance_minor_units - prev_stated_balance as stated_movement
    from stated
    where prev_stated_balance is not null

),

-- Aggregate events into monthly movements for comparison
computed_movements as (

    select
        account_id,
        date_trunc(movement_date, month) as movement_month,
        sum(net_movement) as computed_movement
    from {{ ref('fct_daily_account_movements') }}
    group by account_id, date_trunc(movement_date, month)

),

-- Join stated and computed movements on account + month
joined as (

    select
        s.account_id,
        s.snapshot_date,
        s.stated_movement,
        c.computed_movement
    from stated_movements as s
    inner join computed_movements as c
        on s.account_id = c.account_id
        and date_trunc(s.snapshot_date, month) = c.movement_month

),

-- Flag breaks where difference exceeds threshold (100 pence = £1)
final as (

    select
        account_id,
        snapshot_date,
        stated_movement,
        computed_movement,
        computed_movement - stated_movement as difference,
        {{cents_to_pounds('computed_movement - stated_movement')}} as difference_pounds,
        case
            when abs(computed_movement - stated_movement) > 1000
            then 1 else 0
        end as is_break,
        round(
            (computed_movement - stated_movement) /
            nullif(abs(stated_movement), 0) * 100,
        2) as break_percentage
    from joined

)

select * from final