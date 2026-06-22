with source as (

    select * from {{ source('fenzo_app', 'accounts') }}

),

renamed as (

    select
        account_id,
        customer_id,
        account_type,
        currency,
        CAST(opened_at AS TIMESTAMP) as opened_at,
        status,
        tier
    from source

),

final as (

    select * from renamed

)

select * from final