with source as(
    select * from {{ref('int_events_fx_normalised')}}
),

final as(
    select
        pot_id,
        account_id,
        event_type,
        amount_gbp_minor_units,
        event_timestamp
    from source 
    where event_type in ('pot_transfer_in','pot_transfer_out')
)

select * from final