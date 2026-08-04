with source as(
    select * from {{ref('stg_fenzo_app__pots')}}
),

final as(
    select  
        pot_id,
        account_id,
        pot_name,
        created_at,
        closed_at,
        is_active,
        target_amount_minor_units,
    from source
)

select * from final