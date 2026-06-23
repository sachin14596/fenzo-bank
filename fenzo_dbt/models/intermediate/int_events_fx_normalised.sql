with events_source as(

    select * from {{ref('stg_fenzo_app__events')}}

),

fx_source as(

    select * from {{ref('fx_rates')}}

),

joined as(

    select e.*,f.rate_to_gbp
    from events_source AS e 
    left join fx_source as f
    on date(e.event_timestamp)=f.rate_date
    and e.currency=f.currency

),

transformation as(

    select
        event_id,
        event_timestamp,
        account_id,
        event_type,
        amount_minor_units,
        currency,
        merchant_id,
        pot_id,
        rate_to_gbp,
        case when currency!='GBP' then cast(round(amount_minor_units*rate_to_gbp) as int64) else amount_minor_units end as amount_gbp_minor_units 
    from joined
),

final as(

    select * from transformation

)
select * from final