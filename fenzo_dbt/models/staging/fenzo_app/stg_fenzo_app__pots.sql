with source as (

    select * from {{ source('fenzo_app', 'pots') }}

),

renamed as (

    select
        pot_id,
        account_id,
        pot_name,
        CAST(created_at AS TIMESTAMP) as created_at,
        CAST(closed_at AS TIMESTAMP)  as closed_at,
        closed_at is null             as is_active,
        target_amount_minor_units
    from source

),

final as (

    select * from renamed

)

select * from final