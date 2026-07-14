

with event_source as (

    select * from {{ ref('int_events_fx_normalised') }}

),

filtered as (

    select
        account_id,
        date(event_timestamp) as movement_date,
        amount_gbp_minor_units
    from event_source
    where event_type in (
        'card_payment_settled',
        'faster_payment_in',
        'faster_payment_out',
        'direct_debit_collected',
        'fx_conversion',
        'pot_transfer_in',
        'pot_transfer_out'
    )

),

aggregated as (

    select
        account_id,
        movement_date,
        sum(case when amount_gbp_minor_units > 0 then amount_gbp_minor_units else 0 end) as total_credit,
        sum(case when amount_gbp_minor_units < 0 then amount_gbp_minor_units else 0 end) as total_debit,
        sum(amount_gbp_minor_units) as net_movement
    from filtered
    group by account_id, movement_date

),

final as (

    select * from aggregated

)

select * from final