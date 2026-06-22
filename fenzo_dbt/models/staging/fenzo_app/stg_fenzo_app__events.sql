with source as (

    select * from {{ source('fenzo_app', 'events') }}

),

renamed as (

    select
        event_id,
        event_timestamp,
        account_id,
        event_type,
        amount_minor_units,
        currency,
        merchant_id,
        pot_id
    from source
    qualify row_number() over (partition by event_id order by event_timestamp) = 1

),

final as (

    select * from renamed

)

select * from final