with events as (
    select * from {{ ref('int_events_fx_normalised') }}
),

merchants as (
    select * from {{ ref('merchants') }}
),

joined as (
    select
        date(e.event_timestamp) as transaction_date,
        e.event_type,
        m.category,
        e.amount_gbp_minor_units
    from events as e
    left join merchants as m
        on e.merchant_id = m.merchant_id
    where e.event_type in (
        'card_payment_settled',
        'faster_payment_out',
        'direct_debit_collected'
    )
),

final as (
    select
        transaction_date,
        category,
        count(*) as transaction_count,
        sum(abs(amount_gbp_minor_units)) as total_spend_gbp_minor_units
    from joined
    group by transaction_date, category
)

select * from final